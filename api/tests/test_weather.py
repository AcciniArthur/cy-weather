from datetime import datetime, timezone
from fastapi.testclient import TestClient

from main import app
from src.models.Weather import WeatherResponse, CurrentWeatherData

client = TestClient(app)

def test_current_weather_ok(monkeypatch):
    async def fake_get_current_weather(city: str, country_code=None):
        return WeatherResponse(
            city="Paris",
            country="FR",
            timestamp=datetime(2026, 1, 13, 12, 0, 0, tzinfo=timezone.utc),
            weather=CurrentWeatherData(
                temperature=10.5,
                feels_like=9.0,
                humidity=80,
                pressure=1015,
                wind_speed=3.2,
                description="Couvert",
                icon="04d",
            ),
        )

    # IMPORTANT : on patch l'objet importé dans le module weather_resource
    from src.resources import weather_resource
    monkeypatch.setattr(weather_resource.weather_service, "get_current_weather", fake_get_current_weather)

    r = client.get("/api/weather/current?city=Paris&country_code=FR")
    assert r.status_code == 200

    data = r.json()
    assert data["city"] == "Paris"
    assert data["country"] == "FR"
    assert data["weather"]["temperature"] == 10.5


def test_current_weather_city_required():
    r = client.get("/api/weather/current")
    assert r.status_code == 422  # validation FastAPI





import httpx

def test_current_weather_not_found(monkeypatch):
    async def fake_get_current_weather(city: str, country_code=None):
        # on construit une HTTPStatusError 404 comme ferait httpx
        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(404, request=request)
        raise httpx.HTTPStatusError("Not found", request=request, response=response)

    from src.resources import weather_resource
    monkeypatch.setattr(weather_resource.weather_service, "get_current_weather", fake_get_current_weather)

    r = client.get("/api/weather/current?city=NopeCity")
    assert r.status_code == 404
    assert "non trouvée" in r.json()["detail"]


from src.models.Weather import ForecastResponse, DailyForecastData

def test_forecast_ok(monkeypatch):
    async def fake_get_forecast(city: str, country_code=None):
        return ForecastResponse(
            city="Paris",
            country="FR",
            forecast=[
                DailyForecastData(
                    date="2026-01-13",
                    temp_min=2.0,
                    temp_max=8.0,
                    temp_day=6.0,
                    temp_night=4.0,
                    humidity=50,
                    wind_speed=5.0,
                    description="Couvert",
                    icon="04d",
                    precipitation_probability=20.0,
                )
            ],
        )

    from src.resources import weather_resource
    monkeypatch.setattr(weather_resource.weather_service, "get_forecast", fake_get_forecast)

    r = client.get("/api/weather/forecast?city=Paris")
    assert r.status_code == 200
    data = r.json()
    assert data["city"] == "Paris"
    assert len(data["forecast"]) == 1
    assert data["forecast"][0]["date"] == "2026-01-13"

