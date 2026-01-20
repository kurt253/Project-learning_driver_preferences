from config import LOC_REQUESTS
from config import LOC_INTERMEDIATE
import pandas as pd
import re

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
    df_min_max_rest.to_csv(LOC_INTERMEDIATE/"depot-min-max-paths.csv",index=False)

if __name__ == "__main__" :
    print (f"testing as a standalone script")
    df = get_directories()
    get_min_max_directories(df)

