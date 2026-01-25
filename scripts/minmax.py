from config import LOC_REQUESTS
from config import LOC_INTERMEDIATE
from config import LOC_RESPONSES

import pandas as pd
import re
import json

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
                if ( m.group("time") > "120000"):
                    print (f"ignore {m.groupdict()}")
                else:
                    rows.append( m.groupdict() )
            else:
                print ("no match found.")
        else:
            print(f"directory : {item}")

    df = pd.DataFrame(rows)
    return df

def get_min_max_directories(df):
    df_min_max = df.groupby(["depot","route","date"])["time"].agg([min, max])
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
        # print ( task["id"] )
        # print ( task["address"] )
    return unique_delivery_points


def levenshtein_distance(a: str, b: str) -> int:
    m, n = len(a), len(b)

    # Create a (m+1) x (n+1) DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    print (dp)

    # Base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    print (dp)

    # Fill table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )

    print (dp)
    return dp[m][n]

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

# def read_route ( route_path_req, route_path_resp ):
#     points = list()
#     with open ( route_path_req ) as json_file:
#         json_route = json.load(json_file)
#     for task in json_route["tasks"]:
#         # print ( task["id"] )
#         # print ( task["address"] )
#         points.append(task["address"])
#     df_req = pd.DataFrame(points)
#     points = list()
#     with open ( route_path_resp ) as txt_file:
#         lines = txt_file.readlines()
#     df_resp= pd.DataFrame(lines)
#     return df
    
# def read_route_and_calculate_distance ( loc_route, depot ):
#     df_route = read_route( LOC_REQUESTS/loc_route )
#     depot_route = get_distance_route (df_route, depot)
#     return depot_route

# loc_route = "0521_300-20220617/0521_300-20220617-055733-2-0.json"
# print ( loc_route )
# distance_route = read_route_and_calculate_distance( loc_route, depot )
# print ( f"route {loc_route} - distance {distance_route}")


if __name__ == "__main__" :
    print (f"testing as a standalone script")
    df = get_directories()
    df_min_max = get_min_max_directories(df)
    depot = get_depot_location()
    print (depot)
    loc_route = "0521_300-20220617/0521_300-20220617-055733-2-0.json"
    print ( loc_route )

    print (levenshtein_distance("bompa","bomma"))
    print (levenshtein_distance("bompas","bomma"))
    print (levenshtein_distance("bompa","viva bomma patatten met saucissen"))

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

