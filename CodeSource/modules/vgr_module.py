import requests
import configparser
import os
import time
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime, timedelta
import pytz
import math


class VGRModule:
    def __init__(self, config):
        

        # Read the API key from the provided config
        self.api_key = config['Departure']['vgr_token']
        self.access_token = None
        self.token_expiry = None


    # Function to get an access token
    def get_access_token(self):
    
        # Retrieve a new access token if expired or not set
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        # API Call
        url = "https://ext-api.vasttrafik.se/token"
        auth_encoded = self.api_key

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_encoded}"
        }
        payload = "grant_type=client_credentials"
        response = requests.post(url, headers=headers, data=payload)

        # Handle response from API
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            expires_in = data.get("expires_in", 86400)  # Default to 24 hours if not provided
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)  # Buffer to prevent exact expiry issues
            return self.access_token
        else:
            print("Failed to retrieve access token:", response.status_code, response.text)
            return None

    def get_departures(self, stop_gid):
       
        # Get the access token
        access_token = self.get_access_token()

        if not access_token:
            return []
        
        url = f"https://ext-api.vasttrafik.se/pr/v4/stop-areas/{stop_gid}/departures"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}.")
            return []

        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON. Response is not in JSON format.")
            return []

        results = response_data.get("results", [])  # Ensure this is the correct key

        departures = []
        for result in results:
            try:
                service_journey = result.get("serviceJourney", {})
                line_info = service_journey.get("line", {})
                direction_details = service_journey.get("directionDetails", {})

                short_name = line_info.get("shortName", "Unknown")
                planned_time = result.get("plannedTime", "Unknown")
                estimated_time = result.get("estimatedTime", "Unknown")
                is_Cancelled = result.get("isCancelled", False)
                direction = direction_details.get("shortDirection", "Unknown")  # Check if direction exists

                departures.append({
                    "shortName": short_name,
                    "plannedTime": planned_time,
                    "estimatedTime": estimated_time,
                    "direction": direction,
                    "isCancelled": is_Cancelled
                })
            except Exception as e:
                print("Error processing departure:", e)

        return departures