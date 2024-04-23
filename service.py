from pyrosm import OSM
import geopandas as gpd
import pandas as pd
import networkx as nx
import osmnx as ox
from shapely.geometry import Point
import itertools
import matplotlib.pyplot as plt


# assign file path to osm pbf file.
base_road_path = 'C:/Users/hular/projects/ClosestDestination/testEnvironment/Data/belfast_slightly_trimmed.osm.pbf'

osm = OSM(base_road_path)

#load road network from graph
G = ox.get_network(network_type = 'driving', nodes = True)

#Convert to ga graph (this will create if not a pyrosm source)
if not isinstance(G, nx.Graph):
    G = nx.from_pandas_edgelist(G, source='u', target='v', edge_attr=True)

ox.plot_graph(ox.graph_from_gdfs(G.nodes, G, edges))
