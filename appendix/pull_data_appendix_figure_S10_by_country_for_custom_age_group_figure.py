from db_queries import get_outputs
from db_queries import get_location_metadata
from db_queries import get_age_metadata
from db_queries import get_population
from db_queries import get_cause_metadata

import pandas as pd
import numpy as np

def get_age_ids(age_start, age_end, ages):
    age_ids = ages[(
        (ages['age_group_years_start'] >= age_start) & 
        (ages['age_group_years_end'] <= age_end+1)
    )].age_group_id.unique()
    
    return age_ids

def pull_age_group_results(age_group_ids, start_year, age_group_string):
    causes = get_cause_metadata(release_id=9, cause_set_id=3) 
    causes = causes.query("level == 3")
    cause_ids = list(causes['cause_id'].unique())
    
    
    # subset to regions and global
    locs = get_location_metadata(release_id=9, location_set_id=1).query("level == 3")
    loc_ids = list(locs['location_id'].unique())
    
    # pull deaths
    df_deaths = get_outputs('cause', release_id=9, cause_id=cause_ids,
                      metric_id=1, age_group_id=age_group_ids, year_id=list(range(start_year,2022)),
                      location_id=loc_ids, sex_id=[1,2]
                     )
    df_deaths = df_deaths.groupby(['location_id','location_name','sex_id','sex','cause_id'], as_index=False)['val','upper','lower'].sum()
    
    # pull population
    population = get_population(release_id=9, age_group_id=age_group_ids, 
                                    year_id=list(range(start_year,2022)),
                                    location_id=loc_ids, sex_id=[1,2]
                                   )
    
    population = population.groupby(['location_id','sex_id'], as_index=False)['population'].sum()
    
    df = pd.merge(df_deaths, population)
    
    df[f'val.mr_rate_{age_group_string}'] = (df['val'] / df['population']) * 100000
    df[f'upper.mr_rate_{age_group_string}'] = (df['upper'] / df['population']) * 100000
    df[f'lower.mr_rate_{age_group_string}'] = (df['lower'] / df['population']) * 100000
    
    df = df[['location_id','location_name','sex_id','sex','cause_id',f'val.mr_rate_{age_group_string}',f'upper.mr_rate_{age_group_string}',f'lower.mr_rate_{age_group_string}']]
    
    return df

def main():

    ages = get_age_metadata(release_id=9)
    cause_id = 718

    ages_10_29 = list(get_age_ids(10,29, ages))
    ages_30_49 = list(get_age_ids(30,49, ages))
    ages_50_69 = list(get_age_ids(50,69, ages))
    ages_70_plus = list(get_age_ids(70,200, ages))
    ages_50_plus = list(np.concatenate([ages_50_69, ages_70_plus]))

    df_10_29 = pull_age_group_results(ages_10_29, 2017, "10_to_29")
    df_30_49 = pull_age_group_results(ages_30_49, 2017, "30_to_49")
    df_50_69 = pull_age_group_results(ages_50_69, 2017, "50_to_69")
    df_70_plus = pull_age_group_results(ages_70_plus, 2017, "70_plus")
    df_50_plus = pull_age_group_results(ages_50_plus, 2017, "50_plus")

    df_10_29['age_group_string'] = "10_to_29"
    df_30_49['age_group_string'] = "30_to_49"
    df_50_69['age_group_string'] = "50_to_69"
    df_70_plus['age_group_string'] = "70_plus"
    df_50_plus['age_group_string'] = "50_plus"

    df = pd.merge(df_10_29, df_30_49).merge(df_50_69).merge(df_70_plus)

    OUT_DIR = "FILEPATH"
    df.to_csv(OUT_DIR+"table_5_age_groups_avg_5_years_country_level.csv", index=False)


if __name__ == '__main__':
    main()