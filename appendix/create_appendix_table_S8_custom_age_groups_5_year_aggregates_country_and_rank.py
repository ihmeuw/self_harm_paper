# appendix Table S4 is a subset of this table

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
    causes = get_cause_metadata(release_id=9, cause_set_id=3) # cause set 3 GBD reporting
    causes = causes.query("level == 3")
    cause_ids = list(causes['cause_id'].unique())
    
    
    # subset to regions and global
    locs = get_location_metadata(release_id=9, location_set_id=1).query("level <= 3")
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

def find_rank(df, cause_id, age_group_string, loc_ids):
    df_males_all_locs = df.query("sex_id == 1")
    df_females_all_locs = df.query("sex_id == 2")

    results_male = pd.DataFrame()
    results_female = pd.DataFrame()
    
    # iterate over locations
    for location_id in loc_ids:
        df_males = df_males_all_locs.query(f"location_id == {location_id}")[['location_name','location_id','cause_id',f'val.mr_rate_{age_group_string}']].sort_values(f'val.mr_rate_{age_group_string}', ascending=False)
        df_females = df_females_all_locs.query(f"location_id == {location_id}")[['location_name','location_id','cause_id',f'val.mr_rate_{age_group_string}']].sort_values(f'val.mr_rate_{age_group_string}', ascending=False)

        # reset index, this is the rank
        # index is 0 based so add 1
        df_males = df_males.reset_index(drop=True)
        df_males[f'val.rank_{age_group_string}'] = df_males.index + 1

        df_females = df_females.reset_index(drop=True)
        df_females[f'val.rank_{age_group_string}'] = df_females.index + 1

        # keep only wanted cause rank
        df_males = df_males.query(f"cause_id == {cause_id}").drop(['cause_id',f'val.mr_rate_{age_group_string}'], axis=1)
        df_females = df_females.query(f"cause_id == {cause_id}").drop(['cause_id',f'val.mr_rate_{age_group_string}'], axis=1)

        results_male = pd.concat([results_male, df_males])
        results_female = pd.concat([results_female, df_females])
        
        results_male['sex_id'] = 1
        results_female['sex_id'] = 2
    
    df = pd.concat([results_male, results_female])
    
    return df

def prep_table_for_R(df, df_rank, cause_id, age_group_string):
    df = df.query(f"cause_id == {cause_id}")
    
    df_males = df.query("sex_id == 1")
    df_females = df.query("sex_id == 2")
    
    df_males_rank = df_rank.query("sex_id == 1")
    df_females_rank = df_rank.query("sex_id == 2")
    
    df_males = df_males.merge(df_males_rank)
    df_females = df_females.merge(df_females_rank)
    
    df = pd.concat([df_males, df_females])
    df = df.pivot(index='location_name',columns='sex', values=[f'val.mr_rate_{age_group_string}',f"upper.mr_rate_{age_group_string}",f"lower.mr_rate_{age_group_string}",f'val.rank_{age_group_string}'])
    df.columns = df.columns.map(".".join)
    df = df.reset_index()
    
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

    locs = get_location_metadata(release_id=9, location_set_id=1).query("level <= 3")
    loc_ids = list(locs['location_id'].unique())

    df_10_29_rank = find_rank(df_10_29, cause_id, "10_to_29", loc_ids)
    df_30_49_rank = find_rank(df_30_49, cause_id, "30_to_49", loc_ids)
    df_50_69_rank = find_rank(df_50_69, cause_id, "50_to_69", loc_ids)
    df_70_plus_rank = find_rank(df_70_plus, cause_id, "70_plus", loc_ids)
    df_50_plus_rank = find_rank(df_50_plus, cause_id, "50_plus", loc_ids)

    df_10_29 = prep_table_for_R(df_10_29, df_10_29_rank, cause_id, "10_to_29")
    df_30_49 = prep_table_for_R(df_30_49, df_30_49_rank, cause_id, "30_to_49")
    df_50_69 = prep_table_for_R(df_50_69, df_50_69_rank, cause_id, "50_to_69")
    df_70_plus = prep_table_for_R(df_70_plus, df_70_plus_rank, cause_id, "70_plus")
    df_50_plus = prep_table_for_R(df_50_plus, df_50_plus_rank, cause_id, "50_plus")

    df = pd.merge(df_10_29, df_30_49).merge(df_50_69).merge(df_70_plus)

    df = df.merge(locs[['location_id','level','sort_order']])

    df[[
        'upper.rank_10_to_29.Male', 'lower.rank_10_to_29.Male',
        'upper.rank_10_to_29.Female', 'lower.rank_10_to_29.Female',
        'upper.rank_30_to_49.Male', 'lower.rank_30_to_49.Male',
        'upper.rank_30_to_49.Female', 'lower.rank_30_to_49.Female',
        'upper.rank_50_to_69.Male', 'lower.rank_50_to_69.Male',
        'upper.rank_50_to_69.Female', 'lower.rank_50_to_69.Female',
        'upper.rank_70_plus.Male', 'lower.rank_70_plus.Male',
        'upper.rank_70_plus.Female', 'lower.rank_70_plus.Female'
    ]] = 0

    df = df[[
        'location_name',
        'level','sort_order',
        'val.mr_rate_10_to_29.Male', 'upper.mr_rate_10_to_29.Male', 'lower.mr_rate_10_to_29.Male',
        'val.mr_rate_10_to_29.Female', 'upper.mr_rate_10_to_29.Female', 'lower.mr_rate_10_to_29.Female',
        'val.rank_10_to_29.Male', 'upper.rank_10_to_29.Male', 'lower.rank_10_to_29.Male',
        'val.rank_10_to_29.Female', 'upper.rank_10_to_29.Female', 'lower.rank_10_to_29.Female',
        
        'val.mr_rate_30_to_49.Male', 'upper.mr_rate_30_to_49.Male', 'lower.mr_rate_30_to_49.Male',
        'val.mr_rate_30_to_49.Female', 'upper.mr_rate_30_to_49.Female', 'lower.mr_rate_30_to_49.Female',
        'val.rank_30_to_49.Male', 'upper.rank_30_to_49.Male', 'lower.rank_30_to_49.Male',
        'val.rank_30_to_49.Female', 'upper.rank_30_to_49.Female', 'lower.rank_30_to_49.Female',
        
        'val.mr_rate_50_to_69.Male', 'upper.mr_rate_50_to_69.Male', 'lower.mr_rate_50_to_69.Male',
        'val.mr_rate_50_to_69.Female', 'upper.mr_rate_50_to_69.Female', 'lower.mr_rate_50_to_69.Female',
        'val.rank_50_to_69.Male', 'upper.rank_50_to_69.Male', 'lower.rank_50_to_69.Male',
        'val.rank_50_to_69.Female','upper.rank_50_to_69.Female', 'lower.rank_50_to_69.Female',
        
        'val.mr_rate_70_plus.Male', 'upper.mr_rate_70_plus.Male', 'lower.mr_rate_70_plus.Male',
        'val.mr_rate_70_plus.Female', 'upper.mr_rate_70_plus.Female', 'lower.mr_rate_70_plus.Female',
        'val.rank_70_plus.Male','upper.rank_70_plus.Male', 'lower.rank_70_plus.Male',
        'val.rank_70_plus.Female','upper.rank_70_plus.Female', 'lower.rank_70_plus.Female',
    ]]

    df = df[[
        'location_name',
        'level','sort_order',
        'val.mr_rate_10_to_29.Male', 'upper.mr_rate_10_to_29.Male', 'lower.mr_rate_10_to_29.Male',
        'val.rank_10_to_29.Male', 'upper.rank_10_to_29.Male', 'lower.rank_10_to_29.Male',
        'val.mr_rate_10_to_29.Female', 'upper.mr_rate_10_to_29.Female', 'lower.mr_rate_10_to_29.Female',
        'val.rank_10_to_29.Female', 'upper.rank_10_to_29.Female', 'lower.rank_10_to_29.Female',
        
        'val.mr_rate_30_to_49.Male', 'upper.mr_rate_30_to_49.Male', 'lower.mr_rate_30_to_49.Male',
        'val.rank_30_to_49.Male', 'upper.rank_30_to_49.Male', 'lower.rank_30_to_49.Male',
        'val.mr_rate_30_to_49.Female', 'upper.mr_rate_30_to_49.Female', 'lower.mr_rate_30_to_49.Female',
        'val.rank_30_to_49.Female', 'upper.rank_30_to_49.Female', 'lower.rank_30_to_49.Female',
        
        'val.mr_rate_50_to_69.Male', 'upper.mr_rate_50_to_69.Male', 'lower.mr_rate_50_to_69.Male',
        'val.rank_50_to_69.Male', 'upper.rank_50_to_69.Male', 'lower.rank_50_to_69.Male',
        'val.mr_rate_50_to_69.Female', 'upper.mr_rate_50_to_69.Female', 'lower.mr_rate_50_to_69.Female',
        'val.rank_50_to_69.Female','upper.rank_50_to_69.Female', 'lower.rank_50_to_69.Female',
        
        'val.mr_rate_70_plus.Male', 'upper.mr_rate_70_plus.Male', 'lower.mr_rate_70_plus.Male',
        'val.rank_70_plus.Male','upper.rank_70_plus.Male', 'lower.rank_70_plus.Male',
        'val.mr_rate_70_plus.Female', 'upper.mr_rate_70_plus.Female', 'lower.mr_rate_70_plus.Female',
        'val.rank_70_plus.Female','upper.rank_70_plus.Female', 'lower.rank_70_plus.Female',
    ]]

    df = df.sort_values("location_name")
    df_not_global = df[df['location_name'] != 'Global']
    df_global = df[df['location_name'] == 'Global']
    df = pd.concat([df_global, df_not_global])

    OUT_DIR = "/FILEPATH/"
    df.to_csv(OUT_DIR+"appendix_table_5_age_groups_avg_5_years_all_locs.csv", index=False)


if __name__ == '__main__':
    main()