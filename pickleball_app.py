import streamlit as st
import pandas as pd
import openai

# Hardcoded OpenAI API key
openai.api_key = "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"

# Define your magic string
MAGIC_STRING = "ACM"

# Title of the Streamlit app
st.title('Pickleball Facility Reservation Insights')

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

        # Additional features can be added here like filtering by date, court, or coach

    else:
        st.write("Please upload a CSV file to view insights.")
else:
    st.write("Please enter the correct magic string to access the app.")
