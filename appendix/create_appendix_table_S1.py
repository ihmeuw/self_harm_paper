import pandas as pd
import numpy as np
from db_queries import get_outputs, get_location_metadata, get_population, get_age_metadata
from get_draws.api import get_draws
import os

from db_queries import get_location_metadata
locs = get_location_metadata(release_id=16, location_set_id=21)
locs = locs[['location_id','location_name']]

df = get_age_metadata(release_id=9).sort_values("age_group_days_start")[['age_group_id','age_group_name']]#.merge(male_deaths, how='right')

ages = get_age_metadata(release_id=9)[['age_group_id','age_group_name']]
age_ids = list(ages['age_group_id'].unique())
age_ids.extend([22])
print(age_ids)
male_deaths = get_outputs("cause",release_id=9, cause_id=718, compare_version_id=8016,
            sex_id=[1],
            year_id=2021,
            metric_id=1,
            age_group_id=age_ids
           )[['age_group_id','val','upper','lower']]

male_mr = get_outputs("cause",release_id=9, cause_id=718, compare_version_id=8016,
            sex_id=[1],
            year_id=2021,
            metric_id=3,
            age_group_id=age_ids
           )[['age_group_id','val','upper','lower']]

male_mr['val'] = male_mr['val'] * 100000
male_mr['upper'] = male_mr['upper'] * 100000
male_mr['lower'] = male_mr['lower'] * 100000

male_cf = get_outputs("cause",release_id=9, cause_id=718, compare_version_id=8016,
            sex_id=[1],
            year_id=2021,
            metric_id=2,
            age_group_id=age_ids
           )[['age_group_id','val','upper','lower']]

female_deaths = get_outputs("cause",release_id=9, cause_id=718, compare_version_id=8016,
            sex_id=[2],
            year_id=2021,
            metric_id=1,
            age_group_id=age_ids
           )[['age_group_id','val','upper','lower']]

female_mr = get_outputs("cause",release_id=9, cause_id=718, compare_version_id=8016,
            sex_id=[2],
            year_id=2021,
            metric_id=3,
            age_group_id=age_ids
           )[['age_group_id','val','upper','lower']]

female_mr['val'] = female_mr['val'] * 100000
female_mr['upper'] = female_mr['upper'] * 100000
female_mr['lower'] = female_mr['lower'] * 100000

female_cf = get_outputs("cause",release_id=9, cause_id=718, compare_version_id=8016,
            sex_id=[2],
            year_id=2021,
            metric_id=2,
            age_group_id=age_ids
           )[['age_group_id','val','upper','lower']]

male_deaths = male_deaths.rename(columns={"val":"val.Male Deaths", 'upper':'upper.Male Deaths', "lower":'lower.Male Deaths'})
female_deaths = female_deaths.rename(columns={"val":"val.Female Deaths", 'upper':'upper.Female Deaths', "lower":'lower.Female Deaths'})

male_mr = male_mr.rename(columns={"val":"val.Male Mortality Rate", 'upper':'upper.Male Mortality Rate', "lower":'lower.Male Mortality Rate'})
female_mr = female_mr.rename(columns={"val":"val.Female Mortality Rate", 'upper':'upper.Female Mortality Rate', "lower":'lower.Female Mortality Rate'})

male_cf = male_cf.rename(columns={"val":"val.Male Cause Fraction", 'upper':'upper.Male Cause Fraction', "lower":'lower.Male Cause Fraction'})
female_cf = female_cf.rename(columns={"val":"val.Female Cause Fraction", 'upper':'upper.Female Cause Fraction', "lower":'lower.Female Cause Fraction'})


both_deaths = get_outputs("cause",release_id=9, cause_id=718, compare_version_id=8016,
            sex_id=[3],
            year_id=2021,
            metric_id=1,
            age_group_id=age_ids
           )[['age_group_id','val','upper','lower']]

both_mr = get_outputs("cause",release_id=9, cause_id=718, compare_version_id=8016,
            sex_id=[3],
            year_id=2021,
            metric_id=3,
            age_group_id=age_ids
           )[['age_group_id','val','upper','lower']]

both_mr['val'] = both_mr['val'] * 100000
both_mr['upper'] = both_mr['upper'] * 100000
both_mr['lower'] = both_mr['lower'] * 100000

both_cf = get_outputs("cause",release_id=9, cause_id=718, compare_version_id=8016,
            sex_id=[3],
            year_id=2021,
            metric_id=2,
            age_group_id=age_ids
           )[['age_group_id','val','upper','lower']]

both_deaths = both_deaths.rename(columns={"val":"val.both Deaths", 'upper':'upper.both Deaths', "lower":'lower.both Deaths'})

both_mr = both_mr.rename(columns={"val":"val.both Mortality Rate", 'upper':'upper.both Mortality Rate', "lower":'lower.both Mortality Rate'})

both_cf = both_cf.rename(columns={"val":"val.both Cause Fraction", 'upper':'upper.both Cause Fraction', "lower":'lower.both Cause Fraction'})


df = df.rename(columns={"age_group_name":"Age"})

df = df.merge(male_deaths, how='right')
df = df.merge(female_deaths, how='right')

df = df.merge(male_mr, how='right')
df = df.merge(female_mr, how='right')

df = df.merge(male_cf, how='right')
df = df.merge(female_cf, how='right')

df = df.merge(both_deaths, how='right')

df = df.merge(both_mr, how='right')

df = df.merge(both_cf, how='right')

df = df[~df['val.Male Cause Fraction'].isnull()]

df = df.drop("age_group_id", axis=1)

all_age = df[df['Age'].isnull()]
age_spec = df[~df['Age'].isnull()]

df = pd.concat([all_age, age_spec])
df['Age'] = df['Age'].fillna("All Ages")

df = df[[
    'Age', 
    'val.both Deaths', 'upper.both Deaths', 'lower.both Deaths',
    'val.Male Deaths', 'upper.Male Deaths', 'lower.Male Deaths',
    'val.Female Deaths', 'upper.Female Deaths', 'lower.Female Deaths',

    'val.both Mortality Rate', 'upper.both Mortality Rate','lower.both Mortality Rate', 
    'val.Male Mortality Rate', 'upper.Male Mortality Rate','lower.Male Mortality Rate',
    'val.Female Mortality Rate','upper.Female Mortality Rate', 'lower.Female Mortality Rate',

    'val.both Cause Fraction','upper.both Cause Fraction', 'lower.both Cause Fraction',
    'val.Male Cause Fraction', 'upper.Male Cause Fraction','lower.Male Cause Fraction', 
    'val.Female Cause Fraction','upper.Female Cause Fraction', 'lower.Female Cause Fraction'
    
]]

OUT_DIR = "/FILEPATH/"
df.to_csv(OUT_DIR+"appendix_table_global_metrics_by_age_group.csv", index=False)