# path_voronoimesh
Find shortest path in geodatabase converted to voronoi mesh. We use Python 3.6+

Major dependency is shapely. We use `triangulate`,`voronoi_diagram` & `polygonise` in shapely.ops. At the time of push, you needed shapely 1.8.0 which is not the current stable pip version. \
To install\
`pip3 install git+https://github.com/Toblerity/Shapely`

Other dependencies - `geopandas` & `mapbox`(for getting database for geographical database)

Dependencies in the repository - graph.py, shortest_path.py.

To execute code, follow these steps
```
mkdir data triangles

python3 fetch.py
python3 get_triangles.py
python3 post.py
```
`fetch.py`-Get the database and store it in excel file in data folder. Default name for file is `src.xlsx`. Change the out variable for a different name.
Other paramters - token for mapbox account and dataset code

`get_triangles.py`-Get voronoi diagram for the dataset, remove overlaps and obstacles and perform triangulation. Polygons are read from data folder and triangles are stored in triangles folder. Change default name for file by changing variable read and write

`post.py`-Generate graph and save it. Also used to check shortest path algorithm.
Optional - Update cost by using a geodataframe with column geometry and cost

