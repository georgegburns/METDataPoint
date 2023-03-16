import os
from datetime import date, datetime
from math import asin, cos, radians, sin, sqrt

import pandas as pd
import requests
from APIkeys import MET
from METDictionaries import *

desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 

# Update with api_key generated at https://www.metoffice.gov.uk/services/data/datapoint/getting-started
api_key = MET
today = date.today()

#Haversine Distance Equation as found here https://medium.com/analytics-vidhya/finding-nearest-pair-of-latitude-and-longitude-match-using-python-ce50d62af546
def dist(lat1, long1, lat2, long2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
    # haversine formula 
    dlon = long2 - long1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km

# Search function to search the output to find nearest weather station to desired lat and lng
def METsearch(lat : float, lng: float, key : str):
    # Url is designed to output JSON but can also output XML (http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/xml/)
    url = 'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key=<APIkey>'
    params = {
        'APIkey' : api_key
    }
    res = requests.get(url, params=params)
    data = res.json()
    # Cleaning the JSON data into a workable DF
    temp_df = pd.DataFrame.from_dict(data)
    temp_lst = []
    for i in temp_df['Locations']:
        for j in i:
            temp_lst.append(j)
    output = pd.DataFrame(temp_lst)
    output['elevation'] = output['elevation'].astype(float)
    output['id'] = output['id'].astype(int)
    output['latitude'] = output['latitude'].astype(float)
    output['longitude'] = output['longitude'].astype(float)
    distances = output.apply(
        lambda row: dist(lat, lng, row['latitude'], row['longitude']), 
        axis=1)
    station = output.loc[distances.idxmin(), 'id']
    #To manually check weather station
    print(f'The Nearest MET Weather Station for {lat} {lng} is {station}')
    return station

# Function to call the API, clean the data and store in a output
def METdata(head : str, site : list, tail: str, key : str, all=False, add=pd.DataFrame()):
    limit = len(site)-1
    if all:
        limit = 0
    while limit <= len(site)-1:
        print('Working...')
        code = site[limit]
        url = head + code + tail
        params = {
            'APIkey' : key
        }
        res = requests.get(url, params=params)
        data = res.json()

        index = pd.DataFrame.from_dict(data['SiteRep']['Wx']['Param'])
        # print(index)
        index = index.drop(['units'], axis=1)
        columns = dict(zip(index['name'], index['$']))

        centre = data['SiteRep']['DV']['Location']['name']
        dates = pd.DataFrame.from_dict(data['SiteRep']['DV']['Location']['Period'])

        # print(date)
        dates = dates.drop(['type', 'Rep'], axis=1)
        days = []
        for date in dates['value']:
            day = date[:-1]
            date_object = datetime.strptime(day, '%Y-%m-%d').date()
            days.append(date_object)

        temp_list = []
        for i in data['SiteRep']['DV']['Location']['Period']:
            for j in i['Rep']:
                temp_list.append(j)
                
        weather = pd.DataFrame(temp_list)
        weather = weather.rename(columns=columns)
        count = 0

        date_column = []

        while count <= (len(days)-1):
            for i in weather['$']:
                date_column.append(days[count])
                if i == '1260':
                    count+=1
        weather['date'] = date_column
        weather['centre'] = centre
        
        weather = weather.replace({'$' : time})
        weather = weather.rename(columns={'$' : 'time'})
        
        weather = weather.replace({'Weather Type' : Wtypes})
        weather = weather.replace({'Visibility' : Visibility})
        weather = weather.replace({'Max UV Index' : UV})
        
        if add.empty:
            if all:
                temp = weather
                if limit != 0:
                    output = pd.concat([output, temp])
                else:
                    output = temp
                limit += 1
            else:
                output = weather
        else:
            if all:
                temp = weather
                if limit != 0:
                    output = pd.concat([output, temp])
                else:
                    output = pd.concat([add, temp])
                limit += 1
            else:
                output = pd.concat([add, weather])
        print(f'Complete {centre}') 
    
    output = output.apply(lambda x: x.astype(str).str.lower()).drop_duplicates(subset=['date', 'time','centre'], keep='last')
    if add.empty:
        if all:
            output.to_csv(desktop + f"/MET - {today}.csv", index=False)
    else:
        if all:
            output.to_csv(desktop + f"/MET.csv", index=False)
            
        else: 
            output.to_csv(desktop + f"/MET - {centre} - {today}.csv", index=False)
    print('Data retrieved - file ouput to desktop')
    print(output.tail(5))
        

