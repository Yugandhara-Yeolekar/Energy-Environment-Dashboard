import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Apply Streamlit Theme
st.set_page_config(layout="wide")
theme = st.config.get_option("theme.base")
# Set plotly template based on theme
plot_template = "plotly_dark" if theme == "dark" else "simple_white"

def create_animated_line_chart(df, group_by_col, y_col, y_label, y_suffix, hover_template, title):
    years = sorted(df["Year"].unique())
    fig = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Scatter(
                    x=group_data[group_data['Year'] <= year]['Year'],
                    y=group_data[group_data['Year'] <= year][y_col],
                    mode='lines',
                    name=group,
                    hovertemplate=hover_template.replace("{group}", group)  # Replace {group} with the actual group name
                )
                for group, group_data in df.groupby(group_by_col)
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Add traces for each group
    for group in df[group_by_col].unique():
        group_data = df[df[group_by_col] == group]
        fig.add_trace(
            go.Scatter(
                x=group_data["Year"],
                y=group_data[y_col],
                mode='lines',
                name=group,
                hovertemplate=hover_template.replace("{group}", group)  # Replace {group} with the actual group name
            )
        )

    # Assign frames to the figure
    fig.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 1.2}, "transition": {"duration": 1.2}}], 
             label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig.update_layout(
        title=title,
        title_x=0.45,
        xaxis_title='Year',
        yaxis_title=y_label,
        showlegend=True,
        height=700,
        width=1200,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 1.2, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(l=50, r=50, t=50, b=100),
        xaxis=dict(range=[df["Year"].min(), df["Year"].max()]),
        yaxis=dict(range=[0, df[y_col].max()], ticksuffix=y_suffix),
        template=plot_template
    )

    return fig

def create_choropleth_map(df, code_col, z_col, z_min, z_max, colorbar_title, colorscale, hover_template, customdata_cols, title):

    years = sorted(df["Year"].unique())
    fig = go.Figure()

    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df[df['Year'] == year][code_col],
                    z=df[df['Year'] == year][z_col],
                    colorscale=colorscale,
                    zmin=z_min, zmax=z_max,
                    colorbar=dict(title=colorbar_title),
                    hovertemplate=hover_template.replace("{group}", str(df[df['Year'] == year][customdata_cols[0]].iloc[0])),
                    customdata=df[df['Year'] == year][customdata_cols].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig.add_trace(
        go.Choropleth(
            locations=df[df['Year'] == years[-1]][code_col],
            z=df[df['Year'] == years[-1]][z_col],
            colorscale=colorscale,
            zmin=z_min, zmax=z_max,
            colorbar=dict(title=colorbar_title),
            hovertemplate=hover_template.replace("{group}", str(df[df['Year'] == years[-1]][customdata_cols[0]].iloc[0])),
            customdata=df[df['Year'] == years[-1]][customdata_cols].values
        )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
            args=[[str(year)], {"frame": {"duration": 5, "redraw": True}, "transition": {"duration": 5}}],
            label=str(year))
        for year in years
    ]

    fig.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 5, "redraw": True}, "fromcurrent": True}],
                "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.04, "y": -0.15,
        }],
        margin=dict(l=50, r=50, t=50, b=100),
        width=1200,
        height=700,
    )

    # Assign frames
    fig.frames = frames

    return fig

st.title("CO₂ and Greenhouse Gas Emissions")
st.text("""Greenhouse gas emissions are the main drivers of climate change, trapping heat in the atmosphere and altering global temperatures. While carbon dioxide (CO₂) is the largest contributor, other gases like methane and nitrous oxide also play significant roles. Understanding emission trends, sources, and distributions is essential for tracking climate impact and shaping mitigation strategies.""")

with st.expander("CO₂ Emissions"):
    st.text("""Carbon dioxide (CO₂) emissions are the primary driver of global warming, resulting mainly from fossil fuel combustion, industrial activities, and deforestation. Tracking annual emissions, per capita contributions, global shares, and cumulative outputs helps assess historical responsibility and trends in carbon pollution.""")
    
    # -------------------------------------------------------------------------------------------------
    # Annual C02 Emissions
    # -------------------------------------------------------------------------------------------------

    # Fetch and clean data
    @st.cache_data
    def fetch_and_clean_data():
        df1 = pd.read_csv("https://ourworldindata.org/grapher/annual-co-emissions-by-region.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
        df1 = df1.rename(columns={"emissions_total": "Annual CO₂ Emissions"})
        df1["Annual CO₂ Emissions"] = df1["Annual CO₂ Emissions"] / 1000000000
        df1 = df1[~df1["Entity"].isin(["Africa (GCP)", "Asia (GCP)", "Europe (GCP)", "North America (GCP)", "Oceania (GCP)", "South America (GCP)"])]
        df1 = df1.sort_values(by=["Entity", "Year"])
        df1=df1[df1["Annual CO₂ Emissions"]!=0]

        # Forward-fill missing years for each entity
        df1 = (df1.groupby("Entity", group_keys=False).apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), group["Year"].max() + 1)).ffill().reset_index()))

        # Sort the data again after forward-filling
        df1 = df1.sort_values(by=["Entity", "Year"]).reset_index(drop=True)
        return df1
    df1 = fetch_and_clean_data()


    st.markdown("## Annual CO₂ Emissions")
    st.text("""Emissions from fossil fuels and industry are included, but not land-use change emissions. International aviation andshipping are included as separate entities, as they are not included in any country's emissions.""")

    # User selection for entity type
    view_option_1 = st.selectbox("View by:", ["Country Entity", "Non-Country Entity"], index=0, key="view_option_1")

    # Filter dataframe based on selection
    if view_option_1 == "Country Entity":
        df1_country = df1[df1["Code"].notna()]
        df1_country=df1_country[df1_country["Entity"]!="World"]
        tab1, tab2 = st.tabs(["Chart", "Map"])
        
        with tab1:
            # Chart-specific DataFrame
            df1_chart = df1_country.copy()
            
            selected_entities = st.multiselect("Select Countries:", df1_chart["Entity"].unique(), default=df1_chart[df1_chart["Year"] == df1_chart["Year"].max()].groupby("Entity")["Annual CO₂ Emissions"].sum().nlargest(5).index.tolist(), key="annual_co2_country_entity")
            df1_chart = df1_chart[df1_chart["Entity"].isin(selected_entities)]
            st.plotly_chart(create_animated_line_chart(
                df=df1_chart, 
                group_by_col="Entity", 
                y_col="Annual CO₂ Emissions", 
                y_label="Annual CO₂ Emissions", 
                y_suffix=" billion tonnes", 
                hover_template="<b>Entity:</b> {group}<br><b>Year:</b> %{x}<br><b>Annual CO₂ Emissions:</b> %{y:.2f} billion tonnes<extra></extra>", 
                title="Annual CO₂ Emissions"), use_container_width=True)
            st.caption("Data Source: Global Carbon Budget (2024) – with major processing by Our World in Data")
        
        with tab2:
            df1_map = df1_country.copy()
            st.plotly_chart(create_choropleth_map(
                df=df1_map,
                code_col="Code",
                z_col="Annual CO₂ Emissions",
                z_min=df1_map["Annual CO₂ Emissions"].min(),
                z_max=df1_map["Annual CO₂ Emissions"].max(),
                colorbar_title="Annual CO₂ Emissions (Billion T)\n",
                colorscale="ylgnbu",
                hover_template="<b></b> {group}<br><b>Year:</b> %{customdata[1]}<br><b>Annual CO₂ Emissions:</b> %{z:.2f} Billion Tonnes<extra></extra>",
                customdata_cols=["Entity", "Year"],
                title="Annual CO₂ Emissions by World Region"), use_container_width=True)
            st.caption("Data Source: Global Carbon Budget (2024) – with major processing by Our World in Data")

    else:  # Non-Country Entities
        df1_non_country = df1[df1["Code"].isna()]
        
        selected_entities = st.multiselect("Select Region:", df1_non_country["Entity"].unique(), default=df1_non_country[df1_non_country["Year"] == df1_non_country["Year"].max()].groupby("Entity")["Annual CO₂ Emissions"].sum().nlargest(5).index.tolist(), key="annual_co2_non_country_entity")
        df1_non_country = df1_non_country[df1_non_country["Entity"].isin(selected_entities)]
        st.plotly_chart(create_animated_line_chart(
                df=df1_non_country, 
                group_by_col="Entity", 
                y_col="Annual CO₂ Emissions", 
                y_label="Annual CO₂ Emissions", 
                y_suffix=" billion tonnes", 
                hover_template="<b>Entity:</b> {group}<br><b>Year:</b> %{x}<br><b>Annual CO₂ Emissions:</b> %{y:.2f} billion tonnes<extra></extra>",
                title="Annual CO₂ Emissions"), use_container_width=True)
        st.caption("Data Source: Global Carbon Budget (2024) – with major processing by Our World in Data")


    # -------------------------------------------------------------------------------------------------
    # Per Capita C02 Emissions
    # -------------------------------------------------------------------------------------------------

    # Fetch and clean data
    @st.cache_data
    def fetch_and_clean_data():
        df2 = pd.read_csv("https://ourworldindata.org/grapher/co-emissions-per-capita.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
        df2 = df2.rename(columns={"emissions_total_per_capita": "Per Capita CO₂ Emissions", "Entity": "Country"})
        df2 = df2[df2["Code"].notna()]
        df2 = df2.sort_values(by=["Country", "Year"])
        df2=df2[df2["Per Capita CO₂ Emissions"]!=0]
        df2=df2[df2["Country"]!="World"]

        # For the sake of simplicity of data visualizations, outliers to be removed
        df2 = df2[df2["Per Capita CO₂ Emissions"] <= 100]

        # Forward-fill missing years for each country
        df2 = (df2.groupby("Country", group_keys=False).apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), group["Year"].max() + 1)).ffill().reset_index()))

        # Sort the data again after forward-filling
        df2 = df2.sort_values(by=["Country", "Year"]).reset_index(drop=True)
        return df2
    df2 = fetch_and_clean_data()

    st.markdown("## Per Capita CO₂ Emissions")
    st.text("""Carbon dioxide (CO₂) emissions from fossil fuels and industry. Land-use change is not included.""")

    tab1, tab2 = st.tabs(["Chart", "Map"])
    
    with tab1:
        # Chart-specific DataFrame
        df2_chart = df2.copy()
        
        selected_countries = st.multiselect("Select Region:", df2_chart["Country"].unique(), default=["Australia", "United States", "Canada", "Russia", "India", "United Kingdom"], key="per_capita_co2")
        df2_chart = df2_chart[df2_chart["Country"].isin(selected_countries)]
        st.plotly_chart(create_animated_line_chart(
            df=df2_chart, 
            group_by_col="Country", 
            y_col="Per Capita CO₂ Emissions", 
            y_label="Per Capita CO₂ Emissions", 
            y_suffix=" tonnes", 
            hover_template="<b>Country:</b> {group}<br><b>Year:</b> %{x}<br><b>Per Capita CO₂ Emissions:</b> %{y:.2f} tonnes<extra></extra>", 
            title="Per Capita CO₂ Emissions" ), use_container_width=True)
        st.caption("Data Source: Global Carbon Budget (2024); Population based on various sources (2024) – with major processing by Our World in Data")
    
    with tab2:
        df2_map = df2.copy()
        st.plotly_chart(create_choropleth_map(
            df=df2_map, 
            code_col="Code",
            z_col="Per Capita CO₂ Emissions",
            z_min=df2_map["Per Capita CO₂ Emissions"].min(),
            z_max=20,
            colorbar_title="Per Capita CO₂ Emissions (T)\n",
            colorscale="ylgnbu",
            hover_template="<b></b> {group}<br><b>Year:</b> %{customdata[1]}<br><b>Per Capita CO₂ Emissions:</b> %{z:.2f} Tonnes<extra></extra>",
            customdata_cols=["Country", "Year"],
            title="Per Capita CO₂ Emissions"), use_container_width=True)
        st.caption("Data Source: Global Carbon Budget (2024); Population based on various sources (2024) – with major processing by Our World in Data")

    # -------------------------------------------------------------------------------------------------
    # Share of Global CO₂ Emissions
    # -------------------------------------------------------------------------------------------------

    # Fetch and clean data
    @st.cache_data
    def fetch_and_clean_data():
        df3 = pd.read_csv("https://ourworldindata.org/grapher/annual-share-of-co2-emissions.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
        df3 = df3.rename(columns={"emissions_total_as_share_of_global": "Global Share of CO₂ Emissions", "Entity": "Country"})
        df3 = df3.sort_values(by=["Year", "Country"])

        # Forward-fill missing years for each entity
        df3 = (df3.groupby("Country", group_keys=False).apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), group["Year"].max() + 1)).ffill().reset_index()))

        # Sort the data again after forward-filling
        df3 = df3.sort_values(by=["Country", "Year"]).reset_index(drop=True)
        return df3
    
    df3 = fetch_and_clean_data()

    st.markdown("## Global Share of CO₂ Emissions")
    st.text("""Carbon dioxide (CO₂) emissions from fossil fuels and industry. Land-use change is not included.""")

    tab1, tab2 = st.tabs(["Chart", "Map"])
    
    with tab1:
        # Chart-specific DataFrame
        df3_chart = df3.copy()
        
        selected_countries = st.multiselect("Select Region:", df3_chart["Country"].unique(), default=["United States", "China", "Canada", "Russia", "India", "United Kingdom"], key="share_global_co2")
        df3_chart = df3_chart[df3_chart["Country"].isin(selected_countries)]
        st.plotly_chart(create_animated_line_chart(
            df=df3_chart, 
            group_by_col="Country", 
            y_col="Global Share of CO₂ Emissions", 
            y_label="Share of Global CO₂ Emissions", 
            y_suffix="%", 
            hover_template="<b>Country:</b> {group}<br><b>Year:</b> %{x}<br><b>Global Share of CO₂ Emissions:</b> %{y:.2f}%<extra></extra>", 
            title="Share of Global CO₂ Emissions"), use_container_width=True)
        st.caption("Data Source: Global Carbon Budget (2024) – with major processing by Our World in Data")
    
    with tab2:
        df3_map = df3.copy()
        st.plotly_chart(create_choropleth_map(
            df=df3_map, 
            code_col="Code",
            z_col="Global Share of CO₂ Emissions",
            z_min=0,
            z_max=20,
            colorbar_title="Global Share of CO₂ Emissions (%)\n",
            colorscale="ylgnbu",
            hover_template="<b></b> {group}<br><b>Year:</b> %{customdata[1]}<br><b>Global Share of CO₂ Emissions:</b> %{z:.2f}%<extra></extra>",
            customdata_cols=["Country", "Year"],
            title="Share of Global CO₂ Emissions"), use_container_width=True)
        st.caption("Data Source: Global Carbon Budget (2024) – with major processing by Our World in Data")

    # -------------------------------------------------------------------------------------------------
    # Cumulative C0₂ Emissions
    # -------------------------------------------------------------------------------------------------

    # Fetch and clean data
    @st.cache_data
    def fetch_and_clean_data():
        df4 = pd.read_csv("https://ourworldindata.org/grapher/cumulative-co-emissions.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
        df4 = df4.rename(columns={"cumulative_emissions_total": "Cumulative CO₂ Emissions", "Entity": "Country"})
        df4 = df4[df4["Code"].notna()]
        df4 = df4.sort_values(by=["Year", "Country"])
        df4=df4[df4["Cumulative CO₂ Emissions"]!=0]
        df4=df4[df4["Country"]!="World"]
        df4["Cumulative CO₂ Emissions"] = df4["Cumulative CO₂ Emissions"] / 1000000000


        # Forward-fill missing years for each country
        df4 = (df4.groupby("Country", group_keys=False).apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), group["Year"].max() + 1)).ffill().reset_index()))

        # Sort the data again after forward-filling
        df4 = df4.sort_values(by=["Country", "Year"]).reset_index(drop=True)
        return df4
    
    df4 = fetch_and_clean_data()
    st.markdown("## Cumulative CO₂ Emissions")
    st.text("""Running sum of CO₂ emissions produced from fossil fuels and industry since the first year of recording, measured intonnes. Land-use change is not included.""")

    tab1, tab2 = st.tabs(["Chart", "Map"])
    
    with tab1:
        # Chart-specific DataFrame
        df4_chart = df4.copy()
        
        selected_countries = st.multiselect("Select Region:", df4_chart["Country"].unique(), default=(df4_chart[df4_chart["Year"] == df4_chart["Year"].max()].nlargest(5, "Cumulative CO₂ Emissions")["Country"].tolist()), key="cumulative_co2")
        df4_chart = df4_chart[df4_chart["Country"].isin(selected_countries)]
        st.plotly_chart(create_animated_line_chart(
            df=df4_chart, 
            group_by_col="Country", 
            y_col="Cumulative CO₂ Emissions", 
            y_label="Cumulative CO₂ Emissions", 
            y_suffix=" billion tonnes", 
            hover_template="<b>Country:</b> {group}<br><b>Year:</b> %{x}<br><b>Cumulative CO₂ Emissions:</b> %{y:.2f} billion tonnes<extra></extra>",
            title="Cumulative CO₂ Emissions"
            ), use_container_width=True)
        st.caption("Data Source: Global Carbon Budget (2024) – with major processing by Our World in Data")
    
    with tab2:
        df4_map = df4.copy()
        st.plotly_chart(create_choropleth_map(
            df=df4_map, 
            code_col="Code",
            z_col="Cumulative CO₂ Emissions",
            z_min=0,
            z_max=100,
            colorbar_title="Cumulative CO₂ Emissions (billion tonnes)\n",
            colorscale="ylgnbu",
            hover_template="<b></b> {group}<br><b>Year:</b> %{customdata[1]}<br><b>Cumulative CO₂ Emissions:</b> %{z:.2f} billion tonnes<extra></extra>",
            customdata_cols=["Country", "Year"],
            title="Cumulative CO₂ Emissions"), use_container_width=True)
        st.caption("Data Source: Global Carbon Budget (2024) – with major processing by Our World in Data")

st.divider()
with st.expander("Greenhouse Gas Emissions"):
    st.text("""Greenhouse gases (GHGs) include CO₂, methane, nitrous oxide, and fluorinated gases, all of which trap heat in the atmosphere and contribute to climate change. Analyzing total emissions, per capita distributions, and global shares provides a broader perspective on the sources and impacts of climate-warming pollutants.""")

    # -------------------------------------------------------------------------------------------------
    # Annual Greenhouse Emissions
    # -------------------------------------------------------------------------------------------------

    # Fetch and clean data
    @st.cache_data
    def fetch_and_clean_data():
        df5 = pd.read_csv("https://ourworldindata.org/grapher/ghg-emissions-by-world-region.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

        df5 = df5.rename(columns={"annual_emissions_ghg_total_co2eq": "Annual GHG Emissions (CO₂ Eq)"})
        df5["Annual GHG Emissions (CO₂ Eq)"] = df5["Annual GHG Emissions (CO₂ Eq)"] / 1000000000
        df5 = df5[~df5["Entity"].isin(["Africa (GCP)", "Asia (GCP)", "Europe (GCP)", "North America (GCP)", "Oceania (GCP)", "South America (GCP)"])]
        df5 = df5.sort_values(by=["Entity", "Year"])
        df5=df5[df5["Annual GHG Emissions (CO₂ Eq)"]!=0]

        # Forward-fill missing years for each entity
        df5 = (df5.groupby("Entity", group_keys=False).apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), group["Year"].max() + 1)).ffill().reset_index()))

        # Sort the data again after forward-filling
        df5 = df5.sort_values(by=["Entity", "Year"]).reset_index(drop=True)
        return df5
    
    df5 = fetch_and_clean_data()

    st.markdown("## Annual Greenhouse Gas Emissions")
    st.text("""Greenhouse gas emissions include carbon dioxide, methane and nitrous oxide from all sources, including land-usechange. They are measured in tonnes of carbon dioxide-equivalents over a 100-year timescale.""")

    # User selection for entity type
    view_option_2 = st.selectbox("View by:", ["Country Entity", "Non-Country Entity"], index=0, key="view_option_2")

    # Filter dataframe based on selection
    if view_option_2 == "Country Entity":
        df5_country = df5[df5["Code"].notna()]
        df5_country=df5_country[df5_country["Entity"]!="World"]
        tab1, tab2 = st.tabs(["Chart", "Map"])
        
        with tab1:
            # Chart-specific DataFrame
            df5_chart = df5_country.copy()
            
            selected_entities = st.multiselect("Select Region:", df5_chart["Entity"].unique(), default=df5_chart[df5_chart["Year"] == df5_chart["Year"].max()].groupby("Entity")["Annual GHG Emissions (CO₂ Eq)"].sum().nlargest(5).index.tolist(), key="annual_ghg_country_entity")
            df5_chart = df5_chart[df5_chart["Entity"].isin(selected_entities)]
            st.plotly_chart(create_animated_line_chart(
                df=df5_chart, 
                group_by_col="Entity", 
                y_col="Annual GHG Emissions (CO₂ Eq)",
                y_label="Annual GHG Emissions", 
                y_suffix=" billion tonnes (CO₂ Eq)", 
                hover_template="<b>Entity:</b> {group}<br><b>Year:</b> %{x}<br><b>Annual GHG Emissions:</b> %{y:.2f} billion tonnes (CO₂ Eq)<extra></extra>",
                title="Annual Greenhouse Emissions by World Region"), use_container_width=True)
            st.caption("Data Source: Jones et al. (2024) – with major processing by Our World in Data")
        
        with tab2:
            df5_map = df5_country.copy()
            st.plotly_chart(create_choropleth_map(
                df=df5_map,
                code_col="Code",
                z_col="Annual GHG Emissions (CO₂ Eq)",
                z_min=df5_map["Annual GHG Emissions (CO₂ Eq)"].min(),
                z_max=df5_map["Annual GHG Emissions (CO₂ Eq)"].max(),
                colorbar_title="Annual GHG Emissions (Billion Tonnes of CO₂ Eq)\n",
                colorscale="purples",
                hover_template="<b></b> {group}<br><b>Year:</b> %{customdata[1]}<br><b>Annual GHG Emissions:</b> %{z:.2f} Billion Tonnes (of CO₂ Eq)<extra></extra>",
                customdata_cols=["Entity", "Year"],
                title="Annual Greenhouse Emissions by World Region"), use_container_width=True)
            st.caption("Data Source: Jones et al. (2024) – with major processing by Our World in Data")

    else:  # Non-Country Entities
        df5_non_country = df5[df5["Code"].isna()]
        
        selected_entities = st.multiselect("Select Region:", df5_non_country["Entity"].unique(), default=df5_non_country[df5_non_country["Year"] == df5_non_country["Year"].max()].groupby("Entity")["Annual GHG Emissions (CO₂ Eq)"].sum().nlargest(5).index.tolist(), key="annual_ghg_non_country_entity")
        df5_non_country = df5_non_country[df5_non_country["Entity"].isin(selected_entities)]
        st.plotly_chart(create_animated_line_chart(
            df=df5_non_country,
            group_by_col="Entity",
            y_col="Annual GHG Emissions (CO₂ Eq)",
            y_label="Annual GHG Emissions",
            y_suffix=" billion tonnes (CO₂ Eq)",
            hover_template="<b>Entity:</b> {group}<br><b>Year:</b> %{x}<br><b>Annual GHG Emissions:</b> %{y:.2f} billion tonnes (CO₂ Eq)<extra></extra>",
            title="Annual Greenhouse Emissions by World Region"), use_container_width=True)
        st.caption("Data Source: Jones et al. (2024) – with major processing by Our World in Data")

    # -------------------------------------------------------------------------------------------------
    # Per Capita Greenhouse Emissions
    # -------------------------------------------------------------------------------------------------

    # Fetch and clean data
    @st.cache_data
    def fetch_and_clean_data():
        df6 = pd.read_csv("https://ourworldindata.org/grapher/per-capita-ghg-emissions.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
        df6 = df6.rename(columns={"annual_emissions_ghg_total_co2eq_per_capita": "Per Capita Annual GHG Emissions (CO₂ Eq)", "Entity": "Country"})
        df6 = df6[df6["Code"].notna()]
        df6 = df6.sort_values(by=["Country", "Year"])
        df6=df6[df6["Per Capita Annual GHG Emissions (CO₂ Eq)"]!=0]
        df6=df6[df6["Country"]!="World"]

        # For the sake of simplicity of data visualizations, outliers to be removed
        df6 = df6[df6["Per Capita Annual GHG Emissions (CO₂ Eq)"] <= 100]

        # Forward-fill missing years for each country
        df6 = (df6.groupby("Country", group_keys=False).apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), group["Year"].max() + 1)).ffill().reset_index()))

        # Sort the data again after forward-filling
        df6 = df6.sort_values(by=["Country", "Year"]).reset_index(drop=True)
        return df6
    
    df6 = fetch_and_clean_data()

    st.markdown("## Per Capita Annual Greenhouse Gas Emissions")
    st.text("""Greenhouse gas emissions include carbon dioxide, methane and nitrous oxide from all sources, including land-usechange. They are measured in tonnes of carbon dioxide-equivalents over a 100-year timescale.""")

    tab1, tab2 = st.tabs(["Chart", "Map"])
    
    with tab1:
        # Chart-specific DataFrame
        df6_chart = df6.copy()
        
        selected_countries = st.multiselect("Select Region:", df6_chart["Country"].unique(), default=["Australia", "United States", "Canada", "Russia", "India", "United Kingdom"], key="per_capita_ghg")
        df6_chart = df6_chart[df6_chart["Country"].isin(selected_countries)]
        st.plotly_chart(create_animated_line_chart(
            df=df6_chart, 
            group_by_col="Country",
            y_col="Per Capita Annual GHG Emissions (CO₂ Eq)",
            y_label="Per Capita Annual GHG Emissions",
            y_suffix=" tonnes (CO₂ Eq)",
            hover_template="<b>Country:</b> {group}<br><b>Year:</b> %{x}<br><b>Per Capita Annual GHG Emissions:</b> %{y:.2f} tonnes (CO₂ Eq)<extra></extra>",
            title="Per Capita Greenhouse Emissions"), use_container_width=True)
        st.caption("Data Source: Jones et al. (2024); Population based on various sources (2024) – with major processing by Our World in Data")
    
    with tab2:
        df6_map = df6.copy()
        st.plotly_chart(create_choropleth_map(
            df=df6_map,
            code_col="Code",
            z_col="Per Capita Annual GHG Emissions (CO₂ Eq)",
            z_min=df6_map["Per Capita Annual GHG Emissions (CO₂ Eq)"].min(),
            z_max=30,
            colorbar_title="Per Capita Annual GHG Emissions (tonnes of CO₂ Eq)\n",
            colorscale="purples",
            hover_template="<b></b> {group}<br><b>Year:</b> %{customdata[1]}<br><b>Per Capita Annual GHG Emissions:</b> %{z:.2f} Tonnes (of CO₂ Eq)<extra></extra>",
            customdata_cols=["Country", "Year"],
            title="Per Capita Greenhouse Emissions"), use_container_width=True)
        st.caption("Data Source: Jones et al. (2024); Population based on various sources (2024) – with major processing by Our World in Data")

    # -------------------------------------------------------------------------------------------------
    # Share of Global Greenhouse Gas Emissions
    # -------------------------------------------------------------------------------------------------

    # Fetch and clean data
    @st.cache_data
    def fetch_and_clean_data():
        df7 = pd.read_csv("https://ourworldindata.org/grapher/share-global-ghg-emissions.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
        df7 = df7.rename(columns={"share_of_annual_emissions_ghg_total": "Share of Global GHG Emissions", "Entity": "Country"})
        df7 = df7[df7["Code"].notna()]
        df7 = df7.sort_values(by=["Year", "Country"])
        df7=df7[df7["Country"]!="World"]

        # Forward-fill missing years for each country
        df7 = (df7.groupby("Country", group_keys=False).apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), group["Year"].max() + 1)).ffill().reset_index()))

        # Sort the data again after forward-filling
        df7 = df7.sort_values(by=["Year", "Country"]).reset_index(drop=True)
        return df7
    
    df7 = fetch_and_clean_data()

    st.markdown("## Share of Global Greenhouse Gas Emissions")
    st.text("""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut ullamcorper luctus mi quis consequat. Proin gravida massa sapien, et aliquam nulla aliquam quis. Curabitur eget enim eget arcu malesuada accumsan. Interdum et malesuada fames ac ante ipsum primis in faucibus. Donec ipsum magna, congue maximus tellus ac, maximus pellentesque neque.""")

    tab1, tab2 = st.tabs(["Chart", "Map"])
    
    with tab1:
        # Chart-specific DataFrame
        df7_chart = df7.copy()
        
        selected_countries = st.multiselect("Select Region:", df7_chart["Country"].unique(), default=(df7_chart[df7_chart["Year"] == df7_chart["Year"].max()].nlargest(5, "Share of Global GHG Emissions")["Country"].tolist()), key="share_global_ghg")
        df7_chart = df7_chart[df7_chart["Country"].isin(selected_countries)]
        st.plotly_chart(create_animated_line_chart(
            df=df7_chart,
            group_by_col="Country",
            y_col="Share of Global GHG Emissions",
            y_label="Share of Global GHG Emissions",
            y_suffix="%",
            hover_template="<b>Country:</b> {group}<br><b>Year:</b> %{x}<br><b>Share of Global GHG Emissions:</b> %{y:.2f}%<extra></extra>",
            title="Share of Global Greenhouse Gas Emissions"), use_container_width=True)
        st.caption("Data Source: Jones et al. (2024) – with major processing by Our World in Data")
    
    with tab2:
        df7_map = df7.copy()
        st.plotly_chart(create_choropleth_map(
            df=df7_map,
            code_col="Code",
            z_col="Share of Global GHG Emissions",
            z_min=df7_map["Share of Global GHG Emissions"].min(),
            z_max=20,
            colorbar_title="Share of Global GHG Emissions (%)\n",
            colorscale="purples",
            hover_template="<b></b> {group}<br><b>Year:</b> %{customdata[1]}<br><b>Share of Global GHG Emissions:</b> %{z:.2f}%<extra></extra>",
            customdata_cols=["Country", "Year"],
            title="Share of Global Greenhouse Gas Emissions"), use_container_width=True)
        st.caption("Data Source: Jones et al. (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------------------
# Carbon Intensity of Energy Production
# -------------------------------------------------------------------------------------------------

st.divider()
with st.expander("Carbon Intensity of Energy Production"):

    # Fetch and clean data
    @st.cache_data
    def fetch_and_clean_data():
        df8 = pd.read_csv("https://ourworldindata.org/grapher/co2-per-unit-energy.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
        df8 = df8.rename(columns={"emissions_total_per_unit_energy": "Emissions Per Unit Energy", "Entity": "Country"})
        df8 = df8[df8["Code"].notna()]
        df8 = df8[df8["Country"]!="Antarctica"]
        df8=df8[df8["Country"]!="World"]
        df8 = df8.sort_values(by=["Country", "Year"]).reset_index(drop=True)

        # Forward fill missing data for each country
        df8 = df8.set_index(['Country', 'Year']).reindex(
        pd.MultiIndex.from_product([df8['Country'].unique(), range(df8['Year'].min(), df8['Year'].max() + 1)], names=['Country', 'Year'])).reset_index()
        df8['Code'] = df8.groupby('Country')['Code'].ffill()
        df8['Emissions Per Unit Energy'] = df8.groupby('Country')['Emissions Per Unit Energy'].ffill()

        df8=df8[df8["Emissions Per Unit Energy"].notna()]
        df8 = df8.sort_values(by=["Year", "Country"]).reset_index(drop=True)
        return df8

    df8 = fetch_and_clean_data()

    st.markdown("## Carbon Intensity of Energy Production")
    st.text("""Amount of carbon dioxide emitted per unit of energy production, measured in kilograms of CO₂ per kilowatt-hour.""")
    tab1, tab2 = st.tabs(["Map", "Chart"])

    with tab1:
        df8_map = df8.copy()
        st.plotly_chart(create_choropleth_map(
            df=df8_map,
            code_col="Code",
            z_col="Emissions Per Unit Energy",
            z_min=df8_map["Emissions Per Unit Energy"].min(),
            z_max=0.5,
            colorbar_title="Emissions Per Unit Energy (Kg per KWh)\n",
            colorscale="rdylgn_r",
            hover_template="<b>Country:</b> %{customdata[0]}<br><b>Year:</b> %{customdata[1]}<br><b>Emissions Per Unit Energy:</b> %{z:.2f} Kg per KWh<extra></extra>",
            customdata_cols=["Country", "Year"],
            title="Carbon Intensity of Energy Production"), use_container_width=True)
        st.caption("Data Source: Global Carbon Budget (2024); U.S. Energy Information Administration (2023); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
        
    with tab2:
        # Chart-specific DataFrame
        df8_chart = df8.copy()
        
        selected_countries = st.multiselect("Select Region:", df8_chart["Country"].unique(), default=(df8_chart[df8_chart["Year"] == df8_chart["Year"].max()].nlargest(5, "Emissions Per Unit Energy")["Country"].tolist()), key="emissions_per_unit_energy")
        df8_chart = df8_chart[df8_chart["Country"].isin(selected_countries)]
        st.plotly_chart(create_animated_line_chart(
            df=df8_chart,
            group_by_col="Country",
            y_col="Emissions Per Unit Energy",
            y_label="Emissions Per Unit Energy (Kg per KWh)",
            y_suffix=" kg",
            hover_template="<b>Country:</b> {group}<br><b>Year:</b> %{x}<br><b>Emissions Per Unit Energy:</b> %{y:.2f} Kg per KWh<extra></extra>",
            title="Carbon Intensity of Energy Production"), use_container_width=True)
        st.caption("Data Source: Global Carbon Budget (2024); U.S. Energy Information Administration (2023); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

st.write("\n" * 5)
st.divider()
st.caption("Citation: Hannah Ritchie, Pablo Rosado and Max Roser (2023) - “CO₂ and Greenhouse Gas Emissions” Published online at OurWorldinData.org. Retrieved from: 'https://ourworldindata.org/co2-and-greenhouse-gas-emissions' [Online Resource]")

