import pandas as pd
import numpy as np
import lxml
from bs4 import BeautifulSoup
import re

from Injury_Update_Logic import *


tables = pd.read_html('https://en.wikipedia.org/wiki/List_of_Major_League_Baseball_team_rosters')

team_list = tables[0:30]

#run_team_update(team_list[0])

for team in team_list:

    run_team_update(team)

final_update = pd.read_csv('active_roster.csv')

final_update.drop(columns=['Unnamed: 0', 'Team_y', 'Position_y', 'Role_y', 'Roster_y'], inplace=True)

final_update.to_csv('active_roster.csv')