import os
import re 
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


def extract_or_keep_value(value):
    """
    Extract the string is the string starts with
    a character 
    """
    str_value = str(value)

    if re.match(r"^[A-Za-z]", str_value):
        match = re.match(r"^[A-Za-z]+", str_value)
        return match.group(0) if match else str_value
    return str_value


def extract_if_found_keyword(value, keyword):
    """
    Extract the string with excluding the keyword
    and getting only the part after keyword
    """
    str_value = str(value)
    if re.match(keyword, str_value):
        return str_value.split(" ", 1)
        match = re.match(keyword, str_value)
        _, _, res = str_value.partition(match.group(0))
        return res 
    return str_value


def extract_the_rest_string(value):
    """
    Extract the string excluding the first part of the string name
    """
    str_value = str(value)
    if re.match(r"^[A-Za-z]", str_value):
        match = re.match(r"^[A-Za-z]+", str_value)
        # return match.group(0) if match else str_val
        _, _, res = str_value.partition(match.group(0))
        return res
    return str_value.split(" ", 1)[1]


def extract_the_rest(value):
    """
    """
    str_val = str(value)
    
    if re.match("JTV/SHOW", str_val):
        match = re.match("JTV/SHOW", str_val)
        _, _, res = str_val.partition(match.group(0))
        return res 
    elif re.match("TV/SHOW", str_val):
        match = re.match("TV/SHOW", str_val)
        _, _, res = str_val.partition(match.group(0))
        return res 
    elif re.match(r"^[A-Za-z]", str_val):
        match = re.match(r"^[A-Za-z]+", str_val)
        # return match.group(0) if match else str_val
        _, _, res = str_val.partition(match.group(0))
        return res
    return str_val # str_val.split(" ", 1)[1]


def split_volumne_value(values):
    """
    """
    # val = str(values)
    return [int(val) if val.isdigit() else val for val in re.split(r"(\d+)", values)]
