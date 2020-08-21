import geopandas as gpd
from shapely.ops import voronoi_diagram as svd
from shapely.ops import triangulate
from shapely.geometry import Polygon,Point,LineString,box, MultiPolygon
import os
os.environ['MAPBOX_ACCESS_TOKEN']="pk.eyJ1IjoiZ2FtYml0eDIzNCIsImEiOiJjandhYWp0czgwNDhtNDltZ2FqM3R6cm85In0.jI-6WO9__W9U0biRVnUs5A"
import pandas as pd
import numpy as np
from mapbox import Datasets
import matplotlib.pyplot as plt
import json
import sys
import geopandas as gpd
import descartes
from pandas import json_normalize
import geopandas as gpd
from shapely import wkt
from graph import Graph


df=pd.read_excel('triangles/tri.xlsx')
df['geometry'] = df['geometry'].apply(wkt.loads)
#gex=gpd.read_csv('tri.csv',sep=';')
gdf_vd =  gpd.GeoDataFrame(df, geometry='geometry')

df2=pd.read_excel('data/src.xlsx')
df2=df2[df2['type']=='LineString']
df2['geometry'] = df2['geometry'].apply(wkt.loads)

cost_vd =  gpd.GeoDataFrame(df2, geometry='geometry')



polyl=[]
for polys in gdf_vd.geometry:
	if polys.geom_type=='Polygon':
		polyl.append(polys )
	if polys.geom_type=='MultiPolygon':
		for poly in polys:
			polyl.append(poly)

vis = Graph(gdf_vd=polyl)

#vis.update_cost(cost_vd)
vis.save('jmd.pk1')
print(len(vis.edges))
print(len(vis.graph))
print("Calculating Path")
#path=vis.shortest_path(polyl[5].exterior.coords[2],polyl[505].exterior.coords[2])
print(len(vis.edges))
print(len(vis.graph))
path=vis.shortest_path((8605000,2649000),(8611000,2650500))
print(path)
print("Plotting")
gdf_vd.plot(facecolor='gray')
plt.plot(*zip(*path),color='red',alpha=0.5)
plt.scatter(8605000,2649000,color='green')
plt.scatter(8611000,2650500,color='black')
plt.show()