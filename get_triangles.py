import geopandas as gpd
from shapely.ops import voronoi_diagram as svd
from shapely.ops import triangulate,polygonize
from shapely import wkt
from shapely.geometry import Polygon,Point,LineString,box, MultiPolygon
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
read='src.xlsx'
write='tri.xlsx'
def voronoiDiagram4plg(gdf, mask):
	'''Create Voronoi diagram / Thiessen polygons based on polygons.
	
	Parameters:
		gdf: polygons to be used to create Voronoi diagram
			Type: geopandas.GeoDataFrame
		mask: polygon vector used to clip the created Voronoi diagram
			Type: GeoDataFrame, GeoSeries, (Multi)Polygon
	Returns:
		gdf_vd: Thiessen polygons
			Type: geopandas.geodataframe.GeoDataFrame
	'''
	gdf.reset_index(drop=True)
	#convert to shapely.geometry.MultiPolygon
	smp = gdf.unary_union
	#create primary voronoi diagram by invoking shapely.ops.voronoi_diagram (new in Shapely 1.8.dev0)
	smp_vd = svd(smp,edges=True)
	#convert to GeoSeries and explode to single polygons
	#note that it is NOT supported to GeoDataFrame directly
	gs1 = gpd.GeoSeries([smp_vd]).explode()
	gs=list(polygonize(gs1))
	#convert to GeoDataFrame
	#note that if gdf was shapely.geometry.MultiPolygon, it has no attribute 'crs'
	gdf_vd = gpd.geodataframe.GeoDataFrame(geometry=gs, crs=gdf.crs)
	
	#reset index
	gdf_vd.reset_index(drop=True)	#append(gdf)
	#spatial join by intersecting and dissolve by `index_right`
	gdf_temp = ( gpd.sjoin(gdf_vd, gdf, how='inner', op='intersects')
		.dissolve(by='index_right').reset_index(drop=True) )

	gdf_vd = gpd.clip(gdf_temp, mask)
	gdf_vd = dropHoles(gdf_vd)
	return gdf_vd

def dropHolesBase(plg):
	'''Basic function to remove / drop / fill the holes.
	
	Parameters:
		plg: plg who has holes / empties
			Type: shapely.geometry.MultiPolygon or shapely.geometry.Polygon
	Returns:
		a shapely.geometry.MultiPolygon or shapely.geometry.Polygon object
	'''
	if isinstance(plg, MultiPolygon):
		return MultiPolygon(Polygon(p.exterior) for p in plg)
	elif isinstance(plg, Polygon):
		return Polygon(plg.exterior)

def dropHoles(gdf):
	'''Remove / drop / fill the holes / empties for iterms in GeoDataFrame.
	
	Parameters:
		gdf:
			Type: geopandas.GeoDataFrame
	Returns:
		gdf_nohole: GeoDataFrame without holes
			Type: geopandas.GeoDataFrame
	'''
	gdf_nohole = gpd.GeoDataFrame()
	for g in gdf['geometry']:
		geo = gpd.GeoDataFrame(geometry=gpd.GeoSeries(dropHolesBase(g)))
		gdf_nohole=gdf_nohole.append(geo,ignore_index=True)
	gdf_nohole.rename(columns={gdf_nohole.columns[0]:'geometry'}, inplace=True)
	gdf_nohole.crs = gdf.crs
	return gdf_nohole

def get_triangles(readf=read,writef=write):
	df=pd.read_excel('data/'+readf)
	df['geometry'] = df['geometry'].apply(wkt.loads)
	gdf=  gpd.GeoDataFrame(df, crs=3395,geometry='geometry')

	(minx,miny,maxx,maxy)=gdf.total_bounds

	
	print("Generating Polygons...")
	gdf_vd=voronoiDiagram4plg(gdf,Polygon([(minx,miny),(minx,maxy),(maxx,maxy),(maxx,miny)]))


	print("Cleaning Polygons...")
	for i in tqdm(range(gdf_vd.shape[0])):
		j=i+1
		while(j<gdf_vd.shape[0]):
			if gdf_vd['geometry'][i].intersection(gdf_vd['geometry'][j]).area:
				gdf_vd['geometry'][i]=gdf_vd['geometry'][i].difference(gdf_vd['geometry'][j])
			j+=1
		pip_mask = gdf.intersects(gdf_vd['geometry'][i])
		x= gdf.loc[pip_mask]
		for poly in x['geometry']:
			gdf_vd['geometry'][i]=gdf_vd['geometry'][i].difference(poly)

	polist=[]
	for poly in gdf_vd.geometry:
		if poly.geom_type=='MultiPolygon':
			for pol in poly:
				if pol.geom_type=='MultiPolygon':
					for po in pol:
						polist.append(po)
				else:
					polist.append(pol)
		else:
			polist.append(poly)

	print("Triangulating")
	fff=MultiPolygon(polist)
	triangles = triangulate(fff)
	gex = gpd.GeoDataFrame(crs=3395,geometry=triangles)
	print(gex.shape)
	res_intersection = gpd.overlay(gex, gdf_vd, how='intersection')
	ax = res_intersection.plot()
	gdf.plot(ax=ax,alpha=0.8,color='gray')
	plt.show()
	res_intersection.to_excel('triangles/'+writef)

if __name__ == "__main__":
	get_triangles()