import os
import sys
import pandas as pd
import numpy as np
import openrouteservice as ors
import folium
import geopandas as gpd
import networkx as nx
import osmnx as ox
import geojson
from tqdm import tqdm, trange
import random as rn
from sklearn.metrics.pairwise import haversine_distances
from math import radians

ox.config(use_cache=True,
          log_file=True,
          log_console=False,
          log_filename='download-lisboa',
          cache_folder='cache')

print(ox.__version__)
print(nx.__version__)

ors_profiles = [
    'driving-car',
    'driving-hgv',
    'foot-walking',
    'foot-hiking',
    'cycling-regular',
    'cycling-road',
    'cycling-mountain',
    'cycling-electric']

color_dict = {
    'driving-car': '#F0D954',
    'driving-hgv': '#854F21',
    'foot-walking': '#328BCF',
    'foot-hiking': '#328BCF',
    'cycling-regular': '#2E8533',
    'cycling-road': '#2E8533',
    'cycling-mountain': '#2E8533',
    'cycling-electric': '#2E8533'
}


class ORS(object):
    def __init__(self, server_addr=None, ors_key=None, profiles=ors_profiles):
        self.profiles = profiles
        if server_addr is None:
            self.server = ors.Client(key=ors_key)
        else:
            self.server = ors.Client(base_url=server_addr)

    def compute_route(self, profile, coordinates):
        route = self.server.directions(
            coordinates=coordinates,
            profile=profile,
            format='geojson',
             extra_info=["steepness","suitability","surface","waycategory","waytype","tollways","traildifficulty","osmid","roadaccessrestrictions","countryinfo","green","noise"],
            validate=False)
        try:
            route_distance = route['features'][0]['properties']['summary']['distance']
            route_duration = route['features'][0]['properties']['summary']['duration']
        except :
             route_distance = 0
             route_duration = 0

        # print(profile, '\n==Distance:', route_distance, '\n==Duration:', route_duration, '\n')

        return route, route_distance, route_duration

    def compute_haversine_distance(self, point_a, point_b):
        """Computes the Haversine (Great Circle) distance between pointA and pointB."""

        point_a_in_radians = [radians(_) for _ in point_a]
        point_b_in_radians = [radians(_) for _ in point_b]
        result = haversine_distances([point_a_in_radians, point_b_in_radians])
        result = result * 6371000 / 1000 # to get km

        return result[0,1]



def read_points(file):
    if not os.path.exists(file):
        print('File {} does not exist to read points from. Please recheck the file\'s path'.format(file))
    points = []

    data = pd.read_csv(file, index_col=0)

    with trange(data.shape[0]) as t:
        for i in t:
            point_a = [float(x) for x in data['point_A'][i][1:-1].split(", ")]
            point_b = [float(x) for x in data['point_B'][i][1:-1].split(", ")]

            points.append([point_a, point_b])

    return data, points


def main():

    points_data = 'data/imob_generated_points.csv'
    output_file_sufix = '2020'
    output_file = 'data/dist_time_lisbon_imob_{}.csv'.format(output_file_sufix)

    server_addr = 'http://10.0.28.126:10020/ors'




    print('Creating output pd.Dataframe\n')
    columns = ['point_A', 'point_B', 'haversine_dist']
    for profile in ors_profiles:
        columns.append(profile+'_dist')
        columns.append(profile + '_time')


    print('Connecting to ORS server\n')
    ors_obj = ORS(server_addr=server_addr)

    print('Reading previous selected points\n')
    data, points = read_points(points_data)

    data = data.copy()

    for column in columns:
        data[column] = np.nan

    print('Iterating over points...')

    with trange(len(points)) as t:
        for i in t:
            t.set_description('Point %i' % (i+1))

            map = folium.Map(location=[-9.153140, 38.767118].copy()[::-1], tiles='cartodbpositron', zoom_start=13)

            point_a = points[i][0]
            point_b = points[i][1]

            coordinates = []
            coordinates.append(point_a)
            coordinates.append(point_b)
            data_row = {}
            data_row['point_A'] = point_a
            data_row['point_B'] = point_b

            data_row['vehicle'] = data.iloc[i]['vehicle']
            data_row['weekday'] = data.iloc[i]['weekday']
            data_row['weight'] = data.iloc[i]['weight']

            for profile in ors_profiles:
                try:
                    route, route_distance, route_duration = ors_obj.compute_route(profile, coordinates)
                    data_row[profile+'_dist'] = route_distance
                    data_row[profile+'_time'] = route_duration
                    folium.PolyLine(locations=[list(reversed(coord))
                                               for coord in route['features'][0]['geometry']['coordinates']],
                                    color=color_dict[profile]).add_to(map)
                    route_file = 'routes/imob_'+output_file_sufix+'_'+str(i)+'_'+profile+'.geojson'
                    with open(route_file, 'w') as f:
                        geojson.dump(route, f)
                except ors.exceptions.ApiError:
                    continue

            haversine = ors_obj.compute_haversine_distance(coordinates[0].copy()[::-1], coordinates[-1].copy()[::-1])
            data_row['haversine_dist']  = haversine

            data = data.append(data_row, ignore_index=True, sort=False)

            #map.save('html/'+output_file_sufix+'/index'+str(i)+'.html')

    #data.to_csv(output_file)
    print('Completed! File shape:', data.shape)


if __name__ == "__main__":
    main()

