import pandas as pd
import numpy as np

from db_queries import get_outputs
from db_queries import get_age_metadata
from db_queries import get_location_metadata
from db_queries import get_covariate_estimates
from get_draws.api import get_draws
# run in GBD env

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

def main():
    # get all countries, regions, super regions, and global IDs
    locs = get_location_metadata(release_id=9, location_set_id=1).query("level <= 3")['location_id'].unique()

    ages = create_age_table()

    # pull draws for self-harm parent cause
    df = get_draws("cause_id", 
        718, 
        location_id=list(locs), 
        year_id=list(range(1990,2022)), 
        source="codcorrect", 
        sex_id=[1,2,3],
        release_id=9, 
        measure_id=1)

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

    df_final = df.groupby(DEMOGRAPHIC_COLS, as_index=False)[avg_age_draws].sum()

    df_final['average_age'] = df_final.apply(lambda x: x[avg_age_draws].mean(), axis=1)
    df_final['average_age_upper'] = df_final.apply(lambda x: np.percentile(x[avg_age_draws], 97.5), axis=1)
    df_final['average_age_lower'] = df_final.apply(lambda x: np.percentile(x[avg_age_draws],  2.5), axis=1)

    df_final = df_final.drop(avg_age_draws, axis=1)

    df_final.to_csv("FILEPATH/self_harm_average_age_with_ui.csv", index=False)


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

if __name__ == '__main__':
    main()