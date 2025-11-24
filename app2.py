import streamlit as st
import pandas as pd



from io import StringIO
from sds import delivery_schedule, get_stores_for_day
from csf2 import extract_store_code, get_all_codes_for_day
from clc3 import format_packs

st.set_page_config(page_title="Conduit Tool", layout="wide")

# ---- HEADER ----
st.title("Conduit Logistics Delivery Tool")
st.write("Paste Excel data, filter by delivery day, and calculate packs automatically.")

# Create Streamlit Tabs
tab1, tab2, tab3 = st.tabs(["📦 Filter Orders", "📊 Pack Calculator", "🔍 Schedule Lookup"])

# ============= TAB 1 - Filter Orders =============
with tab1:
    st.header("📦 Filter Orders by Delivery Day")

    # Day selection
    day = st.selectbox("Select delivery day:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])

    # Paste area
    raw_data = st.text_area("📋 Paste orders from Excel here (include headers):", height=220)

    if st.button("Filter Orders"):
        if raw_data.strip() == "":
            st.error("⚠ Please paste data first.")
        else:
            try:
                df = pd.read_csv(StringIO(raw_data), sep="\t")
                df.columns = df.columns.str.strip()

                valid_codes = get_all_codes_for_day(day)
                df["Store_Code"] = df["Customer"].apply(extract_store_code)

                filtered_df = df[df["Store_Code"].isin(valid_codes)].copy()
                filtered_df.drop(columns=["Store_Code"], inplace=True)

                st.success("✅ Orders filtered successfully!")
                st.dataframe(filtered_df)

                st.download_button(
                label="📥 Download Filtered Orders",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="filtered_orders.csv",
                mime="text/csv"
)



            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============= TAB 2 - Pack Calculator =============
with tab2:
    st.header("📊 Pack Calculator")

    raw_pack_data = st.text_area("📋 Paste table for pack calculation:", height=220)

    if st.button("Calculate Packs Needed"):
        try:
            pack_df = pd.read_csv(StringIO(raw_pack_data), sep="\t")
            pack_df.columns = pack_df.columns.str.strip()

            required = ["Customer", "Item", "Quantity", "Pack Quantity"]
            if not all(col in pack_df.columns for col in required):
                st.error("⚠ Missing required columns. Need: Customer, Item, Quantity, Pack Quantity")
            else:
                agg_dict = {"Quantity": "sum", "Pack Quantity": "first",
                            "Item Description": "first" if "Item Description" in pack_df.columns else "first"}

                result = pack_df.groupby(["Customer", "Item"], as_index=False).agg(agg_dict)
                result["Packs Needed"] = result["Quantity"] / result["Pack Quantity"]
                result["Packs Needed"] = result["Packs Needed"].apply(format_packs)

                st.success("📦 Pack calculation complete!")
                st.dataframe(result)

                st.download_button(
                label="📥 Download Pack Results",
                data=result.to_csv(index=False).encode("utf-8"),
                file_name="pack_calculation.csv",
                mime="text/csv")



        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============= TAB 3 - Store Lookup =============
with tab3:
    st.header("🔍 Search Store Schedule")

    search = st.text_input("Search by store code or name:")

    if st.button("Search"):
        results = []
        search_lower = search.lower()

        for day, stores in delivery_schedule.items():
            for store in stores:
                if search_lower in store["code"] or search_lower in store["name"].lower():
                    results.append({"Day": day, "Code": store["code"],
                                    "Store": store["name"], "Weekly": store["weekly_required"]})

        if results:
            st.table(pd.DataFrame(results))
        else:
            st.warning("No matching stores found.")
