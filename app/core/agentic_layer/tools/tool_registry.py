# agentic_layer/tool_registry.py
from langchain.tools import Tool
from app.core.agentic_layer.tools.vehicle_booking_tool import VehicleBookingTool
from app.core.agentic_layer.tools.weather_tool import WeatherTool
from app.core.agentic_layer.tools.feedback_tool import FeedbackTool

def get_registered_tools():
    """
    Registers and returns all available tools for the Agent.
    """
    return [
        VehicleBookingTool().as_tool(),
        WeatherTool().as_tool(),
        FeedbackTool().as_tool(),
    ]
