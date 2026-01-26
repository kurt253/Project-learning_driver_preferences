from config import LOC_REQUESTS
from config import LOC_INTERMEDIATE
from config import LOC_RESPONSES

from MatchResponseWithRequestForLocations import MatchResponseWithRequestForLocations
from BerekenVerschilInSequentie import VerschilInSequentie

import pandas as pd
import re
import json
import math
import matplotlib.pyplot as plt

"""
function : get_directories()
----------------------------
recursively go through all directories of LOC_REQUESTS
search for file match a pattern on (number)_(char,number)-(date)-(time)-(rest).json
matching file names where time > 120000 are ignored from the output.
input :
1. /
output :
1. dataframe with 5 columns matching the () above : depot, route, date, time, rest.
"""
def get_directories():
    rows = list()
    for item in LOC_REQUESTS.rglob("*"):
        # print(type(item))
        if item.is_file():
            # print(f"file : {item} {item.name}")
            m = re.search(r"(?P<depot>\d+)_(?P<route>[A-Z0-9]+)-(?P<date>\d{8})-(?P<time>\d{6})-(?P<rest>.+).json",item.name,)
            if m:
                # print (m.group('route'))
                # print (m.groupdict())
                if ( m.group("time") <= "120000"):
                    rows.append( m.groupdict() )
                # else:
                #     print (f"ignore {m.groupdict()}")
            # else:
            #     print ("no match found.")
        # else:
        #     print(f"directory : {item}")

    df = pd.DataFrame(rows)
    return df

"""
function : get_min_max_directories(df)
------------------------------------
for every combination of depot, route and date :
1. retrieve the minimum and maximum time
2. retrieve the corresponding directory for the minimum and maximum time
3. write the content of the dataframe to a file LOC_INTERMEDIATE/depot-min-max-paths.csv

input : 
1. df : dataframe with columns depot, route, date, time, rest.
output : dataframe with the columns :
1. depot, route, date, time, rest (from the original dataframe)
2. min, max, min_path, max_path (calculated)
3. LOC_INTERMEDIATE/depot-min-max-paths.csv
"""
def get_min_max_directories(df):
    df_min_max = df.groupby(["depot","route","date"])["time"].agg(["min", "max"])
    # display(df_min_max)
    # display(df_min_max.reset_index())
    df_id_1 = pd.merge(df_min_max, df, left_on=["depot","route","date","min"], right_on=["depot","route","date","time"])[["depot","route","date","min","rest","max"]]
    # display(df_id_1)
    df_id_2 = pd.merge(df_id_1, df, left_on=["depot","route","date","max"], right_on=["depot","route","date","time"])[["depot","route","date","min","rest_x","max","rest_y"]]
    # display(df_id_2)
    df_min_max_rest = df_id_2.rename({"rest_x":"min_rest","rest_y":"max_rest"},axis=1)
    # display(df_min_max_rest)
    df_min_max_rest["min_path"] = df_min_max_rest["depot"] + "_" + df_min_max_rest["route"] + "-" + df_min_max_rest["date"] + "/" + df_min_max_rest["depot"] + "_" + df_min_max_rest["route"] + "-" + df_min_max_rest["date"] + "-" + df_min_max_rest["min"]  + "-" + df_min_max_rest["min_rest"] + ".json"
    df_min_max_rest["max_path"] = df_min_max_rest["depot"] + "_" + df_min_max_rest["route"] + "-" + df_min_max_rest["date"] + "/" + df_min_max_rest["depot"] + "_" + df_min_max_rest["route"] + "-" + df_min_max_rest["date"] + "-" + df_min_max_rest["max"]  + "-" + df_min_max_rest["max_rest"] + ".json"
    df_min_max_rest["min_resp_path"] = df_min_max_rest["depot"] + "_" + df_min_max_rest["route"] + "-" + df_min_max_rest["date"] + "/" + df_min_max_rest["depot"] + "_" + df_min_max_rest["route"] + "-" + df_min_max_rest["date"] + "-" + df_min_max_rest["min"]  + "-" + df_min_max_rest["min_rest"] + ".txt"
    df_min_max_rest["max_resp_path"] = df_min_max_rest["depot"] + "_" + df_min_max_rest["route"] + "-" + df_min_max_rest["date"] + "/" + df_min_max_rest["depot"] + "_" + df_min_max_rest["route"] + "-" + df_min_max_rest["date"] + "-" + df_min_max_rest["max"]  + "-" + df_min_max_rest["max_rest"] + ".txt"
    df_min_max_rest.to_csv(LOC_INTERMEDIATE/"depot-min-max-paths.csv",index=False)
    return df_min_max_rest

"""
function : get_unique_delivery_points()
---------------------------------------
recursively go through all directories of LOC_REQUESTS
search for *.json
from the json file extract tasks/address/latitude and tasks/address/longitude
store the unique combinations in a dictionary
input :
1. /
output :
1. list of items
1a. key : (latitude, longitude)
1b.value : (latitude, longitude)
"""
def get_unique_delivery_points():
    unique_delivery_points = dict()
    for loc_route in LOC_REQUESTS.rglob("*.json"):
        # print (loc_route)
        with open ( loc_route ) as json_file:
            json_route = json.load(json_file)
        for task in json_route["tasks"]:
            latitude = task["address"]["latitude"]
            longitude = task["address"]["longitude"]
            if (latitude, longitude) not in unique_delivery_points.keys():
                unique_delivery_points[(latitude, longitude)] = (latitude, longitude) 
    return unique_delivery_points


"""
function : get_levenshtein_distance(a: str, b: str)
---------------------------------------------------
calculate levenshtein distance
input :
1. two strings to compare
output :
1. distance (int)
"""
def get_levenshtein_distance(a: str, b: str) -> int:
    m, n = len(a), len(b)

    # Create a (m+1) x (n+1) DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    # print (dp)

    # Base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    # print (dp)

    # Fill table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )

    return dp[m][n]

"""
function haversine(lat1, lon1, lat2, lon2, radius=6371.0088)
------------------------------------------------------------
calcuates the distance between two points according to the haversine formula
input :
1. lat1, lon1 : latitude, longitude first point
2. lat2, lon2 : latitude, longitude second point
3. radius : earth radius (defaults to km)
output :
1. distance in km
"""
def haversine(lat1, lon1, lat2, lon2, radius=6371.0088):
    """
    Compute the great-circle distance between two points on Earth.
    Parameters:
        lat1, lon1, lat2, lon2 : float (degrees)
        radius : Earth radius (km by default). 
                 Use 6371.0088 km (mean Earth radius) or 3958.7613 miles.
    Returns:
        distance in the same units as 'radius'
    """
    # Convert degrees to radians
    φ1, λ1, φ2, λ2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dφ = φ2 - φ1
    dλ = λ2 - λ1

    a = math.sin(dφ/2)**2 + math.cos(φ1) * math.cos(φ2) * math.sin(dλ/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return radius * c


"""
function : get_distance (lat1, lon1, lat2, lon2)
------------------------------------------------
input :
1. lat1, lon1 : latitude, longitude first point
2. lat2, lon2 : latitude, longitude second point
output :
1. distance in km
"""
def get_distance (lat1, lon1, lat2, lon2):
    return haversine(lat1, lon1, lat2, lon2)

"""
function : get_distance_route (df_route)
----------------------------------------
calculates the distance of a whole route, including start/finish from the depot
input :
1. df_route : dataframe of the route (excl. depot), with columns latitude and longitude
output :
1. total distance in km of the route
"""
def get_distance_route (df_route):
    lat1 = None
    lon1 = None
    distance_route = 0
    for row_index, row_route in df_route.iterrows():
        lat2 = row_route["latitude"]
        lon2 = row_route["longitude"]
        if (lat1 is not None and lon1 is not None):
            distance_row = get_distance(lat1, lon1, lat2, lon2)
            distance_route += distance_row
        lat1 = lat2
        lon1 = lon2
    distance_route = round(distance_route, 3)
    return distance_route

"""
function : get_depot_location()
-------------------------------
retrieve the deport location based on all unique delivery points
retrieve all unique delivery points
calculate the average of all latitudes and average of all longitudes
input :
1. /
output :
1.  hash { "latitude" : average of all latitudes, "longitude" : average of all longitudes }
"""
def get_depot_location():
    unique_delivery_points = get_unique_delivery_points()
    df_unique_delivery_points = pd.DataFrame(unique_delivery_points)
    # display(df_unique_delivery_points)
    df_unique_delivery_points_T = df_unique_delivery_points.transpose()
    # display(df_unique_delivery_points_T)
    depot_route = df_unique_delivery_points_T.mean(axis = 0)
    # display(depot_route)
    depot_latitude = depot_route[0]
    depot_longitude = depot_route[1]
    # print (depot)
    depot = { "latitude" : depot_latitude, "longitude" : depot_longitude }
    return depot


"""
function : read_route ( loc_request, loc_response )
---------------------------------------------------
reads the entire route based on the request and response file
returns a dataframe with the whole route
inpuut :
1. loc_request : location of the request file
2. loc_response : location of the response file
output :
1. dataframe with all latitude, longitude points in sequence
"""
def read_route ( loc_request, loc_response ):
    loc_request = LOC_REQUESTS/loc_request
    loc_response = LOC_RESPONSES/loc_response
    df = MatchResponseWithRequestForLocations( loc_request, loc_response )
    df = df.rename(columns={"address.latitude":"latitude", "address.longitude":"longitude"})
    return df


"""
function read_route_and_calculate_distance ( loc_request, loc_response, depot = None)
-------------------------------------------------------------------------------------
reads the request and response file of a route on a given day, as well as the location of the depot
calculates the total distance of the route
input :
1. loc_request : location of the request file
2. loc_response : location of the response file
3. depot : location of the depot (optional argument, if omitted, distance is calculated of the route only)
output :
1. distance of the route
"""
def read_route_and_calculate_distance ( loc_request, loc_response, depot = None ):
    df_route = read_route( loc_request, loc_response )
    df_route = df_route[["latitude", "longitude"]]
    if depot is not None:
        # add the depot to the start and finish of the route
        df_depot = pd.DataFrame( [ depot ] )
        df_route = pd.concat([df_depot, df_route, df_depot])
    distance = get_distance_route (df_route)
    return distance


"""
function get_levenshtein_string( loc_request, loc_response )
------------------------------------------------------------
for a given route, concatenate all string values of the column "Identifier"
input :
1. loc_request : location of the request file
2. loc_response : location of the response file
output :
1. concatenated string of all values in the "Identifer" column, w/o separator
"""
def get_levenshtein_string( loc_request, loc_response ):
    df_route = read_route( loc_request, loc_response )
    levenshtein_str = df_route["Identifier"].str.cat(sep="")
    return levenshtein_str


"""
function : read_route_and_calculate_number_delivery_points ( loc_request, loc_response, depot = None )
reads the request and response file of a route on a given day, as well as the location of the depot
calculates the total number of delivery points of the route
input :
1. loc_request : location of the request file
2. loc_response : location of the response file
3. depot : location of the depot (optional argument, if omitted, numbber is calculated of the route only)
output :
1. number of delivery points of the route
"""
def read_route_and_calculate_number_delivery_points ( loc_request, loc_response, depot = None ):
    df_route = read_route( loc_request, loc_response )
    count_delivery_points = df_route["latitude"].count()
    df_route = df_route[["latitude", "longitude"]]
    if depot is not None:
        count_delivery_points += 2
    return count_delivery_points


"""
function : calculate_difference_in_sequence(min_req_path, min_resp_path, max_req_path, max_resp_path)
inpuut :
1. min_req_path : id of the depot
2. min_resp_path : id of the route
3. damax_req_pathte : date of the route
4. max_resp_path : summary of all routes
output :
1. difference in sequence
"""
def calculate_difference_in_sequence(min_req_path, min_resp_path, max_req_path, max_resp_path):
    df_route_min = read_route(min_req_path, min_resp_path)
    df_route_max = read_route(max_req_path, max_resp_path)
    
    difference_in_sequence = VerschilInSequentie(df_route_min, df_route_max)
    dict_difference = json.loads(difference_in_sequence)

    return [dict_difference["missing_in_df1_count"], dict_difference["missing_in_df2_count"], dict_difference["sequence_similarity"]]


"""
function : enrich_min_max(df_route)
-----------------------------------
adds additional set of data to the set of routes, like : haversine and levenshtein distances, number of delivery points
input :
1. df_route : dataframe with basic set of parameters for every combination of depot, route and date, the parameters first calculation
   time, last calculation time of the morning, the paths to the respective requests and response files
2. depot : location of the depot
output :
1. enriched dataframe df_route with haversine and levenshtein distances, number of delivery points, missing elements in min,
   missing elements in max, sequence similarity
"""
def enrich_min_max(df_route, depot):
    df_route["min_distance"]=df_route.apply(lambda x : read_route_and_calculate_distance(x["min_path"],x["min_resp_path"], depot), axis = 1)
    df_route["max_distance"]=df_route.apply(lambda x : read_route_and_calculate_distance(x["max_path"],x["max_resp_path"], depot), axis = 1)
    df_route["min_levenshtein_str"]=df_route.apply(lambda x : get_levenshtein_string( x["min_path"],x["min_resp_path"] ), axis = 1)
    df_route["max_levenshtein_str"]=df_route.apply(lambda x : get_levenshtein_string( x["max_path"],x["max_resp_path"] ), axis = 1)
    df_route["levenshtein_distance"]=df_route.apply(lambda x : get_levenshtein_distance(x["min_levenshtein_str"], x["max_levenshtein_str"]), axis = 1)
    df_route["min_number_delivery_points"]=df_route.apply(lambda x : read_route_and_calculate_number_delivery_points(x["min_path"],x["min_resp_path"], depot), axis = 1)
    df_route["max_number_delivery_points"]=df_route.apply(lambda x : read_route_and_calculate_number_delivery_points(x["max_path"],x["max_resp_path"], depot), axis = 1)
    df_route[["missing_in_min","missing_in_max","sequence_similarity"]] = df_route.apply(lambda x : calculate_difference_in_sequence(x["min_path"], x["min_resp_path"], x["max_path"], x["max_resp_path"]), axis = 1, result_type="expand")
    df_route.to_csv(LOC_INTERMEDIATE/"depot-min-max-enriched.csv",index=False)
    return df_route


"""
function : plot_route ( loc_min, loc_max, depot )
-------------------------------------------------
will plot a route - first calculation and last calculation of the morning
route with and without depot will be plotted
input :
1. df_routes : summary of all routes
2. depot : id of the depot
3. route : id of the route
4. date : date of the route
5. loc_depot : location of the depot as dictionary (latitude, longitude)
output :
1. plot of the routes
"""
def plot_route ( depot, route, date, df_routes, loc_depot ):
    plt.rcParams["figure.figsize"] = (24,12)
    fig, axes = plt.subplots(1,3)
    loc_min_req = df_routes[(df_routes["depot"] == depot) & (df_routes["route"] == route) & (df_routes["date"] == date)]["min_path"].iloc[0]
    loc_min_resp = df_routes[(df_routes["depot"] == depot) & (df_routes["route"] == route) & (df_routes["date"] == date)]["min_resp_path"].iloc[0]
    loc_max_req = df_routes[(df_routes["depot"] == depot) & (df_routes["route"] == route) & (df_routes["date"] == date)]["max_path"].iloc[0]
    loc_max_resp = df_routes[(df_routes["depot"] == depot) & (df_routes["route"] == route) & (df_routes["date"] == date)]["max_resp_path"].iloc[0]
    # print ( f"{loc_min_req} {loc_min_resp} {loc_max_req} {loc_max_resp}")

    df_depot = pd.DataFrame([loc_depot])
    df_route_min = read_route(loc_min_req, loc_min_resp)
    df_route_min_with_depot = pd.concat([df_depot, df_route_min, df_depot])
    df_route_max = read_route(loc_max_req, loc_max_resp)
    df_route_max_with_depot = pd.concat([df_depot, df_route_max, df_depot])

    # routes with depot
    axes[0].plot(df_route_min_with_depot["latitude"],df_route_min_with_depot["longitude"],'-r',label='min with depot')
    axes[0].plot(df_route_max_with_depot["latitude"],df_route_max_with_depot["longitude"],'-g',label='max with depot')
    title_0 = f"depot {depot} route {route} date {date}"
    axes[0].legend(title=title_0, prop={'size': 8})
    axes[0].set_xlabel("latitude")
    axes[0].set_ylabel("longitude")
    # routes without depot - min
    axes[1].plot(df_route_min["latitude"],df_route_min["longitude"],'-r',label='min w/o depot')
    title_1 = f"depot {depot} route {route} date {date}"
    axes[1].legend(title = title_1,prop={'size': 8})
    axes[1].set_xlabel("latitude")
    axes[1].set_ylabel("longitude")
    # routes without depot - max
    axes[2].plot(df_route_max["latitude"],df_route_max["longitude"],'-g',label='max w/o depot')
    title_2 = f"depot {depot} route {route} date {date}"
    axes[2].legend(title = title_2,prop={'size': 8})
    axes[2].set_xlabel("latitude")
    axes[2].set_ylabel("longitude")



if __name__ == "__main__" :
    print (f"testing as a standalone script")
    df = get_directories()
    df_min_max = get_min_max_directories(df)
    print (df_min_max)
    # depot = get_depot_location()
    # print (depot)
    # print (depot)
    # loc_route = "0521_300-20220617/0521_300-20220617-055733-2-0.json"
    # print ( loc_route )

    # print (levenshtein_distance("bompa","bomma"))
    # print (levenshtein_distance("bompas","bomma"))
    # print (levenshtein_distance("bompa","viva bomma patatten met saucissen"))

    # unique_delivery_points = get_unique_delivery_points()
    # print ( unique_delivery_points )

    # Example
    # brussels = (50.8503, 4.3517)
    # paris    = (48.8566, 2.3522)
    # print(haversine(*brussels, *paris), "km")

    # loc_req = LOC_REQUESTS/"0521_301-20220531/0521_301-20220531-054500-159-0.json"
    # loc_resp = LOC_RESPONSES/"0521_301-20220531/0521_301-20220531-054500-159-0.txt"
    # df = MatchResponseWithRequestForLocations(loc_req, loc_resp)
    # print(df)

    # loc_req = "0521_301-20220531/0521_301-20220531-054500-159-0.json"
    # loc_resp = "0521_301-20220531/0521_301-20220531-054500-159-0.txt"
    # df = read_route(loc_req, loc_resp)
    # print(df)

    # dist_route_wo_depot = read_route_and_calculate_distance ( loc_req, loc_resp )
    # dist_route_with_depot = read_route_and_calculate_distance ( loc_req, loc_resp, depot )
    # print (f"distance w/o depot : {dist_route_wo_depot}, distance with depot : {dist_route_with_depot}")

    loc_req = "0521_301-20220531/0521_301-20220531-054500-159-0.json"
    loc_resp = "0521_301-20220531/0521_301-20220531-054500-159-0.txt"
    loc_req_2 = "0521_301-20220531/0521_301-20220531-064436-148-148.json"
    loc_resp_2 = "0521_301-20220531/0521_301-20220531-064436-148-148.txt"

    lev_str = get_levenshtein_string( loc_req, loc_resp )
    # print ( f"levenshtein string : {lev_str}")
    lev_str_2 = get_levenshtein_string( loc_req_2, loc_resp_2 )
    # print ( f"levenshtein string 2 : {lev_str_2}")
    lev_dist = get_levenshtein_distance(lev_str, lev_str_2)
    print (f"levenshtein distance : {lev_dist}")

    # subdir_req = "0521_301-20220531/0521_301-20220531-054500-159-0.json"
    # route_path_req = LOC_REQUESTS/subdir_req
    # subdir_resp = "0521_301-20220531/0521_301-20220531-054500-159-0.txt"
    # route_path_resp = LOC_RESPONSES/subdir_resp
    # # route_path = LOC_REQUESTS/"0521_301-20220531/0521_301-20220531-054500-159-0.json"
    # # print (route_path)

    # df_route = read_route ( route_path_req, route_path_resp )
    # display ( df_route)

    # distance_route = read_route_and_calculate_distance( loc_route, depot )
    # print ( f"route {loc_route} - distance {distance_route}")

