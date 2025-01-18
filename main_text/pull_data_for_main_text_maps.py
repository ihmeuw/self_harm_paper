import pandas as pd
from db_queries import get_outputs


map1 = get_outputs("cause", cause_id=718, year_id=2021, 
                 location_id='lvl3', measure_id=1, metric_id= 3, sex_id=3,
                 age_group_id=27, gbd_round_id=7, release_id=9, compare_version_id=7948)

map1_df = map1[['location_id','sex_id','cause_id','val',
                'lower','upper']]
map1_df.to_csv('FILEPATH/self_harm_asmr_2021_results.csv',index=False)

map2 = get_outputs("cause", cause_id=721, year_id=2021, 
                 location_id='lvl3', measure_id=1, metric_id= 3, sex_id=3,
                 age_group_id=27, gbd_round_id=7, release_id=9, compare_version_id=7948)


map2_df = map2[['location_id','sex_id','cause_id','val',
                'lower','upper']]
map2_df.to_csv('FILEPATH/self_harm_by_firearm_asmr_2021_results.csv',index=False)













