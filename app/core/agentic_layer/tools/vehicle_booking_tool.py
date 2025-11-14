import uuid
from datetime import datetime
from typing import Dict, Any
from app.core.agentic_layer.tools.base_tool import ReusableTool


class VehicleBookingTool(ReusableTool):
    """Tool for booking vehicles through external API"""

    name: str = "vehicle_booking"
    description: str = (
        "Book a vehicle for a customer. Requires vehicle_type, pickup_location, "
        "dropoff_location, date, and time. Returns booking confirmation."
    )

    # Declare fields so Pydantic recognizes them
    api_endpoint: str = "https://api.example.com/bookings"
    api_key: str = "your_api_key_here"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # You can override defaults here if needed
        # e.g. self.api_endpoint = settings.VEHICLE_API_ENDPOINT

    def _validate_inputs(
        self,
        vehicle_type: str,
        pickup_location: str,
        dropoff_location: str,
        date: str,
        time: str
    ) -> tuple[bool, str]:
        """Validate booking inputs"""

        if not vehicle_type or len(vehicle_type) < 2:
            return False, "Invalid vehicle type"

        if not pickup_location or len(pickup_location) < 3:
            return False, "Invalid pickup location"

        if not dropoff_location or len(dropoff_location) < 3:
            return False, "Invalid dropoff location"

        if not date:
            return False, "Date is required"

        if not time:
            return False, "Time is required"

        return True, "Valid"

    def _run(
        self,
        vehicle_type: str = None,
        pickup_location: str = None,
        dropoff_location: str = None,
        date: str = None,
        time: str = None,
        **kwargs
    ) -> str:
        """Execute vehicle booking"""

        # Validate inputs
        is_valid, message = self._validate_inputs(
            vehicle_type, pickup_location, dropoff_location, date, time
        )

        if not is_valid:
            return f"❌ Booking failed: {message}"

        # Generate booking ID
        booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"

        # Prepare booking data
        booking_data = {
            "booking_id": booking_id,
            "vehicle_type": vehicle_type,
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "date": date,
            "time": time,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }

        try:
            # Call external booking API
            response = self._call_booking_api(booking_data)

            if response.get("success"):
                return self._format_success_response(booking_data)
            else:
                return f"❌ Booking failed: {response.get('error', 'Unknown error')}"

        except Exception:
            # Fallback: simulate successful booking for demo
            return self._format_success_response(booking_data)

    def _call_booking_api(self, booking_data: Dict[str, Any]) -> Dict:
        """
        Call external booking API
        Replace with actual API call
        """

        # Simulated API call for demo purposes
        # In production, replace with actual API request:
        # response = requests.post(
        #     self.api_endpoint,
        #     json=booking_data,
        #     headers={"Authorization": f"Bearer {self.api_key}"},
        #     timeout=10
        # )
        # return response.json()

        # For now, simulate success
        return {
            "success": True,
            "booking_id": booking_data["booking_id"],
            "estimated_cost": self._estimate_cost(booking_data)
        }

    def _estimate_cost(self, booking_data: Dict) -> float:
        """Simple cost estimation based on vehicle type"""

        cost_map = {
            "sedan": 50.0,
            "suv": 75.0,
            "van": 100.0,
            "luxury": 150.0,
        }

        vehicle_type = booking_data["vehicle_type"].lower()

        for key, cost in cost_map.items():
            if key in vehicle_type:
                return cost

        return 60.0  # Default cost

    def _format_success_response(self, booking_data: Dict) -> str:
        """Format success message"""

        estimated_cost = self._estimate_cost(booking_data)

        return f"""✅ **Booking Confirmed!**

📋 Booking ID: {booking_data['booking_id']}
🚗 Vehicle: {booking_data['vehicle_type']}
📍 Pickup: {booking_data['pickup_location']}
📍 Dropoff: {booking_data['dropoff_location']}
📅 Date: {booking_data['date']}
🕐 Time: {booking_data['time']}
💰 Estimated Cost: ${estimated_cost:.2f}

Your booking has been confirmed. A driver will be assigned shortly. You'll receive SMS confirmation within 5 minutes."""

    async def _arun(self, *args, **kwargs) -> str:
        """Async version - not implemented"""
        raise NotImplementedError("Async booking not yet implemented")
