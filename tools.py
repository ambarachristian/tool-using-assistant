"""Tool definitions (what Claude sees) and tool functions (what your code runs)."""
import json
import operator
from decimal import Decimal
from pathlib import Path


import httpx

CALCULATOR_TOOL = {
    "name": "calculator",
    "description": (
        "Do one arithmetic operation on two numbers and return the exact result. "
        "Use this for any math beyond trivial mental arithmetic instead of "
        "calculating in your head. For multi-step math, call it once per step."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide", "power"],
                "description": "The operation to apply, as: a <operation> b.",
            },
            "a": {"type": "number", "description": "The first number."},
            "b": {"type": "number", "description": "The second number."},
        },
        "required": ["operation", "a", "b"],
    },
}

# Each allowed operation name maps to a Python function that takes (a, b).
OPERATIONS = {
    "add": operator.add,
    "subtract": operator.sub,
    "multiply": operator.mul,
    "divide": operator.truediv,
    "power": operator.pow,
}


def calculator(operation: str, a: float, b: float) -> str:
    """Apply one operation to a and b. Return the result as text for Claude."""
    func = OPERATIONS[operation]
    # Decimal does exact decimal math: 0.1 + 0.2 gives 0.3, not 0.30000000000000004.
    result = func(Decimal(str(a)), Decimal(str(b)))
    return str(result)

WEATHER_TOOL = {
    "name": "get_weather",
    "description": (
        "Get the current weather for a city: temperature, feels-like temperature, "
        "humidity, precipitation, cloud cover and wind speed. Use this whenever "
        "the user asks about weather or conditions somewhere right now. "
        "It cannot give forecasts for future days."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name, e.g. 'Tokyo' or 'Paris'.",
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit. Defaults to celsius.",
            },
        },
        "required": ["city"],
    },
}

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
CURRENT_FIELDS = (
    "temperature_2m,apparent_temperature,relative_humidity_2m,"
    "precipitation,cloud_cover,wind_speed_10m"
)


def get_weather(city: str, unit: str = "celsius") -> str:
    """Look up the current weather for a city. Return it as JSON text for Claude."""
    # 1. Turn the city name into coordinates (the weather API needs them).
    geo = httpx.get(GEOCODING_URL, params={"name": city, "count": 1}, timeout=10)
    geo.raise_for_status()
    place = geo.json()["results"][0]

    # 2. Ask for the current weather at those coordinates.
    forecast = httpx.get(
        FORECAST_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": CURRENT_FIELDS,
            "temperature_unit": unit,
            "timezone": "auto",
        },
        timeout=10,
    )
    forecast.raise_for_status()
    data = forecast.json()

    # 3. Keep only what Claude needs, with units so the numbers make sense.
    return json.dumps({
        "place": f"{place['name']}, {place.get('country', '')}",
        "current": data["current"],
        "units": data["current_units"],
    })

READ_FILE_TOOL = {
    "name": "read_file",
    "description": (
        "Read a text file from the user's notes folder and return its contents. "
        "Use this when the user asks about their notes or names a file. "
        "Paths are relative to the notes folder, e.g. 'shopping.md'. "
        "It cannot list folders or read anything outside the notes folder."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path inside the notes folder, e.g. 'shopping.md'.",
            },
        },
        "required": ["path"],
    },
}

NOTES_DIR = Path(__file__).parent / "notes"
MAX_CHARS = 20_000


def read_file(path: str) -> str:
    """Read a text file inside NOTES_DIR. Refuse any path that leaves it."""
    root = NOTES_DIR.resolve()
    target = (root / path).resolve()
    # resolve() turns "notes/../.env" into the real location, so escapes are caught.
    if not target.is_relative_to(root):
        raise PermissionError(f"'{path}' is outside the notes folder")

    text = target.read_text(encoding="utf-8")
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + f"\n[Truncated: showing {MAX_CHARS} of {len(text)} characters]"
    return text

# Everything Claude can see. Pass this as tools=... on every call.
TOOLS = [CALCULATOR_TOOL, WEATHER_TOOL, READ_FILE_TOOL]

# Tool name (as Claude says it) -> the Python function that does the work.
TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_weather": get_weather,
    "read_file": read_file,
}


def run_tool(name: str, tool_input: dict) -> str:
    """Run the tool Claude asked for and return its result as text."""
    func = TOOL_FUNCTIONS[name]
    return func(**tool_input)
