# **Visualizing Energy and Environmental Data: Insights into Renewables, Climate, and Emissions**

## **Overview**
This interactive **Streamlit** dashboard visualizes key trends in **renewable energy, climate change, and greenhouse gas emissions** using publicly available datasets. The dashboard provides insights into global energy transitions, temperature anomalies, CO₂ emissions, and power generation sources.

## **Features**
- 🌍 **Renewable Energy** – Trends in solar, wind, hydro, and overall renewable adoption.
- 🌡 **Climate Change** – Temperature anomalies, ice sheet changes, and sea level rise.
- 💨 **CO₂ & Greenhouse Gas Emissions** – Annual emissions, per capita trends, and cumulative contributions.
- 🗺 **Global Power Plant Database** – Interactive map of major power plants categorized by fuel type and capacity.

## **Live Dashboard**
[Click here to view the deployed app on Streamlit](https://energy-environment-dashboard.streamlit.app/)  

## **Installation & Usage**

### **🔧 Prerequisites**
Ensure you have Python installed along with the following libraries:
```bash
pip install plotly folium streamlit pandas streamlit_folium
```

### **📥 Clone the Repository**
```bash
git clone https://github.com/your-username/energy-environment-dashboard.git
cd energy-environment-dashboard
```

### **▶️ Run the Streamlit App**
```bash
streamlit run Home.py
```

## **Project Structure**
```
📂 energy-environment-dashboard  
│-- 📄 Home.py                # Main Streamlit file  
│-- 📄 global_power_plant_database.csv  # Power plant dataset  
│-- 📄 requirements.txt       # Dependencies  
│-- 📂 pages/                 # Dashboard pages  
│   │-- 📄 Renewable_Energy.py   # Renewable energy visualizations  
│   │-- 📄 Climate_Change.py     # Climate change visualizations  
│   │-- 📄 Greenhouse_Gas_Emissions.py  # CO₂ & greenhouse gas emissions  
```

## **Data Sources**
- **Energy Institute - Statistical Review of World Energy (2024)** – with major processing by Our World in Data
- **Ember (2024); Energy Institute - Statistical Review of World Energy (2024)** – with major processing by Our World in Data
- **IRENA (2024)** – processed by Our World in Data
- **Global Energy Observatory et al. (2021).** [Global Power Plant Database v1.3.0](https://datasets.wri.org/datasets/global-power-plant-database). License: CC BY 4.0.
- **Contains modified Copernicus Climate Change Service information (2025)** – with major processing by Our World in Data
- **National Snow and Ice Data Center - Sea Ice Index (2025)** – with minor processing by Our World in Data
- **NOAA Global Monitoring Laboratory - Trends in Atmospheric Carbon Dioxide (2025); EPA based on various sources (2022)** – with major processing by Our World in Data
- **EPA based on various sources (2021)** – with major processing by Our World in Data
- **School of Ocean & Earth Science & Technology - Hawaii Ocean Time-series (2024)** – with minor processing by Our World in Data
- **NOAA Climate.gov (2022)** – processed by Our World in Data
- **Jones et al. (2024)** – with major processing by Our World in Data
- **Global Carbon Budget (2024)** – with major processing by Our World in Data
- **Jones et al. (2024); Population based on various sources (2024)** – with major processing by Our World in Data

### **Referenced Reports**
- **Hannah Ritchie, Pablo Rosado and Max Roser (2023) - “CO₂ and Greenhouse Gas Emissions”** [OurWorldinData](https://ourworldindata.org/co2-and-greenhouse-gas-emissions)
- **Hannah Ritchie, Pablo Rosado and Veronika Samborska (2024) - “Climate Change”** [OurWorldinData](https://ourworldindata.org/climate-change)
- **Hannah Ritchie, Max Roser and Pablo Rosado (2020) - “Renewable Energy”** [OurWorldinData](https://ourworldindata.org/renewable-energy)

## **License**
The datasets used in this project are sourced from publicly available repositories and appropriately credited. **The code in this repository may not be used, modified, or distributed without prior permission and proper credit.**

