import os
import math 
import numpy as np 
import pandas as pd
import openpyxl 
from openpyxl.worksheet.pagebreak import Break




def add_page_break(split_dfs: pd.DataFrame, category: str, file_path: str):
  """
  """
  with pd.ExcelWriter(file_path,
                      engine="xlsxwriter",
                      # engine="openpyxl", mode="a", if_sheet_exists="replace"
                      ) as writer:
    sheet_name = category
    current_row = 0
    page_breaks = []

    for df in split_dfs:
        # Write DataFrame to the sheet, tracking the current row
        df = pd.DataFrame(df)
        df.to_excel(writer, sheet_name=sheet_name,
                    startrow=current_row, index=False)

        # page_break = openpyxl.worksheet.pagebreak.Break(id=row_idx)
        # ws.row_breaks.append(page_break)

        # Calculate next starting row (+1 for header, + length of df)
        current_row += len(df) + 1

        # Add the row number where the page break should trigger (right after the table)
        # Note: XlsxWriter uses 0-indexed rows for page breaks
        page_breaks.append(current_row)

        # Add a couple of blank aesthetic rows between tables if desired
        current_row += 0

    # 3. Access the underlying XlsxWriter workbook and worksheet objects
    worksheet = writer.sheets[sheet_name]

    # Remove the very last extra page break appended after the final dataframe
    page_breaks.pop()

    # Apply actual manual horizontal page breaks

    if page_breaks:
        worksheet.set_h_pagebreaks(page_breaks)



def add_page_break_openpyxl(split_dfs, category, file_path):
  """
  """
  with pd.ExcelWriter(file_path, engine="openpyxl",
                      mode="a", if_sheet_exists="replace") as writer:
    sheet_name = category
    current_row = 0
    page_breaks = []

    for df in split_dfs:
        # Write DataFrame to the sheet, tracking the current row
        df = pd.DataFrame(df)
        df.to_excel(writer, sheet_name=sheet_name,
                    startrow=current_row, index=False)

        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        current_row += len(df) + 1

        # Add the row number where the page break should trigger (right after the table)
        # Note: XlsxWriter uses 0-indexed rows for page breaks
        # page_breaks.append(current_row)

        worksheet.row_breaks.append(Break(id=current_row))

        # page_break = openpyxl.worksheet.pagebreak.Break(id=current_row)
        # writer.row_breaks.append(page_break)

        current_row += 1



def split_items_by_chunks(df, chunk_size, column):
    # Create the df
    split_dfs = []

    for name, group in df.groupby([column]):
        for i in range(0, len(group), chunk_size):
           chunk = group.iloc[i : i + chunk_size]
           split_dfs.append(chunk)
           
           # Add an empty row
           empty_row = pd.DataFrame([[np.nan] * len(df.columns)],
                                      columns=df.columns)
           
           # split_dfs.append(empty_row)

    return split_dfs



def split_items_by_category(df:pd.DataFrame, 
                            shelf_category:pd.DataFrame, 
                            date_folder:str):
    """
    """
    # Copy a new df
    df_copy = df.copy()

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

        # Sort items by `Order`, `Author` and `CN`
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
            split_items['LOCCODE'],
            categories=["E", "R", "EC", "EGN",
                        "JF", "JGN", "ENF", "JNF"],
            ordered=True)

        # Sort items by prefered `Order`, `Location` and `CN` 
        split_items = split_items.sort_values(by=['Order', 'LOCATION', 'CN'])
    
       elif category in ['Children DVD']:
        # Add `Order` for preferred Order
        # Sort by order "Easy", "Juvenile FF/TVShow", "Nonfiction"
        split_items['Order'] = pd.Categorical(
            split_items['LOCCODE'], 
            categories=["E", "JFF", "JNF"],
            ordered=True)
        # Sort items by `Order`, `Location` and `CN`
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
       split_dfs = split_items_by_chunks(split_items, chunk_size, 'Category')

       if category == 'SEQ (High/Middle)':
        category = 'SEQ_Children'

       # Add Page Break and save file
       file_path = f'save_data/{date_folder}/Sorted_items_with_break_{category}.xlsx'
       add_page_break(split_dfs, category, file_path)

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
      split_dfs = split_items_by_chunks(df_copy, chunk_size, 'Category')

      # Add Page Break and save file
      file_path = f'save_data/{date_folder}/Sorted_items_with_break_{category}.xlsx'
      add_page_break(split_dfs, category, file_path)

      # df_copy.to_csv(f'save_data/{date_folder}/Sorted_EE_items_Others.csv', index=False)