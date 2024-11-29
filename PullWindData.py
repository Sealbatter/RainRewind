from datetime import datetime, timedelta
import requests
import logging
import pandas as pd
from DataCleaning import round_to_nearest_5_minutes, generate_time_labels, generate_time_lists

def WindMetadataDF_Constructor(metadata: list):
    data = {'id': [], 'name': [], 'latitude': [], 'longitude': []}
    for dict in metadata:
        data['id'].append(dict['id'])
        data['name'].append(dict['name'])
        data['latitude'].append(dict['location']['latitude'])
        data['longitude'].append(dict['location']['longitude'])
    return pd.DataFrame(data=data)

def BuildWindDF(DATE: str, START_TIME: str, END_TIME: str) -> pd.DataFrame:
    '''This function pulls Wind Direction data and Wind Speed data,
    takes 5 minute averages and compiles both 5 minute averaged Wind
    Direction and Wind Speed data into a pandas DataFrame'''

    # Processing Wind Direction data

    hours, minutes = generate_time_lists(START_TIME, END_TIME, 1)

    # Generate list of time labels in HH:MM format
    time_labels = generate_time_labels(hours, minutes)

    logging.info(f'Pulling Wind Direction data from {DATE}, from {START_TIME}H to {END_TIME}H')
    WDmaindf = pd.DataFrame()
    for time_label in time_labels:

        url = f'https://api-open.data.gov.sg/v2/real-time/api/wind-direction?date={DATE}T{time_label}:00'
        response = requests.get(url)
        data = response.json()
        timestamp = DATE + 'T' + time_label + ':00+08:00'
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:00+08:00')
        value = data['data']['readings'][0]['data']

        ToAdd = pd.DataFrame(data={'timestamp': [timestamp for i in range(len(value))], 
                            'stationId': [value[i]['stationId'] for i in range(len(value))], 
                            'value': [value[i]['value'] for i in range(len(value))]})
        WDmaindf = pd.concat([WDmaindf, ToAdd])

    Windmetadata = data['data']['stations']
    WindmetadataDF = WindMetadataDF_Constructor(Windmetadata)

    # Combining the longitude and latitude information with WDmaindf
    new_df = pd.DataFrame(columns=['timestamp', 'stationId', 'value', 'latitude', 'longitude'])
    for WDmetadf_row in WindmetadataDF.iterrows():
        for WDdf_row in WDmaindf.iterrows():
            if WDmetadf_row[1]['id'] == WDdf_row[1]['stationId']:
                latlongseries = pd.Series(data=[WDmetadf_row[1]['latitude'], WDmetadf_row[1]['longitude']], index=['latitude', 'longitude'])
                WDdf_row = pd.concat([WDdf_row[1], latlongseries])
                new_df = pd.concat([new_df, pd.DataFrame(WDdf_row).transpose()])

    WDmaindf = new_df
    # WDmaindf.sort_values('timestamp', inplace=True)
    WDmaindf['timestamp'] = pd.to_datetime(WDmaindf['timestamp'])
    # WDmaindf.set_index('timestamp', inplace=True)

    # Taking 5 min averages for wind data
    newdict = {}
    WindDirectionIntermediate = pd.DataFrame()
    grouped_df = WDmaindf.groupby(['stationId'])
    for key, value in grouped_df:
        intermediate = value[['timestamp', 'value']]
        intermediate.index = pd.to_datetime(value['timestamp'])
        intermediate.loc[:, 'value'] = intermediate['value'].astype(float)
        avg_df = intermediate.value.resample('5min').mean()
        newdict = pd.DataFrame()
        # Check if newdict is empty before concatenation
        if not newdict.empty:
            newdict = pd.concat([newdict, avg_df])
        else:
            newdict = pd.DataFrame(avg_df)  # If empty, just assign avg_df to newdict
        newdict['stationId'] = [key[0] for i in range(len(newdict.index))]
        newdict['latitude'] = [value['latitude'].iloc[0] for i in range(len(newdict.index))]
        newdict['longitude'] = [value['longitude'].iloc[0] for i in range(len(newdict.index))]
        WindDirectionIntermediate = pd.concat([WindDirectionIntermediate, newdict])

    logging.info(f'Pulling Wind Speed data from {DATE}, from {START_TIME}H to {END_TIME}H')
    ## Reading Wind Speed data and preparing Wind Speed dataframe

    WSmaindf = pd.DataFrame()
    for time_label in time_labels:
        url = f'https://api-open.data.gov.sg/v2/real-time/api/wind-speed?date={DATE}T{time_label}:00'
        response = requests.get(url)
        data = response.json()
        timestamp = DATE + 'T' + time_label + ':00+08:00'
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:00+08:00')
        value = data['data']['readings'][0]['data']

        ToAdd = pd.DataFrame(data={'timestamp': [timestamp for i in range(len(value))], 
                            'stationId': [value[i]['stationId'] for i in range(len(value))], 
                            'value': [value[i]['value'] for i in range(len(value))]})
        WSmaindf = pd.concat([WSmaindf, ToAdd])

    # Combining the longitude and latitude information with WDmaindf
    new_df = pd.DataFrame(columns=['timestamp', 'stationId', 'value', 'latitude', 'longitude'])
    for WSmetadf_row in WindmetadataDF.iterrows():
        for WSdf_row in WSmaindf.iterrows():
            if WSmetadf_row[1]['id'] == WSdf_row[1]['stationId']:
                latlongseries = pd.Series(data=[WSmetadf_row[1]['latitude'], WSmetadf_row[1]['longitude']], index=['latitude', 'longitude'])
                WSdf_row = pd.concat([WSdf_row[1], latlongseries])
                new_df = pd.concat([new_df, pd.DataFrame(WSdf_row).transpose()])

    # Taking 5 minute averages for Wind Speed    
    newdict = {}
    WSmaindf = new_df
    WindSpeedIntermediate = pd.DataFrame()
    grouped_df = WSmaindf.groupby(['stationId'])
    for key, value in grouped_df:
        intermediate = value[['timestamp', 'value']]
        intermediate.index = pd.to_datetime(value['timestamp'])
        intermediate.loc[:, 'value'] = intermediate['value'].astype(float)
        avg_df = intermediate.value.resample('5min').mean()
        newdict = pd.DataFrame()
        # Check if newdict is empty before concatenation
        if not newdict.empty:
            newdict = pd.concat([newdict, avg_df])
        else:
            newdict = pd.DataFrame(avg_df)  # If empty, just assign avg_df to newdict
        newdict['stationId'] = [key[0] for i in range(len(newdict.index))]
        newdict['latitude'] = [float(value['latitude'].iloc[0]) for i in range(len(newdict.index))]
        newdict['longitude'] = [float(value['longitude'].iloc[0]) for i in range(len(newdict.index))]
        WindSpeedIntermediate = pd.concat([WindSpeedIntermediate, newdict])
    
    WindDF = WindDirectionIntermediate.copy()
    WindDF['WindDirection'] = WindDirectionIntermediate['value'].astype(float)
    WindDF['WindSpeed'] = WindSpeedIntermediate['value'].astype(float)
    WindDF['timestamp'] = WindDF.index
    WindDF.to_csv('DataFrames/WindDF.csv')
    return WindDF


if __name__ == '__main__':
    DATE = input('Date in yyyy-mm-dd format \n')
    START_TIME = input('Starting time in HH:MM format \n')
    END_TIME = input('Ending time in HH:MM format \n')
    
    BuildWindDF(DATE, START_TIME, END_TIME)
