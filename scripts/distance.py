import random
import pandas as pd

def get_distance_between_two_points (latitude1, longitude1, latitude2, longitude2):
  # returns the distance between two points in km.
  # input : the latitude and longitude of the two points to connect.
  return random.randint(1,10)

def get_distance_for_route (route):
  # returns the total distance for a route 
  # input : DataFrame with two columns (latitude, longitude) - every row consists of one point. 
  # Points are sorted in the order they will be travelled.
  return randam.randint(150,200)

def get_distance_for_all_routes (routes):
  # returns a DataFrame with two columns : route_id and 
  # input : DataFrame with three columns (route_id, latitude, longitude) - every row consists of one point on one row.  
  # Points are sorted in the order they will be travelled.
  rows = list()
  for route in range(20):
    route_id = "ROUTE" + str(route)
    distance = random.randint(150,200)
    rows.append({"route_id":route_id, "distance":distance})
  routes = pd.DataFrame(rows)
  return routes
