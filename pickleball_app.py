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
        # st.error("Config file not found locally.")
        return None, None

MAGIC_STRING, openai_api_key = load_local_settings()
if MAGIC_STRING is None or openai_api_key is None:
    # Fetch settings from Streamlit Cloud secrets
    MAGIC_STRING = st.secrets["general"]["magic_string"]
    openai_api_key = st.secrets["general"]["openai_api_key"]

# Title of the Streamlit app
st.title('Pickleball Facility Reservation Insights')

# Magic string authentication
user_input = st.text_input("Enter the magic string to access the app:")

if user_input == MAGIC_STRING:
    # Assume the CSV file is present locally as combined_reservation_data.csv
    file_path = "combined_total_data.csv"
    # Initialize OpenAI client with the API key
    client = OpenAI(api_key=openai_api_key)
    try:
        # Load the data directly from the CSV file
        data = pd.read_csv(file_path)

        # Calculate key metrics
        total_revenue = data['Revenue'].sum() / data['Date'].nunique()
        # Convert the DataFrame to JSON (records format)
        json_data = data.to_json(orient="records")
        st.header("Ask AI")   
        # Text box for user queries
        query = st.text_input("Ask for insights or analysis related to the data:")
        if query:
            try:
                # Initialize the response_text to accumulate the chunks
                response_text = ""

                if not st.session_state.data_sent:
                    # Send the dataset with the first query, using streaming
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a data analyst."},
                            {"role": "user", "content": f"Here is my dataset: {json_data}. {query}"}
                        ],
                        stream=True
                    )
                    # Mark the data as sent
                    st.session_state.data_sent = True
                else:
                    # Send follow-up queries without the dataset, using streaming
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a data analyst."},
                            {"role": "user", "content": f"Here is my dataset: {json_data}. {query}"}
                        ],
                        stream=True
                    )

                # Iterate over the stream and collect the response chunks
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        response_text += chunk.choices[0].delta.content
                # Only display the response if there is any accumulated content
                st.subheader("Response from OpenAI")
                # Step 3: Display OpenAI response
                st.write(response_text)

            except Exception as e:
                st.error(f"Error communicating with OpenAI: {e}")
        
        
        # Display key metrics
        st.header("Key Metrics")
        st.metric("Avg Daily Total Revenue ($)", f"${total_revenue:,.2f}")

        # Initialize session state to track if data has been sent
        if "data_sent" not in st.session_state:
            st.session_state.data_sent = False
       

    # Display the data
        st.header("Reservation Data")
        st.dataframe(data)

        # Provide the ability to download the processed data
        csv_data = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv_data,
            file_name='processed_reservation_data.csv',
            mime='text/csv',
        )
    except FileNotFoundError:
        st.error("The file combined_reservation_data.csv was not found.")
else:
    st.write("Please enter the correct magic string to access the app.")
