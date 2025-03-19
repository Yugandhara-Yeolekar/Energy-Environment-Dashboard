import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Apply Streamlit Theme
st.set_page_config(page_title="Renewable Energy", layout="wide")
theme = st.config.get_option("theme.base")
# Set plotly template based on theme
plot_template = "plotly_dark" if theme == "dark" else "simple_white"

st.title("Renewable Energy")

# -------------------------------------------------------------------------------------
# Share of Primary Energy Consumption from Renewable Sources
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df2 = pd.read_csv("https://ourworldindata.org/grapher/renewable-share-energy.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    df2 = df2.rename(columns={"Entity": "Country", "renewables__pct_equivalent_primary_energy": "Renewable Percentage"})

    df2=df2[df2["Code"].notna()]
    df2 = df2[df2['Country'] != 'World'].reset_index(drop=True)
    df2=df2.sort_values(by=["Country", "Year"])
    return df2
df2 = fetch_and_clean_data()

def create_choropleth_map(df2):
    years = sorted(df2["Year"].unique())
    fig2 = go.Figure()

    # Define color scale range
    zmin = df2["Renewable Percentage"].min()
    zmax = df2["Renewable Percentage"].max()

    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df2[df2['Year'] == year]['Code'],
                    z=df2[df2['Year'] == year]['Renewable Percentage'],
                    colorscale="Greens",
                    zmin=zmin, zmax=zmax,
                    colorbar=dict(title="Share of Energy Consumption from Renewables (%) \n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Renewable Percentage:</b> %{z:.2f}%<extra></extra>",
                    customdata=df2[df2['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig2.add_trace(
        go.Choropleth(
            locations=df2[df2['Year'] == years[-1]]['Code'],
            z=df2[df2['Year'] == years[-1]]['Renewable Percentage'],
            colorscale="Greens",
            zmin=zmin, zmax=zmax,
            colorbar=dict(title="Share of Energy Consumption from Renewables (%) \n"),
            hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                          "<b>Year:</b> %{customdata[1]}<br>" +
                          "<b>Renewable Percentage:</b> %{z:.2f}%<extra></extra>",
            customdata=df2[df2['Year'] == years[-1]][['Country', 'Year']].values
        )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig2.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig2.frames = frames

    return fig2


def create_animated_line_chart(df2):
    years = sorted(df2["Year"].unique())
    fig3 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Scatter(
                    x=country_data[country_data['Year'] <= year]['Year'],
                    y=country_data[country_data['Year'] <= year]['Renewable Percentage'],
                    mode='lines+markers',
                    name=country,
                    hovertemplate="<b>Country:</b> " + country + "<br>" +
                                  "<b>Year:</b> %{x}<br>" +
                                  "<b>Renewable Percentage:</b> %{y:.2f}%<extra></extra>"
                )
                for country, country_data in df2.groupby('Country')
            ]
        ) for year in years
    ]

    # Add traces for each country
    for country in df2["Country"].unique():
        country_data = df2[df2["Country"] == country]
        fig3.add_trace(
            go.Scatter(
                x=country_data["Year"],
                y=country_data["Renewable Percentage"],
                mode='lines+markers',
                name=country,
                hovertemplate="<b>Country:</b> " + country + "<br>" +
                              "<b>Year:</b> %{x}<br>" +
                              "<b>Renewable Percentage:</b> %{y:.2f}%<extra></extra>"
            )
        )

    # Assign frames to the figure
    fig3.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 50}, "transition": {"duration": 50}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig3.update_layout(
        xaxis_title='Year',
        yaxis_title='Share of Energy Consumption from Renewables',
        showlegend=True,
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[0,100], ticksuffix="%"),
        xaxis=dict(range=[country_data["Year"].min(), country_data["Year"].max()]),
        template=plot_template
    )

    return fig3

st.markdown("## Share of Primary Energy Consumption from Renewable Sources")
st.text("""Measured as a percentage of primary energy. Renewables include hydropower, solar, wind, geothermal, bioenergy, wave, and tidal, but not traditional biofuels, which can be a key energy source, especially in lower-income settings.""")

# Radio button for Map or Chart selection
tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df2), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df2["Country"].unique(), default=["India", "United States", "China", "Norway", "Brazil"])
    df2_selected = df2[df2["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_line_chart(df2_selected), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------
# Share of Electricity Production from Renewables
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df3 = pd.read_csv("https://ourworldindata.org/grapher/share-electricity-renewables.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    df3 = df3.rename(columns={"Entity": "Country", "renewable_share_of_electricity__pct": "Renewable Share of Electricity (%)"})

    df3 = df3[df3["Code"].notna()]
    df3 = df3[df3['Country'] != 'World'].reset_index(drop=True)
    df3 = df3.sort_values(by=["Country", "Year"])
    return df3
df3 = fetch_and_clean_data()

# Fill missing 2023 values with 2022 data
df3 = (
    df3.groupby("Country", group_keys=False)
    .apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), 2024)).ffill())
    .reset_index()
)

# Drop rows where Year is 2023 and the value is still NaN (no data available for 2022 or earlier)
df3 = df3.dropna(subset=["Renewable Share of Electricity (%)"])

# Sort the data again
df3 = df3.sort_values(by=["Country", "Year"]).reset_index(drop=True)

def create_choropleth_map(df3):
    years = sorted(df3["Year"].unique())
    fig4 = go.Figure()

    # Define color scale range
    zmin = df3["Renewable Share of Electricity (%)"].min()
    zmax = df3["Renewable Share of Electricity (%)"].max()

    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df3[df3['Year'] == year]['Code'],
                    z=df3[df3['Year'] == year]['Renewable Share of Electricity (%)'],
                    colorscale="Greens",
                    zmin=zmin, zmax=zmax,
                    colorbar=dict(title="Share of Energy Consumption from Renewables (%) \n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Electricity Production from Renewables:</b> %{z:.2f}%<extra></extra>",
                    customdata=df3[df3['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig4.add_trace(
        go.Choropleth(
            locations=df3[df3['Year'] == years[0]]['Code'],
            z=df3[df3['Year'] == years[0]]['Renewable Share of Electricity (%)'],
            colorscale="Greens",
            zmin=zmin, zmax=zmax,
            colorbar=dict(title="Share of Energy Consumption from Renewables (%) \n"),
            hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                          "<b>Year:</b> %{customdata[1]}<br>" +
                          "<b>Share of Electricity Production from Renewables:</b> %{z:.2f}%<extra></extra>",
            customdata=df3[df3['Year'] == years[0]][['Country', 'Year']].values
        )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig4.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig4.frames = frames

    return fig4


def create_animated_line_chart(df3):
    years = sorted(df3["Year"].unique())
    fig5 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Scatter(
                    x=country_data[country_data['Year'] <= year]['Year'],
                    y=country_data[country_data['Year'] <= year]['Renewable Share of Electricity (%)'],
                    mode='lines+markers',
                    name=country,
                    hovertemplate="<b>Country:</b> " + country + "<br>" +
                                  "<b>Year:</b> %{x}<br>" +
                                  "<b>Share of Electricity Production from Renewables:</b> %{y:.2f}%<extra></extra>"
                )
                for country, country_data in df3.groupby('Country')
            ]
        ) for year in years
    ]

    # Add traces for each country
    for country in df3["Country"].unique():
        country_data = df3[df3["Country"] == country]
        fig5.add_trace(
            go.Scatter(
                x=country_data["Year"],
                y=country_data["Renewable Share of Electricity (%)"],
                mode='lines+markers',
                name=country,
                hovertemplate="<b>Country:</b> " + country + "<br>" +
                              "<b>Year:</b> %{x}<br>" +
                              "<b>Share of Electricity Production from Renewables:</b> %{y:.2f}%<extra></extra>"
            )
        )

    # Assign frames to the figure
    fig5.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 50}, "transition": {"duration": 50}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig5.update_layout(
        xaxis_title='Year',
        yaxis_title='Share of Electricity Production from Renewables',
        showlegend=True,
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[0,100], ticksuffix="%"),
        xaxis=dict(range=[country_data["Year"].min(), country_data["Year"].max()]),
        template=plot_template
    )

    return fig5

st.markdown("## Share of Electricity Production from Renewables")
st.text("""Renewables include electricity production from hydropower, solar, wind, biomass & waste, geothermal, wave, and tidal sources.""")

tab1, tab2 = st.tabs(["Map", "Chart"])

with tab1:
    st.plotly_chart(create_choropleth_map(df3), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df3["Country"].unique(), default=["India", "United States", "China", "Brazil", "Canada", "Norway"])
    df3_selected = df3[df3["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_line_chart(df3_selected), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------
# Renewable Electricity Generation
# -------------------------------------------------------------------------------------

# Fetch the data.
@st.cache_data
def fetch_and_clean_data():
    df4 = pd.read_csv("https://ourworldindata.org/grapher/modern-renewable-energy-consumption.csv?v=1&csvType=full&useColumnShortNames=false", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
    df4 = df4.rename(columns={"Entity": "Country", 
                            "Other renewables (including geothermal and biomass) electricity generation - TWh": "Other Renewables Generation",
                            "Solar generation - TWh": "Solar Generation",
                            "Wind generation - TWh": "Wind Generation",
                            "Hydro generation - TWh": "Hydro Generation"})

    df4 = df4[df4["Code"].notna()]
    df4 = df4.sort_values(by=["Country", "Year"])
    return df4
df4 = fetch_and_clean_data()

def create_line_chart(df4):
    years = sorted(df4["Year"].unique())
    fig6 = go.Figure()

    # Define the energy types
    energy_types = ["Other Renewables Generation", "Solar Generation", "Wind Generation", "Hydro Generation"]

    # Create frames for each year
    frames = [go.Frame(
        name=f"frame_{year}",
        data=[
            go.Scatter(
                x=df4_filtered[df4_filtered["Year"] <= year]["Year"],
                y=df4_filtered[df4_filtered["Year"] <= year][energy_type],
                fill="none",
                name=energy_type,
                hovertemplate=f"%{{x}}<br>{energy_type}: %{{y:.2f}} TWh",
            ) for energy_type in energy_types
        ]
    ) for year in sorted(df4_filtered['Year'].unique())]

    # Add initial data
    for energy_type in energy_types:
        fig6.add_trace(go.Scatter(
            x=df4_filtered[df4_filtered["Year"] <= years[-1]]["Year"],
            y=df4_filtered[df4_filtered["Year"] <= years[-1]][energy_type],
            fill="none",
            name=energy_type,
            hovertemplate=f"%{{x}}<br>{energy_type}: %{{y:.2f}} TWh",
        ))

    # Add frames to the figure
    fig6.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 50}, "transition": {"duration": 50}}], 
              label=str(year)) for year in sorted(df4_filtered['Year'].unique())]

    # Update layout
    fig6.update_layout(
        xaxis_title='Year',
        yaxis_title='Generation (TWh)',
        showlegend=True,
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: ", visible=True), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[0, df4_filtered[energy_types].max().max() * 1.1], ticksuffix=" TWh"),
        xaxis=dict(range=[df4_filtered["Year"].min(), df4_filtered["Year"].max()]),
        template=plot_template
    )

    return fig6
    
def create_animated_pie_chart(df4_filtered):
    years = sorted(df4["Year"].unique())
    fig7 = go.Figure()

    # Define the energy types
    energy_types = ["Other Renewables Generation", "Solar Generation", "Wind Generation", "Hydro Generation"]
    color_map = {energy: color for energy, color in zip(energy_types, px.colors.qualitative.Plotly)}

    # Generate frames for each year
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Pie(
                    labels=energy_types,
                    values=[df4_filtered[df4_filtered["Year"] == year][energy_type].values[0] if not df4_filtered[df4_filtered["Year"] == year].empty else 0
                            for energy_type in energy_types],
                    textinfo="label+percent",
                    hoverinfo="text",
                    textposition="outside",
                    text=[f"{year} - {energy_type}: {df4_filtered[df4_filtered['Year'] == year][energy_type].values[0]:.2f} TWh"
                        if not df4_filtered[df4_filtered["Year"] == year].empty else f"{year} - {energy_type}: 0.00 TWh"
                        for energy_type in energy_types],
                    marker=dict(colors=[color_map[energy_type] for energy_type in energy_types])
                    )
            ],
            layout=dict(title=f"Share of Renewable Energy - {selected_country}, {year}")
        ) for year in sorted(df4_filtered["Year"].unique())
    ]

    # Initial frame (latest year)
    latest_year = sorted(df4_filtered["Year"].unique())[-1]
    fig7.add_trace(
        go.Pie(
            labels=energy_types,
            values=[df4_filtered[df4_filtered["Year"] == latest_year][energy_type].values[0] if not df4_filtered[df4_filtered["Year"] == latest_year].empty else 0
                    for energy_type in energy_types],
            textinfo="label+percent",
            hoverinfo="text",
            textposition="outside",
            text=[f"{latest_year} - {energy_type}: {df4_filtered[df4_filtered['Year'] == latest_year][energy_type].values[0]:.2f} TWh"
                if not df4_filtered[df4_filtered["Year"] == latest_year].empty else f"{latest_year} - {energy_type}: 0.00 TWh"
                for energy_type in energy_types],
            marker=dict(colors=[color_map[energy_type] for energy_type in energy_types])
        )
    )

    # Assign frames to the figure
    fig7.frames = frames

    # Create slider steps dynamically
    steps = [
        dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 50}, "transition": {"duration": 30}}],
             label=str(year)) for year in sorted(df4_filtered["Year"].unique())
    ]

    # Update layout with slider, buttons, and other settings
    fig7.update_layout(
        title=f"Share of Renewable Energy - {selected_country}, {years[-1]}",
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        template=plot_template
    )

    return fig7

st.markdown("## Renewable Electricity Generation")

country_list = sorted(df4["Country"].unique().tolist())
# Dropdown to select region
selected_country = st.selectbox("Select Region", country_list, index=country_list.index("World"))
df4_filtered = df4[df4["Country"] == selected_country]

tab1, tab2=st.tabs(["Pie Chart", "Line Chart"])
with tab1:
    st.plotly_chart(create_animated_pie_chart(df4_filtered), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    st.plotly_chart(create_line_chart(df4_filtered), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------
# Solar Power Generation
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df5 = pd.read_csv("https://ourworldindata.org/grapher/solar-energy-consumption.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df5=df5[df5["Code"].notna()]
    df5=df5[df5["Entity"]!="World"]
    df5=df5[df5["solar_generation__twh"]!=0]
    df5 = df5.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df5.rename(columns={"Entity":"Country","solar_generation__twh":"Solar Generation (TWh)"}, inplace=True)

    # Fill missing 2023 values with 2022 data
    df5 = (
        df5.groupby("Country", group_keys=False)
        .apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), 2024)).ffill())
        .reset_index()
    )

    # Drop rows where Year is 2023 and the value is still NaN (no data available for 2022 or earlier)
    df5 = df5.dropna(subset=["Solar Generation (TWh)"])

    # Sort the data again
    df5 = df5.sort_values(by=["Country", "Year"]).reset_index(drop=True)
    return df5
df5 = fetch_and_clean_data()

years = sorted(df5["Year"].unique())

def create_choropleth_map(df5):
    fig8 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df5[df5['Year'] == year]['Code'],
                    z=df5[df5['Year'] == year]['Solar Generation (TWh)'],
                    colorscale="ylorrd",
                    zmin=df5["Solar Generation (TWh)"].min(), zmax=df5["Solar Generation (TWh)"].max(),
                    colorbar=dict(title="Solar Power Generation (TWh)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Solar Generation (TWh):</b> %{z:.2f}<extra></extra>",
                    customdata=df5[df5['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig8.add_trace(
        go.Choropleth(
            locations=df5[df5['Year'] == years[-1]]['Code'],
                    z=df5[df5['Year'] == years[-1]]['Solar Generation (TWh)'],
                    colorscale="ylorrd",
                    zmin=df5["Solar Generation (TWh)"].min(), zmax=df5["Solar Generation (TWh)"].max(),
                    colorbar=dict(title="Solar Power Generation (TWh)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Solar Generation (TWh):</b> %{z:.2f}<extra></extra>",
                    customdata=df5[df5['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig8.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig8.frames = frames

    return fig8

def create_animated_line_chart(df5):
    fig9 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Scatter(
                    x=country_data[country_data['Year'] <= year]['Year'],
                    y=country_data[country_data['Year'] <= year]['Solar Generation (TWh)'],
                    mode='lines',
                    name=country,
                    hovertemplate="<b>Country:</b> " + country + "<br>" +
                                  "<b>Year:</b> %{x}<br>" +
                                  "<b>Solar Generation (TWh):</b> %{y:.2f}<extra></extra>"
                )
                for country, country_data in df5.groupby('Country')
            ]
        ) for year in years
    ]

    # Add traces for each country
    for country in df5["Country"].unique():
        country_data = df5[df5["Country"] == country]
        fig9.add_trace(
            go.Scatter(
                x=country_data["Year"],
                y=country_data["Solar Generation (TWh)"],
                mode='lines',
                name=country,
                hovertemplate="<b>Country:</b> " + country + "<br>" +
                              "<b>Year:</b> %{x}<br>" +
                              "<b>Solar Generation (TWh):</b> %{y:.2f}<extra></extra>"
            )
        )

    # Assign frames to the figure
    fig9.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 50}, "transition": {"duration": 50}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig9.update_layout(
        xaxis_title='Year',
        yaxis_title='Solar Power Generation',
        showlegend=True,
        height=700,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[0, 600], ticksuffix=" TWh"),
        xaxis=dict(range=[country_data["Year"].min(), country_data["Year"].max()]),
        template=plot_template
    )
    return fig9

st.markdown("## Solar Power Generation")
st.text("""Electricity generation from solar, measured in terawatt-hours (TWh) per year.""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df5), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df5["Country"].unique(), default=df5[df5["Year"] == df5["Year"].max()].sort_values(by="Solar Generation (TWh)",  ascending=False).head(5)["Country"].tolist())
    df5_selected = df5[df5["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_line_chart(df5_selected), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------
# Share of Primary Energy Consumption from Solar
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df6 = pd.read_csv("https://ourworldindata.org/grapher/solar-share-energy.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df6=df6[df6["Code"].notna()]
    df6=df6[df6["Entity"]!="World"]
    df6=df6[df6["solar__pct_equivalent_primary_energy"]!=0]
    df6 = df6.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df6.rename(columns={"Entity":"Country","solar__pct_equivalent_primary_energy":"Share of Solar Energy (%)"}, inplace=True)
    return df6
df6 = fetch_and_clean_data()
years = sorted(df6["Year"].unique())

def create_choropleth_map(df6):
    fig10 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df6[df6['Year'] == year]['Code'],
                    z=df6[df6['Year'] == year]['Share of Solar Energy (%)'],
                    colorscale="ylorrd",
                    zmin=df6["Share of Solar Energy (%)"].min(), zmax=df6["Share of Solar Energy (%)"].max(),
                    colorbar=dict(title="Share of Solar Energy (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Solar Energy:</b> %{z:.2f}%<extra></extra>",
                    customdata=df6[df6['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig10.add_trace(
        go.Choropleth(
            locations=df6[df6['Year'] == years[-1]]['Code'],
                    z=df6[df6['Year'] == years[-1]]['Share of Solar Energy (%)'],
                    colorscale="ylorrd",
                    zmin=df6["Share of Solar Energy (%)"].min(), zmax=df6["Share of Solar Energy (%)"].max(),
                    colorbar=dict(title="Share of Solar Energy (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Solar Energy:</b> %{z:.2f}%<extra></extra>",
                    customdata=df6[df6['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig10.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig10.frames = frames

    return fig10

country_colors = {country: px.colors.qualitative.Prism[i % len(px.colors.qualitative.Prism)]
                  for i, country in enumerate(df6["Country"].unique())}

def create_animated_bar_chart(df6):
    fig11 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Bar(
                    x=df6["Country"].unique(),  # Keep all countries
                    y=[df6[(df6["Country"] == country) & (df6["Year"] <= year)]["Share of Solar Energy (%)"].max()
                       for country in df6["Country"].unique()],  # Only update the height
                    hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Solar Energy: %{y:.2f}%<extra></extra>",  # Hover label with year
                    customdata=[year] * len(df6["Country"].unique()),  # Add year to customdata
                    marker=dict(color=[country_colors[country] for country in df6["Country"].unique()])
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig11.add_trace(
        go.Bar(
            x=df6["Country"].unique(),
            y=[df6[(df6["Country"] == country) & (df6["Year"] <= years[-1])]["Share of Solar Energy (%)"].max()
               for country in df6["Country"].unique()],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Solar Energy: %{y:.2f}%<extra></extra>",  # Hover label with year
            customdata=[years[-1]] * len(df6["Country"].unique()),  # Add year to customdata
            marker=dict(color=[country_colors[country] for country in df6["Country"].unique()])
        )
    )

    # Assign frames to the figure
    fig11.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 100}, "transition": {"duration": 100}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig11.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Share of Solar Energy (%)',
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[0, df6["Share of Solar Energy (%)"].max()], ticksuffix="%"),
        template=plot_template
    )
    return fig11

st.markdown("## Share of Primary Energy Consumption from Solar")
st.text("""Measured as a percentage of primary energy""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df6), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df6["Country"].unique(), default=df6[df6["Year"] == df6["Year"].max()].sort_values(by="Share of Solar Energy (%)",  ascending=False).head(5)["Country"].tolist())
    df6_selected = df6[df6["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_bar_chart(df6_selected), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")


# -------------------------------------------------------------------------------------
# Installed Solar Capacity
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df7 = pd.read_csv("https://ourworldindata.org/grapher/installed-solar-pv-capacity.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df7=df7[df7["Code"].notna()]
    df7=df7[df7["Entity"]!="World"]
    df7=df7[df7["solar__total_gw"]!=0]
    df7 = df7.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df7.rename(columns={"Entity":"Country","solar__total_gw":"Installed Solar Capacity (GW)"}, inplace=True)
    return df7
df7 = fetch_and_clean_data()
years = sorted(df7["Year"].unique())
countries = df7["Country"].unique()

def create_choropleth_map(df7):
    fig12 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df7[df7['Year'] == year]['Code'],
                    z=df7[df7['Year'] == year]['Installed Solar Capacity (GW)'],
                    colorscale="ylorrd",
                    zmin=df7["Installed Solar Capacity (GW)"].min(), zmax=df7["Installed Solar Capacity (GW)"].max(),
                    colorbar=dict(title="Installed Solar Capacity (GW)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Installed Solar Capacity:</b> %{z:.2f} GW<extra></extra>",
                    customdata=df7[df7['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig12.add_trace(
        go.Choropleth(
            locations=df7[df7['Year'] == years[-1]]['Code'],
                    z=df7[df7['Year'] == years[-1]]['Installed Solar Capacity (GW)'],
                    colorscale="ylorrd",
                    zmin=df7["Installed Solar Capacity (GW)"].min(), zmax=df7["Installed Solar Capacity (GW)"].max(),
                    colorbar=dict(title="Installed Solar Capacity (GW)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Installed Solar Capacity:</b> %{z:.2f} GW<extra></extra>",
                    customdata=df7[df7['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig12.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig12.frames = frames

    return fig12

country_colors = {country: px.colors.qualitative.Prism[i % len(px.colors.qualitative.Prism)]
                  for i, country in enumerate(df7["Country"].unique())}

def create_bar_chart(df7):
    fig13 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Bar(
                   x=df7["Country"].unique(),
                   y=[df7[(df7["Country"] == country) & (df7["Year"] <= year)]["Installed Solar Capacity (GW)"].max()
                    for country in df7["Country"].unique()],  # Only update the height
                    hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Installed Solar Capacity: %{y:.2f} GW<extra></extra>",  # Hover label with year
                    customdata=[year] * len(df7["Country"].unique()),  # Add year to customdata
                    marker=dict(color=[country_colors[country] for country in df7["Country"].unique()]) 
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Add initial trace
    fig13.add_trace(
        go.Bar(
            x=df7["Country"].unique(),
            y=[df7[(df7["Country"] == country) & (df7["Year"] <= years[-1])]["Installed Solar Capacity (GW)"].max()
               for country in df7["Country"].unique()],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Installed Solar Capacity: %{y:.2f} GW<extra></extra>",  # Hover label with year
            customdata=[years[-1]] * len(df7["Country"].unique()),  # Add year to customdata
            marker=dict(color=[country_colors[country] for country in df7["Country"].unique()])
            )
        )

    # Assign frames to the figure
    fig13.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 50}, "transition": {"duration": 50}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig13.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Installed Solar Capacity (GW)',
        height=600,
        yaxis=dict(range=[df7["Installed Solar Capacity (GW)"].min(), df7["Installed Solar Capacity (GW)"].max()], ticksuffix=" GW"),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        template=plot_template
    )
    return fig13

st.markdown("## Installed Solar Capacity (GW)")
st.text("""Cumulative installed solar capacity, measured in gigawatts (GW).""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df7), use_container_width=True)
    st.caption("Data Source: IRENA (2024) – processed by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df7["Country"].unique(), default=df7.groupby("Country")["Installed Solar Capacity (GW)"].sum().nlargest(10).index.tolist())
    df7_selected = df7[df7["Country"].isin(selected_countries)]
    st.plotly_chart(create_bar_chart(df7_selected), use_container_width=True)
    st.caption("Data Source: IRENA (2024) – processed by Our World in Data")

# -------------------------------------------------------------------------------------
# Share of Electricity Production from Solar
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df8 = pd.read_csv("https://ourworldindata.org/grapher/share-electricity-solar.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df8=df8[df8["Code"].notna()]
    df8=df8[df8["Code"]!="COK"]
    df8=df8[df8["Entity"]!="World"]
    df8=df8[df8["solar_share_of_electricity__pct"]!=0]
    df8 = df8.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df8.rename(columns={"Entity":"Country","solar_share_of_electricity__pct":"Share of Solar in Electricity (%)"}, inplace=True)
    return df8
df8 = fetch_and_clean_data()
years = sorted(df8["Year"].unique())
# Fill missing 2023 values with 2022 data
df8 = (
    df8.groupby("Country", group_keys=False)
    .apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), 2024)).ffill())
    .reset_index()
)

# Drop rows where Year is 2023 and the value is still NaN (no data available for 2022 or earlier)
df8 = df8.dropna(subset=["Share of Solar in Electricity (%)"])
df8 = df8.sort_values(by=["Year", "Country"]).reset_index(drop=True)

def create_choropleth_map(df8):
    fig14 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df8[df8['Year'] == year]['Code'],
                    z=df8[df8['Year'] == year]['Share of Solar in Electricity (%)'],
                    colorscale="ylorrd",
                    zmin=df8["Share of Solar in Electricity (%)"].min(), zmax=df8["Share of Solar in Electricity (%)"].max(),
                    colorbar=dict(title="Share of Solar in Electricity (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Solar in Electricity:</b> %{z:.2f}%<extra></extra>",
                    customdata=df8[df8['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig14.add_trace(
        go.Choropleth(
            locations=df8[df8['Year'] == years[-1]]['Code'],
                    z=df8[df8['Year'] == years[-1]]['Share of Solar in Electricity (%)'],
                    colorscale="ylorrd",
                    zmin=df8["Share of Solar in Electricity (%)"].min(), zmax=df8["Share of Solar in Electricity (%)"].max(),
                    colorbar=dict(title="Share of Solar in Electricity (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Solar in Electricity:</b> %{z:.2f}%<extra></extra>",
                    customdata=df8[df8['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig14.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig14.frames = frames

    return fig14

country_colors = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
                  for i, country in enumerate(df8["Country"].unique())}

def create_animated_bar_chart(df8):
    fig15 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Bar(
                    x=df8["Country"].unique(),  # Keep all countries
                    y=[df8[(df8["Country"] == country) & (df8["Year"] <= year)]["Share of Solar in Electricity (%)"].max()
                       for country in df8["Country"].unique()],  # Only update the height
                    hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Solar in Electricity: %{y:.2f}%<extra></extra>",
                    customdata=[year] * len(df8["Country"].unique()),  # Add year to customdata
                    marker=dict(color=[country_colors[country] for country in df8["Country"].unique()])
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig15.add_trace(
        go.Bar(
            x=df8["Country"].unique(),
            y=[df8[(df8["Country"] == country) & (df8["Year"] <= years[-1])]["Share of Solar in Electricity (%)"].max()
               for country in df8["Country"].unique()],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Solar in Electricity: %{y:.2f}%<extra></extra>",
            customdata=[years[-1]] * len(df8["Country"].unique()),  # Add year to customdata
            marker=dict(color=[country_colors[country] for country in df8["Country"].unique()])
        )
    )

    # Assign frames to the figure
    fig15.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 100}, "transition": {"duration": 100}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig15.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Share of Solar in Electricity (%)',
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[0,df8["Share of Solar in Electricity (%)"].max()], ticksuffix="%"),
        template=plot_template
    )
    return fig15

st.markdown("## Share of Electricity Production from Solar")
st.text("""Measured as a percentage of total electricity.""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df8), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df8["Country"].unique(), default=df8.groupby("Country")["Share of Solar in Electricity (%)"].sum().nlargest(10).index.tolist())
    df8_selected = df8[df8["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_bar_chart(df8_selected), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")


# -------------------------------------------------------------------------------------
# Wind Power Generation
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df9 = pd.read_csv("https://ourworldindata.org/grapher/wind-generation.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df9=df9[df9["Code"].notna()]
    df9=df9[df9["Entity"]!="World"]
    df9=df9[df9["wind_generation__twh"]!=0]
    df9 = df9.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df9.rename(columns={"Entity":"Country","wind_generation__twh":"Wind Generation (TWh)"}, inplace=True)

    # Fill missing 2023 values with 2022 data
    df9 = (
        df9.groupby("Country", group_keys=False)
        .apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), 2024)).ffill())
        .reset_index()
    )

    # Drop rows where Year is 2023 and the value is still NaN (no data available for 2022 or earlier)
    df9 = df9.dropna(subset=["Wind Generation (TWh)"])

    # Sort the data again
    df9 = df9.sort_values(by=["Year", "Country"]).reset_index(drop=True)
    return df9
df9 = fetch_and_clean_data()


def create_choropleth_map(df9):
    years = sorted(df9["Year"].unique())
    fig16 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df9[df9['Year'] == year]['Code'],
                    z=df9[df9['Year'] == year]['Wind Generation (TWh)'],
                    colorscale="burg",
                    zmin=df9["Wind Generation (TWh)"].min(), zmax=df9["Wind Generation (TWh)"].max(),
                    colorbar=dict(title="Wind Power Generation (TWh)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Wind Generation (TWh):</b> %{z:.2f}<extra></extra>",
                    customdata=df9[df9['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig16.add_trace(
        go.Choropleth(
            locations=df9[df9['Year'] == years[-1]]['Code'],
                    z=df9[df9['Year'] == years[-1]]['Wind Generation (TWh)'],
                    colorscale="burg",
                    zmin=df9["Wind Generation (TWh)"].min(), zmax=df9["Wind Generation (TWh)"].max(),
                    colorbar=dict(title="Wind Power Generation (TWh)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Wind Generation (TWh):</b> %{z:.2f}<extra></extra>",
                    customdata=df9[df9['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig16.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig16.frames = frames

    return fig16

def create_animated_line_chart(df9):
    fig17 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Scatter(
                    x=country_data[country_data['Year'] <= year]['Year'],
                    y=country_data[country_data['Year'] <= year]['Wind Generation (TWh)'],
                    mode='lines+markers',
                    name=country,
                    hovertemplate="<b>Country:</b> " + country + "<br>" +
                                  "<b>Year:</b> %{x}<br>" +
                                  "<b>Wind Generation (TWh):</b> %{y:.2f}<extra></extra>"
                )
                for country, country_data in df9.groupby('Country')
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Add traces for each country
    for country in df9["Country"].unique():
        country_data = df9[df9["Country"] == country]
        fig17.add_trace(
            go.Scatter(
                x=country_data["Year"],
                y=country_data["Wind Generation (TWh)"],
                mode='lines+markers',
                name=country,
                hovertemplate="<b>Country:</b> " + country + "<br>" +
                              "<b>Year:</b> %{x}<br>" +
                              "<b>Wind Generation (TWh):</b> %{y:.2f}<extra></extra>"
            )
        )

    # Assign frames to the figure
    fig17.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 50}, "transition": {"duration": 50}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig17.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        xaxis_title='Year',
        yaxis_title='Wind Power Generation',
        showlegend=True,
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[df9["Wind Generation (TWh)"].min(), df9["Wind Generation (TWh)"].max()], ticksuffix=" TWh"),
        xaxis=dict(range=[df9["Year"].min(), df9["Year"].max()])
    )
    return fig17

st.markdown("## Wind Power Generation")
st.text("""Annual electricity generation from wind is measured in terawatt-hours (TWh) per year. This includes both onshore and offshore wind sources.""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df9), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df9["Country"].unique(), default=df9.groupby("Country")["Wind Generation (TWh)"].sum().nlargest(5).index.tolist())
    df9_selected = df9[df9["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_line_chart(df9_selected), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------
# Share of Primary Energy Consumption from Wind
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df10 = pd.read_csv("https://ourworldindata.org/grapher/wind-share-energy.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df10=df10[df10["Code"].notna()]
    df10=df10[df10["Entity"]!="World"]
    df10=df10[df10["wind__pct_equivalent_primary_energy"]!=0]
    df10 = df10.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df10.rename(columns={"Entity":"Country","wind__pct_equivalent_primary_energy":"Share of Energy Consumption from Wind (%)"}, inplace=True)
    return df10
df10 = fetch_and_clean_data()

def create_choropleth_map(df10):
    years = sorted(df10["Year"].unique())
    fig18 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df10[df10['Year'] == year]['Code'],
                    z=df10[df10['Year'] == year]['Share of Energy Consumption from Wind (%)'],
                    colorscale="burg",
                    zmin=df10["Share of Energy Consumption from Wind (%)"].min(), zmax=df10["Share of Energy Consumption from Wind (%)"].max(),
                    colorbar=dict(title="Share of Energy Consumption from Wind (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Energy Consumption from Wind:</b> %{z:.2f}%<extra></extra>",
                    customdata=df10[df10['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig18.add_trace(
        go.Choropleth(
            locations=df10[df10['Year'] == years[-1]]['Code'],
                    z=df10[df10['Year'] == years[-1]]['Share of Energy Consumption from Wind (%)'],
                    colorscale="burg",
                    zmin=df10["Share of Energy Consumption from Wind (%)"].min(), zmax=df10["Share of Energy Consumption from Wind (%)"].max(),
                    colorbar=dict(title="Share of Energy Consumption from Wind (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Energy Consumption from Wind:</b> %{z:.2f}%<extra></extra>",
                    customdata=df10[df10['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig18.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig18.frames = frames

    return fig18

country_colors = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
                  for i, country in enumerate(df10["Country"].unique())}

def create_animated_bar_chart(df10):
    fig19 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Bar(
                    x=df10["Country"].unique(),
                    y=[df10[(df10["Country"] == country) & (df10["Year"] <= year)]["Share of Energy Consumption from Wind (%)"].max()
                       for country in df10["Country"].unique()],  # Only update the height
                    hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Energy Consumption from Wind: %{y:.2f}%<extra></extra>",  # Hover label with year
                    customdata=[year] * len(df10["Country"].unique()),  # Add year to customdata
                    marker=dict(color=[country_colors[country] for country in df10["Country"].unique()])
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig19.add_trace(
        go.Bar(
            x=df10["Country"].unique(),
            y=[df10[(df10["Country"] == country) & (df10["Year"] <= years[-1])]["Share of Energy Consumption from Wind (%)"].max()
               for country in df10["Country"].unique()],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Energy Consumption from Wind: %{y:.2f}%<extra></extra>",  # Hover label with year
            customdata=[years[-1]] * len(df10["Country"].unique()),  # Add year to customdata
            marker=dict(color=[country_colors[country] for country in df10["Country"].unique()])
        )
    )

    # Assign frames to the figure
    fig19.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 100}, "transition": {"duration": 100}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig19.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Share of Energy Consumption from Wind (%)',
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[df10["Share of Energy Consumption from Wind (%)"].min(), df10["Share of Energy Consumption from Wind (%)"].max()], ticksuffix="%"),
        template=plot_template
    )
    return fig19

st.markdown("## Share of Primary Energy Consumption from Wind")
st.text("""Measured as a percentage of primary energy""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df10), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df10["Country"].unique(), default=df10.groupby("Country")["Share of Energy Consumption from Wind (%)"].sum().nlargest(5).index.tolist())
    df10_selected = df10[df10["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_bar_chart(df10_selected), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")


# -------------------------------------------------------------------------------------
# Installed Wind Capacity
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df11 = pd.read_csv("https://ourworldindata.org/grapher/cumulative-installed-wind-energy-capacity-gigawatts.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df11=df11[df11["Code"].notna()]
    df11=df11[df11["Entity"]!="World"]
    df11=df11[df11["wind__total_gw"]!=0]
    df11 = df11.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df11.rename(columns={"Entity":"Country","wind__total_gw":"Installed Wind Capacity (GW)"}, inplace=True)
    return df11
df11 = fetch_and_clean_data()
countries = df11["Country"].unique()

def create_choropleth_map(df11):
    years = sorted(df11["Year"].unique())
    fig20 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df11[df11['Year'] == year]['Code'],
                    z=df11[df11['Year'] == year]['Installed Wind Capacity (GW)'],
                    colorscale="burg",
                    zmin=df11["Installed Wind Capacity (GW)"].min(), zmax=df11["Installed Wind Capacity (GW)"].max(),
                    colorbar=dict(title="Installed Wind Capacity (GW)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Installed Wind Capacity:</b> %{z:.2f} GW<extra></extra>",
                    customdata=df11[df11['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig20.add_trace(
        go.Choropleth(
            locations=df11[df11['Year'] == years[-1]]['Code'],
                    z=df11[df11['Year'] == years[-1]]['Installed Wind Capacity (GW)'],
                    colorscale="burg",
                    zmin=df11["Installed Wind Capacity (GW)"].min(), zmax=df11["Installed Wind Capacity (GW)"].max(),
                    colorbar=dict(title="Installed Wind Capacity (GW)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Installed Wind Capacity:</b> %{z:.2f} GW<extra></extra>",
                    customdata=df11[df11['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig20.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig20.frames = frames

    return fig20

country_colors = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
                  for i, country in enumerate(df11["Country"].unique())}

def create_bar_chart(df11):
    fig21 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Bar(
                   x=df11["Country"].unique(),
                   y=[df11[(df11["Country"] == country) & (df11["Year"] <= year)]["Installed Wind Capacity (GW)"].max()
                    for country in df11["Country"].unique()],  # Only update the height
                    hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Installed Wind Capacity: %{y:.2f} GW<extra></extra>",  # Hover label with year
                    customdata=[year] * len(df11["Country"].unique()),  # Add year to customdata
                    marker=dict(color=[country_colors[country] for country in df11["Country"].unique()]) 
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Add initial trace
    fig21.add_trace(
        go.Bar(
            x=df11["Country"].unique(),
            y=[df11[(df11["Country"] == country) & (df11["Year"] <= years[-1])]["Installed Wind Capacity (GW)"].max()
               for country in df11["Country"].unique()],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Installed Wind Capacity: %{y:.2f} GW<extra></extra>",  # Hover label with year
            customdata=[years[-1]] * len(df11["Country"].unique()),  # Add year to customdata
            marker=dict(color=[country_colors[country] for country in df11["Country"].unique()])
            )
        )

    # Assign frames to the figure
    fig21.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 50}, "transition": {"duration": 50}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig21.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Installed Wind Capacity (GW)',
        height=600,
        yaxis=dict(range=[df11["Installed Wind Capacity (GW)"].min(), df11["Installed Wind Capacity (GW)"].max()], ticksuffix=" GW"),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
    )
    return fig21

st.markdown("## Installed Wind Capacity (GW)")
st.text("""Cumulative installed wind energy capacity including both onshore and offshore wind sources, measured in gigawatts (GW).""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df11), use_container_width=True)
    st.caption("Data Source: IRENA (2024) – processed by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df11["Country"].unique(), default=df11.groupby("Country")["Installed Wind Capacity (GW)"].sum().nlargest(10).index.tolist())
    df11_selected = df11[df11["Country"].isin(selected_countries)]
    st.plotly_chart(create_bar_chart(df11_selected), use_container_width=True)
    st.caption("Data Source: IRENA (2024) – processed by Our World in Data")

# -------------------------------------------------------------------------------------
# Share of Electricity Production from Wind
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df12 = pd.read_csv("https://ourworldindata.org/grapher/share-electricity-wind.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df12=df12[df12["Code"].notna()]
    df12=df12[df12["Entity"]!="World"]
    df12=df12[df12["wind_share_of_electricity__pct"]!=0]
    df12 = df12.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df12.rename(columns={"Entity":"Country","wind_share_of_electricity__pct":"Share of Wind in Electricity Production (%)"}, inplace=True)
    return df12
df12 = fetch_and_clean_data()
years = sorted(df12["Year"].unique())
# Fill missing 2023 values with 2022 data
df12 = (
    df12.groupby("Country", group_keys=False)
    .apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), 2024)).ffill())
    .reset_index()
)

# Drop rows where Year is 2023 and the value is still NaN (no data available for 2022 or earlier)
df12 = df12.dropna(subset=["Share of Wind in Electricity Production (%)"])
df12 = df12.sort_values(by=["Year", "Country"]).reset_index(drop=True)

def create_choropleth_map(df12):
    fig22 = go.Figure()
    
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df12[df12['Year'] == year]['Code'],
                    z=df12[df12['Year'] == year]['Share of Wind in Electricity Production (%)'],
                    colorscale="burg",
                    zmin=df12["Share of Wind in Electricity Production (%)"].min(), zmax=df12["Share of Wind in Electricity Production (%)"].max(),
                    colorbar=dict(title="Share of Wind in Electricity Production (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Wind in Electricity Production:</b> %{z:.2f}%<extra></extra>",
                    customdata=df12[df12['Year'] == year][['Country', 'Year']].values,
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig22.add_trace(
        go.Choropleth(
            locations=df12[df12['Year'] == years[-1]]['Code'],
            z=df12[df12['Year'] == years[-1]]['Share of Wind in Electricity Production (%)'],
            colorscale="burg",
            zmin=df12["Share of Wind in Electricity Production (%)"].min(), zmax=df12["Share of Wind in Electricity Production (%)"].max(),
            colorbar=dict(title="Share of Wind in Electricity Production (%)\n"),
            hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                          "<b>Year:</b> %{customdata[1]}<br>" +
                          "<b>Share of Wind in Electricity Production:</b> %{z:.2f}%<extra></extra>",
            customdata=df12[df12['Year'] == years[-1]][['Country', 'Year']].values
        )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig22.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig22.frames = frames

    return fig22

country_colors = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
                  for i, country in enumerate(df12["Country"].unique())}

def create_animated_bar_chart(df12):
    fig23 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Bar(
                    x=df12["Country"].unique(),  # Keep all countries
                    y=[df12[(df12["Country"] == country) & (df12["Year"] <= year)]["Share of Wind in Electricity Production (%)"].max()
                       for country in df12["Country"].unique()],  # Only update the height
                    hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Wind in Electricity Production: %{y:.2f}%<extra></extra>",
                    customdata=[year] * len(df12["Country"].unique()),  # Add year to customdata
                    marker=dict(color=[country_colors[country] for country in df12["Country"].unique()])
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig23.add_trace(
        go.Bar(
            x=df12["Country"].unique(),
            y=[df12[(df12["Country"] == country) & (df12["Year"] <= years[-1])]["Share of Wind in Electricity Production (%)"].max()
               for country in df12["Country"].unique()],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Wind in Electricity Production: %{y:.2f}%<extra></extra>",
            customdata=[years[-1]] * len(df12["Country"].unique()),  # Add year to customdata
            marker=dict(color=[country_colors[country] for country in df12["Country"].unique()])
        )
    )

    # Assign frames to the figure
    fig23.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 100}, "transition": {"duration": 100}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig23.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Share of Wind in Electricity Production (%)',
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[df12["Share of Wind in Electricity Production (%)"].min(), df12["Share of Wind in Electricity Production (%)"].max()], ticksuffix="%"),
        template=plot_template
    )
    return fig23

st.markdown("## Share of Electricity Production from Wind")
st.text("""Measured as a percentage of total electricity.""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df12), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df12["Country"].unique(), default=df12.groupby("Country")["Share of Wind in Electricity Production (%)"].sum().nlargest(10).index.tolist())
    df12_selected = df12[df12["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_bar_chart(df12_selected), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------
# Hydro Power Generation
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df13 = pd.read_csv("https://ourworldindata.org/grapher/hydropower-consumption.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df13=df13[df13["Code"].notna()]
    df13=df13[df13["Entity"]!="World"]
    df13=df13[df13["hydro_generation__twh"]!=0]
    df13 = df13.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df13.rename(columns={"Entity":"Country","hydro_generation__twh":"Hydro Generation (TWh)"}, inplace=True)
    return df13
df13 = fetch_and_clean_data()

# Fill missing 2023 values with 2022 data
df13 = (
    df13.groupby("Country", group_keys=False)
    .apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), 2024)).ffill())
    .reset_index()
)

# Drop rows where Year is 2023 and the value is still NaN (no data available for 2022 or earlier)
df13 = df13.dropna(subset=["Hydro Generation (TWh)"])

# Sort the data again
df13 = df13.sort_values(by=["Year", "Country"]).reset_index(drop=True)


def create_choropleth_map(df13):
    years = sorted(df13["Year"].unique())
    fig24 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df13[df13['Year'] == year]['Code'],
                    z=df13[df13['Year'] == year]['Hydro Generation (TWh)'],
                    colorscale="blues",
                    zmin=df13["Hydro Generation (TWh)"].min(), zmax=df13["Hydro Generation (TWh)"].max(),
                    colorbar=dict(title="Hydro Power Generation (TWh)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Hydro Generation (TWh):</b> %{z:.2f}<extra></extra>",
                    customdata=df13[df13['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig24.add_trace(
        go.Choropleth(
            locations=df13[df13['Year'] == years[-1]]['Code'],
                    z=df13[df13['Year'] == years[-1]]['Hydro Generation (TWh)'],
                    colorscale="blues",
                    zmin=df13["Hydro Generation (TWh)"].min(), zmax=df13["Hydro Generation (TWh)"].max(),
                    colorbar=dict(title="Hydro Power Generation (TWh)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Hydro Generation (TWh):</b> %{z:.2f}<extra></extra>",
                    customdata=df13[df13['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig24.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig24.frames = frames

    return fig24

def create_animated_line_chart(df13):
    fig25 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Scatter(
                    x=country_data[country_data['Year'] <= year]['Year'],
                    y=country_data[country_data['Year'] <= year]['Hydro Generation (TWh)'],
                    mode='lines',
                    name=country,
                    hovertemplate="<b>Country:</b> " + country + "<br>" +
                                  "<b>Year:</b> %{x}<br>" +
                                  "<b>Hydro Generation (TWh):</b> %{y:.2f}<extra></extra>"
                )
                for country, country_data in df13.groupby('Country')
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Add traces for each country
    for country in df13["Country"].unique():
        country_data = df13[df13["Country"] == country]
        fig25.add_trace(
            go.Scatter(
                x=country_data["Year"],
                y=country_data["Hydro Generation (TWh)"],
                mode='lines',
                name=country,
                hovertemplate="<b>Country:</b> " + country + "<br>" +
                              "<b>Year:</b> %{x}<br>" +
                              "<b>Hydro Generation (TWh):</b> %{y:.2f}<extra></extra>"
            )
        )

    # Assign frames to the figure
    fig25.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 50}, "transition": {"duration": 50}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig25.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        xaxis_title='Year',
        yaxis_title='Hydro Power Generation',
        showlegend=True,
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[df13["Hydro Generation (TWh)"].min(), df13["Hydro Generation (TWh)"].max()], ticksuffix=" TWh"),
        xaxis=dict(range=[df13["Year"].min(), df13["Year"].max()])
    )
    return fig25

st.markdown("## Hydro Power Generation")
st.text("""Annual hydropower generation is measured in terawatt-hours (TWh).""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df13), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df13["Country"].unique(), default=df13.groupby("Country")["Hydro Generation (TWh)"].sum().nlargest(5).index.tolist())
    df13_selected = df13[df13["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_line_chart(df13_selected), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------
# Share of Primary Energy Consumption from Hydroelectric Power
# -------------------------------------------------------------------------------------

# # Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df14 = pd.read_csv("https://ourworldindata.org/grapher/hydro-share-energy.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df14=df14[df14["Code"].notna()]
    df14=df14[df14["Entity"]!="World"]
    df14=df14[df14["hydro__pct_equivalent_primary_energy"]!=0]
    df14 = df14.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df14.rename(columns={"Entity":"Country","hydro__pct_equivalent_primary_energy":"Share of Energy Consumption from Hydro (%)"}, inplace=True)
    return df14
df14 = fetch_and_clean_data()

# Fill missing 2023 values with 2022 data
df14 = (
    df14.groupby("Country", group_keys=False)
    .apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), 2024)).ffill())
    .reset_index()
)

# Drop rows where Year is 2023 and the value is still NaN (no data available for 2022 or earlier)
df14 = df14.dropna(subset=["Share of Energy Consumption from Hydro (%)"])

# Sort the data again
df14 = df14.sort_values(by=["Year", "Country"]).reset_index(drop=True)


def create_choropleth_map(df14):
    years = sorted(df14["Year"].unique())
    fig26 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df14[df14['Year'] == year]['Code'],
                    z=df14[df14['Year'] == year]['Share of Energy Consumption from Hydro (%)'],
                    colorscale="blues",
                    zmin=df14["Share of Energy Consumption from Hydro (%)"].min(), zmax=df14["Share of Energy Consumption from Hydro (%)"].max(),
                    colorbar=dict(title="Share of Energy Consumption from Hydro (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Energy Consumption from Hydro:</b> %{z:.2f}%<extra></extra>",
                    customdata=df14[df14['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig26.add_trace(
        go.Choropleth(
            locations=df14[df14['Year'] == years[-1]]['Code'],
                    z=df14[df14['Year'] == years[-1]]['Share of Energy Consumption from Hydro (%)'],
                    colorscale="blues",
                    zmin=df14["Share of Energy Consumption from Hydro (%)"].min(), zmax=df14["Share of Energy Consumption from Hydro (%)"].max(),
                    colorbar=dict(title="Share of Energy Consumption from Hydro (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Energy Consumption from Hydro:</b> %{z:.2f}%<extra></extra>",
                    customdata=df14[df14['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig26.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig26.frames = frames

    return fig26

country_colors = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
                  for i, country in enumerate(df14["Country"].unique())}

def create_animated_bar_chart(df14):
    fig26 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Bar(
                    x=df14["Country"].unique(),
                    y=[
                    df14.loc[(df14["Country"] == country) & (df14["Year"] == year), 
                             "Share of Energy Consumption from Hydro (%)"].values[0]
                    if not df14.loc[(df14["Country"] == country) & (df14["Year"] == year),
                                    "Share of Energy Consumption from Hydro (%)"].empty
                    else 0  # Handle missing values
                    for country in df14["Country"].unique()
                    ],
                    hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Energy Consumption from Hydro: %{y:.2f}%<extra></extra>",  # Hover label with year
                    customdata=[year] * len(df14["Country"].unique()),  # Add year to customdata
                    marker=dict(color=[country_colors[country] for country in df14["Country"].unique()])
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig26.add_trace(
        go.Bar(
            x=df14["Country"].unique(),
            y=[
            df14.loc[(df14["Country"] == country) & (df14["Year"] == years[-1]), 
                     "Share of Energy Consumption from Hydro (%)"].values[0]
            if not df14.loc[(df14["Country"] == country) & (df14["Year"] == years[-1]),
                            "Share of Energy Consumption from Hydro (%)"].empty 
            else 0  # Handle missing values
            for country in df14["Country"].unique()
            ],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Energy Consumption from Hydro: %{y:.2f}%<extra></extra>",  # Hover label with year
            customdata=[years[-1]] * len(df14["Country"].unique()),  # Add year to customdata
            marker=dict(color=[country_colors[country] for country in df14["Country"].unique()])
        )
    )

    # Assign frames to the figure
    fig26.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 100}, "transition": {"duration": 100}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig26.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Share of Energy Consumption from Hydro (%)',
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[0, df14["Share of Energy Consumption from Hydro (%)"].max()], ticksuffix="%"),
        template=plot_template
    )
    return fig26

st.markdown("## Share of Primary Energy Consumption from Hydro")
st.text("""Measured as a percentage of the total primary energy.""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df14), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df14["Country"].unique(), default=df14.groupby("Country")["Share of Energy Consumption from Hydro (%)"].sum().nlargest(5).index.tolist())
    df14_selected = df14[df14["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_bar_chart(df14_selected), use_container_width=True)
    st.caption("Data Source: Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------
# Share of Electricity Production from Hydro
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df15 = pd.read_csv("https://ourworldindata.org/grapher/share-electricity-hydro.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df15=df15[df15["Code"].notna()]
    df15=df15[df15["Entity"]!="World"]
    df15=df15[df15["hydro_share_of_electricity__pct"]!=0]
    df15 = df15.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df15.rename(columns={"Entity":"Country","hydro_share_of_electricity__pct":"Share of Electricity Production from Hydro (%)"}, inplace=True)
    return df15
df15 = fetch_and_clean_data()
years = sorted(df15["Year"].unique())

# Fill missing 2023 values with 2022 data
df15 = (
    df15.groupby("Country", group_keys=False)
    .apply(lambda group: group.set_index("Year").reindex(range(group["Year"].min(), 2024)).ffill())
    .reset_index()
)

# Drop rows where Year is 2023 and the value is still NaN (no data available for 2022 or earlier)
df15 = df15.dropna(subset=["Share of Electricity Production from Hydro (%)"])
df15 = df15.sort_values(by=["Year", "Country"]).reset_index(drop=True)

def create_choropleth_map(df15):
    years = sorted(df15["Year"].unique())
    fig27 = go.Figure()
    
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df15[df15['Year'] == year]['Code'],
                    z=df15[df15['Year'] == year]['Share of Electricity Production from Hydro (%)'],
                    colorscale="blues",
                    zmin=df15["Share of Electricity Production from Hydro (%)"].min(), zmax=df15["Share of Electricity Production from Hydro (%)"].max(),
                    colorbar=dict(title="Share of Electricity Production from Hydro (%)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Share of Electricity Production from Hydro:</b> %{z:.2f}%<extra></extra>",
                    customdata=df15[df15['Year'] == year][['Country', 'Year']].values,
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig27.add_trace(
        go.Choropleth(
            locations=df15[df15['Year'] == years[-1]]['Code'],
            z=df15[df15['Year'] == years[-1]]['Share of Electricity Production from Hydro (%)'],
            colorscale="blues",
            zmin=df15["Share of Electricity Production from Hydro (%)"].min(), zmax=df15["Share of Electricity Production from Hydro (%)"].max(),
            colorbar=dict(title="Share of Electricity Production from Hydro (%)\n"),
            hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                          "<b>Year:</b> %{customdata[1]}<br>" +
                          "<b>Share of Electricity Production from Hydro:</b> %{z:.2f}%<extra></extra>",
            customdata=df15[df15['Year'] == years[-1]][['Country', 'Year']].values
        )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig27.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig27.frames = frames

    return fig27

country_colors = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
                  for i, country in enumerate(df15["Country"].unique())}

def create_animated_bar_chart(df15):
    fig28 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Bar(
                    x=df15["Country"].unique(),  # Keep all countries
                    y=[
                    df15.loc[(df15["Country"] == country) & (df15["Year"] == year), 
                             "Share of Electricity Production from Hydro (%)"].values[0]
                    if not df15.loc[(df15["Country"] == country) & (df15["Year"] == year),
                                    "Share of Electricity Production from Hydro (%)"].empty 
                    else 0  # Handle missing values
                    for country in df15["Country"].unique()
                    ],
                    hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Electricity Production from Hydro: %{y:.2f}%<extra></extra>",
                    customdata=[year] * len(df15["Country"].unique()),  # Add year to customdata
                    marker=dict(color=[country_colors[country] for country in df15["Country"].unique()])
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig28.add_trace(
        go.Bar(
            x=df15["Country"].unique(),
            y=[
            df15.loc[(df15["Country"] == country) & (df15["Year"] == years[-1]), 
                     "Share of Electricity Production from Hydro (%)"].values[0]
            if not df15.loc[(df15["Country"] == country) & (df15["Year"] == years[-1]),
                            "Share of Electricity Production from Hydro (%)"].empty 
            else 0  # Handle missing values
            for country in df15["Country"].unique()
            ],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Share of Electricity Production from Hydro: %{y:.2f}%<extra></extra>",
            customdata=[years[-1]] * len(df15["Country"].unique()),  # Add year to customdata
            marker=dict(color=[country_colors[country] for country in df15["Country"].unique()])
        )
    )

    # Assign frames to the figure
    fig28.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 100}, "transition": {"duration": 100}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig28.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Share of Electricity Production from Hydro (%)',
        height=600,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
        yaxis=dict(range=[0, df15["Share of Electricity Production from Hydro (%)"].max()], ticksuffix="%"),
        template=plot_template
    )
    return fig28

st.markdown("## Share of Electricity Production from Hydro")
st.text("""Measured as a percentage of total electricity.""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df15), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df15["Country"].unique(), default=df15.groupby("Country")["Share of Electricity Production from Hydro (%)"].sum().nlargest(10).index.tolist())
    df15_selected = df15[df15["Country"].isin(selected_countries)]
    st.plotly_chart(create_animated_bar_chart(df15_selected), use_container_width=True)
    st.caption("Data Source: Ember (2024); Energy Institute - Statistical Review of World Energy (2024) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------
# Installed Geothermal Capacity
# -------------------------------------------------------------------------------------

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df16 = pd.read_csv("https://ourworldindata.org/grapher/installed-geothermal-capacity.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    # Clean the data
    df16=df16[df16["Code"].notna()]
    df16=df16[df16["Entity"]!="World"]
    df16=df16[df16["geothermal__total"]!=0]
    df16 = df16.sort_values(by=["Year", "Entity"]).reset_index(drop=True)
    df16.rename(columns={"Entity":"Country","geothermal__total":"Installed Geothermal Capacity (MW)"}, inplace=True)
    return df16
df16 = fetch_and_clean_data()

years = sorted(df16["Year"].unique())
countries = df16["Country"].unique()

def create_choropleth_map(df16):
    fig29 = go.Figure()
    # Create frames for animation
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(
                    locations=df16[df16['Year'] == year]['Code'],
                    z=df16[df16['Year'] == year]['Installed Geothermal Capacity (MW)'],
                    colorscale="reds",
                    zmin=df16["Installed Geothermal Capacity (MW)"].min(), zmax=df16["Installed Geothermal Capacity (MW)"].max(),
                    colorbar=dict(title="Installed Geothermal Capacity (MW)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Installed Geothermal Capacity:</b> %{z:.2f} MW<extra></extra>",
                    customdata=df16[df16['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame
    fig29.add_trace(
        go.Choropleth(
            locations=df16[df16['Year'] == years[-1]]['Code'],
                    z=df16[df16['Year'] == years[-1]]['Installed Geothermal Capacity (MW)'],
                    colorscale="reds",
                    zmin=df16["Installed Geothermal Capacity (MW)"].min(), zmax=df16["Installed Geothermal Capacity (MW)"].max(),
                    colorbar=dict(title="Installed Geothermal Capacity (MW)\n"),
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" +
                                  "<b>Year:</b> %{customdata[1]}<br>" +
                                  "<b>Installed Geothermal Capacity:</b> %{z:.2f} MW<extra></extra>",
                    customdata=df16[df16['Year'] == years[-1]][['Country', 'Year']].values
                )
    )

    # Add animation controls
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 100}}],
             label=str(year))
        for year in years
    ]

    fig29.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
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
    fig29.frames = frames

    return fig29

country_colors = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
                  for i, country in enumerate(df16["Country"].unique())}

def create_bar_chart(df16):
    fig30 = go.Figure()

    # Generate frames for each year (show data up to that year)
    frames = [
        go.Frame(
            name=f"frame_{year}",
            data=[
                go.Bar(
                   x=df16["Country"].unique(),
                   y=[
                    df16.loc[(df16["Country"] == country) & (df16["Year"] == year), 
                             "Installed Geothermal Capacity (MW)"].values[0]
                    if not df16.loc[(df16["Country"] == country) & (df16["Year"] == year), 
                                    "Installed Geothermal Capacity (MW)"].empty
                    else 0  # Handle missing values
                    for country in df16["Country"].unique()
                    ],
                    hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Installed Geothermal Capacity: %{y:.2f} MW<extra></extra>",  # Hover label with year
                    customdata=[year] * len(df16["Country"].unique()),  # Add year to customdata
                    marker=dict(color=[country_colors[country] for country in df16["Country"].unique()]) 
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Add initial trace
    fig30.add_trace(
        go.Bar(
            x=df16["Country"].unique(),
            y=[
            df16.loc[(df16["Country"] == country) & (df16["Year"] == years[-1]), 
                     "Installed Geothermal Capacity (MW)"].values[0]
            if not df16.loc[(df16["Country"] == country) & (df16["Year"] == years[-1]), 
                            "Installed Geothermal Capacity (MW)"].empty 
            else 0  # Handle missing values
            for country in df16["Country"].unique()
            ],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Installed Geothermal Capacity: %{y:.2f} MW<extra></extra>",  # Hover label with year
            customdata=[years[-1]] * len(df16["Country"].unique()),  # Add year to customdata
            marker=dict(color=[country_colors[country] for country in df16["Country"].unique()])
            )
        )

    # Assign frames to the figure
    fig30.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 100}, "transition": {"duration": 100}}], 
                  label=str(year)) for year in years]

    # Update layout with slider, buttons, and other settings
    fig30.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Installed Geothermal Capacity (MW)',
        height=600,
        yaxis=dict(range=[0, df16["Installed Geothermal Capacity (MW)"].max()], ticksuffix=" MW"),
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: "), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),
    )
    return fig30

st.markdown("## Installed Geothermal Capacity (MW)")
st.text("""Cumulative installed capacity of geothermal energy, measured in megawatts.""")

tab1, tab2 = st.tabs(["Map", "Chart"])
with tab1:
    st.plotly_chart(create_choropleth_map(df16), use_container_width=True)
    st.caption("Data Source: IRENA (2024) – processed by Our World in Data")
with tab2:
    selected_countries = st.multiselect("Select Countries", df16["Country"].unique(), default=df16.groupby("Country")["Installed Geothermal Capacity (MW)"].sum().nlargest(5).index.tolist())
    df16_selected = df16[df16["Country"].isin(selected_countries)]
    st.plotly_chart(create_bar_chart(df16_selected), use_container_width=True)
    st.caption("Data Source: IRENA (2024) – processed by Our World in Data")

# -------------------------------------------------------------------------------------
# Global Power Plant Database
# -------------------------------------------------------------------------------------

st.markdown("## Major Renewable Energy Power Plants")
st.text("""This map highlights major power plants worldwide, showcasing their locations, capacities, and primary energy sources to provide insights into the global energy landscape.""")

# Reading the global power plant database
@st.cache_data
def fetch_and_clean_data():
    df1 = pd.read_csv("global_power_plant_database.csv")

    df1 = df1.drop("gppd_idnr", axis=1)
    df1 = df1.drop(columns=df1.loc[:, "other_fuel1":"estimated_generation_note_2017"].columns)
    df1 = df1[df1["primary_fuel"].isin(["Solar", "Wind", "Nuclear", "Geothermal", "Wave and Tidal", "Hydro"])]
    df1["Plant Capacity (GW)"] = df1["capacity_mw"]/1000
    df1 = df1.rename(columns={"country": "Country Code", "country_long": "Country", "name": "Plant Name", "capacity_mw": "Plant Capacity (MW)", "latitude": "Latitude", "longitude": "Longitude", "primary_fuel": "Primary Fuel"})

    # Filtering dataset to keep 
    df1 = df1.drop(df1[(df1["Primary Fuel"] == "Solar") & (df1["Plant Capacity (MW)"] < 60)].index)
    df1 = df1.drop(df1[(df1["Primary Fuel"] == "Wind") & (df1["Plant Capacity (MW)"] < 200)].index)
    df1 = df1.drop(df1[(df1["Primary Fuel"] == "Hydro") & (df1["Plant Capacity (MW)"] < 500)].index)
    return df1
df1 = fetch_and_clean_data()

selected_type=st.multiselect("Select Plant Type: ", df1["Primary Fuel"].unique(), default=["Solar"])
filtered = df1[df1["Primary Fuel"].isin(selected_type)]

capacity_range = st.slider(
    "Select a range of plant capacity (GW):",
    filtered["Plant Capacity (GW)"].min(),
    filtered["Plant Capacity (GW)"].max(),
    (filtered["Plant Capacity (GW)"].min(), filtered["Plant Capacity (GW)"].max())  # Default range
)
    
df1_filtered = filtered[(filtered["Plant Capacity (GW)"] >= capacity_range[0]) & (filtered["Plant Capacity (GW)"] <= capacity_range[1])]

def get_icon(fuel_type):
    if fuel_type=="Solar":
        return "solar-panel"
    elif fuel_type=="Wind":
        return "fan"
    elif fuel_type=="Nuclear":
        return "atom"
    elif fuel_type=="Geothermal":
        return "volcano"
    elif fuel_type=="Wave and Tidal":
        return "house-tsunami"
    elif fuel_type=="Hydro":
        return "house-flood-water-circle-arrow-right"
    
def create_map(df1_filtered):
    fig1 = folium.Map(location=[0,0], zoom_start=3)
    for i, row in df1_filtered.iterrows():
        folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f"Plant: {row['Plant Name']}<br><br>"
                  f"Power Plant Type: {row['Primary Fuel']}<br><br>"
                  f"Capacity in Megawatt: {row['Plant Capacity (MW)']:.2f}<br><br>"
                  f"Country: {row['Country']}",    
        tooltip=row["Plant Name"],
        icon=folium.Icon(icon=get_icon(row["Primary Fuel"]), prefix="fa")
                  ).add_to(fig1)
    return fig1

# Generate figure
fig1 = create_map(df1_filtered)

# Display in Streamlit
st_folium(fig1, use_container_width=True)
st.caption("Data Source: Global Energy Observatory et al. (2021). [Global Power Plant Database v1.3.0](https://datasets.wri.org/datasets/global-power-plant-database). License: CC BY 4.0.")
st.write("\n" * 5)
st.divider()
st.caption("Citation: Hannah Ritchie, Max Roser and Pablo Rosado (2020) - “Renewable Energy” Published online at OurWorldinData.org. Retrieved from: 'https://ourworldindata.org/renewable-energy' [Online Resource]")

