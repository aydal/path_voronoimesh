# -*- coding: utf-8 -*-
"""
* Updated on 2020/07/25
* python3
**
* Geoprocessing in Python
"""
import geopandas as gpd
from shapely.ops import voronoi_diagram as svd
from shapely.ops import triangulate
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry import Polygon,Point,LineString,box, MultiPolygon
import os

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
from tqdm import tqdm

tok="pk.eyJ1IjoiZ2FtYml0eDIzNCIsImEiOiJjandhYWp0czgwNDhtNDltZ2FqM3R6cm85In0.jI-6WO9__W9U0biRVnUs5A"
dataset="ck6ub6amu0h6g2nlhtl42fguy"
outf='src.xlsx'


def fetch(token=tok,data=dataset,out=outf):
	os.environ['MAPBOX_ACCESS_TOKEN']=token

	datasets=Datasets()
	col = datasets.list_features(data).json()
	df=pd.read_json(json.dumps(col['features']))
	nyc= json_normalize(df['geometry'])
	pp=[]
	for i in nyc.index:   
		if nyc['type'][i]=='Polygon':
			for ff in nyc['coordinates'][i]:
				pp.append(Polygon(ff))
		elif nyc['type'][i]=='LineString':
			pp.append(LineString(nyc['coordinates'][i]))
	gd=pd.DataFrame(columns=['geometry','type'])
	for poly in pp:

		gd=gd.append({'geometry': poly, 'type': poly.geom_type}, ignore_index=True)
	print(gd.head())
	crs={'init':'epsg:4326'}
	geo_df = gpd.GeoDataFrame(gd,crs=crs,geometry='geometry')
	data_proj = geo_df.to_crs(epsg=3395)
	print(data_proj.head())
	data_proj.to_excel('data/'+outf)
	

if __name__ == "__main__":
	fetch()