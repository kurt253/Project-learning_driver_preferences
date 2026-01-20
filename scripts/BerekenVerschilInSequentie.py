import random
import json
import pandas as pd
import os
from difflib import SequenceMatcher
from IPython.display import display


def VerschilInSequentie(df1, df2):
    
    #Vergelijkt twee DataFrames op basis van de 'id'-kolom en de volgorde.
    
    #Parameters:
    #- df1, df2 : pd.DataFrame
    #    DataFrames met minimaal een kolom 'id'.
        
    #Returns:
    #- json_string : str
    #    JSON-string met:
    #    {
    #        "missing_in_df2": [...],    # ID's in df1 maar niet in df2
    #        "missing_in_df1": [...],    # ID's in df2 maar niet in df1
    #        "sequence_similarity": 0-1  # overeenkomst in volgorde
    #    }
    
    
    # --- 1. Controleer ontbrekende ID's ---
    ids_df1 = set(df1["id"])
    ids_df2 = set(df2["id"])

    missing_in_df2_count = len(ids_df1 - ids_df2)
    missing_in_df1_count = len(ids_df2 - ids_df1)

    # --- 2. Meet sequentie-overeenkomst ---
    seq1 = df1["id"].tolist()
    seq2 = df2["id"].tolist()
    matcher = SequenceMatcher(None, seq1, seq2)
    sequence_similarity = matcher.ratio()  # waarde tussen 0 en 1

    # --- 3. Maak dictionary van resultaten ---
    result = {
        "missing_in_df1_count": missing_in_df1_count,
        "missing_in_df2_count": missing_in_df2_count,
        "sequence_similarity": sequence_similarity
    }

    # --- 4. Converteer naar JSON-string ---
    json_string = json.dumps(result, indent=4)
    return json_string





def TestMain():
    RoutePath = ".\\data\\input\\requests\\0521_301-20220531\\"
    FRoute1 = "0521_301-20220531-054500-159-0.json"
    FRoute2 = "0521_301-20220531-064436-148-148.json"

    with open(os.path.join(RoutePath,FRoute1), "r") as f:
        Route1 = json.load(f)

    tasks = Route1["tasks"]  # data["tasks"] is een lijst van dictionaries
    df_Route1 = pd.json_normalize(tasks)  # json_normalize maakt geneste structuren plat
    
    with open(os.path.join(RoutePath,FRoute2), "r") as f:
        Route2 = json.load(f)

    display(df_Route1)
    
    tasks = Route2["tasks"]  # data["tasks"] is een lijst van dictionaries
    df_Route2 = pd.json_normalize(tasks)  # json_normalize maakt geneste structuren plat

    print(VerschilInSequentie(df_Route1,df_Route2))




if True:
    TestMain()