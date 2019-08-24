import pandas as pd
from pybaseball import pitching_stats_bref

#data files

data = pd.read_csv('daily_stat_update_df.csv')
data5 = pd.read_csv('daily_stat_update_df2.csv')
lookup = pd.read_csv('test_dailypitch_update.csv')
active_roster = pd.read_csv('active_roster.csv')

#data files tidy

active_roster.drop(columns = 'Unnamed: 0', inplace = True)

#Working out weighting of events

def event_percent(df):
    value_counts = df['events_group_b'].value_counts()

    data5 = value_counts.rename_axis('events_group_b').reset_index(name='counts')

    data5['percent_likliehood'] = round(data5['counts'] / data5['counts'].sum(), 3)

    return data5


# Function to find amount to remove from counts

def per_cent_weight_event(df):
    df['weight_event'] = df['counts'] / df['out_base']

    df['percent_assign'] = df['percent_likliehood'] - df['adjusted_percent']

    df['event_count_to_remove'] = df['counts'] * df['percent_assign']

    return df


# reassign counts to add to opposite

def event_swap(df):
    if df['event_group_c'] == 'base':

        df['event_group_c'] = 'out'

        return df

    else:

        df['event_group_c'] = 'base'

        return df


# ignore events that aren't relevant and finds weighting for event

data2 = data[data['events_group_b'] != 'ignore']
data2['event_weighting'] = data2['obp_group'] * data2['events_count']
data2.set_index('pitcher', inplace = True)

data6 = data5[data5['events_group_b'] != 'ignore']
data6['event_weighting'] = data6['obp_group'] * data6['events_count']
data6.set_index('pitcher', inplace = True)


# find league average opponent faced per event

league_avg_event = data2.groupby(['events_group_b']).event_weighting.mean()
league_avg_event_df = league_avg_event.to_frame()
league_avg_event_df.rename(columns = {'event_weighting': 'league_avg_event'}, inplace = True)
league_avg_event_df.reset_index(inplace = True)


# Pitcher value assignment

# Find Todays Starters

pitcher_id = lookup['key_mlbam']
starting_pitcher_list = pitcher_id.tolist()

# Creates a list of dataframes containing pitcher events from data source

def pitcher_result_creation(pitch_list):
    pitcher_df_list = []

    for pitcher in pitch_list:

        try:

            pitch_df = data2.loc[pitcher]

            pitcher_df_list.append(pitch_df)

        except KeyError:

            continue

    return pitcher_df_list


starting_pitcher_df_list = pitcher_result_creation(starting_pitcher_list)

# event_mapping for event percents

event_group = {'field_out' : 'out', 'strikeout': 'out', 'single': 'base', 'walk': 'base', 'double': 'base', 'home_run': 'base', 'double_play': 'out', 'triple': 'base'}
event_group_df = pd.DataFrame.from_dict(event_group, orient = 'index')
event_group_df.columns = ['event_group_c']
eg = event_group_df.reset_index()
eg.columns= ['events_group_b', 'event_group_c']


# analyses pitchers results and reassigns event percentages basde on quality of batter faced

def pitcher_reformat(pitcher_df):
    # pitcher_df.reset_index(inplace = True)

    # work out batter avg quality of pitcher faced per event

    avg_p_vsdf = pitcher_df.groupby(['events_group_b']).event_weighting.mean()

    test = avg_p_vsdf.to_frame()

    avg_p_vsdf.rename(columns={'event_weighting': 'player_avg_event'}, inplace=True)

    avg_p_vsdf.reset_index()

    avg_p_vsdf2 = avg_p_vsdf.to_frame()

    avg_p_vsdf2.rename(columns={0: 'player_avg_event'}, inplace=True)

    # add quality to main dataframe

    df_pitcher_func = pd.merge(pitcher_df, avg_p_vsdf2, how='right', left_on='events_group_b',
                               right_on='events_group_b')

    # add percent chance of event without adjustment

    dftest = df_pitcher_func.groupby('pitcher').apply(event_percent)

    dftest6 = dftest.reset_index()

    avg_p_vsdf.reset_index()

    # add avg quality of pitcher faced by batter to DF

    testdf2 = pd.merge(dftest6, avg_p_vsdf2, how='left', left_on='events_group_b', right_on='events_group_b')

    # add avg quality of pitcher faced by league to DF

    testdf3 = pd.merge(testdf2, league_avg_event_df, how='left', left_on='events_group_b', right_on='events_group_b')

    testdf3['adjusted_percent'] = testdf3['percent_likliehood'] * (
                testdf3['player_avg_event'] / testdf3['league_avg_event'])
    testdf3['percent_var'] = (testdf3['player_avg_event'] - testdf3['league_avg_event']) / testdf3['league_avg_event']
    decimals = pd.Series([2, 2, 2, 3],
                         index=['player_avg_event', 'league_avg_event', 'percent_var', 'adjusted_percent'])

    testdf3.round(decimals)

    # add grouping for out or base

    testdf4 = pd.merge(testdf3, eg, how='left', left_on='events_group_b', right_on='events_group_b')

    out_base = testdf4.groupby('event_group_c').sum()['counts']

    out_base_lookup = pd.Series.to_frame(out_base)

    out_base_lookup2 = out_base_lookup.reset_index()

    out_base_lookup2.columns = ['event_group_c', 'out_base']

    # Adds column to sum outs and bases

    testdf5 = pd.merge(testdf4, out_base_lookup2, how='left')

    # Adds column to show volume of events to move

    testdf6 = testdf5.apply(per_cent_weight_event, axis=1)

    event_move = testdf6.groupby('event_group_c').sum()['event_count_to_remove']

    e_group = pd.Series.to_frame(event_move)

    e_group2 = e_group.reset_index()

    # Swapping events around

    e_group3 = e_group2.apply(event_swap, axis=1)
    e_group3.columns = ['event_group_c', 'event_val_swap']

    # adds total events to each row for events now swapped

    testdf7 = pd.merge(testdf6, e_group3, how='left')

    # Add columns to df to work out adjusted percent

    testdf7['event_add'] = testdf7['event_val_swap'] * testdf7['weight_event']
    testdf7['true_event_value'] = testdf7['counts'] - testdf7['event_count_to_remove'] + testdf7['event_add']
    testdf7["true_event_value"] = testdf7['true_event_value'].round().astype(int)

    testdf7['true_percent'] = testdf7['true_event_value'] / testdf7['true_event_value'].sum()

    decimals2 = pd.Series([3], index=['true_percent'])

    testdf7.round(decimals)

    total = testdf7['true_event_value'].sum()

    testdf7.set_index('pitcher')

    # pivot on adjusted_percent chances of each event for batter

    testdf8 = testdf7.pivot_table(index='pitcher', values='true_percent', columns='events_group_b')
    testdf8['batters_faced_count'] = testdf7['counts'].sum()

    testdf9 = testdf8.reset_index()

    # testdf9.drop(columns = 'events_group_b', inplace = True)

    pitcher_stat_df = pd.read_csv('daily_pitch_stats1.csv')

    pitcher_stat_df.reset_index(drop=True)

    # batter_stat_df.drop(columns = 'Unnamed: 0', inplace = True)

    print(pitcher_stat_df)

    updated_df = pitcher_stat_df.append(testdf9)

    # print(updated_df)

    updated_df2 = updated_df[updated_df.columns.drop(list(updated_df.filter(regex='Unnamed')))]

    updated_df2.fillna(value=0, inplace=True)

    updated_df2.to_csv('daily_pitch_stats1.csv')

    # return(testdf9)


# analyses pitchers results and reassigns event percentages basde on quality of batter faced

# Need a second function to deal with exceptions resulting from some pitcher dataframes having an index set vs not set.

def pitcher_reformat_2(pitcher_df):
    pitcher_df.reset_index(inplace=True)

    # work out batter avg quality of pitcher faced per event

    avg_p_vsdf = pitcher_df.groupby(['events_group_b']).event_weighting.mean()

    test = avg_p_vsdf.to_frame()

    avg_p_vsdf.rename(columns={'event_weighting': 'player_avg_event'}, inplace=True)

    avg_p_vsdf.reset_index()

    avg_p_vsdf2 = avg_p_vsdf.to_frame()

    avg_p_vsdf2.rename(columns={0: 'player_avg_event'}, inplace=True)

    # add quality to main dataframe

    df_pitcher_func = pd.merge(pitcher_df, avg_p_vsdf2, how='right', left_on='events_group_b',
                               right_on='events_group_b')

    # add percent chance of event without adjustment

    dftest = df_pitcher_func.groupby('pitcher').apply(event_percent)

    dftest6 = dftest.reset_index()

    avg_p_vsdf.reset_index()

    # add avg quality of pitcher faced by batter to DF

    testdf2 = pd.merge(dftest6, avg_p_vsdf2, how='left', left_on='events_group_b', right_on='events_group_b')

    # add avg quality of pitcher faced by league to DF

    testdf3 = pd.merge(testdf2, league_avg_event_df, how='left', left_on='events_group_b', right_on='events_group_b')

    testdf3['adjusted_percent'] = testdf3['percent_likliehood'] * (
                testdf3['player_avg_event'] / testdf3['league_avg_event'])
    testdf3['percent_var'] = (testdf3['player_avg_event'] - testdf3['league_avg_event']) / testdf3['league_avg_event']
    decimals = pd.Series([2, 2, 2, 3],
                         index=['player_avg_event', 'league_avg_event', 'percent_var', 'adjusted_percent'])

    testdf3.round(decimals)

    # add grouping for out or base

    testdf4 = pd.merge(testdf3, eg, how='left', left_on='events_group_b', right_on='events_group_b')

    out_base = testdf4.groupby('event_group_c').sum()['counts']

    out_base_lookup = pd.Series.to_frame(out_base)

    out_base_lookup2 = out_base_lookup.reset_index()

    out_base_lookup2.columns = ['event_group_c', 'out_base']

    # Adds column to sum outs and bases

    testdf5 = pd.merge(testdf4, out_base_lookup2, how='left')

    # Adds column to show volume of events to move

    testdf6 = testdf5.apply(per_cent_weight_event, axis=1)

    event_move = testdf6.groupby('event_group_c').sum()['event_count_to_remove']

    e_group = pd.Series.to_frame(event_move)

    e_group2 = e_group.reset_index()

    # Swapping events around

    e_group3 = e_group2.apply(event_swap, axis=1)
    e_group3.columns = ['event_group_c', 'event_val_swap']

    # adds total events to each row for events now swapped

    testdf7 = pd.merge(testdf6, e_group3, how='left')

    # Add columns to df to work out adjusted percent

    testdf7['event_add'] = testdf7['event_val_swap'] * testdf7['weight_event']
    testdf7['true_event_value'] = testdf7['counts'] - testdf7['event_count_to_remove'] + testdf7['event_add']
    testdf7["true_event_value"] = testdf7['true_event_value'].round().astype(int)

    testdf7['true_percent'] = testdf7['true_event_value'] / testdf7['true_event_value'].sum()

    decimals2 = pd.Series([3], index=['true_percent'])

    testdf7.round(decimals)

    total = testdf7['true_event_value'].sum()

    testdf7.set_index('pitcher')

    # pivot on adjusted_percent chances of each event for batter

    testdf8 = testdf7.pivot_table(index='pitcher', values='true_percent', columns='events_group_b')
    testdf8['batters_faced_count'] = testdf7['counts'].sum()

    testdf9 = testdf8.reset_index()

    # testdf9.drop(columns = 'events_group_b', inplace = True)

    pitcher_stat_df = pd.read_csv('daily_pitch_stats1.csv')

    pitcher_stat_df.reset_index(drop=True)

    # batter_stat_df.drop(columns = 'Unnamed: 0', inplace = True)



    updated_df = pitcher_stat_df.append(testdf9)

    # print(updated_df)

    updated_df2 = updated_df[updated_df.columns.drop(list(updated_df.filter(regex='Unnamed')))]
    updated_df2.fillna(value=0, inplace=True)
    #print(updated_df2)

    updated_df2.to_csv('daily_pitch_stats1.csv')


#function to loop through todays starters and add there stats to the stat lookup file.


for pitcher in starting_pitcher_df_list:

    try:
        pitcher_reformat(pitcher)

    except KeyError:

        pitcher_reformat_2(pitcher)

        continue



# Avg Outs worked out from different data source

data = pitching_stats_bref(2019)

df_outs = data[['Name', 'G', 'GS', 'SV', 'IP']]


#innings pitched turned to outs

def outs(outs_df):
    outs_df['Outs'] = outs_df['IP'] * 3

    return outs_df


# avg outs per game calculation


def outs_per(df):
    opg = df['Outs'] / df['G']

    df['OPG'] = round(opg)

    return df


#avg outs worked out and saved as csv for adding to class later

pitcher_outs = outs(df_outs)
pitcher_outs_pg = outs_per(pitcher_outs)
pitcher_outs_pg1 = pitcher_outs_pg[['Name', 'OPG']]

pitcher_outs_pg1.to_csv('outs_count_sp.csv')


# Bullpen assignment (combine results from all active bullpen pitchers for team, can use 2019 stats)


#tidy up bullpen dataframe

active_bullpen = active_roster.loc[active_roster['Role_x'] == 'Bullpen']
data5.reset_index(inplace = True)

testdata = pd.merge(data5, active_bullpen, how = 'left', left_on = 'pitcher', right_on = 'key_mlbam')

testdata2 = testdata[testdata['key_mlbam'].notnull()]
testdata2['Team_y'] = testdata2['Team_x']


#assign percent values to event using results from bullpen from each team

def bullpen_create(df):
    value_counts = df['events_group_b'].value_counts()

    df.reset_index(inplace=True)

    team_name = df['Team_y'].unique()[0] + ' Bullpen'

    df2 = value_counts.rename_axis('events_group_b').reset_index(name='counts')

    df2['percent_likliehood'] = round(df2['counts'] / df2['counts'].sum(), 3)

    df2['Team'] = team_name

    bullpen_df = df2.pivot_table(index='Team', values='percent_likliehood', columns='events_group_b')

    bullpen_df['batters_faced_count'] = df2['counts'].sum()

    return bullpen_df


testbullpen = testdata2.groupby('Team_x').apply(bullpen_create)

testbullpen.to_csv('team_bullpens_2019.csv')







