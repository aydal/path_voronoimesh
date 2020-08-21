"""
The MIT License (MIT)

Copyright (c) 2016 Christian August Reksten-Monsen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from collections import defaultdict
from shapely.geometry import Polygon,Point,LineString
from shortest_path import shortest_path
from tqdm import tqdm
import math
from sys import stdout, version_info
PYTHON3 = version_info[0] == 3
if PYTHON3:
    xrange = range
    import pickle
else:
    import cPickle as pickle


class Edge(object):
    __slots__ = ('p1', 'p2','cost')

    def __init__(self, point1, point2,cost=1):
        self.p1 = point1
        self.p2 = point2
        self.cost= cost

    def get_adjacent(self, point):
        if point == self.p1:
            return self.p2
        return self.p1

    def get_cost(self):
        return self.cost

    def line(self):
        return LineString([self.p1,self.p2])

    def __contains__(self, point):
        return self.p1 == point or self.p2 == point

    def __eq__(self, edge):
        if self.p1 == edge.p1 and self.p2 == edge.p2:
            return True
        if self.p1 == edge.p2 and self.p2 == edge.p1:
            return True
        return False

    def __ne__(self, edge):
        return not self.__eq__(edge)

    def __str__(self):
        return "({}, {})".format(self.p1, self.p2)

    def __repr__(self):
        return "Edge({!r}, {!r})".format(self.p1, self.p2)

    def __hash__(self):
        return self.p1.__hash__() ^ self.p2.__hash__()


class Graph(object):
    """
    A Graph is represented by a dict where the keys are Points in the Graph
    and the dict values are sets containing Edges incident on each Point.
    A separate set *edges* contains all Edges in the graph.

    The input must be a list of polygons, where each polygon is a list of
    in-order (clockwise or counter clockwise) Points. If only one polygon,
    it must still be a list in a list, i.e. [[Point(0,0), Point(2,0),
    Point(2,1)]].

    *polygons* dictionary: key is a integer polygon ID and values are the
    edges that make up the polygon. Note only polygons with 3 or more Points
    will be classified as a polygon. Non-polygons like just one Point will be
    given a polygon ID of -1 and not maintained in the dict.
    """

    def __init__(self, gdf_vd=[]):
        self.graph = defaultdict(set)
        self.edges = set()
        self.triangles=[]
        if len(gdf_vd):
            print("hello")
            for polys in gdf_vd:
                if polys.geom_type=='Polygon':
                    self.triangles.append(polys)
                    polygon=polys.exterior.coords[:-1]
                    for i, point in enumerate(polygon):
                        sibling_point = polygon[(i + 1) % len(polygon)]
                        edge = Edge(point, sibling_point)
                        self.add_edge(edge)

    def get_adjacent_points(self, point):
        return [edge.get_adjacent(point) for edge in self[point]]

    def get_points(self):
        return list(self.graph)

    def get_edges(self):
        return self.edges

    def load(self, filename):
        """Load obstacle graph and visibility graph. """
        with open(filename, 'rb') as load:
            self.graph,self.edges,self.triangles = pickle.load(load)

    def save(self, filename):
        """Save obstacle graph and visibility graph. """
        with open(filename, 'wb') as output:
            pickle.dump((self.graph,self.edges,self.triangles), output, -1)

    def update_cost(self,gdf):
        print("Updating Cost")
        tmp_list=list(self.edges)
        for i,edge in enumerate(tqdm(tmp_list)):
            #print(i,edge.p1,edge.p2)
            pip=gdf.intersects(edge.line())
            pip_mask=gdf.loc[pip]
            cost = pip_mask['cost'].max()
            if not math.isnan(cost):
                tmp_list[i].cost=cost
        self.edges=set(tmp_list)


    def add_edge(self, edge):
        self.graph[edge.p1].add(edge)
        self.graph[edge.p2].add(edge)
        self.edges.add(edge)

    def __contains__(self, item):
        if isinstance(item, Point):
            return item in self.graph
        if isinstance(item, Edge):
            return item in self.edges
        return False

    def __getitem__(self, point):
        if point in self.graph:
            return self.graph[point]
        return set()

    def __str__(self):
        res = ""
        for point in self.graph:
            res += "\n" + str(point) + ": "
            for edge in self.graph[point]:
                res += str(edge)
        return res

    def __repr__(self):
        return self.__str__()

    def visible_vertices(self, pt):
        dist = self.triangles[0].distance(pt)
        listx=[]
        for poly in self.triangles:
            tmp=pt.distance(poly)
            if tmp==0.0:
                return poly.exterior.coords[:-1]
            if tmp<dist:
                    dist=tmp
                    listx=poly.exterior.coords[:-1]
        return listx


    def shortest_path(self, origin, destination):
        """Find and return shortest path between origin and destination.

        Will return in-order list of Points of the shortest path found. If
        origin or destination are not in the visibility graph, their respective
        visibility edges will be found, but only kept temporarily for finding
        the shortest path. 
        """

        origin_exists = origin in self.graph
        dest_exists = destination in self.graph
        if origin_exists and dest_exists:
            return shortest_path(self.graph, origin, destination)
        orgn = None if origin_exists else origin
        dest = None if dest_exists else destination
        add_to_graph = Graph()
        if not origin_exists:
            for v in self.visible_vertices(Point(origin)):
                add_to_graph.add_edge(Edge(origin, v))
        if not dest_exists:
            for v in self.visible_vertices(Point(destination)):
                add_to_graph.add_edge(Edge(destination, v))
        return shortest_path(self.graph, origin, destination, add_to_graph)