# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the launch site data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

#All this looooong workaround just for the dropdown sice there is no way to
#create one with a hardcoded item and the others made from iterating over an iterable (gives layout error in the browser).
series_unique_site_names = pd.Series(spacex_df['Launch Site'].unique()) #get the unique site names as a Pandas Series object
df_for_dropdown = pd.concat([series_unique_site_names, series_unique_site_names], axis=1) #make a dataframe with two columns with the same strings
df_for_dropdown.loc[-1] = ['All Sites', 'ALL'] #add a row with the hardcoded strings with -1 index
df_for_dropdown.index = df_for_dropdown.index + 1  # shift indexes so -1 becomes 0 and so on
df_for_dropdown.sort_index(inplace=True) # added row with hardcoded valoes will appear as first in the dropdown menu

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),
                                
                                dcc.Dropdown(id='site-dropdown',
                                         options=[
                                             #{'label': 'All Sites', 'value': 'ALL'},
                                             #{'label': 'site1', 'value': 'site1'},
                                             #({'label': i, 'value': i} for i in spacex_df['Launch Site'].unique())  --> dunno why this simpler code gives error in browser!!!
                                             {'label': i, 'value': j} for i, j in zip(df_for_dropdown[0], df_for_dropdown[1]) #0->labels, #1->values/IDs
                                         ],
                                         value='ALL',
                                         placeholder="Select a Launch Site here",
                                         searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    #marks=[{i: i} for i in range(0, 10000, 1000)], --> this doesn't work! Bad, bad, Plotly!
                                    marks={0: '0', 1000: '1000', 2000: '2000', 3000: '3000', 4000: '4000', 5000: '5000'
                                           , 6000: '6000', 7000: '7000', 8000: '8000', 9000: '9000', 10000: '10000'},
                                    value=[min_payload, max_payload]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df[spacex_df['class']==1]
        fig = px.pie(filtered_df, 
                     values='class', #only works if class is 1.  Any other values will likely result in wrong proportions.
                     names='Launch Site', 
                     title='Total successful launches by site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        filtered_df['counter'] = 1 #adding a counter column to get the correct proportions of 1's (successes) and 0's (failures) in the pie chart
        di = {0: "Failure", 1: "Success"} #The 0's and 1's will be replaced with their textual meanings in the resulting chart.
        filtered_df["class"].replace(di, inplace=True)  #filtered_df['class'].map(di).fillna(filtered_df['class']) is faster but it's giving a warn and replace is not done
        fig = px.pie(filtered_df, 
                     values='counter', 
                     names='class', 
                     title='Mission outcomes for site ' + entered_site)
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value'))
def get_scatter_plot(entered_site, entered_payload_range_kg):
    if entered_site == 'ALL':
        #Filter by payload range only.
        filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(entered_payload_range_kg[0], entered_payload_range_kg[1])]
        title="Correlation between Payload and Success for all sites (between " + str(entered_payload_range_kg[0]) + "kg and " + str(entered_payload_range_kg[1]) + "kg)"
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class", color="Booster Version Category", title=title)
        return fig
    else:
        #Filter by selected launch site.
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        #Filter by payload range.
        filtered_df = filtered_df[filtered_df['Payload Mass (kg)'].between(entered_payload_range_kg[0], entered_payload_range_kg[1])]
        title="Correlation between Payload and Success for " + entered_site + " site (between " + str(entered_payload_range_kg[0]) + " and " + str(entered_payload_range_kg[1]) + "kg)"
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class", color="Booster Version Category", title=title)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
