import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from shapely.affinity import translate
import random

# Load the dataset
gdf = gpd.read_file(r'C:\Users\hular\projects\ClosestDestination\testEnvironment\pointer\pointer.shp')

# Uncomment this to drop random amounts of the data, although, don't think it's necessary if i shift the data about randomly
# number_to_drop = len(gdf) // 10
# features_to_drop = gdf.sample(n=number_to_drop).index
# gdf_modified = gdf.drop(features_to_drop)

# Random50% of data to shift about 
#to_shift = gdf.sample(frac=0.50)

# Max shift and define the tuple of randomly selected points to shift randomly select between a range of integers
# Ranomise the max shift and then also again for EXTRA random I suppose. Currently will shift by 100 either direction maximum.
max_shift = random.randint(0,100)
shifts_x = np.random.uniform(-max_shift, max_shift, size=len(gdf))
shifts_y = np.random.uniform(-max_shift, max_shift, size=len(gdf))

#add them to the to_shift df
gdf['shift_x'] = shifts_x
gdf['shift_y'] = shifts_y

# Loop through each row in to_shift to translate randomly
for i, row in gdf.iterrows():
    current_geometry = row['geometry']
    new_geometry = translate(current_geometry, xoff=row['shift_x'], yoff=row['shift_y'])
    gdf.at[i, 'geometry'] = new_geometry


gdf.to_file(r'C:\Users\hular\projects\ClosestDestination\testEnvironment\Data\pointer_randomised.shp')
