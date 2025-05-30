# Weather API Tool using FastMCP
# This script provides a FastMCP server that allows users to get weather alerts
# and forecasts using the National Weather Service (NWS) API.
import sys
from typing import Any
import httpx
from anthropic import Anthropic
from mcp.server.fastmcp import FastMCP
import pandas as pd


# Initialize FastMCP server
mcp = FastMCP("luna", description="Luna PE API Tool using FastMCP", version="1.0.0")
#mcp = FastMCP("weather", description="Weather API Tool using FastMCP", version="1.0.0")


# Constants
XLSX_FILE = "/Users/johnsolder/Library/CloudStorage/OneDrive-Coherent/Excel Examples/Mortgage Model/MTG_AMORT_CALC/mortgage-amort-calculator.xlsx"
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

def convert_xls_to_df(xlsx_file: str) -> pd.DataFrame:
    """Convert an XLSX file to a Pandas DataFrame."""
    try:
        #df = pd.read_excel(xlsx_file, engine='openpyxl')
        dfs = pd.read_excel(xlsx_file, sheet_name=None,engine='openpyxl')
        combined_df = pd.concat(dfs.values(), ignore_index=True)
        return dfs
    except Exception as e:
        print(f"Error reading XLSX file: {e}", file=sys.stderr)
        return pd.DataFrame()  # Return empty DataFrame on error        

 def convert_df_to_md_table(df: pd.DataFrame) -> str:
    """Convert a Pandas DataFrame to a Markdown table."""
    if df.empty:
        return "No data available."

    md_table = df.to_markdown(index=False)
    print(markdown_table)

    return md_table   

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

if __name__ == "__main__":
    # Initialize and run the server
    #mcp.run(transport='stdio')
    print('IN LUNA.PY +++++++++++++++++++++++', file=sys.stderr)
    print('Sheet',XLSX_FILE, file=sys.stderr)
    #convert_xls_to_df(XLSX_FILE)
    new_md_table = convert_df_to_md_table(convert_xls_to_df(XLSX_FILE))
