from db_queries import get_outputs
from db_queries import get_location_metadata
import pandas as pd

OUT_DIR = "FILEPATH"

def main():
    # pulls incidence and deaths
    # calculates the ratio between the 2
    cause_id = 718
    # subset to regions and global
    locs = get_location_metadata(release_id=9, location_set_id=1).query("level == 0 | level == 2")
    loc_ids = list(locs['location_id'].unique())

    df_2021_deaths = get_outputs('cause', release_id=9, cause_id=cause_id,
                          metric_id=1, age_group_id=22, year_id=2021,
                          location_id=loc_ids, sex_id=[1,2]
                         )

    df_2021_gun_deaths = get_outputs('cause', release_id=9, cause_id=721,
                          metric_id=1, age_group_id=22, year_id=2021,
                          location_id=loc_ids, sex_id=[1,2]
                         )

    df_2021_incidence = get_outputs('cause', release_id=9, cause_id=cause_id,
                          metric_id=1, age_group_id=22, year_id=2021,
                          measure_id=6,
                          location_id=loc_ids, sex_id=[1,2]
                         )

    df_2021_deaths = df_2021_deaths[['location_name','sex','val','upper','lower']]
    df_2021_gun_deaths = df_2021_gun_deaths[['location_name','sex','val','upper','lower']]
    df_2021_incidence = df_2021_incidence[['location_name','sex','val','upper','lower']]

    df_2021_deaths= df_2021_deaths.rename(columns={"val":"val.deaths", "upper":"upper.deaths", "lower":"lower.deaths"})
    df_2021_gun_deaths= df_2021_gun_deaths.rename(columns={"val":"val.gun_deaths", "upper":"upper.gun_deaths", "lower":"lower.gun_deaths"})
    df_2021_incidence = df_2021_incidence.rename(columns={"val":"val.incidence", "upper":"upper.incidence", "lower":"lower.incidence"})

    df = df_2021_deaths.merge(df_2021_incidence).merge(df_2021_gun_deaths)
    df['val.ratio'] = df["val.incidence"] / df["val.deaths"]
    df['val.firearm_pct'] = (df["val.gun_deaths"] / df["val.deaths"]) * 100

    df["upper.ratio"] = 0
    df["lower.ratio"] = 0
    df["upper.firearm_pct"] = 0
    df["lower.firearm_pct"] = 0

    df = df.pivot(index='location_name',columns='sex', values=[
        "val.deaths","upper.deaths", "lower.deaths",
        "val.incidence","upper.incidence", "lower.incidence",
        "val.ratio", "upper.ratio", "lower.ratio",
        "val.firearm_pct","upper.firearm_pct", "lower.firearm_pct"

    ])

    df.columns = df.columns.map(".".join)
    df = df.reset_index()


    df = df[[
        'location_name',

        "val.deaths.Male","upper.deaths.Male", "lower.deaths.Male",
        "val.incidence.Male","upper.incidence.Male", "lower.incidence.Male",
        "val.ratio.Male", "upper.ratio.Male", "lower.ratio.Male",
        "val.firearm_pct.Male","upper.firearm_pct.Male", "lower.firearm_pct.Male",

        "val.deaths.Female","upper.deaths.Female", "lower.deaths.Female",
        "val.incidence.Female","upper.incidence.Female", "lower.incidence.Female",
        "val.ratio.Female", "upper.ratio.Female", "lower.ratio.Female",
        "val.firearm_pct.Female","upper.firearm_pct.Female", "lower.firearm_pct.Female"
    ]]

    # order rows so that global is at the top
    # sort the remaining locations by the highest ratios for Females
    df = df.sort_values("val.ratio.Female", ascending=False)
    df_not_global = df[df['location_name'] != 'Global']
    df_global = df[df['location_name'] == 'Global']
    df = pd.concat([df_global, df_not_global])

    df.to_csv(OUT_DIR+"FILEPATH", index=False)

if __name__ == '__main__':
    main()