import pandas as pd
import numpy as np
from pybaseball import statcast
from pybaseball import playerid_reverse_lookup


def pitcher_result(data):
    total_events_value = data['events_value'].sum()

    total_events_count = data['events_count'].sum()

    if total_events_count >= 400:

        data['pitcher_value'] = total_events_value / total_events_count

        return data

    elif total_events_count < 400 and total_events_count >= 350:

        data['pitcher_value'] = (total_events_value / total_events_count) + 0.01

        return data

    elif total_events_count < 350 and total_events_count >= 300:

        data['pitcher_value'] = (total_events_value / total_events_count) + 0.02

        return data


    elif total_events_count < 300 and total_events_count >= 250:

        data['pitcher_value'] = (total_events_value / total_events_count) + 0.03

        return data

    elif total_events_count < 250 and total_events_count >= 200:

        data['pitcher_value'] = (total_events_value / total_events_count) + 0.04

        return data

    elif total_events_count < 200 and total_events_count >= 150:

        data['pitcher_value'] = (total_events_value / total_events_count) + 0.05

        return data


    else:

        data['pitcher_value'] = (total_events_value / total_events_count) + 0.06

        return data


def pitching_group(df):
    pitcher_ranking = df['pitcher_value'].mean()

    if pitcher_ranking < 0.4:

        df['pitching_group'] = 1.4

        return df

    elif pitcher_ranking >= 0.4 and pitcher_ranking < 0.48:

        df['pitching_group'] = 1

        return df

    else:

        df['pitching_group'] = 0.75

        return df


def ob_value(df):
    df['on_base_value'] = df['pitching_group'] * df['obp_value']

    return df


def bat_obp_group(df):
    if df['standard_obp'] >= 0.370:

        df['obp_group'] = 1

        return df

    elif df['standard_obp'] >= 0.305 and df['standard_obp'] < 0.370:

        df['obp_group'] = 2

        return df


    else:

        df['obp_group'] = 3

        return df


def batter_obp(df):

    total_ob_events_value = df['on_base_value'].sum()

    total_ob_events_count = df['pitching_group'].sum()

    events_count = df['events_count'].sum()

    obp_value = df['obp_value'].sum()

    df['true_obp'] = total_ob_events_value / total_ob_events_count

    df['standard_obp'] = obp_value / events_count

    df['event_count'] = events_count

    return df

players_raw = pd.read_csv('percent_assign_stats_new.csv')


lookup_dict = {'events': ['field_out', 'double', 'single', 'strikeout', 'field_error',
       'walk', 'home_run', 'triple', 'force_out', 'hit_by_pitch',
       'grounded_into_double_play', 'sac_bunt', 'strikeout_double_play',
       'sac_fly', 'caught_stealing_2b', 'fielders_choice_out',
       'double_play', 'pickoff_1b', 'catcher_interf',
       'caught_stealing_3b', 'sac_fly_double_play', 'pickoff_2b',
       'pickoff_caught_stealing_2b', 'other_out', 'fielders_choice',
       'triple_play', 'caught_stealing_home', 'sac_bunt_double_play',
       'pickoff_caught_stealing_3b', 'pickoff_caught_stealing_home',
       'pickoff_3b', 'run', 'batter_interference'],
              'events_value': [0, 2, 1, 0, 0, 1, 4, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}



lookup_df = pd.DataFrame(lookup_dict)





season1 = pd.merge(players_raw, lookup_df, how = 'left')

season1['events_count'] = 1

season2 = season1[['game_date', 'player_name', 'pitcher', 'events', 'events_value', 'events_count', 'batter']]

season2a = season2.dropna(subset = ['events'])

season3 = season2a.groupby('player_name').apply(pitcher_result)

season4 = season3[['player_name', 'pitcher_value']]

season4dict = season4.set_index('player_name').to_dict()

season5 = pd.DataFrame.from_dict(season4dict)

season5['player_name'] = season5.index

season6 = pd.merge(season2, season5, how = 'outer')

season7 = season6.groupby('player_name').apply(pitching_group)

onbase_lookup_dict = {'events': ['field_out', 'double', 'single', 'strikeout', 'field_error',
       'walk', 'home_run', 'triple', 'force_out', 'hit_by_pitch',
       'grounded_into_double_play', 'sac_bunt', 'strikeout_double_play',
       'sac_fly', 'caught_stealing_2b', 'fielders_choice_out',
       'double_play', 'pickoff_1b', 'catcher_interf',
       'caught_stealing_3b', 'sac_fly_double_play', 'pickoff_2b',
       'pickoff_caught_stealing_2b', 'other_out', 'fielders_choice',
       'triple_play', 'caught_stealing_home', 'sac_bunt_double_play',
       'pickoff_caught_stealing_3b', 'pickoff_caught_stealing_home',
       'pickoff_3b', 'run', 'batter_interference'],
              'obp_value': [0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}


on_base_df = pd.DataFrame(onbase_lookup_dict)

season8 = pd.merge(season7, on_base_df, how = 'left')

season9 = season8.groupby('batter').apply(ob_value)

season10 = season9.groupby('batter').apply(batter_obp)

df2 = season10[['batter', 'standard_obp']]

df_lookup = df2.drop_duplicates(subset = 'batter', keep = 'first')

dfgroup = df_lookup.apply(bat_obp_group, axis = 1)

df4 = pd.merge(season10, dfgroup, how = 'left')

lookup_dict_bats = {'events': ['field_out', 'double', 'single', 'strikeout', 'field_error',
       'walk', 'home_run', 'triple', 'force_out', 'hit_by_pitch',
       'grounded_into_double_play', 'sac_bunt', 'strikeout_double_play',
       'sac_fly', 'caught_stealing_2b', 'fielders_choice_out',
       'double_play', 'pickoff_1b', 'catcher_interf',
       'caught_stealing_3b', 'sac_fly_double_play', 'pickoff_2b',
       'pickoff_caught_stealing_2b', 'other_out', 'fielders_choice',
       'triple_play', 'caught_stealing_home', 'sac_bunt_double_play',
       'pickoff_caught_stealing_3b', 'pickoff_caught_stealing_home',
       'pickoff_3b', 'run', 'batter_interference'],
              'events_group_b': ['field_out', 'double', 'single', 'strikeout', 'field_out', 'walk', 'home_run', 'triple',
                               'field_out', 'walk', 'double_play', 'ignore' , 'strikeout', 'ignore','ignore', 'field_out', 'double_play',
                               'ignore','ignore', 'ignore', 'ignore', 'ignore', 'ignore','ignore', 'field_out', 'double_play', 'ignore','ignore','ignore','ignore','ignore', 'ignore', 'ignore']}


lookup_dict_bats_2 = {'events_group_b': ['strikeout','field_out', 'home_run', 'single', 'walk',
       'ignore', 'double_play', 'triple', 'double'],
               'events_group_b_result': ['Out', 'Out', 'On_Base', 'On_Base', 'On_Base', 'Out', 'Out', 'On_Base', 'On_Base']}


lookup_df_bats = pd.DataFrame(lookup_dict_bats)
lookup_df_bats_2 = pd.DataFrame(lookup_dict_bats_2)

df5 = pd.merge(df4, lookup_df_bats, how = 'left')
df6 = pd.merge(df5, lookup_df_bats_2, how = 'left')

df6.set_index('pitcher', inplace = True)

#print(df6.columns)

df6.to_csv('daily_stat_update_df.csv')