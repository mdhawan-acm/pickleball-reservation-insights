import os
import streamlit as st
import pandas as pd
import yaml
from openai import OpenAI

# Function to load settings locally from config.yaml
def load_local_settings():
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
            return config["magic_string"], config["openai_api_key"]
    except FileNotFoundError:
        st.error("Config file not found locally.")
        return None, None

# Determine if running locally or on Streamlit Cloud
if "STREAMLIT_SERVER_URL" in os.environ:
    # Running on Streamlit Cloud: Fetch settings from secrets
    MAGIC_STRING = st.secrets["general"]["magic_string"]
    openai_api_key = st.secrets["general"]["openai_api_key"]
else:
    # Running locally: Load settings from the local file
    MAGIC_STRING, openai_api_key = load_local_settings()

# Title of the Streamlit app
st.title('Pickleball Facility Reservation Insights')

# Initialize OpenAI client with the API key
client = OpenAI(api_key=openai_api_key)

# Magic string authentication
user_input = st.text_input("Enter the magic string to access the app:")

if user_input == MAGIC_STRING:
    # Upload the CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Load the data
        data = pd.read_csv(uploaded_file)

        # Convert Fees to numeric values
        data['Fees'] = data['Fees'].replace('[\$,]', '', regex=True).astype(float)

        # Calculate Revenue
        data['Revenue'] = data['Fees'] * data['Registrants']

        # Function to count courts booked
        def count_courts(court_string):
            if pd.isna(court_string):
                return 0
            return len(court_string.split(','))

        # Add a column for the number of courts booked
        data['CourtCount'] = data['Court'].apply(count_courts)

        # Calculate court utilization (court hours used)
        data['CourtUtilization'] = data['CourtCount'] * data['Duration']

        # Calculate key metrics
        total_revenue = data['Revenue'].sum()
        total_court_utilization = data['CourtUtilization'].sum()
        total_registrants = data['Registrants'].sum()

        # Display key metrics
        st.header("Key Metrics")
        st.metric("Total Revenue ($)", f"${total_revenue:,.2f}")
        st.metric("Total Court Utilization (Court-Hours)", total_court_utilization)
        st.metric("Total Registrants", total_registrants)

        # Display the data
        st.header("Reservation Data")
        st.dataframe(data)

        # Step 1: Text box to query OpenAI's LLM
        query = st.text_input("Ask for insights or analysis related to the data:")

        if query:
            # Step 2: Send query to OpenAI and get response
            try:
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": query}],
                    stream=True,
                )
                response_text = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        response_text += chunk.choices[0].delta.content
                # Step 3: Display OpenAI response
                st.subheader("Response from OpenAI")
                st.write(response_text)
            except Exception as e:
                st.error(f"Error communicating with OpenAI: {e}")

    else:
        st.write("Please upload a CSV file to view insights.")
else:
    st.write("Please enter the correct magic string to access the app.")
