#functions created to automate some of the pandas tasks or apply more specifically.
import pandas as pd


def fill_na_with_zero(df, columns):
    """
      Returns a  pd.DataFrame. The modified DataFrame with NaN values are replaced by 0 in specified columns.
    Parameters:
        df (pd.DataFrame): The DataFrame to modify.
        columns (list): List of column names to fill NaN values in.

    """   
    # Fill NaN values with 0 in the specified columns
    df[columns] = df[columns].fillna(0)
    return df


def append_col_prefix(df, col_names:list, prefix):
    """ Renames columns in a pandas DataFrame to append a prefix to a column name, useful for when data is unstacked.
        Parameters:
    - df (DataFrame): input dataframe, can be geopandas or pandas.
    - col_names (list): List of columns to append.
    - prefix (str|int): Prefix to append to the column names.
    
    """
    rename_dict = {}
    
    for name in col_names:
        float_name = f'{float(name)}'
        #this handles if it's a float to convert nicely
        if float_name in df.columns:
            rename_dict[float_name] = f'{prefix}_{(name)}'
        # handles otherwise
        else:
            rename_dict[f'{name}'] = f'{prefix}_{(name)}'
      
    df.rename(columns=rename_dict, inplace=True)

    return df
  
  
def append_col_prefix(df, col_names:list, prefix):
    """ Renames columns in a pandas DataFrame to append a prefix to a column name, useful for when data is unstacked.
        Parameters:
    - df (DataFrame): input dataframe, can be geopandas or pandas.
    - col_names (list): List of columns to append.
    - prefix (str|int): Prefix to append to the column names.
    
    """
    rename_dict = {}
    
    for name in col_names:
        float_name = float(name)
        #this handles if it's a float to convert nicely
        if float_name in df.columns:
            rename_dict[float_name] = f'{prefix}_{name}'
        # handles otherwise
        elif name in df.columns:
            rename_dict[name] = f'{prefix}_{name}'
        else:
            #print failed column check and continues
            print(f'{name} not in dataframe')
            
            
    df.rename(columns=rename_dict, inplace=True)

    return df