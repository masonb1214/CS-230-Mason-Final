#Name: Mason Behl
#CS230: Section 1
#DATA: Top 2000 Global Companies
#URL: https://cs-230-final-qv4g3hv6ivuasg43rtjnnu.streamlit.app/
#Description: This program analyzes the information regarding the top 2000 global companies. It groups them into
#countries, provides information about profitability, and even allows potential investors to find hidden gems. The data
#is visualized through maps, line charts, and bar charts.


import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk
import seaborn as sns

#python -m streamlit run "C:\Users\mason\OneDrive - Bentley University\CS 230\Final_Project.py"

while True:
    #[PY3] Error checking with try/except
    try:
        df_companies = pd.read_csv("Final Data.csv", index_col="Global Rank")
        break
    except:
        print("Error loading file, will try again")


#[DA1] Clean the data
df_companies = df_companies.drop_duplicates()
df_companies = df_companies.dropna()
df_companies = df_companies[df_companies["Sales ($billion)"] > 0]
df_companies = df_companies[df_companies["Assets ($billion)"] > 0]
df_companies["Profit Margin"] = df_companies["Profits ($billion)"]/df_companies["Sales ($billion)"]
df_companies["Unit (Sales, Profits, Assets)"] = "Billions of Dollars"

df_companies = df_companies.rename(columns={"Market Value ($billion)": "Market_Value"}) #AI Code 1: Code for renaming columns based on CHATGPT


#[PY5] A dictionary where you write code to access its keys values, or items
country_sales_dict = {}

#[DA8] Iterate through rows of Dataframe with iterrows()
for index, row in df_companies.iterrows():  #AI code 2: Code for iterating through rows based on CHATGPT
    country = row["Country"]
    sales = row["Sales ($billion)"]

    if country in country_sales_dict:
       country_sales_dict[country] += sales
    else:
        country_sales_dict[country] = sales

sales_series = pd.Series(country_sales_dict) #AI Code 3: Code for creating a series with pandas based on CHATGPT
sales_series = sales_series.nlargest(20)


def company_filter_by_profits(df, sort_if_profitable, min_revenue):
    data = df[(df["Sales ($billion)"] > min_revenue)]
    if sort_if_profitable == True:
        data = data[data["Profits ($billion)"]>0]

    # [DA2] - Sort data in ascending or descending order
    data = data.sort_values("Profits ($billion)", ascending=False)
    return data

#[PY2] A function that returns more than one value
def revenue_summary(df, Country=None):
    if Country is not None:
        # [DA4] Filter data by one condition
        df = df[df["Country"] == Country]
        country_name = Country
    else:
        country_name = "All Countries"

    summary_data = {
    "Country": country_name,
    # [DA3] Find top Largest or smallest values of a column
    "Max Sales ($B)": df["Sales ($billion)"].max(),
    "Min Sales ($B)": df["Sales ($billion)"].min(),
    "Average Sales ($B)": df["Sales ($billion)"].mean()
    }
    return summary_data

def profitability(df):
    #[PY4] A list comprehension
    good_margins = [company for company in df[df["Profit Margin"] > .15 ]["Company"]]
    return good_margins

#[PY1] A function with two or more parameters, one which has a default value
def best_picks(df, profit_margin_min = .20, max_valuation = 30):
    # [DA5] Filter Data by two or more conditions with AND or OR
    compare_df = df[(df["Profit Margin"]> profit_margin_min) & (df["Market_Value"]<max_valuation)]
    return compare_df

#[ST4] - Radio
page = st.sidebar.radio("Navigate", ["Home", "Country Insights", "Company Profitability Rankings", "Hidden Gems"]) #AI CODE 4: Code for creating sidebar was based on CHATGPT
if page == "Home":
    st.title("Stock Performance of Top 2000 Global Companies")
    st.text("By: Mason Behl")
    st.markdown("---") #AI CODE 5: Code for creating horizontal line was based on CHATGPT
    st.subheader("Map of Countries Analyzed and Corresponding Market Value")

    #[MAP] #AI CODE 6: Code for creating a map was based on CHATGPT
    column_layer=pdk.Layer(
        type ="ColumnLayer",
        data=df_companies,
        get_position='[Longitude_final, Latitude_final]',
        get_elevation="Market_Value",
        elevation_scale=10000,
        radius=40000,
        get_fill_color='[65, 105, 225]',
        pickable=True
    )

    view = pdk.ViewState(
        longitude= -98,
        latitude=39,
        zoom=1,
        pitch=30
    )

    tooltip = {
        "html": "<b>{Company}</b>",
        "style": {"backgroundColor": "black", "color": "white"}
    }

    map_style = "mapbox://styles/mapbox/light-v9"

    r = pdk.Deck(
        layers=column_layer,
        initial_view_state=view,
        map_style = map_style,
        tooltip=tooltip
    )
    st.pydeck_chart(r)

elif page == "Country Insights":
    st.subheader("Revenue of Leading Countries")
    # [ST4] - Columns
    col1, col2 = st.columns([2,1]) #AI CODE 7: Code for creating columns was based on CHATGPT
    with col1:
        #[CHART1]
        sales_series.plot(kind="bar", color="grey")
        plt.ylabel("Sales ($billions)")
        plt.title("Total Company Sales by Country (Top 20 Countries)")
        st.pyplot(plt)
    with col2:
        country_selection = st.selectbox("Select Nation:", (sales_series.nlargest(20).index)) #AI CODE 8: Code for  creating selectbox and metric output was based on CHATGPT
        st.metric(f"{country_selection}'s Total Sales (B)", f"${round(country_sales_dict[country_selection],2)}")


    st.subheader("Revenue Summary for Companies of Selected Nations")
    # [ST1] Selectbox
    selected_country = st.selectbox("Option 1: Select a country out of global leaders", ("All Countries","USA", "Japan", "China", "UK", "France", "Germany", "South Korea"))
    manual_country = st.text_input("Option 2: Or type a country name manually (optional)")

    if manual_country:
        country_using = manual_country.strip()
    else:
        country_using = selected_country

    if country_using == "All Countries":
        summary = revenue_summary(df_companies)
    else:
        summary = revenue_summary(df_companies, country_using)

    col3, col4, col5 = st.columns([1,1,1])
    with col3:
        st.metric("Max Sales ($B)", f"{summary['Max Sales ($B)']:.2f}")
    with col4:
        st.metric("Min Sales ($B)", f"{summary['Min Sales ($B)']:.2f}")
    with col5:
        st.metric("Average Sales ($B)", f"{summary['Average Sales ($B)']:.2f}")

    st.subheader(f"Distribution of Company Sales in {country_using}")

        # Filter the DataFrame for the selected country
    country_df = df_companies[df_companies["Country"] == country_using]

    #[SEA1]
    if not country_df.empty: #AI CODE 9: Code for  this visual was based on CHATGPT
        country_df = country_df.sort_values("Sales ($billion)", ascending=False).head(20)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=country_df, x="Company", y="Sales ($billion)", color="lightgrey", ax=ax)
        ax.set_title(f"Top 20 Companies by Sales in {country_using}")
        ax.set_ylabel("Sales ($B)")
        ax.set_xlabel("")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.warning(f"No data available for {country_using}.") #AI Code 10: Code for the warning was based on CHATGPT

elif page == "Company Profitability Rankings":
    st.subheader("Sort Companies on Revenue")

    col6, col7, col8 = st.columns([1, 1, 1])
    with col6:
        slide= st.slider("Option 1: Select a minimum revenue (Billions)", 0, (int(df_companies["Sales ($billion)"].max())))

    with col7:
        Yes_OR_NO =st.selectbox("Option 2: Would you like to only analyze profitable countries?", ("YES","NO"))
    if Yes_OR_NO == "YES":
        profitable = True
    else:
        profitable = False

    with col8:
        list_of_countries = company_filter_by_profits(df_companies, profitable, slide)
        filter_by_margin = st.checkbox("Option 3: Only show companies with Great Profit Margin (15%)")


    if filter_by_margin:
        high_margin_companies = profitability(df_companies)
        list_of_countries = list_of_countries[list_of_countries["Company"].isin(high_margin_companies)]
    st.markdown("---")
    st.subheader("Ranked Companies")
    st.dataframe(list_of_countries[["Company", "Country", "Sales ($billion)", "Profits ($billion)"]]) #AI Code 11: Code for creating dataframe is based on CHATGPT

elif page == "Hidden Gems":
    st.subheader("Hidden Gems")
    st.markdown(
        "*Note: Hidden Gems are companies with high profit margins and low market value unless otherwise specified.*") #AI Code 12: Code for italicizing is based on CHATGPT
    st.markdown("---")

    col10, col11 = st.columns([1,1])
    with col10:
        # [ST2] - Radio
        use_custom = st.radio("Would you like to set custom thresholds?", ["No", "Yes"])

        if use_custom == "Yes":
            min_margin = st.slider("Minimum Profit Margin (percent)", 0, 500, 0)
            min_margin = min_margin/100
            # [ST3] - Slider
            max_value = st.slider("Maximum Market Value ($B)", 0, 300, 0)
            custom_results = best_picks(df_companies, profit_margin_min=min_margin, max_valuation=max_value)
            results_to_show = custom_results
        else:
            results_to_show = best_picks(df_companies)

    if results_to_show.empty:
            st.warning("No companies match the criteria. Try adjusting your thresholds.")
    else:
        st.subheader(f"Hidden Gems Found")
        st.dataframe(
            results_to_show[["Company", "Country", "Profit Margin", "Market_Value"]]
            .sort_values("Profit Margin", ascending=False)
            .round(2)
            .rename(columns={"Market_Value": "Market Value"}) #AI Code 13: Code for refining the dataframe based on CHATGPT
        )

        with col11:
            #[CHART2]
            st.subheader("Profit Margin vs. Market Value")
            sorted_results = results_to_show.sort_values("Market_Value")
            plt.figure(figsize=(10, 5))
            plt.plot(sorted_results["Market_Value"],sorted_results["Profit Margin"], marker='o', linestyle='-') #AI CODE 14: Code for refining visual based on CHATGPT
            plt.xlabel("Market Value ($B)")
            plt.ylabel("Profit Margin")
            plt.title("Profit Margin Trends vs. Market Value")
            plt.grid(True)
            st.pyplot(plt)


