import pandas as pd
import random
from classesv2 import *


#Stat import for class creation

pitcher_list = pd.read_csv('daily_pitch_stats1.csv')
batter_list = pd.read_csv('daily_bat_stats1.csv')

daily_games_df = pd.read_csv('test_dailygame_update.csv')
batter_lookup = pd.read_csv('test_dailybat_update.csv')
pitcher_lookup1 = pd.read_csv('test_dailypitch_update.csv')
pitcher_outs = pd.read_csv('outs_count_sp.csv')
bullpen_df = pd.read_csv('team_bullpens_2019.csv')

bullpen_df.fillna(value=0,inplace=True)

#tidy up dataframe

daily_games_df.drop(columns = ['Unnamed: 0'], inplace = True)
batter_list.drop(columns = 'Unnamed: 0', inplace = True)
pitcher_list.drop(columns = 'Unnamed: 0', inplace = True)
pitcher_lookup1.drop(columns = 'Unnamed: 0', inplace = True)
pitcher_outs.drop(columns = 'Unnamed: 0', inplace = True)
#bullpen_df.drop(columns = 'Unnamed: 0', inplace = True)



#function to put games into tuple

def game_day3(df):
    games = []

    for i in daily_games_df.itertuples():
        games.append(i)

    return games


gamelist = game_day3(daily_games_df)


#merge pitcher dataframes for class creation

pitcher_outs['Name'] = pitcher_outs['Name'].str.lower()

pitcher_lookup = pd.merge(pitcher_lookup1, pitcher_outs, how = 'left', left_on = 'daily player reformat', right_on = 'Name')

#merge and tidy batter dataframes for class creation

batter_lookup2 = batter_lookup[['Team_x', 'key_mlbam', 'Player_x', 'Position_x']]

daily_player_stat_df = pd.merge(batter_list, batter_lookup2, how = 'left', left_on = 'batter', right_on = 'key_mlbam')

daily_player_stat_df.fillna(0, inplace = True)

daily_player_stat_df2 = daily_player_stat_df.round(3)

daily_player_stat_df2.fillna(0, inplace = True)


#create team objects

def team_creation(game_tuple):
    team1_name = game_tuple[2]
    team2_name = game_tuple[5]

    t1 = Team(team1_name)
    t2 = Team(team2_name)

    t1.OpposingTeam = t2
    t2.OpposingTeam = t1

    return (t1, t2)

#update gamelist value to choose game to sim

game1 = gamelist[7]


#Creates Team Objects and retrives Teams batters from player dataframe

game1_teams = team_creation(game1)

t1 = game1_teams[0]
t2 = game1_teams[1]

t1_player_df = daily_player_stat_df2[daily_player_stat_df2['Team_x'] == t1.Name]
t2_player_df = daily_player_stat_df2[daily_player_stat_df2['Team_x'] == t2.Name]


#Function for creating player objects


def bat_factory_test(attribute_df):
    name = attribute_df['Player_x']

    if attribute_df['Team_x'] == t1.Name:

        myteam = t1

    else:

        myteam = t2

    bid = attribute_df['key_mlbam']

    # applies league average stats to players < 200 at bats

    if attribute_df['at_bat_count'] < 200 or None:

        # C is Chance, contains % likliehood of result

        singleC = 0.145 * 1000
        doubleC = 0.045 * 1000
        tripleC = 0.005 * 1000
        homerunC = 0.032 * 1000
        walkC = 0.093 * 1000
        soC = 0.23 * 1000
        FlyGrC = 0.429 * 1000
        DPC = 0.021 * 1000

        source = 'league avg'

        print(name + ' ' + myteam.Name + ' ' + source)


    else:

        # C is Chance, contains % likliehood of result

        singleC = attribute_df['single'] * 1000
        doubleC = attribute_df['double'] * 1000
        homerunC = attribute_df['home_run'] * 1000
        walkC = attribute_df['walk'] * 1000
        tripleC = attribute_df['triple'] * 1000
        soC = attribute_df['strikeout'] * 1000
        FlyGrC = attribute_df['field_out'] * 1000
        DPC = attribute_df['double_play'] * 1000




        source = 'player at bat'

    b = Player(name, myteam, bid, singleC, doubleC, tripleC, homerunC, walkC, soC, FlyGrC, DPC, source)

    return b


#Tidies up returned player objects and assigns to Teams

team1_batters = t1_player_df.apply(bat_factory_test, axis = 1)
team2_batters = t2_player_df.apply(bat_factory_test, axis = 1)

team1_batters_list = team1_batters.values.tolist()
team2_batters_list = team2_batters.values.tolist()

t1.Players = team1_batters_list
t2.Players = team2_batters_list


#Move onto Starting Pitchers

#Merge and Tidy Starting Pitchers for Creation

pitcher_list.fillna(0, inplace = True)
pitcher_lookup2 = pitcher_lookup[['Player_x', 'Team_x', 'key_mlbam', 'OPG']]
pitcher_list2 = pd.merge(pitcher_lookup2, pitcher_list, how = 'left', left_on = 'key_mlbam', right_on = 'pitcher')
pitcher_list3 = pitcher_list2.round(3)

pitcher_list3.fillna(0, inplace = True)


#Function for creating Starting Pitcher objects


def pitch_factory_starters(attribute_df):
    name = attribute_df['Player_x']

    if attribute_df['OPG'] == None:

        opg = 17

    else:

        opg = attribute_df['OPG']

    if attribute_df['Team_x'] == t1.Name:

        myteam = t1

    elif attribute_df['Team_x'] == t2.Name:

        myteam = t2


    else:

        return

    bid = attribute_df['key_mlbam']

    # applies league average stats to players < 120 at bats

    if attribute_df['batters_faced_count'] < 120:

        # C is Chance, contains % likliehood of result

        singleC = 0.145 * 1000
        doubleC = 0.045 * 1000
        tripleC = 0.005 * 1000
        homerunC = 0.032 * 1000
        walkC = 0.093 * 1000
        soC = 0.23 * 1000
        FlyGrC = 0.429 * 1000
        DPC = 0.021 * 1000

        source = 'league avg'

        print(name + ' ' + myteam.Name + ' ' + source)


    else:

        # C is Chance, contains % likliehood of result

        singleC = attribute_df['single'] * 1000
        doubleC = attribute_df['double'] * 1000
        tripleC = attribute_df['triple'] * 1000
        homerunC = attribute_df['home_run'] * 1000
        walkC = attribute_df['walk'] * 1000
        soC = attribute_df['strikeout'] * 1000
        FlyGrC = attribute_df['field_out'] * 1000
        DPC = attribute_df['double_play'] * 1000

        source = 'player at bat'

    p = Pitcher(name, myteam, bid, opg, singleC, doubleC, tripleC, homerunC, walkC, soC, FlyGrC, DPC, source)

    return p

#Creates and Tidies up Starting Pitcher Objects

t1_pitcher_df = pitcher_list3[pitcher_list3['Team_x'] == t1.Name]
t2_pitcher_df = pitcher_list3[pitcher_list3['Team_x'] == t2.Name]

team1_pitcher = t1_pitcher_df.apply(pitch_factory_starters, axis = 1)
team2_pitcher = t2_pitcher_df.apply(pitch_factory_starters, axis = 1)

team1_pitcher_list = team1_pitcher.tolist()
team2_pitcher_list = team2_pitcher.tolist()

pt1 = team1_pitcher_list[0]
pt2 = team2_pitcher_list[0]


#Bullpen Object Creation

bullpendf_t1 = bullpen_df.loc[bullpen_df['Team_x'] == t1.Name]
bullpendf_t2 = bullpen_df.loc[bullpen_df['Team_x'] == t2.Name]


#Function for creating Bullpen Pitcher objects


def pitch_factory_bullpen(attribute_df):
    name = attribute_df['Team']

    avgouts = 27

    if attribute_df['Team_x'] == t1.Name:

        myteam = t1

    elif attribute_df['Team_x'] == t2.Name:

        myteam = t2


    else:

        return

    bid = 50

    singleC = attribute_df['single'] * 1000
    doubleC = attribute_df['double'] * 1000
    tripleC = attribute_df['triple'] * 1000
    homerunC = attribute_df['home_run'] * 1000
    walkC = attribute_df['walk'] * 1000
    soC = attribute_df['strikeout'] * 1000
    FlyGrC = attribute_df['field_out'] * 1000
    DPC = attribute_df['double_play'] * 1000

    source = 'player at bat'

    p = Pitcher(name, myteam, bid, avgouts, singleC, doubleC, tripleC, homerunC, walkC, soC, FlyGrC, DPC, source)

    return p

#Creates and Tidies up Starting Pitcher Objects

t1_bp_series = bullpendf_t1.apply(pitch_factory_bullpen, axis = 1)
t2_bp_series = bullpendf_t2.apply(pitch_factory_bullpen, axis = 1)

t1_bp_list = t1_bp_series.tolist()
t2_bp_list = t2_bp_series.tolist()

t1_bp = t1_bp_list[0]
t2_bp = t2_bp_list[0]


#Assigns Starting Pitcher and Bullpen Pitchers to Team

t1.Pitcher = pt1
t2.Pitcher = pt2

t1.Pitchers = [pt1, t1_bp]
t2.Pitchers = [pt2, t2_bp]


Bases = [Base('The Plate'),Base('Base 1'),Base('Base 2'),Base('Base 3')]


Game1 = Game(t1, t2)

Game1.PlayRepeat(10000, Bases)

