import pandas as pd
import numpy as np
import lxml
from bs4 import BeautifulSoup
import re


tables = pd.read_html('https://en.wikipedia.org/wiki/List_of_Major_League_Baseball_team_rosters')


def clean_team(dirtylist):
    cleanlist = []

    for player in dirtylist:
        cleanplayer = player.strip()

        cleanlist.append(cleanplayer)

    return cleanlist

def run_team_update(team1):

    team1_name = team1[0][0][:-10]

    team1_pitchers = team1[0][2]

    team1_pitchers1 = re.sub("Closer", " ", team1_pitchers)

    team1p_split = team1_pitchers1.split('Bullpen')

    team1_starters = team1p_split[0]

    team1_bullpen = team1p_split[1]

    team1_starters2 = re.sub("0|1|2|3|4|5|6|7|8|9|\xa0", "(", team1_starters)


    team1_starters3 = team1_starters2.split('((')

    team1_bullpen2 = re.sub("0|1|2|3|4|5|6|7|8|9|\xa0", "(", team1_bullpen)

    team1_bullpen3 = team1_bullpen2.split('((')

### Starters into Dataframe

    starters = clean_team(team1_starters3)

    starters_final = starters[1:]

    df = pd.DataFrame(np.array(starters_final))

    df['Team'] = team1_name
    df['Position'] = 'Pitcher'
    df['Role'] = 'Starter'
    df['Roster'] = 'Active'
    df.rename(columns = {0 : 'Player'}, inplace = True)


### Bullpen into Dataframe

    team1_bullpen4 = clean_team(team1_bullpen3)
    bullpen_final = team1_bullpen4[1:]
    df2 = pd.DataFrame(np.array(bullpen_final))

    df2['Team'] = team1_name
    df2['Position'] = 'Pitcher'
    df2['Role'] = 'Bullpen'
    df2['Roster'] = 'Active'
    df2.rename(columns = {0 : 'Player'}, inplace = True)

    df_3 = df.append(df2)

    df_3.reset_index()

####### Active Batters

    team1_active_batters = team1[2][2]

    team1_bat1 = team1_active_batters.split('Infielders')

    team1_catchers = team1_bat1[0]

    team1_bat2 = team1_bat1[1].split('Outfielders')
    team1_infield = team1_bat2[0]
    team1_outfield = team1_bat2[1]

    team1_catchers1 = re.sub("0|1|2|3|4|5|6|7|8|9|\xa0|Designated hitters|designated hitters", "(", team1_catchers)
    team1_infield1 = re.sub("0|1|2|3|4|5|6|7|8|9|\xa0|Designated hitters|designated hitters", "(", team1_infield)
    team1_outfield1 = re.sub("0|1|2|3|4|5|6|7|8|9|\xa0|Designated hitters|designated hitters", "(", team1_outfield)

    team1_catchers2 = team1_catchers1.split('((')
    team1_infield2 = team1_infield1.split('((')
    team1_outfield2 = team1_outfield1.split('((')

    team1_catchers3 = team1_catchers2[1:]
    team1_infield3 = team1_infield2[1:]
    team1_outfield3 = team1_outfield2[1:]

    catchers_final = clean_team(team1_catchers3)
    infield_final = clean_team(team1_infield3)
    outfield_final = clean_team(team1_outfield3)

    df6 = pd.DataFrame(np.array(catchers_final))
    df4 = pd.DataFrame(np.array(infield_final))
    df5 = pd.DataFrame(np.array(outfield_final))

    df6['Team'] = team1_name
    df6['Position'] = 'Catcher'
    df6['Role'] = 'Batter'
    df6['Roster'] = 'Active'
    df6.rename(columns = {0 : 'Player'}, inplace = True)

    df4['Team'] = team1_name
    df4['Position'] = 'Infield'
    df4['Role'] = 'Batter'
    df4['Roster'] = 'Active'
    df4.rename(columns = {0 : 'Player'}, inplace = True)

    df5['Team'] = team1_name
    df5['Position'] = 'Outfield'
    df5['Role'] = 'Batter'
    df5['Roster'] = 'Active'
    df5.rename(columns = {0 : 'Player'}, inplace = True)

##inactive players

    inactive_list = team1[4][2]

    #print(inactive_list)

    inactive_list1 = re.sub("Pitchers|Catchers|Outfielders|Infielders|Designated hitters|designated hitters" , " ", inactive_list)
    inactive_list2 = re.sub("0|1|2|3|4|5|6|7|8|9|'\xa0'|-", "(", inactive_list1)
    inactive_list3 = inactive_list2.split('((')
    inactive_list4 = inactive_list3[1:]
    inactive_final = clean_team(inactive_list4)

    df8 = pd.DataFrame(np.array(inactive_final))

    df8['Team'] = team1_name
    df8['Position'] = 'Inactive'
    df8['Role'] = 'Inactive'
    df8['Roster'] = 'Inactive'
    df8.rename(columns = {0 : 'Player'}, inplace = True)

    id_lookup = pd.read_csv('player_lookup_master1.csv')

    id_lookup.drop(columns = ['Unnamed: 0'], inplace = True)


    df7 = df_3.append([df6, df4, df5, df8])

    df7['Player'] = df7['Player'].str.lower()


    temp_df = pd.merge(df7, id_lookup, how = 'left', left_on= 'Player', right_on= 'Player')

    temp_df['daily player reformat'] = temp_df['daily player reformat'].str.lower()

    if team1_name == 'Baltimore Orioles':

        temp_df.to_csv('active_roster.csv')

    else:

        df10 = pd.read_csv('active_roster.csv')

        df10.drop(columns=['Unnamed: 0'], inplace=True)



        df11 = df10.append(temp_df)

        df11.to_csv('active_roster.csv')