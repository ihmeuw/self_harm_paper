from db_queries import get_outputs
from db_queries import get_location_metadata
import pandas as pd

OUT_DIR = "FILEPATH/"

def create_percent_change_table(cause_id=718):
    # this table shows the ASMR of a cause in 1990 and 2021
    # columns for both sexes, male, and female
    # provides % change from 1990 to 2021
    
    # subset to regions and global
    locs = get_location_metadata(release_id=9, location_set_id=1).query("level == 0 | level == 2")
    loc_ids = list(locs['location_id'].unique())
    
    
    # Pull 2021 information
    df_2021 = get_outputs('cause', release_id=9, cause_id=cause_id,
                          metric_id=3, age_group_id=27, year_id=2021,
                          location_id=loc_ids, sex_id=[1,2,3]
                         )
    # convert to rate per 100k
    df_2021['val'] = df_2021['val'] * 100000
    df_2021['upper'] = df_2021['upper'] * 100000
    df_2021['lower'] = df_2021['lower'] * 100000
    
    # format columns
    df_2021 = df_2021[['location_id','sex_id','acause','location_name','sex','val','upper','lower']]
    df_2021 = df_2021.rename(columns={"val":"val.2021", "upper":"upper.2021", "lower":"lower.2021"})

    # reshape to be wide on sex
    df_2021 = df_2021.pivot(index='location_name',columns='sex', values=['val.2021','upper.2021','lower.2021'])
    
    
    # Pull 1990 information
    df_1990 = get_outputs('cause', release_id=9, cause_id=cause_id,
                          metric_id=3, age_group_id=27, year_id=1990,
                          location_id=loc_ids, sex_id=[1,2,3]
                         )
    
    # convert to rate per 100k
    df_1990['val'] = df_1990['val'] * 100000
    df_1990['upper'] = df_1990['upper'] * 100000
    df_1990['lower'] = df_1990['lower'] * 100000
    
    # format columns
    df_1990 = df_1990[['location_id','sex_id','acause','location_name','sex','val','upper','lower']]
    df_1990 = df_1990.rename(columns={"val":"val.1990", "upper":"upper.1990", "lower":"lower.1990"})
    
    # reshape to be wide on sex
    df_1990 = df_1990.pivot(index='location_name',columns='sex', values=['val.1990','upper.1990','lower.1990'])
    
    # Pull percent change from 1990 to 2021 information
    df_change_1990_2021 = get_outputs('cause', release_id=9, cause_id=718,
                          metric_id=3, age_group_id=27,
                          location_id=loc_ids, sex_id=[1,2,3], 
                          year_start_id=1990, year_end_id=2021
                         )
    
    # convert to rate per percentage
    df_change_1990_2021['val'] = df_change_1990_2021['val'] * 100
    df_change_1990_2021['upper'] = df_change_1990_2021['upper'] * 100
    df_change_1990_2021['lower'] = df_change_1990_2021['lower'] * 100
    
    # format columns
    df_change_1990_2021 = df_change_1990_2021[['location_id','sex_id','acause','location_name','sex','val','upper','lower']]
    df_change_1990_2021 = df_change_1990_2021.rename(columns={"val":"val.pct_change_1990", "upper":"upper.pct_change_1990", "lower":"lower.pct_change_1990"})
    
    # reshape to be wide on sex
    df_change_1990_2021 = df_change_1990_2021.pivot(index='location_name',columns='sex', values=['val.pct_change_1990','upper.pct_change_1990','lower.pct_change_1990'])
    

    # Pull 2019 information
    df_2019 = get_outputs('cause', release_id=9, cause_id=cause_id,
                          metric_id=3, age_group_id=27, year_id=2019,
                          location_id=loc_ids, sex_id=[1,2,3]
                         )
    
    # convert to rate per 100k
    df_2019['val'] = df_2019['val'] * 100000
    df_2019['upper'] = df_2019['upper'] * 100000
    df_2019['lower'] = df_2019['lower'] * 100000
    
    # format columns
    df_2019 = df_2019[['location_id','sex_id','acause','location_name','sex','val','upper','lower']]
    df_2019 = df_2019.rename(columns={"val":"val.2019", "upper":"upper.2019", "lower":"lower.2019"})
    
    # reshape to be wide on sex
    df_2019 = df_2019.pivot(index='location_name',columns='sex', values=['val.2019','upper.2019','lower.2019'])

    # Pull percent change from 1990 to 2021 information #####
    df_change_2019_2021 = get_outputs('cause', release_id=9, cause_id=718,
                          metric_id=3, age_group_id=27,
                          location_id=loc_ids, sex_id=[1,2,3], 
                          year_start_id=2019, year_end_id=2021
                         )
    
    # convert to rate per percentage
    df_change_2019_2021['val'] = df_change_2019_2021['val'] * 100
    df_change_2019_2021['upper'] = df_change_2019_2021['upper'] * 100
    df_change_2019_2021['lower'] = df_change_2019_2021['lower'] * 100
    
    # format columns
    df_change_2019_2021 = df_change_2019_2021[['location_id','sex_id','acause','location_name','sex','val','upper','lower']]
    df_change_2019_2021 = df_change_2019_2021.rename(columns={"val":"val.pct_change_2019", "upper":"upper.pct_change_2019", "lower":"lower.pct_change_2019"})
    
    # reshape to be wide on sex
    df_change_2019_2021 = df_change_2019_2021.pivot(index='location_name',columns='sex', values=['val.pct_change_2019','upper.pct_change_2019','lower.pct_change_2019'])

    # merge all 5 dataframes
    df = df_1990.merge(df_2021,on='location_name').merge(df_change_1990_2021,on='location_name').merge(df_2019,on='location_name').merge(df_change_2019_2021,on='location_name')
    
    # reshape columns so that it follows the pattern expected by the table maker code
    # val.actual_value.header, upper.actual_value.header, lower.actual_value.header
    df.columns = df.columns.map(".".join)
    
    df = df.reset_index()
    df.drop
    
    return df

def re_order_df(df):
    # order columns
    df = df[[
        'location_name',
        'val.1990.Both', 'upper.1990.Both', 'lower.1990.Both',
        'val.2019.Both', 'upper.2019.Both', 'lower.2019.Both',
        'val.2021.Both', 'upper.2021.Both', 'lower.2021.Both',
        'val.pct_change_1990.Both', 'upper.pct_change_1990.Both', 'lower.pct_change_1990.Both',
        'val.pct_change_2019.Both', 'upper.pct_change_2019.Both', 'lower.pct_change_2019.Both',

        'val.1990.Male', 'upper.1990.Male', 'lower.1990.Male',
        'val.2019.Male','upper.2019.Male', 'lower.2019.Male',
        'val.2021.Male','upper.2021.Male', 'lower.2021.Male',
        'val.pct_change_1990.Male', 'upper.pct_change_1990.Male', 'lower.pct_change_1990.Male',
        'val.pct_change_2019.Male', 'upper.pct_change_2019.Male', 'lower.pct_change_2019.Male',

        'val.1990.Female', 'upper.1990.Female', 'lower.1990.Female', 
        'val.2019.Female',  'upper.2019.Female', 'lower.2019.Female',
        'val.2021.Female',  'upper.2021.Female', 'lower.2021.Female',
        'val.pct_change_1990.Female', 'upper.pct_change_1990.Female', 'lower.pct_change_1990.Female',
        'val.pct_change_2019.Female', 'upper.pct_change_2019.Female', 'lower.pct_change_2019.Female'
    ]]

    # order rows so that global is at the top
    df = df.sort_values("location_name")
    df_not_global = df[df['location_name'] != 'Global']
    df_global = df[df['location_name'] == 'Global']
    df = pd.concat([df_global, df_not_global])
    return df

def main():

    df = create_percent_change_table()

    df = re_order_df(df)

    df.to_csv(OUT_DIR+"table_2_asmr_change_1990_2019_2021.csv", index=False)

if __name__ == '__main__':
    main()