import pandas as pd
import numpy as np

from db_queries import get_outputs
from db_queries import get_age_metadata
from db_queries import get_location_metadata
from db_queries import get_covariate_estimates
from get_draws.api import get_draws

OUT_DIR = "FILEPATH"

NUMBER_OF_DRAWS = 500

DEMOGRAPHIC_COLS = ['location_id','year_id','sex_id','cause_id']

draw_cols = []
for i in range(NUMBER_OF_DRAWS):
    draw_cols.append(f"draw_{i}")
    
avg_age_draws = []
for draw in draw_cols:
    avg_age_draws.append(f'{draw}_age_avg')
    
draws_total = []
for draw in draw_cols:
    draws_total.append(f"{draw}_total")

def create_age_table():
    # function to create age table with the average value of each age group 
    ages = get_age_metadata(release_id=9)
    ages = ages[['age_group_id','age_group_name']]
    age_group_ids = ages['age_group_id'].unique()

    ages['age_est'] = ages['age_group_name']

    ages['age_est'].replace("Early Neonatal", .04,inplace=True)
    ages['age_est'].replace("Late Neonatal", .08,inplace=True)
    ages['age_est'].replace("1-5 months", .25,inplace=True)
    ages['age_est'].replace("6-11 months", .7,inplace=True)
    ages['age_est'].replace("12 to 23 months", 1.5,inplace=True)
    ages['age_est'].replace("2 to 4", 3,inplace=True)
    ages['age_est'].replace("5 to 9", 7,inplace=True)
    ages['age_est'].replace("10 to 14", 12,inplace=True)
    ages['age_est'].replace("15 to 19", 17,inplace=True)
    ages['age_est'].replace("20 to 24", 22,inplace=True)
    ages['age_est'].replace("25 to 29", 27,inplace=True)
    ages['age_est'].replace("30 to 34", 32,inplace=True)
    ages['age_est'].replace("35 to 39", 37,inplace=True)
    ages['age_est'].replace("40 to 44", 42,inplace=True)
    ages['age_est'].replace("45 to 49", 47,inplace=True)
    ages['age_est'].replace("50 to 54", 52,inplace=True)
    ages['age_est'].replace("55 to 59", 57,inplace=True)
    ages['age_est'].replace("60 to 64", 62,inplace=True)
    ages['age_est'].replace("65 to 69", 67,inplace=True)
    ages['age_est'].replace("70 to 74", 72,inplace=True)
    ages['age_est'].replace("75 to 79", 77,inplace=True)
    ages['age_est'].replace("80 to 84", 82,inplace=True)
    ages['age_est'].replace("85 to 89", 87,inplace=True)
    ages['age_est'].replace("90 to 94", 92,inplace=True)
    ages['age_est'].replace("95 plus", 95,inplace=True)

    return ages

def prep_year_table(year_id, loc_ids, ages, cause_id=718):
    
    # pull draws for self-harm parent cause
    df = get_draws("cause_id", 
        cause_id, 
        location_id=list(loc_ids), 
        year_id=year_id,
        source="codcorrect", 
        release_id=9, 
        sex_id=[1,2,3],
        measure_id=1)

    assert len(df.columns) == NUMBER_OF_DRAWS + 8
    
    # subset to only ages present in a given cause
    ages = ages[ages['age_group_id'].isin(df['age_group_id'].unique())]
    
    # merge on the age group's average ages
    df = df.merge(ages[['age_group_id','age_est']],how='left', on='age_group_id')

    # get total deaths by demographic. 
    df_year_loc = df.groupby(DEMOGRAPHIC_COLS, as_index=False)[draw_cols].sum()
    # rename the cols to merge on
    for draw in draw_cols:
        df_year_loc = df_year_loc.rename(columns={f"{draw}":f"{draw}_total"})

    df = pd.merge(df,df_year_loc)
    
    # calculate average age at the draw level
    # the sum of the resulting col is the average age
    for draw in draw_cols:
        df[f'{draw}_age_est_val'] = df['age_est'] * df[draw]
        df[f'{draw}_age_avg'] = df[f'{draw}_age_est_val'] / df[f"{draw}_total"]
        
    df = df.groupby(DEMOGRAPHIC_COLS, as_index=False)[avg_age_draws].sum()
    
    df['average_age'] = df.apply(lambda x: x[avg_age_draws].mean(), axis=1)
    df['average_age_upper'] = df.apply(lambda x: np.percentile(x[avg_age_draws], 97.5), axis=1)
    df['average_age_lower'] = df.apply(lambda x: np.percentile(x[avg_age_draws],  2.5), axis=1)

    df = df.drop(avg_age_draws, axis=1)
    
    # rename columns for R lancet table code
    df = df.rename(columns={"average_age":f"val.{year_id}", "average_age_upper":f"upper.{year_id}", "average_age_lower":f"lower.{year_id}"})
    df['sex'] = df['sex_id']
    df['sex'] = df['sex'].replace({1:'Male',2:"Female",3:"Both"})
    ####
    df = df.pivot(index='location_id',columns='sex', values=[f"val.{year_id}",f"upper.{year_id}",f"lower.{year_id}"])
    df.columns = df.columns.map(".".join)
    df = df.reset_index()
    
    return df

def re_order_df(df):
    # order columns for lancet table 
    df = df[[
        'location_name',
        "level","sort_order",
        'val.1990.Male', 'upper.1990.Male', 'lower.1990.Male',
        'val.2021.Male','upper.2021.Male', 'lower.2021.Male',

        'val.1990.Female', 'upper.1990.Female', 'lower.1990.Female', 
        'val.2021.Female',  'upper.2021.Female', 'lower.2021.Female',

        'val.1990.Both', 'upper.1990.Both', 'lower.1990.Both',
        'val.2021.Both', 'upper.2021.Both', 'lower.2021.Both',
    ]]

    # order rows so that global is at the top
    df = df.sort_values("location_name")
    df_not_global = df[df['location_name'] != 'Global']
    df_global = df[df['location_name'] == 'Global']
    df = pd.concat([df_global, df_not_global])
    return df

def main():
    # get all countries, regions, super regions, and global IDs
    locs = get_location_metadata(release_id=9, location_set_id=1).query("level <= 3")
    loc_ids = locs['location_id'].unique()

    ages = create_age_table()

    df_1990 = prep_year_table(1990, loc_ids=loc_ids, ages=ages)
    df_2021 = prep_year_table(2021, loc_ids=loc_ids, ages=ages)

    df = df_2021.merge(df_1990)

    df = df.merge(locs[['location_id','location_name','level','sort_order']])
    
    df = re_order_df(df)

    df.to_csv(OUT_DIR+"appendix_table_2_average_age_1990_2021_country_level.csv", index=False)

if __name__ == '__main__':
    main()