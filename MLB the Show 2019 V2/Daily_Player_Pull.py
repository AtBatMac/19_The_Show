import pandas as pd
import numpy as np
import lxml
import pybaseball
from bs4 import BeautifulSoup
import requests


def daily_player_scrape():
    playerlist = []

    players = [div.a for div in
               soup.findAll('li', attrs={'class': 'lineup__player'})]

    for link in players:
        playerlist.append(link['title'])

    return playerlist


def daily_pitcher_scrape():
    pitcherlist = []

    for pitcher in pitchers:
        pitcherlist.append(pitcher.text)

    return pitcherlist


def get_away_team():
    a = []

    for team in soup.find_all('div', class_="lineup__mteam is-visit"):
        a.append(team.text)

    return a


def awayteamlist(dirtylist):
    awayteamlist = []

    for team in dirtylist:
        b = team[3:]

        c = '('
        rest = b.split(c, 1)[0].strip()

        awayteamlist.append(rest)

    return awayteamlist


def get_home_team():
    h = []

    for team in soup.find_all('div', class_="lineup__mteam is-home"):
        h.append(team.text)

    return h


def hometeamlist(dirtylist):
    hometeamlist = []

    for team in dirtylist:
        b = team[3:]

        c = '('
        rest = b.split(c, 1)[0].strip()

        hometeamlist.append(rest)

    return hometeamlist


page = requests.get('https://www.rotowire.com/baseball/daily-lineups.php')

soup = BeautifulSoup(page.content, 'html.parser')

hometeam = get_home_team()
awayteam = get_away_team()

hometeam_array = hometeamlist(hometeam)
awayteam_array = awayteamlist(awayteam)

hometeam_df = pd.DataFrame(np.array(hometeam_array))
awayteam_df = pd.DataFrame(np.array(awayteam_array))

hometeam_df.rename(columns = {0 : 'home'}, inplace = True)
awayteam_df.rename(columns = {0 : 'away'}, inplace = True)

teamname_df = pd.read_csv('teamlookup.csv')

hometeam = pd.merge(hometeam_df, teamname_df, how = 'left', left_on = 'home', right_on = 'Team Y')

awayteam = pd.merge(awayteam_df, teamname_df, how = 'left', left_on = 'away', right_on = 'Team Y')


daily_matchup = pd.concat([awayteam, hometeam], axis = 1)



dailyplayers = daily_player_scrape()

pitchers = [div.a for div in soup.findAll('li', attrs={'class': 'lineup__player-highlight mb-0'})]

dailypitchers = daily_pitcher_scrape()


player_lookup = pd.read_csv('active_roster.csv')

player_lookup.drop(columns = ['Unnamed: 0'], inplace = True)

dailyplayers_df = pd.DataFrame(np.array(dailyplayers))
dailyplayers_df.rename(columns = {0 : 'Player'}, inplace = True)

dailypitchers_df = pd.DataFrame(np.array(dailypitchers))
dailypitchers_df.rename(columns = {0 : 'Player'}, inplace = True)


dailyplayers_df['Player'] = dailyplayers_df['Player'].str.lower()
dailypitchers_df['Player'] = dailypitchers_df['Player'].str.lower()

test_bat_df = pd.merge(dailyplayers_df, player_lookup, how = 'left', left_on = 'Player', right_on = 'daily player reformat')

test_pitch_df = pd.merge(dailypitchers_df, player_lookup, how = 'left', left_on = 'Player', right_on = 'daily player reformat')

#test_df.drop_duplicates(subset = ['key_mlbam'], inplace = True)

test_bat_df.to_csv('test_dailybat_update.csv')

test_pitch_df.to_csv('test_dailypitch_update.csv')

daily_matchup.to_csv('test_dailygame_update.csv')

