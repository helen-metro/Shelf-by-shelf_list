import os
import glob
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime 
import zipfile

import utils 
import add_page_break
from category import Categories, Exceptional_categories 
from config import Path, Save_data_folder, Data_folder



def preprocessing_stage(path, 
                        input_data_folder, 
                        saved_folder, 
                        date_folder):
    """
    Preprocessing data by loading data, format data based on format type,
    column name
    """
    # Create saved folder
    utils.create_saved_folder(path, f'{saved_folder}/{date_folder}')

    # Load data for items
    print("Starting to load data folders ...")
    items = utils.load_csv_file(f'{path}/{input_data_folder}/Items_{date_folder}.csv')
    branch = utils.load_csv_file(f'{path}/{input_data_folder}/Branch_{date_folder}.csv')
    media = utils.load_csv_file(f'{path}/{input_data_folder}/Media_{date_folder}.csv')
    location = utils.load_csv_file(f'{path}/{input_data_folder}/Location_{date_folder}.csv')
    bbibmap = utils.load_csv_file(f'{path}/{input_data_folder}/BBIMAP_{date_folder}.csv')
    print("Finished loading data!")


    # Rename data columns
    items.rename(columns={'OWNINGBRANCH': 'BRANCHNUMBER'}, 
                 inplace=True)
    media.rename(columns={'MEDNUMBER': 'MEDIA'}, inplace=True)
    location.rename(columns={'LOCNUMBER': 'LOCATION'}, inplace=True)

    # Merge all tables respectively
    print("Starting to merge item info ...")
    items_by_branch = pd.merge(items, branch, on='BRANCHNUMBER', how='left')
    items_by_branch = pd.merge(items_by_branch, media, on='MEDIA', how='left')
    items_by_branch = pd.merge(items_by_branch, location, on='LOCATION', how='left')
    items_by_branch = pd.merge(items_by_branch, bbibmap, on='BID', how='left')
    print("All item info have been merged!")

    return items_by_branch



def categorize_items_by_categories(data: pd.DataFrame, 
                                   categories: dict,
                                   exceptional_categories: list):
    """
    """
    # Create a column for `Category` and assign NAN at first 
    data['Category'] = pd.NA 

    # Extract only selected columns
    df = data[['CN', 'ITEM', 'LOCNAME', 'MEDNAME', 
               'Category', 'AUTHOR', 'LOCCODE']]

    df.rename(columns={'LOCNAME': 'LOCATION', 
                       'MEDNAME': 'MEDIA'}, inplace=True)

    print("-- Start categorizing: ")

    for key in categories.keys():
        value = list(categories[key].keys())
        print(f"{key}: {value}")
        if len(value) == 1: 
            df.loc[(df[value[0]].isin(categories[key][value[0]])) & 
                    (df['Category'].isna()), 'Category'] = key
        elif len(value) == 2:
            df.loc[(df[value[0]].isin(categories[key][value[0]])) & 
                    (df[value[1]].isin(categories[key][value[1]])) & 
                    (df['Category'].isna()), 'Category'] = key
    
        # print("--- Start categorizing 2nd stage: ")

        for val in exceptional_categories:
           for cat in categories.keys():
                if val in categories[cat]['LOCATION']:
                    print(val)
                    if len(categories[cat].keys()) == 1:
                        df.loc[(df['LOCATION'].str.contains(val)) & 
                               (df['Category'].isna()), 'Category'] = cat
                    elif len(categories[cat].keys()) == 2:
                        df.loc[(df['LOCATION'].str.contains(val)) & 
                               (df['MEDIA'].isin(categories[cat]['MEDIA'])) & 
                               (df['Category'].isna()), 'Category'] = cat

    print("---- Finished categorizing items!")

    return df



def split_items_to_shelf(df:pd.DataFrame, 
                         shelf_category:pd.DataFrame,
                         saved_folder:str):
    """
    """
    # Copy a new df
    df_copy = df.copy()

    print("Starting splitting stage ...")

    for category, total_shelf in zip(shelf_category['Category'], shelf_category['Total']):
        print(category, total_shelf)

        # Skip category that do NOT have assigned shelf
        if total_shelf == 0:
            continue

        # Extract only items in the current category
        split_items = df_copy[df_copy['Category'] == category]

        # Skip category if there is NO items in the current category 
        if split_items.shape[0] < 1:
            continue

        # Drop all extracted items in the current category in the main df 
        df_copy.drop(split_items.index, inplace=True)

        if category == 'Audio':
            # Add `Order` for preferred Order
            # Sort "ADULT NON-FICTION" items 
            split_items['Order'] = pd.Categorical(
                split_items['LOCCODE'], 
                categories=["ANF"], 
                ordered=True)
            
            # Sort items by `Author` and `CN`
            split_items = split_items.sort_values(by=['Order', 'CN', 'AUTHOR'],
                                                  ascending=[False, True, True],
                                                  na_position='first')

        elif category in ['JFiction', 'YA', 'YGN', 'SEQ (High/Middle)']:
            # Sort items by `Author`
            split_items = split_items.sort_values(by=['AUTHOR', 'CN'])

        elif category in ['Children Audio', 'AEB']:
            # Sort items in the order [Easy, Reader, Early Chapter, 
            # Early Graphic, Juvenile Fiction, Juvenile Graphic, 
            # Early Nonfiction, Juvenile Nonfiction] 
            split_items['Order'] = pd.Categorical(
                split_items['LOCATION'], 
                categories=["E", "R", "EC", "EGN",
                            "JF", "JGN", "ENF", "JNF"],
                ordered=True)
    
            # Sort items by prefered `Order`
            split_items = split_items.sort_values(by=['Order', 'LOCATION', 'CN'])
        
        elif category in ['Children DVD']:
            # Add `Order` for preferred Order
            # Sort by order "Easy", "Juvenile FF/TVShow", "Nonfiction"
            split_items['Order'] = pd.Categorical(
                split_items['LOCATION'], 
                categories=["E", "JFF", "JNF"],
                ordered=True)
            # Sort items by `Location` and `CN`
            split_items = split_items.sort_values(by=['Order', 'LOCATION', 'CN'])

        else:
            # Sort all other categories by `Category` and `CN`  
            split_items = split_items.sort_values(by=['Category', 'CN'])


        # Remove the columns `LOCCODE` and `Order`
        if 'LOCCODE' in split_items.columns:
            split_items.drop(['LOCCODE'], axis=1, inplace=True)
        if 'Order' in split_items.columns:
            split_items.drop(['Order'], axis=1, inplace=True)


        # Calculate the chunk size by shelf number
        try:
            chunk_size = math.ceil(split_items.shape[0] / total_shelf)
            print(split_items.shape, chunk_size)
        except:
            chunk_size = 50

        # Split items by chunks
        split_dfs = add_page_break.split_items_by_chunks(split_items, 
                                                         chunk_size, 
                                                         'Category')

        if category == 'SEQ (High/Middle)':
            category = 'SEQ_Children'

        # Add Page Break and save file
        file_path = f'{saved_folder}/Sorted_items_with_break_{category}.xlsx'
        add_page_break.add_page_break(split_dfs, category, file_path)

        """
        add_page_break_openpyxl(split_dfs, category,
                                f'save_data/{date_folder}/Sorted_items_with_break_{date_folder}.xlsx')
        """

    if df_copy.shape[0] > 0:
        chunk_size = 50
        category = "Other"

        # Assign "Other" to NAN values in the `Category`
        df_copy['Category'] = df_copy['Category'].fillna("Other")
        
        # Split items by chunks
        split_dfs = add_page_break.split_items_by_chunks(df_copy, 
                                                         chunk_size, 
                                                         'Category')
        
        # Add Page Break and save file
        file_path = f'{saved_folder}/Sorted_items_with_break_{category}.xlsx'
        add_page_break.add_page_break(split_dfs, category, file_path)

    print("Completed splitting stage!")



def run_splitting_process(branchnumber:int, date_folder:str):
    """
    """
    path = Path
    data = Data_folder
    save_data = Save_data_folder
    input_data_folder = f"{data}/{date_folder}"

    items = preprocessing_stage(path, input_data_folder,
                                save_data, 
                                date_folder)

    items = utils.filter_items_by_branch(items, branchnumber)

    # Categorize items
    items_with_category = categorize_items_by_categories(items, 
                                                         Categories,
                                                         Exceptional_categories)

    try: 
        shelf_category = pd.read_excel(f'{path}/{input_data_folder}/Shelf_by_Category.xlsx')
    except: 
        shelf_category = pd.read_csv(f'{path}/{input_data_folder}/Shelf_by_Category.csv')
    
    split_items_to_shelf(items_with_category, 
                         shelf_category, 
                         f'{path}/{save_data}/{date_folder}')



