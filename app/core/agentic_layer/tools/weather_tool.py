import requests
from app.core.agentic_layer.tools.base_tool import ReusableTool


class WeatherTool(ReusableTool):
    name: str = "get_weather"
    description: str = (
        "Fetch current weather for a given city using an external weather API."
    )

    def _run(self, city: str) -> str:
        api_key = "your_weather_api_key"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"🌤️ The weather in {city} is {desc} with {temp}°C."
            else:
                return f"⚠️ Could not fetch weather for {city}. API responded with {response.status_code}"
        except Exception as e:
            return f"⚠️ Error while fetching weather: {str(e)}"

    async def _arun(self, *args, **kwargs) -> str:
        raise NotImplementedError("Async not implemented for WeatherTool.")
