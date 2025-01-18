from get_draws.api import get_draws
from db_queries import get_outputs
from db_queries import get_location_metadata
import pandas as pd
from db_queries import get_population 
import numpy as np

cause_id = 718
# subset to regions and global
locs = get_location_metadata(release_id=9, location_set_id=1).query("level <= 2")
loc_ids = list(locs['location_id'].unique())

draw_cols = []
for i in range(500):
    draw_cols.append(f"draw_{i}")

def calc_ratio(sex_id, location_id):
    pop = get_population(release_id=9, sex_id=sex_id, year_id=2021, location_id=location_id)

    df_2021_deaths_draws = get_draws("cause_id", source='codcorrect', gbd_id=718, release_id=9, year_id=2021, 
              location_id=location_id, age_group_id=22, sex_id=[sex_id], measure_id=1
             )

    df_2021_gun_deaths_draws = get_draws("cause_id", source='codcorrect', gbd_id=721, release_id=9, year_id=2021, 
              location_id=location_id, age_group_id=22, sex_id=[sex_id], measure_id=1
             )

    df_2021_incidence_draws = get_draws("cause_id", source='como', gbd_id=718, release_id=9, year_id=2021, 
              location_id=location_id, age_group_id=22, sex_id=[sex_id], measure_id=6)

    
    for draw in draw_cols:
        df_2021_incidence_draws[draw] = df_2021_incidence_draws[draw] * pop['population'][0]
        
    df_2021_incidence_ratio = df_2021_incidence_draws.copy()
    for draw in draw_cols:
        df_2021_incidence_ratio[draw] = df_2021_incidence_ratio[draw] / df_2021_deaths_draws[draw]
        
    df_2021_pct_firearm = df_2021_deaths_draws.copy()
    for draw in draw_cols:
        df_2021_pct_firearm[draw] = df_2021_gun_deaths_draws[draw] / df_2021_pct_firearm[draw]
    
    if sex_id == 1:
        df_2021_incidence_draws['val.incidence.Male'] = df_2021_incidence_draws[draw_cols].mean(axis=1)
        df_2021_incidence_draws['upper.incidence.Male'] = df_2021_incidence_draws.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1)
        df_2021_incidence_draws['lower.incidence.Male'] = df_2021_incidence_draws.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1)
        
        df_2021_deaths_draws['val.deaths.Male'] = df_2021_deaths_draws[draw_cols].mean(axis=1)
        df_2021_deaths_draws['upper.deaths.Male'] = df_2021_deaths_draws.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1)
        df_2021_deaths_draws['lower.deaths.Male'] = df_2021_deaths_draws.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1)
        
        df_2021_incidence_ratio['val.ratio.Male'] = df_2021_incidence_ratio[draw_cols].mean(axis=1)
        df_2021_incidence_ratio['upper.ratio.Male'] = df_2021_incidence_ratio.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1)
        df_2021_incidence_ratio['lower.ratio.Male'] = df_2021_incidence_ratio.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1)
        
        df_2021_gun_deaths_draws['val.firearm_deaths.Male'] = df_2021_gun_deaths_draws[draw_cols].mean(axis=1)
        df_2021_gun_deaths_draws['upper.firearm_deaths.Male'] = df_2021_gun_deaths_draws.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1)
        df_2021_gun_deaths_draws['lower.firearm_deaths.Male'] = df_2021_gun_deaths_draws.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1)
        
        df_2021_pct_firearm['val.firearm_pct.Male'] = df_2021_pct_firearm[draw_cols].mean(axis=1) * 100
        df_2021_pct_firearm['upper.firearm_pct.Male'] = df_2021_pct_firearm.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1) * 100
        df_2021_pct_firearm['lower.firearm_pct.Male'] = df_2021_pct_firearm.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1) * 100
        
        df_2021_incidence_draws = df_2021_incidence_draws[['location_id', 'val.incidence.Male','upper.incidence.Male','lower.incidence.Male']]
        df_2021_deaths_draws = df_2021_deaths_draws[['location_id', 'val.deaths.Male','upper.deaths.Male','lower.deaths.Male']]
        df_2021_incidence_ratio = df_2021_incidence_ratio[['location_id', 'val.ratio.Male','upper.ratio.Male','lower.ratio.Male']]
        df_2021_gun_deaths_draws = df_2021_gun_deaths_draws[['location_id', 'val.firearm_deaths.Male','upper.firearm_deaths.Male','lower.firearm_deaths.Male']]
        df_2021_pct_firearm = df_2021_pct_firearm[['location_id', 'val.firearm_pct.Male','upper.firearm_pct.Male','lower.firearm_pct.Male']]
        
        
    else: 
        df_2021_incidence_draws['val.incidence.Female'] = df_2021_incidence_draws[draw_cols].mean(axis=1)
        df_2021_incidence_draws['upper.incidence.Female'] = df_2021_incidence_draws.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1)
        df_2021_incidence_draws['lower.incidence.Female'] = df_2021_incidence_draws.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1)
        
        df_2021_deaths_draws['val.deaths.Female'] = df_2021_deaths_draws[draw_cols].mean(axis=1)
        df_2021_deaths_draws['upper.deaths.Female'] = df_2021_deaths_draws.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1)
        df_2021_deaths_draws['lower.deaths.Female'] = df_2021_deaths_draws.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1)
        
        df_2021_incidence_ratio['val.ratio.Female'] = df_2021_incidence_ratio[draw_cols].mean(axis=1)
        df_2021_incidence_ratio['upper.ratio.Female'] = df_2021_incidence_ratio.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1)
        df_2021_incidence_ratio['lower.ratio.Female'] = df_2021_incidence_ratio.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1)
        
        df_2021_gun_deaths_draws['val.firearm_deaths.Female'] = df_2021_gun_deaths_draws[draw_cols].mean(axis=1)
        df_2021_gun_deaths_draws['upper.firearm_deaths.Female'] = df_2021_gun_deaths_draws.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1)
        df_2021_gun_deaths_draws['lower.firearm_deaths.Female'] = df_2021_gun_deaths_draws.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1)
        
        df_2021_pct_firearm['val.firearm_pct.Female'] = df_2021_pct_firearm[draw_cols].mean(axis=1) * 100
        df_2021_pct_firearm['upper.firearm_pct.Female'] = df_2021_pct_firearm.apply(lambda x: np.percentile(x[draw_cols], 97.5), axis=1) * 100
        df_2021_pct_firearm['lower.firearm_pct.Female'] = df_2021_pct_firearm.apply(lambda x: np.percentile(x[draw_cols], 2.5), axis=1) * 100
        
        df_2021_incidence_draws = df_2021_incidence_draws[['location_id', 'val.incidence.Female','upper.incidence.Female','lower.incidence.Female']]
        df_2021_deaths_draws = df_2021_deaths_draws[['location_id', 'val.deaths.Female','upper.deaths.Female','lower.deaths.Female']]
        df_2021_incidence_ratio = df_2021_incidence_ratio[['location_id', 'val.ratio.Female','upper.ratio.Female','lower.ratio.Female']]
        df_2021_gun_deaths_draws = df_2021_gun_deaths_draws[['location_id', 'val.firearm_deaths.Female','upper.firearm_deaths.Female','lower.firearm_deaths.Female']]
        df_2021_pct_firearm = df_2021_pct_firearm[['location_id', 'val.firearm_pct.Female','upper.firearm_pct.Female','lower.firearm_pct.Female']]
        
    df = pd.merge(df_2021_deaths_draws, df_2021_incidence_draws).merge(df_2021_incidence_ratio).merge(df_2021_gun_deaths_draws).merge(df_2021_pct_firearm)
        
    return df

male_df = pd.DataFrame()
female_df = pd.DataFrame()
for loc in loc_ids:
    male_df = pd.concat([male_df, calc_ratio(1, loc)])
    female_df = pd.concat([female_df, calc_ratio(2, loc)])
    
df = pd.merge(male_df, female_df)

df = pd.merge(df,locs[['location_id','location_name','level','sort_order']])

df = df[['location_name',
         "level","sort_order",
         'val.deaths.Male', 'upper.deaths.Male',
       'lower.deaths.Male', 'val.incidence.Male', 'upper.incidence.Male',
       'lower.incidence.Male', 'val.ratio.Male', 'upper.ratio.Male',
       'lower.ratio.Male',
       'val.firearm_deaths.Male','upper.firearm_deaths.Male','lower.firearm_deaths.Male',
       'val.firearm_pct.Male', 'upper.firearm_pct.Male',
       'lower.firearm_pct.Male', 'val.deaths.Female', 'upper.deaths.Female',
       'lower.deaths.Female', 'val.incidence.Female', 'upper.incidence.Female',
       'lower.incidence.Female', 'val.ratio.Female', 'upper.ratio.Female',
       'lower.ratio.Female', 
       'val.firearm_deaths.Female','upper.firearm_deaths.Female','lower.firearm_deaths.Female',
       'val.firearm_pct.Female', 'upper.firearm_pct.Female',
       'lower.firearm_pct.Female']]

df = df.sort_values("val.ratio.Female", ascending=False)
df_not_global = df[df['location_name'] != 'Global']
df_global = df[df['location_name'] == 'Global']
df = pd.concat([df_global, df_not_global])

df.to_csv("table_1.csv", index=False)
