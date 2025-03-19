import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Apply Streamlit Theme
st.set_page_config(page_title="Climate Change", layout="wide")
theme = st.config.get_option("theme.base")
# Set plotly template based on theme
plot_template = "plotly_dark" if theme == "dark" else "simple_white"

st.title("Climate Change")

# -------------------------------------------------------------------------------------------------
# Global Temperature Anomalies
# -------------------------------------------------------------------------------------------------

st.markdown("## Global Temperature Anomalies")
st.text("""The deviation in a specific month's average surface temperature from the mean temperature of the same month during the period 1990-2020, measured in degrees Celsius.""")

# Fetch and clean data
@st.cache_data
def fetch_and_clean_data():
    df1 = pd.read_csv("https://ourworldindata.org/grapher/global-temperature-anomalies-by-month.csv?v=1&csvType=full&useColumnShortNames=true",
                    storage_options={'User-Agent': 'Our World In Data data fetch/1.0'})
    df1 = df1.drop("Code", axis=1).rename(columns={"Entity": "Month", "temperature_anomaly": "Temperature Anomaly"})
    df1["Year"] = df1["Year"].astype(int)
    df1 = df1.sort_values(by=["Year", "Month"]).reset_index(drop=True)
    return df1
df1 = fetch_and_clean_data()

# User input for month selection
selected_month = st.selectbox("Select a Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])

# Function to create temperature anomaly chart
def create_temperature_anomaly_chart(df, selected_month):
    filtered_df = df[df['Month'] == selected_month]
    years = sorted(filtered_df["Year"].unique())

    fig = go.Figure()
    initial_data = filtered_df[filtered_df["Year"] == years[0]]
    fig.add_trace(go.Bar(x=initial_data["Year"], y=initial_data["Temperature Anomaly"],
                         marker_color=["crimson" if v > 0 else "royalblue" for v in initial_data["Temperature Anomaly"]],
                         hovertemplate="Year: %{x} <br>Temperature Anomaly: %{y:.2f} °C", name=""))

    # Create animation frames
    frames = [
        go.Frame(
            data=[go.Bar(x=filtered_df[filtered_df["Year"] <= year]["Year"],
                         y=filtered_df[filtered_df["Year"] <= year]["Temperature Anomaly"],
                         marker_color=["crimson" if v > 0 else "royalblue" for v in filtered_df[filtered_df["Year"] <= year]["Temperature Anomaly"]],
                         hovertemplate="Year: %{x} <br>Temperature Anomaly: %{y:.2f} °C", name="")],
            name=str(year)
        ) for year in years
    ]
    fig.update(frames=frames)

    # Add animation controls
    steps = [dict(method="animate", args=[[str(year)], {"frame": {"duration": 100, "redraw": True}}], label=str(year)) for year in years]

    fig.update_layout(
        title=f"Global Temperature Anomaly for {selected_month}",
        xaxis_title="Year", yaxis_title="Temperature Anomaly (°C)",
        height=600,
        sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="Year: ", visible=True), pad=dict(t=60))],
        yaxis=dict(range=[df["Temperature Anomaly"].min(), df["Temperature Anomaly"].max()], ticksuffix=" °C"),
        xaxis=dict(tickformat="d", range=[df["Year"].min()-1, df["Year"].max()+1]),
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}], "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}], "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2
        }],
        margin=dict(t=50, b=120),
    )
    return fig

fig1 = create_temperature_anomaly_chart(df1, selected_month)
st.plotly_chart(fig1, use_container_width=True)
st.caption("Data Source: Contains modified Copernicus Climate Change Service information (2025) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------------------
# Antarctic Sea Ice Extent Trends
# -------------------------------------------------------------------------------------------------
    
st.markdown("## Antarctic Sea Ice Extent Trends Over Time")
st.text("""The minimum and maximum sea ice extent typically occur in February and September each year.""")

@st.cache_data
def fetch_and_clean_data():
    df2=pd.read_csv("https://ourworldindata.org/grapher/antarctica-sea-ice-extent.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
    df2=df2.drop(["Entity", "Code"], axis=1)
    df2 = df2.rename(columns={"antarctic_sea_ice_extent_max": "Maximum (September)","antarctic_sea_ice_extent_min": "Minimum (February)"})
    df2=df2.sort_values(by=["Year"]).reset_index(drop=True)
    return df2
df2 = fetch_and_clean_data()

def create_animated_line_chart(data):

    years = data["Year"].unique()
    # Initialize figure
    fig2 = go.Figure()

    # Add traces for both Maximum (September) and Minimum (February)
    fig2.add_trace(go.Scatter(x=data['Year'], y=data['Maximum (September)'], line=dict(color='royalblue'), mode='lines+markers', name='Maximum (September)', hovertemplate="Year: %{x} <br> Antarctic Sea Ice Extent: %{y:.2f} million km²"))
    fig2.add_trace(go.Scatter(x=data['Year'], y=data['Minimum (February)'], line=dict(color='crimson'), mode='lines+markers', name='Minimum (February)', hovertemplate="Year: %{x} <br> Antarctic Sea Ice Extent: %{y:.2f} million km²"))

    # Generate frames for each year
    frames = [go.Frame(
        name=f"frame_{year}",
        data=[
            go.Scatter(x=data['Year'][:i+1], y=data['Maximum (September)'][:i+1], mode='lines+markers', line=dict(color='royalblue'), hovertemplate="Year: %{x} <br> Antarctic Sea Ice Extent: %{y:.2f} million km²"),
            go.Scatter(x=data['Year'][:i+1], y=data['Minimum (February)'][:i+1], mode='lines+markers', line=dict(color='crimson'), hovertemplate="Year: %{x} <br> Antarctic Sea Ice Extent: %{y:2f} million km²")
        ],
        layout=dict(title=f"{year}")
    ) for i, year in enumerate(data['Year'])]

    fig2.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": "100", "redraw": True}, "transition": {"duration": "100"}}], label=str(year)) for year in data['Year']]

    # Update layout with slider, buttons, and other settings
    fig2.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        yaxis_title='Sea Ice Extent (Million km²)',
        showlegend=True, height=600,
        sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="Year: ", visible=True), pad=dict(t=60))],
        yaxis=dict(range=[data["Minimum (February)"].min(), data["Maximum (September)"].max()*1.1], ticksuffix=" million km²"),
        xaxis=dict(range=[data["Year"].min(), data["Year"].max()]),
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

    return fig2


fig2 = create_animated_line_chart(df2)

# Display the plot in Streamlit
st.plotly_chart(fig2, use_container_width=True)
st.caption("Data Source: National Snow and Ice Data Center - Sea Ice Index (2025) – with minor processing by Our World in Data")

# -------------------------------------------------------------------------------------------------
# Arctic Sea Ice Extent Trends
# -------------------------------------------------------------------------------------------------

st.markdown("## Arctic Sea Ice Extent Trends Over Time")
st.text("""The minimum and maximum sea ice extent typically occur in September and February each year.""")

@st.cache_data
def fetch_and_clean_data():
    df3 = pd.read_csv("https://ourworldindata.org/grapher/arctic-sea-ice.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
    df3=df3.drop(["Entity", "Code"], axis=1)
    df3 = df3.rename(columns={"arctic_sea_ice_extent_max": "Maximum (February)","arctic_sea_ice_extent_min": "Minimum (September)"})
    df3=df3.sort_values(by=["Year"]).reset_index(drop=True)
    return df3
df3 = fetch_and_clean_data()

def create_animated_line_chart(data):
    years=data["Year"].unique()

    # Initialize figure
    fig3 = go.Figure()

    # Add traces for both Minimum (September) and Maximum (February)
    fig3.add_trace(go.Scatter(x=data['Year'], y=data['Minimum (September)'], line=dict(color='crimson'), mode='lines+markers', name='Minimum (September)',
                           hovertemplate="Year: %{x} <br> Arctic Sea Ice Extent: %{y:.2f} million km²"))
    fig3.add_trace(go.Scatter(x=data['Year'], y=data['Maximum (February)'], line=dict(color='royalblue'), mode='lines+markers', name='Maximum (February)',
                           hovertemplate="Year: %{x} <br> Arctic Sea Ice Extent: %{y:.2f} million km²"))

    # Generate frames for each year
    frames = [go.Frame(
        name=f"frame_{year}",
        data=[
            go.Scatter(x=data['Year'][:i+1], y=data['Minimum (September)'][:i+1], mode='lines+markers', line=dict(color='crimson'), 
                       hovertemplate="Year: %{x} <br> Arctic Sea Ice Extent: %{y:.2f} million km²"),
            go.Scatter(x=data['Year'][:i+1], y=data['Maximum (February)'][:i+1], mode='lines+markers', line=dict(color='royalblue'),
                       hovertemplate="Year: %{x} <br> Arctic Sea Ice Extent: %{y:.2f} million km²")
        ],
        layout=dict(title=f"{year}")
    ) for i, year in enumerate(data['Year'])]

    fig3.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": "100", "redraw": True}, "transition": {"duration": "100"}}], label=str(year)) for year in data['Year']]

    # Update layout with slider, buttons, and other settings
    fig3.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        xaxis_title='Year', yaxis_title='Sea Ice Extent (Million km²)',
        showlegend=True, height=600,
        sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="Year: ", visible=True), pad=dict(t=60))],
        yaxis=dict(range=[data["Minimum (September)"].min(), data["Maximum (February)"].max()*1.1], ticksuffix=" million km²"),
        xaxis=dict(range=[data["Year"].min(), data["Year"].max()]),
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

    return fig3


fig3 = create_animated_line_chart(df3)

# Display the plot in Streamlit
st.plotly_chart(fig3, use_container_width=True)
st.caption("Data Source: National Snow and Ice Data Center - Sea Ice Index (2025) – with minor processing by Our World in Data")

# -------------------------------------------------------------------------------------------------
# Carbon Dioxide Concentrations in the Atmosphere
# -------------------------------------------------------------------------------------------------

st.markdown("## Carbon Dioxide Concentrations in the Atmosphere")
st.text("""Atmospheric carbon dioxide (CO₂) concentration is measured in parts per million (ppm). Long-term trends in CO₂ concentrations can be measured at high-resolution using preserved air samples from ice cores.""")

@st.cache_data
def fetch_and_clean_data():
    df4 = pd.read_csv("https://ourworldindata.org/grapher/co2-long-term-concentration.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    df4=df4.drop(["Entity", "Code"], axis=1)
    df4 = df4.rename(columns={"co2_concentration": "CO2 Concentration"})
    df4["Year"] = df4["Year"].astype(int)
    df4 = df4[df4["Year"] > 0].reset_index(drop=True)
    return df4
df4 = fetch_and_clean_data()


def create_animated_line_chart(data):
    years=data["Year"].unique()
    # Initialize figure
    fig4 = go.Figure()

    fig4.add_trace(go.Scatter(x=data['Year'], y=data['CO2 Concentration'], line=dict(color='royalblue'), mode='lines', name='',
                           hovertemplate="Year: %{x} <br> C02 Concentration: %{y:.2f} ppmv"))

    # Generate frames for each year
    frames = [go.Frame(
        name=f"frame_{year}",
        data=[
            go.Scatter(x=data['Year'][:i+1], y=data['CO2 Concentration'][:i+1], mode='lines', line=dict(color='royalblue'), 
                       hovertemplate="Year: %{x} <br> C02 Concentration: %{y:.2f} ppmv")
        ],
        layout=dict(title=f"{year}")
    ) for i, year in enumerate(data['Year'])]

    fig4.frames = frames
    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": "1.1", "redraw": True}, "transition": {"duration": "1.1"}}], label=str(year)) for year in data['Year']]

    # Update layout with slider, buttons, and other settings
    fig4.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        xaxis_title='Year',
        yaxis_title='Carbon Dioxide Concentration',
        showlegend=False,
        height=600,
        xaxis=dict(range=[df4["Year"].min(), (df4["Year"].max())]),
        yaxis=dict(range=[df4["CO2 Concentration"].min(), (df4["CO2 Concentration"].max())], ticksuffix=" ppmv"),
        sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="Year: ", visible=True), pad=dict(t=60))],
        updatemenus=[{
        "buttons": [
            {"args": [None, {"frame": {"duration": 1.1, "redraw": True}, "fromcurrent": True}],
             "label": "Play", "method": "animate"},
            {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
             "label": "Pause", "method": "animate"}
        ],
        "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
    }],
    margin=dict(t=50, b=100), 
    )
    return fig4

fig4 = create_animated_line_chart(df4)

# Display the plot in Streamlit
st.plotly_chart(fig4, use_container_width=True)
st.caption("Data Source: NOAA Global Monitoring Laboratory - Trends in Atmospheric Carbon Dioxide (2025); EPA based on various sources (2022) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------------------
# Ice Sheet Mass Balance
# -------------------------------------------------------------------------------------------------
    
st.markdown("## Ice Sheet Mass Balance")
st.text("""Cumulative change in mass of ice sheets, measured relative to a base year of 2002. For reference, 1,000 billion metric tons is equal to about 260 cubic miles of ice—enough to raise sea level by about 3 millimeters.""")

@st.cache_data
def fetch_and_clean_data():
    df5=pd.read_csv("https://ourworldindata.org/grapher/ice-sheet-mass-balance.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
    df5=df5.drop(["Code"], axis=1)
    df5['Day'] = pd.to_datetime(df5['Day'])
    df5 = df5.rename(columns={"land_ice_mass_nasa": "Land Ice Mass","Entity": "Region", "Day": "Date"})
    df5=df5[df5["Land Ice Mass"]!=0].reset_index(drop=True)
    df5["Date"] = pd.to_datetime(df5["Date"]).dt.date
    return df5
df5 = fetch_and_clean_data()

# Function to create the animated line chart
def create_animated_line_chart(data):
    dates=data["Date"].unique()
    # Initialize figure
    fig = go.Figure()

    # Add traces for each region
    regions = data['Region'].unique()
    colors = ['purple', 'cyan']

    for region, color in zip(regions, colors):
        region_data = data[data['Region'] == region]
        fig.add_trace(go.Scatter(x=region_data['Date'], y=region_data['Land Ice Mass'], line=dict(color=color), mode='lines', name=region, hovertemplate="Date: %{x} <br> Ice Sheet Mass Balance: %{y:.2f} billion tonnes"))
    # Generate frames for each date
    frames = []
    for i, date in enumerate(data['Date'].unique()):
        frame_data = data[data['Date'] <= date]
        frames.append(go.Frame(
            name=f"frame_{date}",
            data=[
                go.Scatter(x=frame_data[frame_data['Region'] == region]['Date'], y=frame_data[frame_data['Region'] == region]['Land Ice Mass'],
                    mode='lines', line=dict(color=color), hovertemplate="Date: %{x} <br> Ice Sheet Mass Balance: %{y:.2f} billion tonnes"
                ) for region, color in zip(regions, colors)
            ],
            layout=dict(title=f"{date}")
        ))

    fig.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{date}"], {"frame": {"duration": 5, "redraw": True}, "transition": {"duration": 5}}],
        label=date.strftime('%Y-%m-%d')
    ) for date in data['Date'].unique()]

    # Update layout with slider, buttons, and other settings
    fig.update_layout(
        title=f"{dates[-1]}",
        title_x=0.45,
        xaxis_title='Date', yaxis_title='Land Ice Mass (billion tonnes)', showlegend=True, height=600,
        sliders=[dict(active=len(dates) - 1, steps=steps, currentvalue=dict(prefix="Date: ", visible=True), pad=dict(t=60))],
        xaxis=dict(range=[data["Date"].min(), data["Date"].max()], tickformat="%Y-%m-%d", tickangle=30),
        yaxis=dict(range=[data["Land Ice Mass"].min(), data["Land Ice Mass"].max()], ticksuffix=" billion tonnes"),
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 5, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100),  # Only adjust margin at the top and bottom
    )
    return fig

# Create the animated chart
fig = create_animated_line_chart(df5)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)
st.caption("Data Source: EPA based on various sources (2021) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------------------
# Ocean Acidification
# -------------------------------------------------------------------------------------------------
    
st.markdown("## Ocean Acidification")
st.text("""Mean seawater pH is shown based on in-situ measurements of pH from the Aloha station in Hawaii.""")

@st.cache_data
def fetch_and_clean_data():
    df6 = pd.read_csv("https://ourworldindata.org/grapher/seawater-ph.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    df6=df6.drop(["Code", "Entity"], axis=1)
    df6['Day'] = pd.to_datetime(df6['Day'])
    df6 = df6.rename(columns={"ocean_ph": "Monthly Average", "ocean_ph_yearly_average": "Yearly Average", "Day": "Date"})
    df6["Date"] = pd.to_datetime(df6["Date"]).dt.date
    return df6
df6 = fetch_and_clean_data()

# Function to create the animated line chart
def create_animated_line_chart(data):
    dates=data["Date"].unique()
    fig6 = go.Figure()
    
    # Initial trace for the plot
    fig6.add_trace(go.Scatter(x=data['Date'], y=data['Monthly Average'], mode='lines+markers', line=dict(color='cyan'), name='Monthly Average', hovertemplate="Date: %{x} <br> %{y:.2f} pH"))
    fig6.add_trace(go.Scatter(x=data['Date'], y=data['Yearly Average'], mode='lines+markers', line=dict(color='crimson'), name='Yearly Average', hovertemplate="Date: %{x} <br> %{y:.2f} pH"))
    
    # Reduce frames by selecting a subset of dates
    unique_dates = data['Date'].unique()
    step_size = max(1, len(unique_dates) // 50)
    selected_dates = unique_dates[::step_size]

    # Generate frames for selected dates
    frames = []
    for date in selected_dates:
        frame_data = data[data['Date'] <= date]
        frames.append(go.Frame(
            name=f"frame_{date}",
            data=[
                go.Scatter(x=frame_data['Date'], y=frame_data['Monthly Average'], mode='lines+markers', line=dict(color='cyan'), hovertemplate="Date: %{x} <br> %{y:.2f} pH"),
                go.Scatter(x=frame_data['Date'], y=frame_data['Yearly Average'], mode='lines+markers', line=dict(color='crimson'), hovertemplate="Date: %{x} <br> %{y:.2f} pH")
            ],
            layout=dict(title=f"{date}")
        ))
    
    fig6.frames = frames
    
    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{date}"], {"frame": {"duration": 2, "redraw": True}, "transition": {"duration": 2}}], label=date.strftime('%Y-%m-%d')
    ) for date in selected_dates]
    
    # Update layout with slider and buttons
    fig6.update_layout(
        title=f"{dates[-1]}",
        title_x=0.45,
        xaxis_title='Date', yaxis_title='Ocean pH Level', showlegend=True, height=600,
        sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="Date: ", visible=True), pad=dict(t=60))],
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=30, range=[data['Date'].min(), data['Date'].max()]),
        yaxis=dict(ticksuffix=" pH", range=[data['Monthly Average'].min(), data['Monthly Average'].max()]),
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 2, "redraw": True}, "fromcurrent": True}], "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}], "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100)
    )
    return fig6

# Create the animated chart
fig6 = create_animated_line_chart(df6)

# Display the plot in Streamlit
st.plotly_chart(fig6, use_container_width=True)
st.caption("Data Source: School of Ocean & Earth Science & Technology - Hawaii Ocean Time-series (2024) – with minor processing by Our World in Data")

# -------------------------------------------------------------------------------------------------
# Sea Level Rise
# -------------------------------------------------------------------------------------------------
    
st.markdown("## Sea Level Rise")
st.text("""Global mean sea level rise is measured relative to the 1993 - 2008 average sea level. This is shown as three series: the widely-cited Church & White dataset; the University of Hawaii Sea Level Center (UHLSC); and the average of the two.""")

@st.cache_data
def fetch_and_clean_data():
    df7 = pd.read_csv("https://ourworldindata.org/grapher/sea-level.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    df7=df7.drop(["Code", "Entity"], axis=1)
    df7['Day'] = pd.to_datetime(df7['Day'])
    df7 = df7.rename(columns={"sea_level_church_and_white_2011": "Church and White (2011)", "sea_level_uhslc": "UHSLC", "sea_level_average": "Average Sea Level", "Day": "Date"})
    df7["Date"] = pd.to_datetime(df7["Date"]).dt.date
    return df7
df7 = fetch_and_clean_data()

# Checkboxes to toggle between the three datasets
c1, c2, c3 = st.columns(3)
with c1:
    show_church_white = st.checkbox("Church and White (2011)", value=False)
with c2:
    show_UHSLC = st.checkbox("UHSLC", value=False)
with c3:
    show_avg = st.checkbox("Average Sea Level", value=True)

# Function to create the animated line chart
def create_animated_line_chart(data, show_church_white, show_UHSLC, show_avg):
    fig7 = go.Figure()
    
    # Conditional traces based on user selection
    if show_church_white:
        fig7.add_trace(go.Scatter(x=data['Date'], y=data['Church and White (2011)'], mode='lines+markers', line=dict(color='cyan'), name='Church and White (2011)', hovertemplate="Date: %{x} <br> Sea Level Rise: %{y:2f} mm"))
    if show_UHSLC:
        fig7.add_trace(go.Scatter(x=data['Date'], y=data['UHSLC'], mode='lines+markers', line=dict(color='crimson'), name='UHSLC', hovertemplate="Date: %{x} <br> Sea Level Rise: %{y:2f} mm"))
    if show_avg:
        fig7.add_trace(go.Scatter(x=data['Date'], y=data['Average Sea Level'], mode='lines+markers', line=dict(color='yellow'), name='Average Sea Level', hovertemplate="Date: %{x} <br> Sea Level Rise: %{y:2f} mm"))

    # Reduce frames by selecting a subset of dates
    unique_dates = data['Date'].unique()
    step_size = max(1, len(unique_dates) // 50)
    selected_dates = unique_dates[::step_size]

    # Generate frames for selected dates
    frames = []
    for date in selected_dates:
        frame_data = data[data['Date'] <= date]
        frame_traces=[]
        if show_church_white:
            frame_traces.append(go.Scatter(x=frame_data['Date'], y=frame_data['Church and White (2011)'], mode='lines+markers', line=dict(color='cyan'), hovertemplate="Date: %{x} <br> Sea Level Rise: %{y:2f} mm"))
        if show_UHSLC:
            frame_traces.append(go.Scatter(x=frame_data['Date'], y=frame_data['UHSLC'], mode='lines+markers', line=dict(color='crimson'), hovertemplate="Date: %{x} <br> Sea Level Rise: %{y:2f} mm"))
        if show_avg:
            frame_traces.append(go.Scatter(x=frame_data['Date'], y=frame_data['Average Sea Level'], mode='lines+markers', line=dict(color='yellow'), hovertemplate="Date: %{x} <br> Sea Level Rise: %{y:2f} mm"))
            
        frames.append(go.Frame(name=f"frame_{date}", data=frame_traces))

    fig7.frames = frames
    
    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{date}"], {"frame": {"duration": 2, "redraw": True}, "transition": {"duration": 2}}], label=date.strftime('%Y-%m-%d')
    ) for date in selected_dates]
    
    # Update layout with slider and buttons
    fig7.update_layout(
        xaxis_title='Date', yaxis_title='Sea Level Rise', showlegend=True, height=600,
        sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="Date: ", visible=True), pad=dict(t=60))],
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=30, range=[data['Date'].min(), data['Date'].max()]),
        yaxis=dict(ticksuffix=" mm", 
                   range=[data[['Church and White (2011)', 'UHSLC', 'Average Sea Level']].min().min(), 
                          data[['Church and White (2011)', 'UHSLC', 'Average Sea Level']].max().max()]),
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 2, "redraw": True}, "fromcurrent": True}], "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}], "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100)
    )

    return fig7

# Create the animated chart
fig7 = create_animated_line_chart(df7, show_church_white, show_UHSLC, show_avg)

# Display the plot in Streamlit
st.plotly_chart(fig7, use_container_width=True)
st.caption("Data Source: NOAA Climate.gov (2022) – processed by Our World in Data")

# -------------------------------------------------------------------------------------------------
# Annual Temperature Anomalies
# -------------------------------------------------------------------------------------------------

st.markdown("## Annual Temperature Anomalies")
st.text("""The deviation of a specific year's average surface temperature from the 1991-2020 mean, in degrees Celsius.""")

@st.cache_data
def fetch_and_clean_data():
    df8 = pd.read_csv("https://ourworldindata.org/grapher/annual-temperature-anomalies.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

    df8 = df8.rename(columns={"Entity": "Country", "temperature_anomaly": "Temperature Anomaly"})
    return df8
df8 = fetch_and_clean_data()

# Get unique years for animation
years = sorted(df8['Year'].unique())

global_zmin = -2
global_zmax = 1.5
global_zmid = 0.25

def create_choropleth_map(df8):
    # Base figure
    fig8 = go.Figure()

    # Create frames for each year
    frames = [
        go.Frame(
            name=str(year),
            data=[
                go.Choropleth(locations=df8[df8['Year'] == year]['Code'],
                    z=df8[df8['Year'] == year]['Temperature Anomaly'], colorscale="rdbu",
                    zmin=global_zmin, zmax=global_zmax, zmid=global_zmid, colorbar=dict(ticksuffix=" °C"), reversescale=True,
                    hovertemplate="<b>Country:</b> %{customdata[0]}<br>" + "<b>Year:</b> %{customdata[1]}<br>" + "<b>Temperature Anomaly:</b> %{z:.2f}°C<extra></extra>",
                    customdata=df8[df8['Year'] == year][['Country', 'Year']].values
                )
            ],
            layout=dict(title=f"{year}")
        ) for year in years
    ]

    # Initial Frame (First Year)
    fig8.add_trace(
        go.Choropleth(
            locations=df8[df8['Year'] == years[-1]]['Code'],
            z=df8[df8['Year'] == years[-1]]['Temperature Anomaly'], colorscale="rdbu",
            zmin=global_zmin, zmax=global_zmax, zmid=global_zmid, colorbar=dict(ticksuffix=" °C"), reversescale=True, 
            hovertemplate="<b>Country:</b> %{customdata[0]}<br>" + "<b>Year:</b> %{customdata[1]}<br>" + "<b>Temperature Anomaly:</b> %{z:.2f}°C<extra></extra>",
            customdata=df8[df8['Year'] == years[-1]][['Country', 'Year']].values
        )
    )

    # Add slider steps for each year
    steps = [
        dict(method="animate",
             args=[[str(year)], {"frame": {"duration": 150, "redraw": True}, "transition": {"duration": 150}}],
             label=str(year))
        for year in years
    ]

    # Update figure layout
    fig8.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        geo=dict(showcoastlines=True, projection_type="equirectangular"),
        template=plot_template,
        sliders=[dict(active=len(years) - 1, steps=steps, currentvalue=dict(prefix="Year: ", visible=True), pad=dict(t=60))],
        updatemenus=[{
        "buttons": [
            {"args": [None, {"frame": {"duration": 150, "redraw": True}, "fromcurrent": True}],
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

# Generate figure
fig8 = create_choropleth_map(df8)

# Display in Streamlit
st.plotly_chart(fig8, use_container_width=True)
st.caption("Data Source: Contains modified Copernicus Climate Change Service information (2025) – with major processing by Our World in Data")

# -------------------------------------------------------------------------------------------------
# Contributions to the Change in Global Mean Surface Temperature
# -------------------------------------------------------------------------------------------------

st.markdown("## Contributions to the Change in Global Mean Surface Temperature")
st.text("""This is shown as a region's share of the global mean surface temperature change as a result of its cumulative emissionsof three gases – carbon dioxide, methane, and nitrous oxide.""")

# Fetch the data
@st.cache_data
def fetch_and_clean_data():
    df9 = pd.read_csv("https://ourworldindata.org/grapher/contributions-global-temp-change.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
    df9 = df9.rename(columns={"Entity": "Country", "share_of_temperature_response_ghg_total": "Contribution to Temperature Change"})
    df9=df9.dropna(subset=["Code"])
    df9 = df9[df9['Country'] != 'World']
    return df9
df9 = fetch_and_clean_data()

# Streamlit Dropdown to select countries
countries = df9['Country'].unique()
selected_countries = st.multiselect("Select Countries", options=countries, default=df9.groupby("Country")["Contribution to Temperature Change"].mean().nlargest(7).index.tolist())

# Filter the dataframe based on the selected country
df_filtered = df9[df9['Country'].isin(selected_countries)].reset_index()

def create_animated_line_chart(df_filtered):
    years = sorted(df_filtered["Year"].unique())
    # Initialize figure
    fig9 = go.Figure()

    # Add traces for each country
    for country in df_filtered["Country"].unique():
        country_data = df_filtered[df_filtered["Country"] == country]
        fig9.add_trace(go.Scatter(x=country_data['Year'],  y=country_data['Contribution to Temperature Change'],  mode='lines', name=country, 
                                  hovertemplate="<b>Country:</b> " + country + "<br><b>Year:</b> %{x}<br><b>Contribution:</b> %{y:.2f}%<extra></extra>"))

    # Generate frames for each year (show data up to the year)
    frames = [go.Frame(
        name=f"frame_{year}",
        data=[
            go.Scatter(x=country_data[country_data['Year'] <= year]['Year'],  # Include all data up to the current year
                       y=country_data[country_data['Year'] <= year]['Contribution to Temperature Change'], 
                       mode='lines', name=country,
                       hovertemplate="<b>Country:</b> " + country + "<br><b>Year:</b> %{x}<br><b>Contribution:</b> %{y:.2f}%<extra></extra>"
                       )
            for country, country_data in df_filtered.groupby('Country')
        ],
        layout=dict(title=f"{year}")
    ) for year in sorted(df_filtered['Year'].unique())]

    # Assign frames to the figure
    fig9.frames = frames

    # Create slider steps dynamically
    steps = [dict(method="animate", args=[[f"frame_{year}"], {"frame": {"duration": 25}, "transition": {"duration": 25}}], 
                  label=str(year)) for year in sorted(df_filtered['Year'].unique())]

    # Update layout with slider, buttons, and other settings
    fig9.update_layout(
        title=f"{years[-1]}",
        title_x=0.45,
        xaxis_title='Year',
        yaxis_title='Contribution to Temperature Change',
        showlegend=True,
        height=600,
        yaxis=dict(range=[0, df_filtered["Contribution to Temperature Change"].max()*1.1], ticksuffix="%"),
        xaxis=dict(range=[df_filtered["Year"].min(), df_filtered["Year"].max()]),
        sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="Year: ", visible=True), pad=dict(t=60))],
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 25, "redraw": True}, "fromcurrent": True}],
                 "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                 "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "showactive": False, "type": "buttons", "x": -0.05, "y": -0.2,
        }],
        margin=dict(t=50, b=100)
    )

    return fig9

# Generate figure
fig9 = create_animated_line_chart(df_filtered)

# Display in Streamlit
st.plotly_chart(fig9, use_container_width=True)
st.caption("Data Source: Jones et al. (2024) – with major processing by Our World in Data")

st.write("\n" * 5)
st.divider()
st.caption("Citation: Hannah Ritchie, Pablo Rosado and Veronika Samborska (2024) - “Climate Change” Published online at OurWorldinData.org. Retrieved from: 'https://ourworldindata.org/climate-change' [Online Resource]")
