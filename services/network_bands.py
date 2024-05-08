
from pyrosm import OSM
import geopandas as gpd
import pandas as pd
import networkx as nx
import osmnx as ox
from shapely.geometry import Point
import matplotlib.pyplot as plt
import alphashape
from faker import Faker
import time
import services.function_progress as function_progress
import uuid

def load_osm_network(file_path:str, network_type:str, graph_type:str):
    """ Load an OSM file and extract the network (driving, walking etc) as a graph (e.g. networkx graph) along with its nodes and edges.
    G, nodes, edges = load_osm_network(args) to extract.
    RETURNS: G, nodes and edges
    
        Parameters:
    - file_path (str): File path of OSM road data, a .pbf file.
    - network_type (str): Type of transport, e.g. driving, walking, cycling.
    - graph_type: Type of graph to create, available types: networkx, pandana, igraph. Likely choose networkx for use with rest of the methods.
    """

    osm = OSM(file_path)
    nodes, edges = osm.get_network(network_type=network_type, nodes=True)
    G = osm.to_graph(nodes, edges, graph_type=graph_type)
    
    return G, nodes, edges

def csv_to_gdf(csv, x_col:str, y_col:str, input_crs:int, crs_conversion:int = None):
    """ function to convert csv to a gdf based off X, Y coordinates and input CRS. Optional CRS conversion.
        Parameters:
    - csv: source data as csv with geom x and y column separate.
    - x_col (str): column name for the x coordinate.
    - y_col (str): str, column name for the y coordinate.
    - input_crs (int): int, EPSG code for input coordinate reference system.
    - crs_conversion (int):optional EPSG code for converting CRS.
    """
    #create a list for each row of geom by zipping and turn into a point tuple
    try:
        csv['geometry'] = list(zip(csv[x_col], csv[y_col]))
        csv['geometry'] = csv['geometry'].apply(Point)
        # Convert to GeoDataFrame
        gdf = gpd.GeoDataFrame(csv, geometry='geometry', crs=f'EPSG:{input_crs}')
        #Only converts if specified
        if crs_conversion:
            gdf = gdf.to_crs(epsg=crs_conversion)
            
        #adds a uuid - useful to avoid duplicates.
        uuid_list = []
        for i in range(len(gdf)):
            new_uuid = uuid.uuid4()
            uuid_list.append(new_uuid)
        gdf['uuid'] = uuid_list
        
        return gdf
    except Exception:
        print(f'Exception error: {Exception}')
        
        
def nearest_node_and_name(graph, start_locations: gpd.GeoDataFrame, location_name: str = None, 
                          anon_name: bool = False, progress: bool = True):
    """ Creates a dictionary of location names and nearest node on Graph. If no location name column specified, creates a list.
    Anonymised naming can be enabled by not inputting location_name and anon_name = True. This also forces a dictionary type if you only have point data.
    
    Parameters:
        graph (networkx.Graph): The graph representing the network.
        start_locations (GeoDataFrame): Geopandas GeoDataFrame of start locations.
        location_name (str): Optional; column storing name of start location.
        anon_name (bool): If True, generates fake names.
    """   
    # Initialise service_xy based on the presence of location_name
    if location_name is None and not anon_name:
        service_xy = []
    else:
        service_xy = {}
    
    # Generate fake names if required. Anonymised naming. Also forces a workaround forcing dictionary if no name data. Bit experimental
    if location_name is None and anon_name:
        fake = Faker()
        fake_names = []
        for i in range(len(start_locations)):
            fake_names.append(fake.city())
        start_locations['Fake Name'] = fake_names
        location_name = 'Fake Name' 
        
    # Calculate the nearest note for each start_location
    for index, row in start_locations.iterrows():
        print(f"{index+1} of {len(start_locations)}")
        location_x = row['geometry'].x
        location_y = row['geometry'].y
        nearest_node = ox.distance.nearest_nodes(graph, location_x, location_y)
        
        # Add nearest node name to service_xy
        if location_name:
            name = row[location_name]
            service_xy[name] = {'nearest_node': nearest_node}        
        else:
            service_xy.append({'nearest_node': nearest_node})

    return service_xy



def network_areas(nearest_node_dict:dict, graph, search_distances:list, alpha_value:int, weight:str, 
                  progress=False, save_output:bool = False):
    """
    Generates a GeoDataFramecontaining polygons of service areas calculated using Dijkstra's shortest path algorithm within a networkx graph. 
    Each polygon represents a service area contour defined by a maximum distance from a source node.

    Parameters:
        nearest_node_dict (dict): A dictionary with names as keys and the nearest node on the graph as values. This is an output from the `nearest_node_and_name` function.
        graph (networkx.Graph): The graph representing the network, often designated as `G` in networkx.
        cutoffs (list of int): Distances in meters that define the bounds of each service area.
        alpha_value (int): The alpha value used to create non-convex polygons via the alphashape method.
        weight (str): The edge attribute in the graph to use as a weight.
        progress (bool): If True, will print progress of the function.

    """
    
    # service_areas_dict = {} #uncomment with services_ares_dict[name]
    data_for_gdf = []
    #for time tracking.
    ongoing_time=[]
    cumulative_total = 0
    
    #For each start location [name] creates a polygon around the point.
    for index, (name, node_info) in enumerate(nearest_node_dict.items()):
        print(f'Creating network service of sizes: {search_distances} metres')    
        start_time = time.time() 
        print(f'Processing: location {index+1} of {len(nearest_node_dict)}: {name}. ')
        #cycle through each distance in list supplied
        for distance in search_distances:
            #Extract nearest node to the name (start location)
            nearest_node = node_info['nearest_node']
            subgraph = nx.single_source_dijkstra_path_length(graph, nearest_node, cutoff=distance, weight = weight)
            
            #Creates a list of all nodes which are reachable within the cutoff.
            reachable_nodes = list(subgraph.keys())
            node_points_list = []
            for node in reachable_nodes:
                x = graph.nodes[node]['x']
                y = graph.nodes[node]['y']
                node_points_list.append(Point(x, y))

            # Makes the x,y values into just a list of tuples to be used to create alphashapes
            node_points_series = pd.Series(node_points_list)
            node_point_series_tuples_list = node_points_series.apply(lambda point: (point.x, point.y))
            correct_points_list = node_point_series_tuples_list.tolist()
            
            #Create an alpha shape for each polygon and append to dataframe.
            alpha_shape = alphashape.alphashape(correct_points_list, alpha_value)
            data_for_gdf.append({'name': name, 'distance':distance, 'geometry': alpha_shape})
            # service_areas_dict[name] = alpha_shape #uncomment to check if function returns correct variables
        
        end_time = time.time()
        #Small timer to assess roughly progress.
        if progress:
            cumulative_progress = function_progress.function_progress(start_time=start_time, end_time=end_time,
                                                                      ongoing_time=ongoing_time, total_tasks=len(nearest_node_dict))
            cumulative_total += cumulative_progress
            print(f'{cumulative_progress}')
            print(f'The process has been running for {round(cumulative_total,2)} seconds.')

    gdf_alpha = gpd.GeoDataFrame(data_for_gdf, crs= 4326)
    if save_output:
        gdf_alpha.to_file('network_areas.gpkg')
     #return the geodataframe
    return gdf_alpha


def network_service_areas(geodataframe:gpd.GeoDataFrame, dissolve_cat:str, aggfunc:str ='first', 
                          show_graph:bool = False, save_output:bool = False):
    """ 
    Dissolves polygons in a GeoDataFrame by category type. Currently only supports dissolve categories which are buffer area integers.
    Parameters:
        geodataframe (gpd.GeoDataFrame): Geopandas Data Frame.
        dissolve_cat (str): Column to dissolve dataframe by.
        aggfunc (func or str): ame as geopandas aggfunc aggregation. Defaults to first.
        show_graph (bool): If true, will show a basic graph of output. Defaults to false.
        """
        #Smallest first, e.g. 1000, then 2000, then 3000
    data_for_gdf = []
    differenced_geoms = []
    category_values = []
    #Subset dataframe by dissolve category then run dissolve, dissolving and then subsetting creates invalid geoms.
    search_distances = geodataframe[dissolve_cat].unique()
    for distance in search_distances:
        filtered_data = geodataframe[geodataframe[dissolve_cat] == distance].reset_index(drop=True)
        filtered_data_dissolved = filtered_data.dissolve(aggfunc=aggfunc)
        data_for_gdf.append(filtered_data_dissolved)
    #Create gdf for each dissolved category
    gdf_dissolve = gpd.GeoDataFrame(pd.concat(data_for_gdf, ignore_index=True), crs='EPSG:4326')
    
    #sort data so that the smallest area which cannot be differenced is exluded.
    #iterates so that the larger area which is a lower indexis differenced by the geom above it.
    gdf_dissolve_sorted = gdf_dissolve.sort_values(by=dissolve_cat, ascending=False)
    for index in range(0,len(gdf_dissolve_sorted)-1):
        differenced_part = gdf_dissolve_sorted.geometry.iloc[index].difference(gdf_dissolve_sorted.geometry.iloc[index+1])
        differenced_geoms.append(differenced_part)
        category_values.append(gdf_dissolve_sorted.iloc[index][dissolve_cat])

    #append the smallest geom as this is excluded from the dissolve difference loop.
    final_index = (len(gdf_dissolve_sorted)-1)
    differenced_geoms.append(gdf_dissolve_sorted.iloc[final_index]['geometry'])
    category_values.append(gdf_dissolve_sorted.iloc[final_index][dissolve_cat])
    #append geometry to geodataframe to return as final result
    differenced_gdf = gpd.GeoDataFrame({'geometry': differenced_geoms, dissolve_cat: category_values}, crs=geodataframe.crs)
    print('Network areas have successfully been dissolved and differenced')
    #produces a quick and ready map for instant analysis.
    if show_graph:
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        differenced_gdf.plot(column=dissolve_cat, cmap='cividis', alpha=0.8, ax=ax, legend=True,
                                legend_kwds={'label': dissolve_cat, 'orientation': 'horizontal',
                                            'fraction': 0.036})
        plt.autoscale(enable=True, axis='both', tight=True)
        plt.show()
        print('A map showing network contours has been created.')
    
    if save_output:
        differenced_gdf.to_file('network_service_areas.gpkg')
    
    return differenced_gdf

