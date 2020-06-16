"""
Created on Thu Jun 04 22:39:04 2020

@author: Fraser D
"""

import pandas as pd
from os import path
from sklearn import preprocessing 
import matplotlib.pyplot as plt
import shapefile as shp

csv_loc = r'munro_data.csv'
shp_loc = r'shapefile/NUTS_Level_1/NUTS_Level_1__January_2018__Boundaries'

# get the data if it isn't there already
if not path.exists(csv_loc):
    print("File not found, writing CSV to %s" % csv_loc)
    url = "https://munroapi.herokuapp.com/munros"
    df = pd.read_json(url)
    df.to_csv(csv_loc, encoding='utf-8')
else:
    print("File found at %s, request not made" % csv_loc)
    df = pd.read_csv(csv_loc, index_col=0)
    


#convert these uniqe letters into map distances - see https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid
grid_letters = {
'NN': (200000,700000), 
'NJ': (300000,800000), 
'NH': (200000,800000),
'NO': (300000,700000), 
'NG': (100000,800000), 
'NM': (100000,700000), 
'NC': (200000,900000)
}


def get_eastings(x):
    return grid_letters[x][0]


def get_northings(x):
    return grid_letters[x][1]

df['mapref_eastings'] = df["gridref_letters"].map(lambda x: get_eastings(x)) + df["gridref_eastings"]
df['mapref_northings'] = df["gridref_letters"].map(lambda x: get_northings(x)) + df["gridref_northings"]


#make new col for region categoricals
labelEnc = preprocessing.LabelEncoder()    
df["region_enc"] = labelEnc.fit_transform(df['region'])

#==============================================================================
# PLOTTING START
#==============================================================================

sf = shp.Reader(shp_loc)

#Plot  Country Outlines
for record in sf.shapeRecords():
    if record.record['nuts118nm'] != 'Scotland':
        continue
    num_parts = len(record.shape.parts)
    for i in range(num_parts):
        i_start = record.shape.parts[i]
        if i == (num_parts - 1):
            i_end = len(record.shape.points)
        else:
            i_end = record.shape.parts[i + 1]
        x = [i[0]  for i in record.shape.points[i_start:i_end]] 
        y = [i[1]  for i in record.shape.points[i_start:i_end]]
        plt.plot(x,y)


#Plot Munros in groups
groups = df.groupby('region')
for name, group in groups:
    plt.plot(group['mapref_eastings'], group['mapref_northings'], marker='o',  linestyle='', markersize=5, label=name)

#plot lims - all UK
#plt.xlim(0,700000)
#plt.ylim(0, 1250000)

#plot lims - all Scotland
#plt.xlim(0,500000)
#plt.ylim(500000, 1000000)

#plot lims - munros only
plt.xlim(75000,375000)
plt.ylim(675000, 975000)

#plot scaling if you need it - ensures each northing/easting unit has same scale on map
xL, xR = plt.xlim()
yL, yR = plt.ylim()
y_scale = (yR - yL)/(xR - xL)
x_inches = 5

plt.rcParams["figure.figsize"] = (x_inches, x_inches)
 
plt.legend(bbox_to_anchor=(1.04,1.03), loc="upper left")
       
plt.xlabel('Eastings')
plt.xticks(rotation=90) 
plt.ylabel('Northings') 
plt.show()

#==============================================================================
# SRIPT END
#==============================================================================
