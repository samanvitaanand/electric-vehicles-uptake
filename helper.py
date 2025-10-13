import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster

import plotly.express as px
import plotly.graph_objects as go




def level_by_month():
    # Read the data from the CSV file
    file_path = "data_organized/Vehicle_Registration_Transactions.csv"
    df = pd.read_csv(file_path)

    # Convert 'Transaction Month and Year' to datetime and filter the date range
    df['Transaction Month and Year'] = pd.to_datetime(df['Transaction Month and Year'], format='%m/%d/%Y')
    start_date = '2020-01-01'
    end_date = '2024-04-30'
    df = df[(df['Transaction Month and Year'] >= start_date) & (df['Transaction Month and Year'] <= end_date)]

    #Extract the month and year for grouping
    df['Transaction Month'] = df['Transaction Month and Year'].dt.to_period('M')

    #  Group by month and electrification level, then count occurrences
    grouped = df.groupby(['Transaction Month', 'Electrification Level']).size().unstack(fill_value=0)

    # Calculate the percentages
    percentages = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Plot the stacked bar chart
    percentages.plot(kind='bar', stacked=True, figsize=(14, 8))

    plt.ylabel('Percentage')
    plt.xlabel('Transaction Month')
    plt.title('Vehicle Electrification Level by Month (Jan 2020 - Apr 2024)')
    plt.legend(title='Electrification Level', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
    plt.tight_layout()
    plt.savefig("plot/level_by_month.png")


def proportion_of_ev():
        # Load data from CSV file
        #file_path = "data_organized/Vehicle_Registration_Transactions.csv"
        file_path = "raw_data/VRT.csv"
        df = pd.read_csv(file_path)

        # Convert 'Transaction Month and Year' column to datetime
        df['Transaction Month and Year'] = pd.to_datetime(df['Transaction Month and Year'], format='%m/%d/%Y')

        # Determine if a vehicle is an EV based on the 'Electrification Level'
        df['Is_EV'] = df['Electrification Level'].str.contains('EV|Electric', case=False, na=False)
        #print(df.columns)

        # Calculate the total number of EVs and non-EVs
        total_evs = df[df['Is_EV']]['Transaction Count'].sum()
        #print(total_evs)

        total_vehicles = df['Transaction Count'].sum()
        total_non_evs = total_vehicles - total_evs

        # Create a pie chart
        labels = ['Electric Vehicles (EVs)', 'Non-Electric Vehicles']
        sizes = [total_evs, total_non_evs]
        colors = ['#ff9999', '#66b3ff']
        #colors = ['#FD4659', '#006400']   #006400
        #colors = ['#D23B68', '#006400']
        explode = (0.1, 0)  # explode the first slice

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=140)
        plt.title('Proportion of Electric Vehicle Registrations')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.savefig("plot/proportion_of_ev.png")


def growth_of_ev():
    # Load EV data
    ev_data = pd.read_csv('raw_data/EVP.csv')

    # Convert 'Date' to datetime format
    ev_data['Date'] = pd.to_datetime(ev_data['Date'])

    # Group and sum data by date
    ev_grouped = ev_data.groupby('Date').sum().reset_index()

    # Plotting
    plt.figure(figsize=(14, 8))
    plt.plot(ev_grouped['Date'], ev_grouped['Battery Electric Vehicles (BEVs)'], label='BEVs')
    plt.plot(ev_grouped['Date'], ev_grouped['Plug-In Hybrid Electric Vehicles (PHEVs)'], label='PHEVs')
    plt.plot(ev_grouped['Date'], ev_grouped['Electric Vehicle (EV) Total'], label='Total EVs')

    plt.xlabel('Date')
    plt.ylabel('Number of Vehicles')
    plt.title('Growth of Electric Vehicles in Washington State')
    plt.legend()
    plt.grid(True)
    plt.savefig("plot/growth_of_ev")


def vrt_by_countyfuelTypes():
     # Load vehicle registration data
    vrt_data = pd.read_csv('raw_data/VRT.csv')

    # Aggregate data by county and fuel type
    county_fuel_counts = vrt_data.groupby(['County', 'Fuel Type Primary']).size().unstack().fillna(0)

    # Plotting
    county_fuel_counts.plot(kind='bar', stacked=True, figsize=(14, 8))

    plt.xlabel('County')
    plt.ylabel('Number of Vehicle Registrations')
    plt.title('Vehicle Registration Trends by County and Fuel Type in WA')
    plt.legend(title='Fuel Type')
    plt.grid(True)
    plt.savefig("plot/vrt_by_countyfuelTypes")


def interactive():    
     # Load geospatial data for Washington State counties
    washington_map = gpd.read_file('data_organized/us-county-boundaries.shp')

    # Load fuel station data
    stations_data = pd.read_csv('raw_data/fuel_stations.csv')
    stations_data = stations_data[stations_data['State'] == 'WA']

    # Initialize map
    m = folium.Map(location=[47.7511, -120.7401], zoom_start=7)  # Centered on WA

    # Add markers for each station
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in stations_data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Station Name']} ({row['Fuel Type Code']})",
            icon=folium.Icon(color='blue' if row['Fuel Type Code'] == 'ELEC' else 'green' if row['Fuel Type Code'] == 'CNG' else 'red')
        ).add_to(marker_cluster)

    # Save map to HTML file
    #display(m)
    m.save('plot/wa_fuel_stations.html')


def geo():
    gdf = gpd.read_file("data_organized/us-county-boundaries.shp")
    wa_gdf = gdf[gdf['stusab'] == 'WA']

    #ev_count_df = pd.read_csv("Electric_Vehicle_Population_Size.csv")
    ev_count_df = pd.read_csv("data_organized/Electric_Vehicle_Population_Size.csv")
    pop = ev_count_df.groupby("County").sum()
    merged_gdf = wa_gdf.merge(pop, left_on='name', right_on = "County")
    #print(merged_gdf)

    fig , ax1 = plt.subplots(1,1)
    #fig, ax = plt.subplots(1,1, figsize=(7,5))


    merged_gdf.plot(ax=ax1, legend=True, column="Electric Vehicle (EV) Total", cmap='viridis', linewidth=0.5, edgecolor='0.8')

    fuel_stations_df = pd.read_csv("raw_data/fuel_stations.csv")
    fuel_stations_geometry = [Point(xy) for xy in zip(fuel_stations_df["Longitude"], fuel_stations_df["Latitude"])]
    fuel_stations_gdf = gpd.GeoDataFrame(fuel_stations_df, geometry=fuel_stations_geometry)
    fuel_stations_gdf.plot(ax=ax1, marker='o', label='Fuel Stations', color='green', markersize=1.5)

    y = [49.0, 48.5, 48.0, 47.5,47.0, 46.5, 46.0, 45.5]
    ax1.set_yticks(y)
    plt.savefig('plot/geo.png')
    #ax.setxlabe


def top_ten():        
    data = "raw_data/EVP.csv"

    df = pd.read_csv(data)
    new_df = df[df['State'] == 'WA'].copy()
    new_df['Date'] = pd.to_datetime(new_df['Date'], format='%B %d %Y')

    # Convert 'Date' column to string format
    new_df['Date'] = new_df['Date'].dt.strftime('%B %d %Y')

    # Group by county and sum the total number of vehicles
    county_totals = new_df.groupby('County').sum()

    # Sort by electric vehicle total and select the top 10 counties
    top_counties = county_totals.nlargest(10, 'Electric Vehicle (EV) Total')

    # Create a stacked bar plot comparing the number of electric and non-electric vehicles for the top N counties
    plt.figure(figsize=(10, 6))

    # Plot Electric Vehicle (EV) Totals
    plt.bar(top_counties.index, top_counties['Electric Vehicle (EV) Total'], label='Electric Vehicles (EV)', color='blue')

    # Plot Non-Electric Vehicle Totals
    plt.bar(top_counties.index, top_counties['Non-Electric Vehicle Total'], bottom=top_counties['Electric Vehicle (EV) Total'], label='Non-Electric Vehicles', color='pink')

    plt.xlabel('County')
    plt.ylabel('Number of Vehicles')
    plt.title('Top 10 Counties with Highest Number of Electric Vehicles')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig('plot/top_ten.png')



# def population():
#     # washington_map = gpd.read_file('data_organized/us-county-boundaries.shp')

#     # # Load population data
#     # print(washington_map.columns)
#     # pop_data = pd.read_csv('data_organized/Pop.csv')
#     # pop_data['Population Density'] = pop_data['2023'] / washington_map['aland']  # Assuming 'area' is in sq miles

#     # # Load fuel station data
#     # stations_data = pd.read_csv('raw_data/fuel_stations.csv')
#     # stations_data = stations_data[stations_data['State'] == 'WA']
#     # stations_count = stations_data.groupby('County').size().reset_index(name='Station Count')

#     # # Merge population density and station count
#     # merged_data = pd.merge(pop_data, stations_count, left_on='Geographic Area', right_on='County')

#     # # Plotting
#     # plt.figure(figsize=(10, 6))
#     # plt.scatter(merged_data['Population Density'], merged_data['Station Count'], alpha=0.6, edgecolor='k')

#     # plt.xlabel('Population Density (people/sq mile)')
#     # plt.ylabel('Number of EV Charging Stations')
#     # plt.title('Correlation Between Population Density and EV Charging Stations in WA')
#     # plt.grid(True)
#     # plt.savefig('plot/pop.png')


#     washington_map = gpd.read_file('data_organized/us-county-boundaries.shp')

#     # Print the columns to confirm the names
#     #print(washington_map.columns)

#     # Ensure 'aland' (land area) is in the correct format (assuming square meters)
#     # Convert 'aland' from square meters to square miles
#     washington_map['ALAND_sq_miles'] = washington_map['aland'].astype(float) / 2_589_988.11

#     # Load population data
#     pop_data = pd.read_csv('data_organized/Pop.csv')

#     # Convert population column to numeric, assuming the column name is '2023'
#     pop_data['2023'] = pd.to_numeric(pop_data['2023'], errors='coerce')

#     # Merge geographic data with population data
#     pop_data = pop_data.rename(columns={'Geographic Area': 'County'})
#     merged_geo_pop = pd.merge(washington_map, pop_data, left_on='name', right_on='County')

#     # Calculate population density (people per square mile)
#     merged_geo_pop['Population Density'] = merged_geo_pop['2023'] / merged_geo_pop['ALAND_sq_miles']
#     print("merged ", merged_geo_pop)
#     # Load fuel station data
#     stations_data = pd.read_csv('raw_data/fuel_stations.csv')
#     stations_data = stations_data[stations_data['State'] == 'WA']

#     # Count the number of stations per county
#     stations_count = stations_data.groupby('County').size().reset_index(name='Station Count')

#     # Merge population density and station count
#     merged_data = pd.merge(merged_geo_pop, stations_count, left_on='name', right_on='County')

#     # Plotting
#     plt.figure(figsize=(10, 6))
#     plt.scatter(merged_data['Population Density'], merged_data['Station Count'], alpha=0.6, edgecolor='k')

#     plt.xlabel('Population Density (people/sq mile)')
#     plt.ylabel('Number of EV Charging Stations')
#     plt.title('Correlation Between Population Density and EV Charging Stations in WA')
#     plt.grid(True)
#     plt.tight_layout()
#     plt.savefig('plot/pop.png')


def line_plotly():

        # Load data
    pop_data = pd.read_csv("data_organized/Pop.csv")
    ev_data = pd.read_csv("raw_data/EVP.csv")
    fuel_stations_data = pd.read_csv("data_organized/fuel_stations.csv")

    # Clean up data if needed (remove commas from population)
    pop_data['County'] = pop_data['County'].astype(str)

    # Drop rows with missing or NaN values in the 'County' column
    pop_data.dropna(subset=['County'], inplace=True)

    # Convert population data to integers after removing commas and NaN values
    for year in ['2020', '2021', '2022', '2023']:
        pop_data[year] = pop_data[year].apply(lambda x: int(float(str(x).replace(',', ''))) if pd.notnull(x) else 0)

    # Bar chart for population over the years
    fig1 = px.bar(pop_data, x='County', y=['2020', '2021', '2022', '2023'],
                  title='Population Over the Years by County',
                  labels={'value': 'Population', 'variable': 'Year'},
                  barmode='group')

    # Line chart for electric vehicle adoption over time
    fig2 = px.line(ev_data, x='Date', y='Electric Vehicle (EV) Total',
                   color='County', title='Electric Vehicle Adoption Over Time')

    # Scatter plot for fuel stations
    fig3 = px.scatter_mapbox(fuel_stations_data, lat='Latitude', lon='Longitude',
                             hover_name='Station Name', hover_data=['City', 'Fuel Type Code'],
                             title='Fuel Stations in Washington',
                             mapbox_style="carto-positron", zoom=6)

    # Show plots
    fig1.show()
    fig2.show()
    fig3.show()

def top_ten_plotly():        

    data = "raw_data/EVP.csv"

    df = pd.read_csv(data)
    new_df = df[df['State'] == 'WA'].copy()
    new_df['Date'] = pd.to_datetime(new_df['Date'], format='%B %d %Y')

    # Convert 'Date' column to string format
    new_df['Date'] = new_df['Date'].dt.strftime('%B %d %Y')

    # Group by county and sum the total number of vehicles
    county_totals = new_df.groupby('County').sum()

    # Sort by electric vehicle total and select the top 10 counties
    top_counties = county_totals.nlargest(10, 'Electric Vehicle (EV) Total')

    # Create a stacked bar plot comparing the number of electric and non-electric vehicles for the top N counties
    fig = px.bar(top_counties, x=top_counties.index, y=['Electric Vehicle (EV) Total', 'Non-Electric Vehicle Total'],
                 barmode='stack', labels={'value': 'Number of Vehicles', 'variable': 'Vehicle Type'},
                 title='Top 10 Counties with Highest Number of Electric Vehicles',
                 color_discrete_sequence=['blue', 'orange'])

    # Add text annotation for the date range
    fig.update_layout(xaxis_tickangle=-45, xaxis_title='County', yaxis_title='Number of Vehicles',
                      annotations=[dict(x=0.5, y=-0.15, showarrow=False,
                                        text="Data from: {} to {}".format(new_df['Date'].min(), new_df['Date'].max()),
                                        xref="paper", yref="paper")])
    fig.show()


def level_by_month_plotly():
    # # Read the data from the CSV file
    # file_path = "raw_data/VRT.csv"
    # df = pd.read_csv(file_path)

    # # Convert 'Transaction Month and Year' to datetime and filter the date range
    # df['Transaction Month and Year'] = pd.to_datetime(df['Transaction Month and Year'], format='%m/%d/%Y')
    # start_date = '2020-01-01'
    # end_date = '2024-04-30'
    # df = df[(df['Transaction Month and Year'] >= start_date) & (df['Transaction Month and Year'] <= end_date)]

    # # Extract the month and year for grouping
    # df['Transaction Month'] = df['Transaction Month and Year'].dt.to_period('M')

    # # Group by month and electrification level, then count occurrences
    # grouped = df.groupby(['Transaction Month', 'Electrification Level']).size().unstack(fill_value=0)

    # # Calculate the percentages
    # percentages = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # # Reset index to make 'Transaction Month' a regular column
    # percentages = percentages.reset_index()

    # # Melt DataFrame to long format for plotting with Plotly
    # melted_df = pd.melt(percentages, id_vars='Transaction Month', value_vars=['ICE (Internal Combustion Engine)', 'Standard Hybrid', 'Plug-In Hybrid', 'Battery Electric Vehicle'])

    # # Plot the stacked bar chart using Plotly
    # fig = px.bar(melted_df, x='Transaction Month', y='value', color='Electrification Level', barmode='stack',
    #              labels={'value': 'Percentage', 'Transaction Month': 'Transaction Month'},
    #              title='Vehicle Electrification Level by Month (Jan 2020 - Apr 2024)',
    #              category_orders={'Electrification Level': ['ICE (Internal Combustion Engine)', 'Standard Hybrid', 'Plug-In Hybrid', 'Battery Electric Vehicle']})

    # fig.update_layout(xaxis_title='Transaction Month', yaxis_title='Percentage')
    # fig.show()
    # Read the data from the CSV file
    # file_path = "data_organized/Vehicle_Registration_Transactions.csv"
    # df = pd.read_csv(file_path)

    # # Convert 'Transaction Month and Year' to datetime and filter the date range
    # df['Transaction Month and Year'] = pd.to_datetime(df['Transaction Month and Year'], format='%m/%d/%Y')
    # start_date = '2020-01-01'
    # end_date = '2024-04-30'
    # df = df[(df['Transaction Month and Year'] >= start_date) & (df['Transaction Month and Year'] <= end_date)]

    # # Extract the month and year for grouping
    # df['Transaction Month'] = df['Transaction Month and Year'].dt.to_period('M')

    # # Group by month and electrification level, then count occurrences
    # grouped = df.groupby(['Transaction Month', 'Electrification Level']).size().unstack(fill_value=0)

    # # Calculate the percentages
    # percentages = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # # Reset index to make 'Transaction Month' a regular column
    # percentages = percentages.reset_index()

    # # Melt DataFrame to long format for plotting with Plotly
    # melted_df = pd.melt(percentages, id_vars='Transaction Month', value_vars=percentages.columns[1:])

    # # Plot the stacked bar chart using Plotly
    # fig = px.bar(melted_df, x='Transaction Month', y='value', color='Electrification Level', barmode='stack',
    #              labels={'value': 'Percentage', 'Transaction Month': 'Transaction Month'},
    #              title='Vehicle Electrification Level by Month (Jan 2020 - Apr 2024)',
    #              category_orders={'Electrification Level': sorted(df['Electrification Level'].unique())})

    # fig.update_layout(xaxis_title='Transaction Month', yaxis_title='Percentage')
    # fig.show()
    file_path = "data_organized/Vehicle_Registration_Transactions.csv"
    df = pd.read_csv(file_path)

    # Convert 'Transaction Month and Year' to datetime and filter the date range
    df['Transaction Month and Year'] = pd.to_datetime(df['Transaction Month and Year'], format='%m/%d/%Y')
    start_date = '2020-01-01'
    end_date = '2024-04-30'
    df = df[(df['Transaction Month and Year'] >= start_date) & (df['Transaction Month and Year'] <= end_date)]

    # Extract the month and year for grouping
    df['Transaction Month'] = df['Transaction Month and Year'].dt.to_period('M')

    # Group by month and electrification level, then count occurrences
    grouped = df.groupby(['Transaction Month', 'Electrification Level']).size().unstack(fill_value=0)

    # Calculate the percentages
    percentages = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Reset index to make 'Transaction Month' a regular column
    percentages = percentages.reset_index()

    # Convert 'Transaction Month' to string for plotting
    percentages['Transaction Month'] = percentages['Transaction Month'].astype(str)

    # Melt DataFrame to long format for plotting with Plotly
    melted_df = pd.melt(percentages, id_vars='Transaction Month', value_vars=percentages.columns[1:])

    # Plot the stacked bar chart using Plotly
    fig = px.bar(melted_df, x='Transaction Month', y='value', color='Electrification Level', barmode='stack',
                 labels={'value': 'Percentage', 'Transaction Month': 'Transaction Month'},
                 title='Vehicle Electrification Level by Month (Jan 2020 - Apr 2024)',
                 category_orders={'Electrification Level': sorted(df['Electrification Level'].unique())})

    fig.update_layout(xaxis_title='Transaction Month', yaxis_title='Percentage')
    fig.show()


def growth_of_ev_plotly():
    # Load EV data
    ev_data = pd.read_csv('raw_data/EVP.csv')

    # Convert 'Date' to datetime format
    ev_data['Date'] = pd.to_datetime(ev_data['Date'])

    # Group and sum data by date
    ev_grouped = ev_data.groupby('Date').sum().reset_index()

    # Plotting using Plotly
    fig = px.line(ev_grouped, x='Date', y=['Battery Electric Vehicles (BEVs)', 'Plug-In Hybrid Electric Vehicles (PHEVs)', 'Electric Vehicle (EV) Total'],
                  labels={'value': 'Number of Vehicles', 'Date': 'Date'},
                  title='Growth of Electric Vehicles in Washington State')

    fig.update_layout(xaxis_title='Date', yaxis_title='Number of Vehicles')
    fig.show()


def geo_plotly():
    gdf = gpd.read_file("data_organized/us-county-boundaries.shp")
    wa_gdf = gdf[gdf['stusab'] == 'WA']

    ev_count_df = pd.read_csv("data_organized/Electric_Vehicle_Population_Size.csv")
    pop = ev_count_df.groupby("County").sum()
    merged_gdf = wa_gdf.merge(pop, left_on='name', right_on="County")

    fig = go.Figure()

    # Add county boundaries
    fig.add_trace(go.Choroplethmapbox(geojson=merged_gdf.geometry.__geo_interface__,
                                       locations=merged_gdf.index,
                                       z=merged_gdf["Electric Vehicle (EV) Total"],
                                       colorscale="Viridis",
                                       marker_opacity=0.7,
                                       marker_line_width=0))

    # Add fuel stations
    fuel_stations_df = pd.read_csv("raw_data/fuel_stations.csv")
    fig.add_trace(go.Scattermapbox(lat=fuel_stations_df["Latitude"],
                                    lon=fuel_stations_df["Longitude"],
                                    mode="markers",
                                    marker=dict(size=4, color="orange"),
                                    name="Fuel Stations"))

    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=5,
                      mapbox_center={"lat": 47.5, "lon": -120.5},
                      margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      showlegend=True,
                      title="Washington State - Electric Vehicle Population and Fuel Stations")
    
    fig.show()

# def proportion_of_ev_plotly():
#     # Load data from CSV file
#     file_path = "raw_data/VRT.csv"
#     df = pd.read_csv(file_path)

#     # Convert 'Transaction Month and Year' column to datetime
#     df['Transaction Month and Year'] = pd.to_datetime(df['Transaction Month and Year'], format='%m/%d/%Y')

#     # Determine if a vehicle is an EV based on the 'Electrification Level'
#     df['Is_EV'] = df['Electrification Level'].str.contains('EV|Electric', case=False, na=False)

#     # Calculate the total number of EVs and non-EVs
#     total_evs = df[df['Is_EV']]['Transaction Count'].sum()
#     total_vehicles = df['Transaction Count'].sum()
#     total_non_evs = total_vehicles - total_evs

#     # Create a pie chart
#     labels = ['Electric Vehicles (EVs)', 'Non-Electric Vehicles']
#     sizes = [total_evs, total_non_evs]
#     colors = ['#ff9999', '#66b3ff']
#     explode = (0.1, 0)  # explode the first slice

#     fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=0.3)])
#     fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
#                       marker=dict(colors=colors, line=dict(color='#000000', width=2)))
#     fig.update_layout(title='Proportion of Electric Vehicle Registrations', title_x=0.5)
#     fig.show()


def vrt_by_countyfuelTypes_plotly():
    vrt_data = pd.read_csv('raw_data/VRT.csv')

    # Parse the 'Transaction Month and Year' column
    if 'Transaction Month and Year' in vrt_data.columns:
        vrt_data['Transaction Month and Year'] = pd.to_datetime(vrt_data['Transaction Month and Year'], format='%m/%d/%Y')

    # Determine the date range for annotation
    if 'Transaction Month and Year' in vrt_data.columns:
        min_date = vrt_data['Transaction Month and Year'].min().strftime('%B %d, %Y')
        max_date = vrt_data['Transaction Month and Year'].max().strftime('%B %d, %Y')
        date_range_label = f'Data from {min_date} to {max_date}'
    else:
        date_range_label = 'Date range not available'

    # Aggregate data by county and fuel type
    county_fuel_counts = vrt_data.groupby(['County', 'Fuel Type Primary']).size().unstack().fillna(0)

    # Convert the dataframe to a format suitable for Plotly
    county_fuel_counts = county_fuel_counts.reset_index()
    melted_df = county_fuel_counts.melt(id_vars='County', var_name='Fuel Type', value_name='Count')

    # Create the stacked bar chart using Plotly
    fig = px.bar(melted_df, x='County', y='Count', color='Fuel Type', 
                 title='Vehicle Registration Trends by County and Fuel Type in WA',
                 labels={'Count': 'Number of Vehicle Registrations'},
                 width=1400, height=800)

    fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'}, 
                      xaxis_title='County', yaxis_title='Number of Vehicle Registrations')

    # Add date range annotation to the plot
    fig.add_annotation(
        text=date_range_label,
        xref="paper", yref="paper",
        x=1, y=1.05, showarrow=False,
        font=dict(size=12)
    )

    # Save the plot as an HTML file
    fig.write_html('plot/vrt_by_countyfuelTypes.html')

    # Show the plot
    fig.show()


def proportion_of_ev_plotly():
    # Load data from CSV file
    file_path = "raw_data/VRT.csv"
    df = pd.read_csv(file_path)

    # Convert 'Transaction Month and Year' column to datetime
    df['Transaction Month and Year'] = pd.to_datetime(df['Transaction Month and Year'], format='%m/%d/%Y')

    # Determine if a vehicle is an EV based on the 'Electrification Level'
    df['Is_EV'] = df['Electrification Level'].str.contains('EV|Electric', case=False, na=False)

    # Calculate the total number of EVs and non-EVs
    total_evs = df[df['Is_EV']]['Transaction Count'].sum()
    total_vehicles = df['Transaction Count'].sum()
    total_non_evs = total_vehicles - total_evs

    # Create a pie chart
    labels = ['Electric Vehicles (EVs)', 'Non-Electric Vehicles']
    sizes = [total_evs, total_non_evs]
    colors = ['#ff9999', '#66b3ff']
    explode = (0.1, 0)  # explode the first slice

    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=0.3)])
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                      marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    fig.update_layout(title='Proportion of Electric Vehicle Registrations', title_x=0.5)
    fig.show()
    
    # Determine the time range
    start_date = df['Transaction Month and Year'].min()
    end_date = df['Transaction Month and Year'].max()
    print(f"Data covers from {start_date.year} to {end_date.year}")


def proportion_of_ev_plotly2():
    # Load data from CSV file
    file_path = "raw_data/VRT.csv"
    df = pd.read_csv(file_path)

    # Convert 'Transaction Month and Year' column to datetime
    df['Transaction Month and Year'] = pd.to_datetime(df['Transaction Month and Year'], format='%m/%d/%Y')
    df['Year'] = df['Transaction Month and Year'].dt.year

    # Determine if a vehicle is an EV based on the 'Electrification Level'
    df['Is_EV'] = df['Electrification Level'].str.contains('EV|Electric', case=False, na=False)

    # Group by year and calculate the total number of EVs and non-EVs for each year
    yearly_data = df.groupby('Year').agg(
        total_evs=('Transaction Count', lambda x: x[df['Is_EV']].sum()),
        total_vehicles=('Transaction Count', 'sum')
    ).reset_index()
    yearly_data['total_non_evs'] = yearly_data['total_vehicles'] - yearly_data['total_evs']

    # Create pie charts for each year
    for _, row in yearly_data.iterrows():
        year = row['Year']
        total_evs = row['total_evs']
        total_non_evs = row['total_non_evs']
        
        labels = ['Electric Vehicles (EVs)', 'Non-Electric Vehicles']
        sizes = [total_evs, total_non_evs]
        colors = ['#ff9999', '#66b3ff']
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=0.3)])
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                          marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        fig.update_layout(title=f'Proportion of Electric Vehicle Registrations in {year}', title_x=0.5)
        fig.show()


def top_ten_plotly2():
    data = "raw_data/EVP.csv"

    df = pd.read_csv(data)
    new_df = df[df['State'] == 'WA'].copy()
    new_df['Date'] = pd.to_datetime(new_df['Date'], format='%B %d %Y')
    new_df['Year'] = new_df['Date'].dt.year

    # Group by county and year, then sum the total number of vehicles
    numeric_columns = ['Electric Vehicle (EV) Total', 'Non-Electric Vehicle Total']
    yearly_county_totals = new_df.groupby(['Year', 'County'])[numeric_columns].sum().reset_index()

    # Create a stacked bar plot for each year
    for year in yearly_county_totals['Year'].unique():
        year_df = yearly_county_totals[yearly_county_totals['Year'] == year]
        top_counties = year_df.nlargest(10, 'Electric Vehicle (EV) Total')
        
        fig = px.bar(top_counties, x='County', y=['Electric Vehicle (EV) Total', 'Non-Electric Vehicle Total'],
                     barmode='stack', labels={'value': 'Number of Vehicles', 'variable': 'Vehicle Type'},
                     title=f'Top 10 Counties with Highest Number of Electric Vehicles in {year}',
                     color_discrete_sequence=['blue', 'orange'])

        fig.update_layout(xaxis_tickangle=-45, xaxis_title='County', yaxis_title='Number of Vehicles')
        fig.show()

def top_ten_plotly3():
    data = "raw_data/EVP.csv"

    df = pd.read_csv(data)
    new_df = df[df['State'] == 'WA'].copy()
    new_df['Date'] = pd.to_datetime(new_df['Date'], format='%B %d %Y')
    new_df['Year'] = new_df['Date'].dt.year

    # Check for and remove duplicate entries
    new_df = new_df.drop_duplicates()

    # Remove unrealistic outliers
    numeric_columns = ['Electric Vehicle (EV) Total', 'Non-Electric Vehicle Total']
    for col in numeric_columns:
        new_df = new_df[new_df[col] < new_df[col].quantile(0.99)]  # Remove top 1% as outliers

    # Group by county and year, then sum the total number of vehicles
    yearly_county_totals = new_df.groupby(['Year', 'County'])[numeric_columns].sum().reset_index()

    # Create a stacked bar plot for each year
    for year in yearly_county_totals['Year'].unique():
        year_df = yearly_county_totals[yearly_county_totals['Year'] == year]
        top_counties = year_df.nlargest(10, 'Electric Vehicle (EV) Total')
        
        fig = px.bar(top_counties, x='County', y=['Electric Vehicle (EV) Total', 'Non-Electric Vehicle Total'],
                     barmode='stack', labels={'value': 'Number of Vehicles', 'variable': 'Vehicle Type'},
                     title=f'Top 10 Counties with Highest Number of Electric Vehicles in {year}',
                     color_discrete_sequence=['blue', 'orange'])

        fig.update_layout(xaxis_tickangle=-45, xaxis_title='County', yaxis_title='Number of Vehicles')
        fig.show()

def top_ten_plotly4():
    data = "raw_data/EVP.csv"

    df = pd.read_csv(data)
    new_df = df[df['State'] == 'WA'].copy()
    new_df['Date'] = pd.to_datetime(new_df['Date'], format='%B %d %Y')
    new_df['Year'] = new_df['Date'].dt.year

    # Check for and remove duplicate entries
    new_df = new_df.drop_duplicates()

    # Define a function to remove outliers using IQR
    def remove_outliers(df, column):
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

    # Remove outliers from numeric columns
    numeric_columns = ['Electric Vehicle (EV) Total', 'Non-Electric Vehicle Total']
    for col in numeric_columns:
        new_df = remove_outliers(new_df, col)

    # Group by county and year, then sum the total number of vehicles
    yearly_county_totals = new_df.groupby(['Year', 'County'])[numeric_columns].sum().reset_index()

    # Create a stacked bar plot for each year
    for year in yearly_county_totals['Year'].unique():
        year_df = yearly_county_totals[yearly_county_totals['Year'] == year]
        top_counties = year_df.nlargest(10, 'Electric Vehicle (EV) Total')
        
        fig = px.bar(top_counties, x='County', y=['Electric Vehicle (EV) Total', 'Non-Electric Vehicle Total'],
                     barmode='stack', labels={'value': 'Number of Vehicles', 'variable': 'Vehicle Type'},
                     title=f'Top 10 Counties with Highest Number of Electric Vehicles in {year}',
                     color_discrete_sequence=['blue', 'orange'])

        fig.update_layout(xaxis_tickangle=-45, xaxis_title='County', yaxis_title='Number of Vehicles')
        fig.show()


def geo_plotly2():
    # Load the shapefile for county boundaries
    gdf = gpd.read_file("data_organized/us-county-boundaries.shp")
    wa_gdf = gdf[gdf['stusab'] == 'WA']

    # Load the electric vehicle population data
    ev_count_df = pd.read_csv("data_organized/Electric_Vehicle_Population_Size.csv")
    ev_count_df['Date'] = pd.to_datetime(ev_count_df['Date'], format='%B %d %Y')
    ev_count_df['Year'] = ev_count_df['Date'].dt.year

    # Load fuel stations data
    fuel_stations_df = pd.read_csv("raw_data/fuel_stations.csv")

    # Generate a plot for each year
    for year in ev_count_df['Year'].unique():
        yearly_ev_count_df = ev_count_df[ev_count_df['Year'] == year]
        pop = yearly_ev_count_df.groupby("County").sum()
        merged_gdf = wa_gdf.merge(pop, left_on='name', right_on="County")

        fig = go.Figure()

        # Add county boundaries and EV counts
        fig.add_trace(go.Choroplethmapbox(geojson=merged_gdf.geometry.__geo_interface__,
                                          locations=merged_gdf.index,
                                          z=merged_gdf["Electric Vehicle (EV) Total"],
                                          colorscale="Viridis",
                                          marker_opacity=0.7,
                                          marker_line_width=0))

        # Add fuel stations
        fig.add_trace(go.Scattermapbox(lat=fuel_stations_df["Latitude"],
                                       lon=fuel_stations_df["Longitude"],
                                       mode="markers",
                                       marker=dict(size=4, color="orange"),
                                       name="Fuel Stations"))

        fig.update_layout(mapbox_style="carto-positron",
                          mapbox_zoom=5,
                          mapbox_center={"lat": 47.5, "lon": -120.5},
                          margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          showlegend=True,
                          title=f"Washington State - Electric Vehicle Population and Fuel Stations in {year}")

        fig.show()

def geo_plotly4():
    # Load the shapefile for county boundaries
    gdf = gpd.read_file("data_organized/us-county-boundaries.shp")
    wa_gdf = gdf[gdf['stusab'] == 'WA']

    # Load the electric vehicle population data
    ev_count_df = pd.read_csv("data_organized/Electric_Vehicle_Population_Size.csv")
    ev_count_df['Date'] = pd.to_datetime(ev_count_df['Date'], format='%B %d %Y')
    ev_count_df['Year'] = ev_count_df['Date'].dt.year

    # Load fuel stations data
    fuel_stations_df = pd.read_csv("raw_data/fuel_stations.csv")

    # Generate a plot for each year
    for year in ev_count_df['Year'].unique():
        yearly_ev_count_df = ev_count_df[ev_count_df['Year'] == year]

        # Group by County and sum numeric columns only
        pop = yearly_ev_count_df.groupby("County")['Electric Vehicle (EV) Total'].sum().reset_index()

        # Merge with geographical data
        merged_gdf = wa_gdf.merge(pop, left_on='name', right_on="County")

        fig = go.Figure()

        # Add county boundaries and EV counts
        fig.add_trace(go.Choroplethmapbox(geojson=merged_gdf.geometry.__geo_interface__,
                                          locations=merged_gdf.index,
                                          z=merged_gdf["Electric Vehicle (EV) Total"],
                                          colorscale="Viridis",
                                          marker_opacity=0.7,
                                          marker_line_width=0))

        # Add fuel stations
        fig.add_trace(go.Scattermapbox(lat=fuel_stations_df["Latitude"],
                                       lon=fuel_stations_df["Longitude"],
                                       mode="markers",
                                       marker=dict(size=4, color="orange"),
                                       name="Fuel Stations"))

        fig.update_layout(mapbox_style="carto-positron",
                          mapbox_zoom=5,
                          mapbox_center={"lat": 47.5, "lon": -120.5},
                          margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          showlegend=True,
                          title=f"Washington State - Electric Vehicle Population and Fuel Stations in {year}")

        fig.show()

def geo_plotly5():
    # Load the shapefile for county boundaries
    gdf = gpd.read_file("data_organized/us-county-boundaries.shp")
    wa_gdf = gdf[gdf['stusab'] == 'WA']

    # Load the electric vehicle population data
    ev_count_df = pd.read_csv("data_organized/Electric_Vehicle_Population_Size.csv")
    ev_count_df['Date'] = pd.to_datetime(ev_count_df['Date'], format='%B %d %Y')
    ev_count_df['Year'] = ev_count_df['Date'].dt.year

    # Load fuel stations data
    fuel_stations_df = pd.read_csv("raw_data/fuel_stations.csv")

    # Generate a plot for each year
    for year in ev_count_df['Year'].unique():
        yearly_ev_count_df = ev_count_df[ev_count_df['Year'] == year]

        # Group by County and sum numeric columns only
        pop = yearly_ev_count_df.groupby("County")['Electric Vehicle (EV) Total'].sum().reset_index()

        # Merge with geographical data
        merged_gdf = wa_gdf.merge(pop, left_on='name', right_on="County")

        fig = go.Figure()

        # Add county boundaries and EV counts
        fig.add_trace(go.Choroplethmapbox(geojson=merged_gdf.geometry.__geo_interface__,
                                          locations=merged_gdf.index,
                                          z=merged_gdf["Electric Vehicle (EV) Total"],
                                          colorscale="Viridis",
                                          marker_opacity=0.7,
                                          marker_line_width=0))

        # Add fuel stations
        fig.add_trace(go.Scattermapbox(lat=fuel_stations_df["Latitude"],
                                       lon=fuel_stations_df["Longitude"],
                                       mode="markers",
                                       marker=dict(size=4, color="orange"),
                                       name="Fuel Stations"))

        fig.update_layout(mapbox_style="carto-positron",
                          mapbox_zoom=5,
                          mapbox_center={"lat": 47.5, "lon": -120.5},
                          margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          showlegend=True,
                          title=f"Washington State - Electric Vehicle Population and Fuel Stations in {year}",
                          annotations=[dict(
                              text=f"Year: {year}",
                              x=0.5,
                              y=0.1,
                              showarrow=False,
                              font=dict(size=16),
                              xref="paper",
                              yref="paper"
                          )])
        
        fig.show()


def top_ten_plotly4():
    data = "raw_data/EVP.csv"

    df = pd.read_csv(data)
    new_df = df[df['State'] == 'WA'].copy()
    new_df['Date'] = pd.to_datetime(new_df['Date'], format='%B %d %Y')

    # Filter data for the year 2023
    new_df = new_df[new_df['Date'].dt.year == 2023]

    # Convert 'Date' column to string format
    new_df['Date'] = new_df['Date'].dt.strftime('%B %d %Y')

    # Group by county and sum the total number of vehicles
    county_totals = new_df.groupby('County').sum()

    # Sort by electric vehicle total and select the top 10 counties
    top_counties = county_totals.nlargest(10, 'Electric Vehicle (EV) Total')

    # Create a stacked bar plot comparing the number of electric and non-electric vehicles for the top N counties
    fig = px.bar(top_counties, x=top_counties.index, y=['Electric Vehicle (EV) Total', 'Non-Electric Vehicle Total'],
                 barmode='stack', labels={'value': 'Number of Vehicles', 'variable': 'Vehicle Type'},
                 title='Top 10 Counties with Highest Number of Electric Vehicles in 2023',
                 color_discrete_sequence=['blue', 'orange'])

    # Add text annotation for the date range
    fig.update_layout(xaxis_tickangle=-45, xaxis_title='County', yaxis_title='Number of Vehicles',
                      annotations=[dict(x=0.5, y=-0.15, showarrow=False,
                                        text="Data from: {} to {}".format(new_df['Date'].min(), new_df['Date'].max()),
                                        xref="paper", yref="paper")])
    fig.show()

