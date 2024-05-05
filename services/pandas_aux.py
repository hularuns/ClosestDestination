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
