"""
Pack Calculator processing functions
Used by Streamlit to group items and calculate pack quantities
"""

import pandas as pd

def format_packs(value):
    """Removes decimal if value is whole number."""
    if pd.isna(value):
        return value
    if value == int(value):
        return int(value)
    return value


def calculate_packs(df):
    """Group by Customer + Item, sum quantities, and calculate packs needed."""
    
    # Standardize expected column names
    rename_map = {
        "Item_Number": "Item",
        "Pack_Quantity": "Pack Quantity",
        "Item_Description": "Item Description",
    }
    df = df.rename(columns=rename_map)

    required_cols = ["Customer", "Item", "Quantity", "Pack Quantity"]
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        raise KeyError(f"Missing required columns: {missing}")

    agg_dict = {"Quantity": "sum", "Pack Quantity": "first"}
    if "Item Description" in df.columns:
        agg_dict["Item Description"] = "first"

    result = df.groupby(["Customer", "Item"], as_index=False).agg(agg_dict)
    result["Packs Needed"] = result["Quantity"] / result["Pack Quantity"]
    result["Packs Needed"] = result["Packs Needed"].apply(format_packs)

    return result
