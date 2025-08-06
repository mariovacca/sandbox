# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list here
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # TASK 3: Add a slider to select payload
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, 
        max=10000, 
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For all sites, show overall success rate by site
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site'
        )
        return fig
    else:
        # For a specific site, filter data and show success vs. failure
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Count successes and failures
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        
        # Map 0/1 to Failure/Success for better readability in pie chart
        success_counts['class'] = success_counts['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(
            success_counts, 
            values='count', 
            names='class', 
            title=f'Success vs Failure Rate for {entered_site}'
        )
        return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    # Filter by payload range
    low, high = payload_range
    df_payload = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                          (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        # For all sites
        fig = px.scatter(
            df_payload, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites',
            labels={'class': 'Launch Outcome (0=Failure, 1=Success)'}
        )
        return fig
    else:
        # For a specific site
        filtered_df = df_payload[df_payload['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for {entered_site}',
            labels={'class': 'Launch Outcome (0=Failure, 1=Success)'}
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run()
