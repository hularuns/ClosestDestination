import os
import pandas as pd


def batch_csv_read(file_paths:list):
    """ Function to read all CSVs and place into a dictionary of dataframes for subsequent analysis and joining.
    File paths should be from the parent folder onwards. Do not include C:/User etc.
    
    Parameters:
    -----------
        file_paths (list): A list of file paths, each string should look like '/data/stored/here/mydata.csv'.
        
    Example:
    --------
    >>> # Define file paths – relative path for each csv
    >>> file_paths = [
    >>> '/testEnvironment/Data/census_data/ni-2021-usual-residents.csv',
    >>> '/testEnvironment/Data/census_data/ni-2021-households.csv',
    >>> '/testEnvironment/Data/census_data/ni-2021-employment-deprivation.csv'
    >>> ]
    >>> load all defined csvs
    >>> loaded_csv = batch_csv.batch_csv_read(file_paths)
    
    """
    base_dir = os.getcwd()
    csv_loaded = {}
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        key = os.path.splitext(filename)[0]
        csv_loaded[key] = pd.read_csv(base_dir+file_path)

    return csv_loaded