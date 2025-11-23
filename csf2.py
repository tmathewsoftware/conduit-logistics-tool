"""
Customer Store Filter functions
Used by Streamlit app to filter data based on delivery day.
"""

import pandas as pd
from sds import delivery_schedule

def extract_store_code(customer_string):
    """Extract store code from Customer field values."""
    if pd.isna(customer_string):
        return None
    parts = str(customer_string).split(" - ")
    return parts[0].strip() if parts else None


def get_all_codes_for_day(day):
    """Return all store codes allowed for the selected day, including SA/TAS/MISC."""
    valid_codes = set()

    if day in delivery_schedule:
        for store in delivery_schedule[day]:
            valid_codes.add(store["code"])

    for region in ["SA", "TAS", "MISC"]:
        if region in delivery_schedule:
            for store in delivery_schedule[region]:
                valid_codes.add(store["code"])

    return valid_codes


def filter_orders_by_day(df, day):
    """Apply filtering logic directly to dataframe."""
    df["Store_Code"] = df["Customer"].apply(extract_store_code)
    valid_codes = get_all_codes_for_day(day)
    filtered_df = df[df["Store_Code"].isin(valid_codes)].copy()
    filtered_df.drop(columns=["Store_Code"], inplace=True)
    return filtered_df
