import os
from datetime import date

import pandas as pd
from APIkeys import MET
from METWeather import METdata, METsearch

desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 
today = date.today()

# Latitude and longitude of the desired area you want to locate
lat = 51.7400
lng = -2.4054

SL = str(METsearch(lat, lng, MET))

lat = 51.473998104
lng = -0.226165762

LO = str(METsearch(lat, lng, MET))

lat = 53.623
lng = -2.869

MM = str(METsearch(lat, lng, MET))

#Use this to manually check weather station
# print(df.loc[df['id'] == LO])

head = 'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/'
tail = '?res=3hourly&key=<APIkey>'
key = MET

# ---WILL ONLY WORK IF .CSV IS CLOSED---
#If you want just a single site for 5 days, don't include all
# Slimbridge
# site = SL
# METdata(head, site, tail, key)

#If you want all for the next 5 days, then specify at the end
# site = [SL, LO, MM]
# METdata(head, site, tail, key, all=True)

#If you want to add to a pre-existing df
df = pd.read_csv(desktop + "/MET.csv")
site = [SL, LO, MM]
METdata(head, site, tail, key, all=True, add=df)
