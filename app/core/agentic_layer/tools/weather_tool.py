# agentic_layer/tools/weather_tool.py
import requests
from agentic_layer.tools import ReusableTool

class WeatherTool(ReusableTool):
    name = "get_weather"
    description = "Fetch current weather for a given city using an external weather API."

    def _run(self, city: str) -> str:
        api_key = "your_weather_api_key"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                return f"🌤️ The weather in {city} is {desc} with {temp}°C."
            else:
                return f"⚠️ Could not fetch weather for {city}."
        except Exception as e:
            return str(e)
