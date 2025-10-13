'''
This file is intended to do the following types of work:
* download data from APIs
* screenscrape data from websites
* reduce the size of large datasets to something more manageable
* clean data: reducing/renaming columns, normalizing strings,
* generate data through relatively complicated calculations

To reduce processing time and to establish a "milestone", you should
save your processed data into the folder 'data_organized'.
You can do this with:
   df.to_csv('data_organized/filename.csv')

You may have helper files. But, this file should be the entry point.

You should test this file's code in `run_tests.py`. 
'''

import pandas as pd
import geopandas as gpd


def pre_process_fuel_stations():
    file_path = 'raw_data/fuel_stations.csv'
    dtype_dict = {'Fuel Type Code': 'str', 
                  'Station Name': 'str', 
                  'Street Address': 'str', 
                  'City': 'str', 
                  'State': 'str', 
                  'ZIP': 'str', 
                  'Latitude':'float',
                  'Longitude': 'float'}
    
    df = pd.read_csv(file_path, dtype=dtype_dict)
    #df = df.astype(str)
    new_df = df[df['State'] == 'WA' ]#and df['Fuel Type Code'] == 'ELEC']
    selected_cols = new_df[list(dtype_dict.keys())].copy()
    #selected_cols = df[list(dtype_dict.keys())].copy()
    selected_cols.dropna(inplace=True)
    selected_cols.drop_duplicates(inplace=True)
    selected_cols.to_csv('data_organized/fuel_stations.csv')
    #print(selected_cols)



def pre_process_Electric_Vehicle_Population():
    file_path = 'raw_data/EVP.csv'
    dtype_dict = {'Date': 'str',
                 'County': 'str',
                 'State': 'str',
                 'Battery Electric Vehicles (BEVs)': 'int',
                 'Plug-In Hybrid Electric Vehicles (PHEVs)': 'int',
                 'Electric Vehicle (EV) Total': 'int',
                 'Non-Electric Vehicle Total': 'int',
                 'Total Vehicles': 'int',
                 'Percent Electric Vehicles': 'float'}
    
    df = pd.read_csv(file_path, dtype=dtype_dict)
    new_df = df[df['State'] == 'WA']
    selected_cols = new_df[list(dtype_dict.keys())].copy()
    #selected_cols = df[list(dtype_dict.keys())].copy()
    selected_cols.dropna(inplace=True)
    selected_cols.drop_duplicates(inplace=True)
    selected_cols.to_csv('data_organized/Electric_Vehicle_Population_Size.csv')
    #print(selected_cols)


def pre_process_registration():
    file_path = 'raw_data/VRT.csv'
    
    dtype_dict = {'County': 'str',
                    'State': 'str',
                    'Postal Code': 'str',
                    'Electrification Level': 'str',
                    'Owner Type': 'str',
                    'Fuel Type Primary': 'str',
                    'Vehicle Type': 'str',
                    'Model Year': 'int',
                    'Model': 'str',
                    'Make': 'str',
                    'Transaction Month and Year': 'str'}
    
    df = pd.read_csv(file_path, dtype=dtype_dict)
    #selected_cols = df[list(dtype_dict.keys())].copy()
    new_df = df[df['State'] == 'WA']
    selected_cols = new_df[list(dtype_dict.keys())].copy()
    selected_cols.dropna(inplace=True)
    #print(selected_cols)
    selected_cols.to_csv('data_organized/Vehicle_Registration_Transactions.csv')



def pre_process_population():
    file_path = 'raw_data/POP.csv'
    df = pd.read_csv(file_path, skiprows=3)
    df = df.rename(columns={'Unnamed: 1': 'County'})
    df = df.drop(columns=['Unnamed: 0'])
    df['County'] = df['County'].str.replace('.', '').str.replace(' County, Washington', '').str.strip()
    population_columns = ['2020', '2021', '2022', '2023']
    for col in population_columns:
        df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')

    #print(df)
    df.to_csv('data_organized/Pop.csv')


    #print(gdf)



def main():
    #pre_process_registration()
    pre_process_fuel_stations()
    pre_process_population()
    #pre_process_Electric_Vehicle_Population()
    #pre_process_staes_provnces()


if __name__ == '__main__':
    main()

    
