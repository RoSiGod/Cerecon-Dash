import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="Timesheet Data Analyzer", page_icon=":bar_chart:", layout="wide")

def fetch_timesheet_data(api_key, slug, start_date_int, num_weeks, ID):
    """Fetches timesheet data from the API for a given date range."""

    url_base = 'https://api.totalsynergy.com/api/v2/Organisation/'
    target_URL = 'Timesheet/Week/'
    headers = {'access-token': api_key}
    all_weeks_data = []

    for i in range(num_weeks):
        current_week_start = start_date_int + timedelta(weeks=i)
        url_config = url_base + slug + target_URL
        params = {'includeCustomFields': 'true', 'criteria.id': ID, 'DateAsInt': int(current_week_start.strftime('%Y%m%d'))}
        response = requests.get(url_config, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if 'time' in data:
                for entry in data['time']:
                    project = entry.get('project')
                    stage = entry.get('stage')
                    mon = entry.get('mon', 0)
                    tue = entry.get('tue', 0)
                    wed = entry.get('wed', 0)
                    thu = entry.get('thu', 0)
                    fri = entry.get('fri', 0)
                    total_hours = mon + tue + wed + thu + fri
                    all_weeks_data.append({'Stage': stage, 'Project': project, 'Total Hours': total_hours})
        else:
            print(f"Error fetching data for week starting {current_week_start}: {response.status_code}")
            print(response.text)
    return pd.DataFrame(all_weeks_data)


def create_project_hours_chart(df):
    """Creates a bar chart of total hours by project using Plotly."""

    df_agg_project = df.groupby('Project')['Total Hours'].sum().reset_index()

    chart = px.bar(
        df_agg_project.sort_values(by='Total Hours', ascending=False),
        x='Project',
        y='Total Hours',
        title='Total Hours by Project',
        labels={'Total Hours': 'Total Hours', 'Project': 'Project'},  # More explicit labels
        
    )
    chart.update_layout(
        xaxis_tickangle=-45,  # Rotate x-axis labels for readability
        xaxis_title_standoff=25,
        yaxis_title_standoff=25,
    )

    return chart

def create_stage_hours_chart(df):
    """Creates a bar chart of total hours by project using Plotly."""

    df_agg_stage = df.groupby('Stage')['Total Hours'].sum().reset_index()

    chart = px.bar(
        df_agg_stage.sort_values(by='Total Hours', ascending=False),
        x='Stage',
        y='Total Hours',
        title='Total Hours by Stage',
        labels={'Total Hours': 'Total Hours', 'Stage': 'Stage'},  # More explicit labels
        
    )
    chart.update_layout(
        xaxis_tickangle=-90,  # Rotate x-axis labels for readability
        xaxis_title_standoff=25,
        yaxis_title_standoff=25,
    )

    return chart


def create_project_cost_chart(df):
    """Creates a bar chart of total cost by project using Plotly."""

    df_agg_project = df.groupby('Project')['Total Hours'].sum().reset_index()
    df_agg_project['Total Cost'] = df_agg_project['Total Hours']*210
 

    chart = px.bar(
        df_agg_project.sort_values(by='Total Cost', ascending=False),
        x='Project',
        y='Total Cost',
        
        title='Total Cost by Project',
        labels={'Total Hours': 'Total Cost (AUD)', 'Project': 'Project'},  # More explicit labels
        
    )
    chart.update_layout(
        xaxis_tickangle=-45,  # Rotate x-axis labels for readability
        xaxis_title_standoff=25,
        yaxis_title_standoff=25,
    )

    return chart

def create_stage_cost_chart(df):
    """Creates a bar chart of total cost by project using Plotly."""

    df_agg_project = df.groupby('Stage')['Total Hours'].sum().reset_index()
    df_agg_project['Total Cost'] = df_agg_project['Total Hours']*210

    chart = px.bar(
        df_agg_project.sort_values(by='Total Cost', ascending=False),
        x='Stage',
        y='Total Cost',
        color = 'Stage',
        title='Total Cost by Project',
        labels={'Total Hours': 'Total Cost (AUD)', 'Stage': 'Stage'},  # More explicit labels
        
    )
    chart.update_layout(
        xaxis_tickangle=-45,  # Rotate x-axis labels for readability
        xaxis_title_standoff=25,
        yaxis_title_standoff=25,
    )

    return chart




def main():
    st.title("Timesheet Data Analyzer")

    # API Key Input
    api_key_default = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InNnb2Rib2xlQGNlcmVjb24uY29tLmF1IiwiYXBwbGljYXRpb25pZCI6MCwidXNlcm5hbWUiOiJzaWRkaGVzaCIsInRlbmFudCI6IiIsImNvZGVfZXhwaXJlcyI6NjM5MTA4NjI3ODg1NjcxMDg0LCJ1c2VyX3R5cGUiOiIyIn0.hlIw1TaEMZLcTU8jcQD_iJ7bFExkZv54ZZQyHaKpLTw'

    api_key = st.text_input('Enter API Key',value = api_key_default)
    if st.button('help me find my API KEY'):
        st.text('In Synergy, click on the top right menu icon and choose "edit profile')
        st.text('Under the profile page, click the menu elipsis and choose API key')
        st.text('Copy the complete API key and use it as as an access-token')
        st.text('This API key is valid for one or three years, depending which one you choose.')
    
    # # Slug Input
    slug = "cerecon/"

    # Enter employee ID
    ID = st.text_input('Enter Employee ID', value = "9502417")

    # Date Selection
    selected_date = st.date_input("Select a date:", datetime.now().date())

    # Number of Weeks Input
    num_weeks_back = st.number_input("Enter the number of weeks to go back:", min_value=1, max_value=52, value=12)



    if st.button("Fetch and Analyze Data"):
        if api_key:
            start_date = selected_date - timedelta(weeks=num_weeks_back - 1)
            start_date_int = start_date

            with st.spinner("Fetching data..."):
                data_df = fetch_timesheet_data(api_key, slug, start_date, num_weeks_back, ID)
                

                all_data_df = data_df


            if not all_data_df.empty:
                st.subheader("Raw Data:")
                st.dataframe(all_data_df)

                with st.container(height=500):
                    col1, col2 = st.columns([1,1])
                    with col1:
                        st.subheader("Total Hours by Project:")
                        project_hours_chart = create_project_hours_chart(all_data_df)
                        st.plotly_chart(project_hours_chart, use_container_width=True)
                    with col2:
                        st.subheader("Total Cost by Project")
                        project_cost_chart = create_project_cost_chart(all_data_df)
                        st.plotly_chart(project_cost_chart, theme = None, use_container_width=True)

                with st.container(height=1000):
                    st.subheader("Total Hours by Stage:")
                    project_hours_chart = create_stage_hours_chart(all_data_df)
                    st.plotly_chart(project_hours_chart,theme = 'streamlit', use_container_width=True)
                with st.container(height=1000):   
                    st.subheader("Total Cost by Stage")
                    project_cost_chart = create_stage_cost_chart(all_data_df)
                    st.plotly_chart(project_cost_chart, theme = 'streamlit',  use_container_width=True)


            else:
                st.warning("No data fetched. Please check your API key and date range.")
        else:
            st.error("Please enter your API Key.")


if __name__ == "__main__":
    main()
