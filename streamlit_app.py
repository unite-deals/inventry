# importing libraries
import pandas as pd
import streamlit as st

# use whole page width
st.set_page_config(page_title="My Streamlit App", layout="wide")

# read csv file
df = pd.read_csv("inventory.csv")

# preparing check boxes for the dataframe
df["selected"] = [False for i in range(df.shape[0])]

list_sub_category = df["sub-category"].sort_values().unique().tolist()

# le title
st.header("Inventory Manager")
st.divider()

# defining dataframe we want to dynamically interact with and make changes to within streamlit session. 
# declared once at the beginning, like this:
if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame(columns = df.columns)
if 'full' not in st.session_state:
        st.session_state.full = df.copy()
# create page columns
a1,a2,a3 = st.columns([.75,.25,2])

# first column's content
with a1:
    st.subheader("Add item to inventory")

    # selecting sub-category before scrolling through product names
    sub_category = st.selectbox("Select product category:", list_sub_category)
    # retrieving list of recorded items in inventory
    list_item = df["product_name"][df["sub-category"] == sub_category].sort_values().unique().tolist()

    # to give an option to search items within all category names:
    if st.toggle("Search in all category"):
        list_item = df["product_name"].sort_values().unique().tolist()
    
    st.write("Num. of products in this category:",len(list_item))
    st.write(" ")
    st.write(" ")
    # setting up a variable to save a product name that will be chosen by user during the interaction
    name = ""
    name = st.selectbox("Product Name:", list_item)
    
    # option to put a new item in the list if the product is not yet recorded in inventory list
    not_in_list = st.checkbox("Item not in the list.")
    if not_in_list:
        name = st.text_input("Product Name:")
        name = name.title()
        product_id = st.text_input("Product ID:")
        category = st.text_input("Category:")
        sub_category = st.text_input("Sub-Category:")
    
    # setting up variables to fill in other columns for each entry (row)
    sel = False
    if not_in_list == False:
        product_id = df["product_id"][df["product_name"] == name].values[0]
        category = df["category"][df["product_name"] == name].values[0]
        sub_category = df["sub-category"][df["product_name"] == name].values[0]
    quantity = st.text_input("Quantity:")

    # check if the quantity is a number
    q_isnumber = False
    if quantity != "":
        try:
            quantity = float(quantity)
            q_isnumber = True
        except:
            st.error("Quantity must be a number.")

    # preparing a button that records/appends the user input to the list/dataframe
    if st.button("Add to cart") and q_isnumber == True:
        st.session_state.df = st.session_state.df.append({
        "selected":sel, 
        "product_id":product_id,
        "category":category,
        "sub-category":sub_category,
        "product_name":name, 
        "quantity":quantity
        }, ignore_index = True)
        # pops a small notification on below-right
        st.toast("Added to list.")

with a3:
    st.subheader("Items to be added")
    # not sure why session state is declared again here lol
    if 'df' not in st.session_state:
        st.session_state.df = df.copy()
    
    # toggle button
    if st.toggle("Show data"):
        # to display the number of item in the list
        st.write("Num. of entry:", st.session_state.df.shape[0])
        st.session_state.df = st.data_editor(st.session_state.df.groupby(["selected","product_name","category","sub-category","product_id"]).agg({"quantity":"sum"}).reset_index(), 
        column_config = {
        "selected": st.column_config.CheckboxColumn("selected", default = False)
        }, hide_index = True, use_container_width=True)
        b1,b2,b3 = st.columns([1,1.5,1.5])
        with b1:
            if st.button("Delete selected"):
                st.session_state.df = st.session_state.df[st.session_state.df["selected"] == False]
                st.success("Data deleted.")
        with b2:
            if st.button("Delete all"):
                cols = st.session_state.df.columns
                st.session_state.df = pd.DataFrame(columns = cols)
                st.success("Data deleted.")
        with b3:
            if st.button("Save changes to inventory data"):
                for i,j in list(zip(st.session_state.df["product_name"],st.session_state.df["quantity"])):
                    st.session_state.full["quantity"][st.session_state.full["product_name"] == i] += j
                cols = st.session_state.df.columns
                st.session_state.df = pd.DataFrame(columns = cols)
                st.success("Inventory updated. Scroll down to see your inventory data.")

st.divider()
b1,b2,b3 = st.columns([1,3,1])
with b2:
    search_sub_category = st.selectbox("Select category to display:", list_sub_category)
    if st.toggle("Display data of selected category"):
        st.dataframe(st.session_state.full[st.session_state.full["sub-category"] == search_sub_category])
