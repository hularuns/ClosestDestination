# %%
import os
import geopandas as gpd
import pandas as pd
import uuid
import folium
from folium.features import GeoJsonPopup
from folium.plugins import Search
import branca.colormap as cm
import json

#project specific packages

from services import network_bands, batch_csv, census_merge, pandas_aux as pdaux

# %% [markdown]
# ---------------------------------------------------SERVICE AREA AND BAND CREATION---------------------------------------------------

# %% [markdown]
# This first section will focus on leveraging the use of the functions found within <u>network_bands.py</u>, which will create a networkx graph resulting in the creation of service areas and finally service bands which are dissolved and differenced multipolygons of the service areas.
# 
# Initially load road network data into base_road_path.
# 
# Then create the road network using the <b>load_osm_network()</b> function.

# %%
#set base directory for data file paths.
base_dir = os.getcwd()
# create network graph and edges.
base_road_path = f'{base_dir}\\testEnvironment\\Data\\belfast.osm.pbf'
G, nodes, edges = network_bands.load_osm_network(file_path=base_road_path, network_type='driving', graph_type='networkx')

# %% [markdown]
# Load start locations to create service areas from and ensure in GeoDataFrame with CRS of 4326 if using NetworkX. If the start locations are in CSV format with separate X and Y columns for coordinates in any CRS, these can be converted to a GeoDataFrame using the <b>csv_to_gdf()</b> function.

# %%
#Start locations
start_locations = pd.read_csv(f'{base_dir}\\testEnvironment\\Data\\libraries_belfast_2024.csv')
print(start_locations.columns)
#Ensure data is converted to a dataframe
start_locations_gdf = network_bands.csv_to_gdf(csv = start_locations, x_col = 'X COORDINATE', y_col = 'Y COORDINATE', 
                                               input_crs = 29902, crs_conversion = 4326)

# %% [markdown]
# Using <b>nearest_node_and_name()</b> create a dictionary of the nearest node on the network graph to each start location point. If no names are present in the dataset  or you wish to anonymise the data, use the argument, <b>anon_name = True</b> to create random names.

# %%
#Create a dictionary of start locations and their nearest node on the network graph.
start_locations_nearest_node = network_bands.nearest_node_and_name(graph=G, start_locations=start_locations_gdf,  
                                                                   location_name = 'Static Library Name')


# %% [markdown]
# Create the service areas around the start locations on the network graph and then converting these to service bands.
# 
# The <b>service_areas()</b> fuction creates polygons which are then dissolved and differenced by <b>service_bands()</b> to create non-overlapping multipolygons. The dissolving and differencing ensures that the polygons which are closer to the start location take precedence. For this to work,

# %%
#Create the network areas and service areas - Considering making this into a Class with basic GUI, but for now fine as this.

#input custom distances as a list.
search_distances = [1000,2000,3000]
#Create individual service_areas around start locations. alpha area of 500 quite good for Belfast and the density of points in this dataset
service_areas = network_bands.service_areas(nearest_node_dict = start_locations_nearest_node, graph = G, 
                                                    search_distances = search_distances, alpha_value = 500, weight = 'length', 
                                                    save_output=True)
#Create network service areas by dissolving and differencing polygons based on distance.
service_bands = network_bands.service_bands(service_areas, dissolve_cat = 'distance',aggfunc = 'first', 
                                                            show_graph = True, save_output = True)

# %% [markdown]
# --------------------------------------------------------DATA ANALYSIS EXAMPLE--------------------------------------------------------
# 
# Using example NISRA Census 2021 data, example data can be manipulated and plotted using a variety of methods.
# This can be further extended with statistics.
# 
# Using the data in testEnvironment/Data a basic population map is created using folium.
# 
# - Load in the census data zones and filter to only include the location being analysed (Belfast)
# - Load in the pointer household dataset which has been randomised multiple times as to remove any commercial value.
# - Ensure all data is projected to CRS 4326.
# 

# %%
# Using the ancillary functions in census_merge, batch_csv and pandas_aux, example data analysis
#Load in data zones from 2021  census
#Ensure evrything's in 4326 for network analysis, probably can change it back to tm65.
data_zones = gpd.read_file(f'{base_dir}\\testEnvironment\\Data\\DZ2021.shp')
data_zones.to_crs(4326, inplace=True)
#extract only belfast datazones
belfast_zones = data_zones[data_zones['LGD2014_nm'] == 'Belfast']

#Load in house data 
pointer = gpd.read_file(f'{base_dir}\\testEnvironment\\Data\\pointer_randomised.shp')
#create uuid, might be useful, not entirely necessary.
pointer['uuid'] = pointer.apply(lambda i: uuid.uuid4(), axis=1)
#ensure all are in the same crs (should be 4326 or 3857)
pointer.to_crs(4326, inplace=True)
belfast_zones.to_crs(pointer.crs, inplace=True)

# %% [markdown]
# Spatial join the data zones with the pointer dataset to calculate how many households (points) within each data zone. 
# 
# Group by datazone and .count() the points, creating a new dataframe, merging this back to the data zone dataset.

# %%
# Perform a spatial join of pointer households and datazones in Belfast to calculate households in each datazone
joined_gdf = gpd.sjoin(pointer, belfast_zones, how='left', predicate='intersects' )
#number of points found within each datazone
datazone_pointer_count = joined_gdf.groupby('DZ2021_cd')['DZ2021_cd'].count().rename('actual_households').reset_index()
belfast_zones = pd.merge(belfast_zones, datazone_pointer_count, how = 'left')

# %% [markdown]
# Load in census data, this can be batch loaded using the <b>batch_csv_read()</b> function. Once loaded, rename any columns before commencing further; it may also be necessary to ensure column names are all upper or lower case as this can help avoid any issues later down the line.
# 
# 

# %%
#Load the Census data, file_paths in file_paths.
file_paths = [
    '/testEnvironment/Data/census_data/ni-2021-usual-residents.csv',
    '/testEnvironment/Data/census_data/ni-2021-households.csv',
    '/testEnvironment/Data/census_data/ni-2021-employment-deprivation.csv'
]
#load all defined csvs
loaded_csv = batch_csv.batch_csv_read(file_paths)

#check data is loaded loaded
print(loaded_csv.keys())

#force rename to maintain consistency of important join value column.
loaded_csv['ni-2021-employment-deprivation'].rename(columns={'Census 2021 Data Zone Code':'Geography code',
                                                             'Count':'employment_deprivation_count'}, inplace=True)

#Data can have irregular capitalisation, avoids this bug by forcing lower case. Some are 'Geography Code', 'geography Code' etc.
# Need to incorporate this properly into function 
for key, df in loaded_csv.items():
    df.columns = df.columns.str.lower()
    

# %% [markdown]
# Join the census data together based on the 'geography code', which can be the DataZone code, SuperDataZone etc using the join_census_csv() function. Drop any extraneous columns which may not be necessary if you wish to maintain a tidier DataFrame.

# %%

#Join the CSV data together based on common ID column such as geography code in NISRA census 2021 data.
joined_census_data = census_merge.join_census_csv(loaded_csv, 'geography code',  drop=True,join_type='left')
#dropping some extraneous columns as they are not needed and clutter the dataset
joined_census_data.drop(columns=['household deprivation (employment) code','household deprivation (employment) label'], inplace=True)

# %% [markdown]
# Merge the data zone polygons with a Pandas merge with the joined census data, in this case with the DataZone code. Assigning suffixes allows for the subsequent <b>drop_dupe_cols()</b> function to intelligently drop the right hand column, retaining the left hand column where there is a duplication. This also renames the left column ensuring that it there is no suffix appended.

# %%
# Merge the data zones with the loaded census data.
belfast_zones_census = pd.merge(belfast_zones, joined_census_data, left_on='DZ2021_cd', right_on='geography code', 
                                how='left', suffixes=('_left', '_right'))

# Drop the duplicate columns from the merged dataframe
census_merge.drop_dupe_cols(belfast_zones_census, ('_left', '_right'))

# %% [markdown]
# Calculate your statistics based upon the joined household count data and joined census data. Not all statistics calculated here were used in the end map result, however the extent of this is shown to show how extensive this can be.

# %%
#Calculate CENSUS METRICS PER HOUSE in pointer data
#Need to force these to numeric. Ensure coerce for any nulls
belfast_zones_census['all households'] = pd.to_numeric(belfast_zones_census['all households'], errors = 'coerce')
belfast_zones_census['all usual residents'] = pd.to_numeric(belfast_zones_census['all usual residents'], errors = 'coerce')

## Calculate additional metrics. Average resident per house etc.

#average residents per household
belfast_zones_census['avg_resi_house'] = (belfast_zones_census['all usual residents'] / belfast_zones_census['actual_households'])
#actual residents based off pointer
belfast_zones_census['actual_total_residents'] = (belfast_zones_census['avg_resi_house'] * belfast_zones_census['actual_households'])
#average number of employment deprived people per household. - Super relevant for this analysis.
belfast_zones_census['avg_emp_dep_per_house'] = (belfast_zones_census['employment_deprivation_count'] / belfast_zones_census['actual_households'])*belfast_zones_census['avg_resi_house']
#average number of employmenet deprived people per resident.
belfast_zones_census['avg_emp_dep_per_capita'] = (belfast_zones_census['employment_deprivation_count'] / belfast_zones_census['all usual residents'])*belfast_zones_census['avg_resi_house']

#Force to gdf, currently will be a panda series
belfast_zones_census = gpd.GeoDataFrame(belfast_zones_census, crs = 4326)



# %% [markdown]
# Currently the census data is is homogenous across each DataZone and does not consider the impact of distance to the nearest library. 
# 
# This is similar to the step earlier which was used to calculate the number of points within each DataZone.
# 
# - Spatial join to identify which househould point is situated within each network_band.
# - This data is then spatially joined with the DataZone data.
# - This is grouped by DataZone code and unstacked, which create separate columns. 
# - The unstacked column names are then assigned a prefix, in this case, households_ using the <b>append_col_prefix()</b> function.
# - Remove any NaN values with <b>fill_na_with_zero()</b> function.
# 

# %%
# Spatial join to find which network band each household falls into
households_with_contour = gpd.sjoin(pointer, service_bands, how="left", predicate="within")
households_with_contour = households_with_contour.drop(columns='index_right').reset_index(drop=True)

# spatial to join data zone data to each household
households_with_zones = gpd.sjoin(households_with_contour, belfast_zones_census, how="left", predicate="within").drop(columns='index_right').reset_index(drop=True)

# Group by census zone and distance and then count. Unstacks the distance columns to create separate columns for each distance.
household_counts = households_with_zones.groupby(['DZ2021_cd', 'distance']).size().unstack(fill_value=0)

#join this back to the belfast_census_zones to add the counts as new columns
belfast_zones_census = belfast_zones_census.merge(household_counts, on='DZ2021_cd', how='left')

# append column name to unstacked columns
belfast_zones_census = pdaux.append_col_prefix(belfast_zones_census, [1000, 2000,3000], prefix='households')        

#replace NaNs with 0s
pdaux.fill_na_with_zero(belfast_zones_census, ['households_1000','households_2000','households_3000'])


# %% [markdown]
# The data is plotted with folium, the calculated households within each network band per datazone is shown in a popup for each datazone. Datazones can be searched for in this example by DZ2021_cd and their Name.

# %%
#Create a folium map - This part's quite manual.
#turn this into a bunch of functions to get this smaller and more refined down the line.
#Numbers will be off due to randomisation of pointer dataset.
belfast_census_data_geojson = json.loads(belfast_zones_census.to_json())
service_bands_geojson = json.loads(service_bands.to_json())

# Create the Folium map centered around the average coordinates of datazone geometries, can ignore warning
map_center = belfast_zones_census.geometry.centroid.unary_union.centroid
m = folium.Map(location=[map_center.y, map_center.x], zoom_start=12)

###could turn this network_service_areas_style creation into a larger func
distances = [1000, 2000, 3000] 
colours = ['green', 'orange', 'red']
color_map = cm.LinearColormap(
    colors=colours,
    vmin=min(distances),
    vmax=max(distances),
    caption='Distance to Network Contours'
)
distance_colours = {dist: colour for dist, colour in zip(distances, colours)}
def network_service_areas_style(feature):
    """Apply styles based on the distance attribute."""
    distance = feature['properties']['distance']
    return {
        'color': distance_colours.get(distance, 'gray'),
        'weight': 2,
        'opacity': 0.8,
        'fillColor': distance_colours.get(distance, 'gray'), 
        'fillOpacity': 0.5
    }

#basic styling for the polygons
def basic_poly_styling(feature):
    return {
        'color': 'black',
        'weight':1,
        'fillOpacity': 0.1
    }

#defines the highlight colour
def highlight_function(feature):
    return {
        'color': 'yellow',
        'weight': 2,
        'fillOpacity':0.2
    }
network_service_bands_layer = folium.GeoJson(
    service_bands_geojson,
    style_function=network_service_areas_style,
    name = 'Search Area Bands',
    tooltip=folium.GeoJsonTooltip(
        fields=['distance'],
        aliases=['Distance:'],
        localize = True
    )
)
network_service_bands_layer.add_to(m)


#census zone layer
data_zone_layer = folium.GeoJson(
    belfast_census_data_geojson,
    name='Houses within 1000m',
    style_function=basic_poly_styling,
    highlight_function=highlight_function,

    popup = GeoJsonPopup(
        fields=['DZ2021_cd', 'DZ2021_nm', 'actual_households', 'households_1000','households_2000','households_3000'],
        aliases=['Data Zone:', 'Data Zone Name:', 'Households:', 'Households within 1km:', 
                'Households within 2km:', 'Households within 3km:'],
        localize=True,
        labels=True
    )
)
data_zone_layer.add_to(m)
#Search layer for datazone code
search_dz_code = Search(
    layer=data_zone_layer,
    geom_type='Polygon',
    placeholder='Search for Data Zone Code',
    search_label='DZ2021_cd',
    search_zoom=14,
    position='topleft'
)
search_dz_code.add_to(m)

#can search by name as well
search_dz_name = Search(
    layer=data_zone_layer,
    geom_type='Polygon',
    placeholder='Search for Data Zone Name',
    search_label='DZ2021_nm',
    search_zoom=14,
    position='topleft'
)
search_dz_name.add_to(m)

# layer control
folium.LayerControl().add_to(m)

save_name = 'test'
# Save the map to an HTML file 
m.save(f'{save_name}.html', cdn_resources='cdn')
print(f'Map has been saved as {save_name}')
m


