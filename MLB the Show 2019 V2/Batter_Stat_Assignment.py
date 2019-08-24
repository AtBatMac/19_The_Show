import pandas as pd
import numpy as np

data = pd.read_csv('daily_stat_update_df.csv')

lookup = pd.read_csv('test_dailybat_update.csv')

#Working out weighting of events

def event_percent(df):
    value_counts = df['events_group_b'].value_counts()

    data6 = value_counts.rename_axis('events_group_b').reset_index(name='counts')

    data6['percent_likliehood'] = round(data6['counts'] / data6['counts'].sum(), 3)

    return data6


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


# reassign counts to add to opposite

def event_swap(df):
    if df['event_group_c'] == 'base':

        df['event_group_c'] = 'out'

        return df

    else:

        df['event_group_c'] = 'base'

        return df



#data dataframe tidy

data2 = data[data['events_group_b'] != 'ignore']
data2['event_weighting'] = data2['pitching_group'] * data2['events_count']
data2.set_index('batter', inplace = True)


# find league average opponent faced per event

league_avg_event = data2.groupby(['events_group_b']).event_weighting.mean()
league_avg_event_df = league_avg_event.to_frame()
league_avg_event_df.rename(columns = {'event_weighting': 'league_avg_event'}, inplace = True)
league_avg_event_df.reset_index(inplace = True)


# batter percent assignment starts


batter_id = lookup['key_mlbam']
batter_list = batter_id.tolist()


#creates list of dataframes containing batter data

def bat_result_creation(bat_list):
    batter_df_list = []

    for batter in bat_list:

        try:

            bat_df = data2.loc[batter]

            batter_df_list.append(bat_df)

        except KeyError:

            continue

    return batter_df_list


# stores batters dataframes in list using id of batters playing today

batter_df_list = bat_result_creation(batter_list)

# event weighting and assignment

event_group = {'field_out' : 'out', 'strikeout': 'out', 'single': 'base', 'walk': 'base', 'double': 'base', 'home_run': 'base', 'double_play': 'out', 'triple': 'base'}
event_group_df = pd.DataFrame.from_dict(event_group, orient = 'index')
event_group_df.columns = ['event_group_c']
eg = event_group_df.reset_index()
eg.columns= ['events_group_b', 'event_group_c']


# analyses batters results and reassigns event percentages basde on quality of pitcher faced


def batter_reformat(batter_df):

    # batter_df.reset_index(inplace = True)

    # work out batter avg quality of pitcher faced per event

    avg_p_vsdf = batter_df.groupby(['events_group_b']).event_weighting.mean()

    test = avg_p_vsdf.to_frame()

    avg_p_vsdf.rename(columns={'event_weighting': 'player_avg_event'}, inplace=True)

    avg_p_vsdf.reset_index()

    avg_p_vsdf2 = avg_p_vsdf.to_frame()

    avg_p_vsdf2.rename(columns={0: 'player_avg_event'}, inplace=True)

    # add quality to main dataframe

    df_batter_func = pd.merge(batter_df, avg_p_vsdf2, how='right', left_on='events_group_b', right_on='events_group_b')

    # add percent chance of event without adjustment

    dftest = df_batter_func.groupby('batter').apply(event_percent)

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

    testdf7.set_index('batter')

    # pivot on adjusted_percent chances of each event for batter

    testdf8 = testdf7.pivot_table(index='batter', values='true_percent', columns='events_group_b')
    testdf8['at_bat_count'] = testdf7['counts'].sum()

    testdf9 = testdf8.reset_index()

    # testdf9.drop(columns = 'events_group_b', inplace = True)

    batter_stat_df = pd.read_csv('daily_bat_stats1.csv')

    batter_stat_df.reset_index(drop=True)

    # batter_stat_df.drop(columns = 'Unnamed: 0', inplace = True)

    # print(batter_stat_df)

    updated_df = batter_stat_df.append(testdf9)

    # print(updated_df)

    updated_df2 = updated_df[updated_df.columns.drop(list(updated_df.filter(regex='Unnamed')))]

    # print(updated_df2)
    updated_df2.fillna(value=0, inplace=True)

    updated_df2.to_csv('daily_bat_stats1.csv')

    # return(testdf9)


# analyses batters results and reassigns event percentages basde on quality of pitcher faced

# Need a second function to deal with exceptions resulting from some pitcher dataframes having an index set vs not set.


def batter_reformat_2(batter_df):

    batter_df.reset_index(inplace=True)

    # work out batter avg quality of pitcher faced per event

    avg_p_vsdf = batter_df.groupby(['events_group_b']).event_weighting.mean()

    test = avg_p_vsdf.to_frame()

    avg_p_vsdf.rename(columns={'event_weighting': 'player_avg_event'}, inplace=True)

    avg_p_vsdf.reset_index()

    avg_p_vsdf2 = avg_p_vsdf.to_frame()

    avg_p_vsdf2.rename(columns={0: 'player_avg_event'}, inplace=True)

    # add quality to main dataframe

    df_batter_func = pd.merge(batter_df, avg_p_vsdf2, how='right', left_on='events_group_b', right_on='events_group_b')

    # add percent chance of event without adjustment

    dftest = df_batter_func.groupby('batter').apply(event_percent)

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

    testdf7.set_index('batter')

    # pivot on adjusted_percent chances of each event for batter

    testdf8 = testdf7.pivot_table(index='batter', values='true_percent', columns='events_group_b')
    testdf8['at_bat_count'] = testdf7['counts'].sum()

    testdf9 = testdf8.reset_index()

    # testdf9.drop(columns = 'events_group_b', inplace = True)

    batter_stat_df = pd.read_csv('daily_bat_stats1.csv')

    batter_stat_df.reset_index(drop=True)

    # batter_stat_df.drop(columns = 'Unnamed: 0', inplace = True)

    # print(batter_stat_df)

    updated_df = batter_stat_df.append(testdf9)

    # print(updated_df)

    updated_df2 = updated_df[updated_df.columns.drop(list(updated_df.filter(regex='Unnamed')))]

    #print(updated_df2)

    updated_df2.fillna(value = 0, inplace=True)
    updated_df2.to_csv('daily_bat_stats1.csv')

    # return(testdf9)


#function to loop through todays starters and add there stats to the stat lookup file.

for batter in batter_df_list:

    try:
        batter_reformat(batter)

    except KeyError:

        batter_reformat_2(batter)

        continue


