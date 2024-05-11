# Service Area Tools
![Python](https://img.shields.io/badge/python-3.06+-blue.svg) 
![GitHub Release](https://img.shields.io/github/v/release/hularuns/Service-Area-Tools)

## Overview

This repository contains Python scripts aimed at automating the creation of road service areas 
 performing complex spatial and network analyses, specifically tailored for geographical data processing and visualization, focusing on census data integration with network-based spatial analysis.

These tools can be used in standalone projects, simply by including the [services](services/) folder within your project's repository.

## How To Use

### Requirements
- Python 3.06+
- Jupyter Notebooks (optional)
- Currently if you utilise these tools from start to finish, offline OSM `.pbf` data is used for the creation of the road networks. The use of tools such as [osmconvert](https://wiki.openstreetmap.org/wiki/Osmconvert) or [Osmosis](https://wiki.openstreetmap.org/wiki/Osmosis) can be used to obtain large road network areas.

### Installation/Set-up
#### Cloning
First, clone the GitHub repository. This can be done using gitbash (alternatives are available):

```gitbash
git clone https://github.com/hularuns/ClosestDestination
```
#### Dependencies
**Pip**

All dependencies can be installed using pip with the following command: 

 ```bash 
 pip install "python>=3.6,<3.13" "geopandas<=0.14.3" "pandas<=2.2.2" networkx ipykernel matplotlib alphashape faker folium jupyter
 ````

**Conda**
Optionally, you can also install all dependencies using conda with the following steps:

Using conda terminal navigate to the cloned repository where the [environment.yml](environment.yml) file is found  and run the following commands:

Create the environment: `conda env create -f environment.yml` then activate the environment: `conda activate netgeo_env`


### Using In Your Own Project:

The functions in this script can be added to your project simply by including the entirety of the [services/](services/) folder and then imported into your project, for example with similar code to as below:

```python
import services

services.network_bands.network_start_locations_nearest_node  =  network_bands.nearest_node_and_name(
                                                                                graph = G, 
                                                                                start_locations = start_locations_gdf, 
                                                                                location_name  =  'Static Library Name')
```

### Example Script:

-  **data_analysis.ipynb**: This is a script showcasing how to use the tool and example subsequent analysis and output with data stored in [testEnvironment/Data](testEnvironment/Data). 
- With the `netgeo_env` conda environment activated, navigate to the cloned repository folder and run the example script from the conda terminal: ``jupyter notebook data_analysis.ipynb``
- If successful an interactive webmap using folium is created in the parent folder of the repository called [index.html](index.html).

#### Example Usage:

This directory contains modules that provide various functionalities such as data loading, transformation, spatial analysis, and visualization. Below is an example of how to use the core functions of this repository to create a network service areas.

Please read the [How-to guide](Documentation/how-to) for a more more in-depth guide on how to install, use and debug the code with specific use cases and examples.


<details>
<summary><b>Click Here To Show Example Code Usage</b></summary>
  
```python
import  services.network_bands  as  network_bands

# Load the network graph
# Ensure all data is in same CRS as pbf (likely EPSG:4326)
file_path = '/path/to/city.osm.pbf'

G, nodes, edges = network_bands.load_osm_network(file_path=file_path, network_type='driving', graph_type='networkx')


# Define start locations and distances for creating service areas
# Start locations are the location of each service, e.g. each library, hospital, supermarket.

#Example of GeoDataframe of start locations
print(start_locations_gdf)
| Static Library Name             |geometry                   |
|---------------------------------|---------------------------|
| Ardoyne Library                 | POINT (-5.97089 54.61635) |
| Ballyhackamore Library	      | POINT (-5.86641 54.59504) |
| Belfast Central Library	      | POINT (-5.93147 54.60270) |

# Obtain the nearest nodes on the Graph
start_locations_nearest_node  =  network_bands.nearest_node_and_name(
graph = G, 
start_locations = start_locations_gdf, 
location_name  =  'Static Library Name')

print(start_locations_nearest_node)
{'Ardoyne Library': {'nearest_node': 475085580}, 'Ballyhackamore Library': 
{'nearest_node': 73250694}, 'Belfast Central Library': {'nearest_node': 4513699587}}

# Generate service areas
## Define the distance bands in a list.
distances = [1000,2000,3000] # Distances in meters

## Create individual service area polygons for each start location and distance.
network_areas  =  network_bands.service_areas(nearest_node_dict = start_locations_nearest_node, 
                                              graph = G , #networkX graph
                                              search_distances = search_distances, 
                                              alpha_value=500, # Value for alpha shape
                                              weight  =  'length', # chooses shortest path based off length
                                              progress = True, # Prints ongoing progress
                                              save_output = True) #Saves output automatically to .gpkg
## Create tidy service area polygons by dissolving and differencing based on attributes.
network_service_areas  =  network_bands.service_bands(geodataframe=network_areas, #output of network_areas() or service areas gdf.
                                                              dissolve_cat = 'distance', # column to dissolve by
                                                              aggfunc = 'first', #geopandas aggregate arg
                                                              show_graph = True, #displays output
                                                              save_output = True) #Saves output automatically to .gpkg

# Do subsequent analysis. See data_analysis.ipynb for an example.
```
</details>

## Use Cases
The tools within this repository are useful for the following:
-  **Calculates service areas based on network distance:** Generates services areas around many start locations based on nearest network nodes within specified distances. The output of which can be dissolved and is useful for visualising and analysing accessibility to a range of services such as healthcare, amenities, education etc.

-  **Visual representation of accessibility:** Assists in modelling how far services can extend from certain points, crucial for resource allocation and planning of new governmental projects or identifying commercial opportunities.


## Roadmap

The roadmap provides a glimpse into the current plans and priorities for future releases:

### Upcoming Features (v1.1)
- **Improved Example**: Increase the complexity of the `data_analysis.ipynb` example script.

### Upcoming Features (v1.2)

- **Online Road Network Compatibility**: Graph creation will be handled more dynamically with packages such as `pyrosm` and `osmnx`

### Planned Features (v1.3+)

- **Individual Start-to-End Shortest Routes**: Create additional tools to handle computationally intensive shortest routes between start and end location. The goal will be to iterate over numerous start and end locations to calculate the shortest route between each start location and end location.
- **Develop GUI**: A GUI will be developed to enable non-code users to engage with some of the more basic and principal tools.
- **Graph Creation of Other Formats**: A tool to handle the creation of network graphs, extracting the nodes and edges from other geospatial file formats. Note: This might be expedited to an earlier release


### Known Issues & Limitations

- **Issue 1**: Currently only handles off-line .pbf files - due to be handled in v1.1 release
- **Issue 2**: Graph creation from other file formats not currently supported.
- **Issue 3**: Dissolved network service areas currently do not retain parent information - this should change soon.

## Contributing

We will be welcoming contributions from the community, particularly with bugs. You can contribute by:

- [Submitting bugs and feature requests](https://github.com/username/project-name/issues), and help us verify as they are checked in.


## License

This project is licensed under the GNU License - see the [LICENSE.md](LICENSE) file for details.

## Authors

- **Sam Groves** - [hularuns](https://github.com/hularuns)

## Acknowledgments

- Thank you stack overflow!

###### All pointer data has been randomised multiple times to ensure that the data is defunct for any nefarious use and is solely for use as an easy example. A partial example of how this was randomised is included in the [services](services/randomise_data/randomise_data.py)
