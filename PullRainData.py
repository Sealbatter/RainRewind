from datetime import datetime, timedelta
import requests
import logging
import pandas as pd
from DataCleaning import round_to_nearest_5_minutes, generate_time_labels, generate_time_lists


def MetadataDF_Constructor(metadata: list):
    data = {'id': [], 'name': [], 'latitude': [], 'longitude': []}
    for dict in metadata:
        data['id'].append(dict['id'])
        data['name'].append(dict['name'])
        data['latitude'].append(dict['location']['latitude'])
        data['longitude'].append(dict['location']['longitude'])
    return pd.DataFrame(data=data)

def BuildRainDF(DATE: str, START_TIME: str, END_TIME: str) -> pd.DataFrame:

    START_TIME = round_to_nearest_5_minutes(START_TIME)
    END_TIME = (datetime.strptime(round_to_nearest_5_minutes(END_TIME), '%H:%M') - timedelta(minutes=1)).strftime('%H:%M')

    # Generate HourList and MinutesList
    hours, minutes = generate_time_lists(START_TIME, END_TIME, 5)
    # Generate list of time labels in HH:MM format
    time_labels = generate_time_labels(hours, minutes)

    # Now we are in a good position to mass pull data from data.gov.sg
    precipmaindf = pd.DataFrame()

    logging.info(f'Pulling rainfall data from {DATE}, from {START_TIME}H to {END_TIME}H')
    # CALLING DATA.GOV.SG API
    for time_label in time_labels:
        count = 0
        url = f'https://api-open.data.gov.sg/v2/real-time/api/rainfall?date={DATE}T{time_label}:00'
        response = requests.get(url)
        data = response.json()
        timestamp = DATE + 'T' + time_label + ':00+08:00'
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:00+08:00')
        value = data['data']['readings'][0]['data']

        ToAdd = pd.DataFrame(data={'timestamp': [timestamp for i in range(len(value))], 
                            'stationId': [value[i]['stationId'] for i in range(len(value))], 
                            'value': [value[i]['value'] for i in range(len(value))]})
        
        precipmaindf = pd.concat([precipmaindf, ToAdd])
        count += 1

    metadata = data['data']['stations']
    metadataDF = MetadataDF_Constructor(metadata)
    
    # Combining longitude and latitude information with precipmaindf
    new_df = pd.DataFrame(columns=['timestamp', 'stationId', 'value', 'latitude', 'longitude'])
    for precipmetadf_row in metadataDF.iterrows():
        for precipdf_row in precipmaindf.iterrows():
            if precipmetadf_row[1]['id'] == precipdf_row[1]['stationId']:
                latlongseries = pd.Series(data=[precipmetadf_row[1]['latitude'], precipmetadf_row[1]['longitude']], index=['latitude', 'longitude'])
                precipdf_row = pd.concat([precipdf_row[1], latlongseries])
                new_df = pd.concat([new_df, pd.DataFrame(precipdf_row).transpose()])
    precipmaindf = new_df

    precipmaindf.to_csv('DataFrames/RainDF.csv')
    return precipmaindf

if __name__ == '__main__':
    DATE = input('Date in yyyy-mm-dd format \n')
    START_TIME = input('Starting time in HH:MM format \n')
    END_TIME = input('Ending time in HH:MM format \n')

    BuildRainDF(DATE, START_TIME, END_TIME)
