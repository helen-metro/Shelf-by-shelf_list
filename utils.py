import os
import pandas as pd


# Create a saved folder for storage
def create_saved_folder(path, folder):
    """
    """
    try:
        os.mkdir(f'{path}/{folder}')
    except:
        print("Folder already exists!!")


# Load csv file
def load_csv_file(file):
    """
    """
    try: 
        return pd.read_csv(file)
    except:
        print(f"Cannot load {file}!!!")


def filter_items_by_branch(data:pd.DataFrame, branchnumber:int):
    """
    Filter item data by branchnumber
    """
    return data[data['BRANCHNUMBER'] == branchnumber].reset_index()