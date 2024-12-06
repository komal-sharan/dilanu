import streamlit as st
import requests
import google.generativeai as palm
import jwt
import datetime
import ssl
import certifi
import pytz
from geopy.geocoders import Nominatim

# Configure Palm API
palm.configure(api_key="AIzaSyAEVqt8aK8F81m3yO0dNpCw2Fww4GPCTUc")

# Define function to get latitude and longitude from place name
def get_lat_lon(place_name):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    geolocator = Nominatim(user_agent="geo_locator", ssl_context=ssl_context)
    location = geolocator.geocode(place_name)

    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Generate JWT token
public_key = "jVHXSTMhKqKyW2z9SwxKoj45"
secret_key = "behavior news billion buy enough health think sit station the"

def generate_token():
    payload = {
        'iss': 'prodilanu.com',
        'sub': 'komalssharan@gmail.com',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=3600),
        'iat': datetime.datetime.now(datetime.timezone.utc)
    }
    token = jwt.encode(payload, key=secret_key, algorithm='HS256')
    return token

# Check the token
jwt_token = generate_token()

url = "https://prodilanu.com/api/user-match/"
headers = {
    "Authorization": f"Bearer {jwt_token}", 
    "Content-Type": "application/json",
    "Public-Key": public_key
}

# Timezone mapping
timezones = {
    "Pacific Time (US & Canada)": "US/Pacific",
    "Eastern Time (US & Canada)": "US/Eastern",
    "Central European Time": "Europe/Berlin",
    "India Standard Time": "Asia/Kolkata",
    "China Standard Time": "Asia/Shanghai",
    "Greenwich Mean Time": "Etc/Greenwich",
    "Japan Standard Time": "Asia/Tokyo",
    "Australian Eastern Time": "Australia/Sydney",
}

# Add login screen
def login():
    st.title("Astrological Compatibility Analyzer - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Simple hardcoded authentication (replace with real logic in production)
    if username == "dilanuser" and password == "universe":
        st.session_state.logged_in = True
        st.session_state.username = username  # Store the username (optional)
        st.success("Login successful!")
        return True
    else:
        if username and password:
            st.error("Invalid username or password")
        else:
            st.warning("Please enter your username and password.")
        return False

# Main application function (only shows if logged in)
def main():
    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        if not login():
            return
    
    # Main app content - show once logged in
    st.title("Astrological Compatibility Analyzer")
    st.header("Enter Birth Details of Two Individuals")
    
    # Input for Person 1
    st.subheader("Person 1")
    name1 = st.text_input("Name", key="name1")

    date1 = st.date_input(
    "Select a date",
    value=datetime.date.today(),  
    min_value=datetime.date(1900, 1, 1),  
    max_value=datetime.date(2100, 12, 31))

    time1 = st.text_input("Enter time in 24-hour format (HH:MM:SS)", key="time1")
    place1 = st.text_input("Place of Birth", key="place1")
    tz_offset1 = 0
    selected_tz1 = st.selectbox("Select a time zone1", list(timezones.keys()), key="tz1")

    if selected_tz1:
        tz_name = timezones[selected_tz1]
        now = datetime.datetime.now(pytz.timezone(tz_name))
        tz_offset1 = now.utcoffset().total_seconds() / 3600  # Offset in hours
    
    # Input for Person 2
    st.subheader("Person 2")
    name2 = st.text_input("Name", key="name2")

    date2 = st.date_input(
    "Select a date1",
    value=datetime.date.today(),  
    min_value=datetime.date(1900, 1, 1),  
    max_value=datetime.date(2100, 12, 31))

    time2 = st.text_input("Enter time in 24-hour format (HH:MM:SS)", key="time2")
    place2 = st.text_input("Place of Birth", key="place2")
    lat2, long2 = get_lat_lon(place2)
    tz_offset2 = 0
    selected_tz2 = st.selectbox("Select a time zone2", list(timezones.keys()), key="tz2")

    if selected_tz2:
        tz_name = timezones[selected_tz2]
        now = datetime.datetime.now(pytz.timezone(tz_name))
        tz_offset2 = now.utcoffset().total_seconds() / 3600  # Offset in hours
    
    if st.button("Analyze Compatibility"):
        # Validate inputs
        if all([name1, date1, time1, place1, name2, date2, time2, place2]):
            
            date1 = date1.strftime('%Y-%m-%d')
            date2 = date2.strftime('%Y-%m-%d')
            datetime1 = datetime.datetime.strptime(time1, '%H:%M:%S')
            time1 = datetime1.strftime('%H:%M:%S')
            datetime2 = datetime.datetime.strptime(time2, '%H:%M:%S')
            time2 = datetime2.strftime('%H:%M:%S')

            lat1, long1 = get_lat_lon(place1)

            payload = {
                "user": {
                    "id": "1", 
                    "bdatetime": date1 + " " + str(time1),
                    "blat": lat1, 
                    "blon": long2, 
                    "tz": tz_offset1
                },
                "matches": [{
                    "id": "2", 
                    "bdatetime": date2 + " " + str(time2),
                    "blat": lat2, 
                    "blon": long2, 
                    "tz": tz_offset2
                }]
            }

            url = "https://prodilanu.com/api/user-match/"
            try:
                response_api = requests.post(url, headers=headers, json=payload)

                if response_api.status_code == 200:
                    print("Request successful!")
                    print("Response:", response_api.json())
                else:
                    print("Request failed!")
                    print("Response:", response_api.text)

                model = palm.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(f"Given these results tell me about the compatibility of the two people{str(response_api.json())}")

                # Display result
                st.subheader("Compatibility Analysis Result")
                st.text_area("Output", response.text, height=300)

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to API: {e}")
        else:
            st.warning("Please fill in all fields for both individuals.")
    
if __name__ == "__main__":
    main()
