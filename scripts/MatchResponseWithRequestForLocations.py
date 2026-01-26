import json
import pandas as pd

def MatchResponseWithRequestForLocations(requestfile,responsefile):
    # geeft terug : een dataframe met de locaties in volgorde van de response.
    with open(requestfile, "r") as f:
        RouteRequest = json.load(f)
    tasks = RouteRequest["tasks"]  # data["tasks"] is een lijst van dictionaries
    df_Request = pd.json_normalize(tasks)  # json_normalize maakt geneste structuren plat
    
    df_Request["Identifier"] = (
        ( 10**8 * df_Request["address.latitude"]).astype(int).astype(str)
        + "_"
        + (10**8 * df_Request["address.longitude"]).astype(int).astype(str)
    )


    df_response = pd.read_csv(responsefile, header=None, names=["tasks"])


    df_response["tasks"] = df_response["tasks"].astype(str)
    df_Request["id"] = df_Request["id"].astype(str)
    df_result = df_response.merge(df_Request,left_on="tasks",right_on="id", how="left")

    return df_result