#functions created to automate some of the pandas tasks or apply more specifically.
import pandas as pd


def fill_na_with_zero(df, columns):
    """
      Replaces all NaN values with a 0 in specified columns in a pandas DataFrame.
      Returns a pd.DataFrame.
      
    Parameters:
    -----------
        df (pd.DataFrame): Pandas DataFrame with columns to modify.
        columns (list): List of column names to fill NaN values in.

    Example:
    --------
    >>> #Replace all NaN values in a dataframe with 0
    >>> pdaux.fill_na_with_zero(df, ['col_1','col_2','col_3'])

    """   
    # Fill NaN values with 0 in the specified columns
    df[columns] = df[columns].fillna(0)
    return df
  
def append_col_prefix(df, col_names:list, prefix):
    """ Renames columns in a pandas DataFrame to append a prefix to a column name, useful for when numerical data in a column is unstacked.
    Function handles float and integer numerical values.
    
    Parameters:
    -----------
    - df (DataFrame): input dataframe, can be geopandas or pandas.
    - col_names (list): List of columns to append.
    - prefix (str or int): Prefix to append to the column names.
    
    Example:
    --------
    >>> df.column # dataframe with numerical values
    >>> Index([1000.0, 2000.0, 3000.0], dtype='float64', name = 'distance')
    >>>
    >>> df_renamed = pdaux.append_col_prefix(df = df, col_names = [1000, 2000,3000], prefix = 'households')   
    >>>
    >>> # Print renamed columns.  
    >>> df_renamed.columns
    >>> Index([households_1000, households_2000, households_3000], dtype = 'object) 
    
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