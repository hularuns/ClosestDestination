import pandas as pd

### Join census CSV data together, merging and dropping duplicate columns excluding the join_column

def join_census_csv(dict_of_df:dict, join_column:str, drop:bool, join_type='left'):
    """ Join census data by geographic code. Deletes duplicated. Ensure there are not any duplicate label names.
    geography_code or whaterver the join column is should be returned as dropped from the right dataframe.
    
    Parameters: 
    -----------
        dict_of_df (dict): dictionary of dataframes, a result of the mass_csv_read() function.
        join_column (str): column name to join by.
        drop (bool): Drop duplicate columns if true, else keep them.
        join_type (str): type of join - SQL-like, see pd.merge() docs. Recommended to use 'left' or 'inner' join where possible.

    Example:
    --------
    >>> joined_census_data = census_merge.join_census_csv(loaded_csv, 'geography code',  
                                                          drop=True,join_type='left')
"""
    joined_df = next(iter(dict_of_df.values()))
    columns_dropped = []
    for key, df in dict_of_df.items():
        
        if df is not joined_df: #ensure it doesn't join self
            #clean the data first. using .drop_duplicated() producted awkward column names. This way is cleaner.
            columns_to_drop = []
            for column in df.columns:
                if column in joined_df.columns and column != join_column:
                    columns_to_drop.append(column)
            #ensures data join happens regardless of if dropping columns happens or not
            df_to_join = df 
            if drop == True:
                df_to_join = df.drop(columns=columns_to_drop)
                
            columns_dropped.append(columns_to_drop)
            joined_df = pd.merge(joined_df, df_to_join, on=join_column, how=join_type)
    #without this the dataframe can be doubled in length dependiung on what's joined.           
    joined_df.drop_duplicates(subset=join_column, inplace=True)
    
    if drop:
        print(f'The following columns were duplicates from the right join and were dropped: {columns_dropped}')
    else:
        print('No columns were dropped, all duplicate columns retained.')
    return joined_df

## Remove duplicates if they are the right suffix. Retains the Left suffix variant and cleans the names
def drop_dupe_cols(df:pd.DataFrame, suffixes:tuple):
    """ Drops the suffixes from the merged pandas dataframe and removing duplicate columns from the right table if they are prsent in the left table.
    Parameters:
        - df (DataFrame): Pandas DataFrame which has duplicate columns appended due to a merge or join operation, such as ‘name_left’ and ‘name_right’.
        - suffixes (tuple): Tuples (left_suffix, right_suffix) which were used to retain duplicate columns, e.g. ‘name_left’ and ‘name_right’.

        """
    left_suffix, right_suffix = suffixes
    columns_to_drop = []
    
    for column in df.columns:
        
        if column.endswith(right_suffix):
            columns_to_drop.append(column)
            
        elif column.endswith(left_suffix):
            new_name = column[:-len(left_suffix)]  # Slice off the suffix
            df.rename(columns={column: new_name}, inplace=True)
    
    # drops the right suffix columns
    df.drop(columns=columns_to_drop, inplace=True)