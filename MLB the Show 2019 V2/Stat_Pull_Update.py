import pandas as pd
import numpy as np
from pybaseball import statcast
from pybaseball import playerid_reverse_lookup


#june18_oct18 = pd.read_csv('2018_base_stats.csv')

#season19 = statcast('2019-03-26', '2019-04-25')

#daily_stat_update_df = season19.dropna(subset = ['events'])

#daily_stat_update_df2 = june18_oct18.append(season19, sort= True)

#daily_stat_update_df2.to_csv('percent_assign_stats_new.csv')


# read current datasource Jun 18 - today, append latest days stats and write file back

current_df = pd.read_csv('percent_assign_stats_new.csv')

current_df.to_csv('percent_assign_stats_old.csv')


update_df = statcast('2019-07-25', '2019-07-25')

#update_df.dropna(subset = 'events')

filtered_df = update_df[update_df['events'].notnull()]

#print(update_df.head())
#print(update_df.tail())

new_df = current_df.append(filtered_df, sort = True)

new_df.to_csv('percent_assign_stats_new.csv')



# 2019 only below

current_2019 = pd.read_csv('percent_assign_stats_2019.csv')

current_2019.to_csv('percent_assign_stats_old_2019.csv')

stats_2019 = statcast('2019-07-25', '2019-07-25')

filtered_stats_2019 = stats_2019[stats_2019['events'].notnull()]

new_df2 = current_2019.append(filtered_stats_2019, sort = True)

new_df2.to_csv('percent_assign_stats_2019.csv')


#update_2019 = pd.read_csv('percent_assign_stats_2019.csv')

#update_2019.to_csv('percent_assign_stats_2019_old.csv')

#new_stats = statcast('2019-05-17', '2019-05-17')

#new_stats_filtered = new_stats[new_stats['events'].notnull()]

#new_update = update_2019.append(new_stats_filtered)

#new_update.to_csv('percent_assign_stats_2019.csv')