# agentic_layer/tools/vehicle_booking_tool.py
import requests
from agentic_layer.tools import ReusableTool

class VehicleBookingTool(ReusableTool):
    name = "book_vehicle"
    description = "Book or hail a vehicle based on user details such as pickup, dropoff, and vehicle type."

    def _run(self, pickup: str, dropoff: str, vehicle_type: str = "sedan") -> str:
        api_url = "https://example.com/api/book_vehicle"
        payload = {
            "pickup": pickup,
            "dropoff": dropoff,
            "vehicle_type": vehicle_type
        }

        try:
            response = requests.post(api_url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return f"✅ Vehicle booked successfully! Booking ID: {data.get('booking_id')}"
            else:
                return f"❌ Failed to book vehicle. API responded with {response.status_code}"
        except Exception as e:
            return f"⚠️ Error while booking vehicle: {str(e)}"
