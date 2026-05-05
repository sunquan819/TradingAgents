import os
import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO
from pathlib import Path
from tradingagents.dataflows.config import get_config

API_BASE_URL = "https://www.alphavantage.co/query"

# Cache configuration
CACHE_DIR = None
CACHE_EXPIRY_HOURS = 72  # Cache expires after 72 hours (3 days)

def _init_cache_dir():
    """Initialize cache directory."""
    global CACHE_DIR
    if CACHE_DIR is None:
        config = get_config()
        CACHE_DIR = Path(config.get("data_cache_dir", os.path.join(os.path.expanduser("~"), ".tradingagents", "cache")))
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR

def _get_cache_path(function_name: str, symbol: str, params: dict) -> Path:
    """Get cache file path for a specific API call."""
    cache_dir = _init_cache_dir()
    # Create a unique cache key based on function, symbol, and params
    param_str = "_".join([f"{k}={v}" for k, v in sorted(params.items()) if k not in ["function", "apikey", "source"]])
    cache_key = f"{function_name}_{symbol}_{param_str}.csv"
    return cache_dir / "alpha_vantage" / cache_key

def _check_cache(cache_path: Path) -> str | None:
    """Check if cached data exists and is still valid."""
    if not cache_path.exists():
        return None
    
    # Check cache age
    cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
    age_hours = (datetime.now() - cache_time).total_seconds() / 3600
    
    if age_hours > CACHE_EXPIRY_HOURS:
        return None
    
    try:
        return cache_path.read_text(encoding="utf-8")
    except Exception:
        return None

def _save_cache(cache_path: Path, data: str):
    """Save data to cache."""
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(data, encoding="utf-8")
    except Exception as e:
        print(f"Warning: Failed to save cache: {e}")

def get_api_key() -> str:
    """Retrieve the API key for Alpha Vantage from environment variables."""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY environment variable is not set.")
    return api_key

def format_datetime_for_api(date_input) -> str:
    """Convert various date formats to YYYYMMDDTHHMM format required by Alpha Vantage API."""
    if isinstance(date_input, str):
        # If already in correct format, return as-is
        if len(date_input) == 13 and 'T' in date_input:
            return date_input
        # Try to parse common date formats
        try:
            dt = datetime.strptime(date_input, "%Y-%m-%d")
            return dt.strftime("%Y%m%dT0000")
        except ValueError:
            try:
                dt = datetime.strptime(date_input, "%Y-%m-%d %H:%M")
                return dt.strftime("%Y%m%dT%H%M")
            except ValueError:
                raise ValueError(f"Unsupported date format: {date_input}")
    elif isinstance(date_input, datetime):
        return date_input.strftime("%Y%m%dT%H%M")
    else:
        raise ValueError(f"Date must be string or datetime object, got {type(date_input)}")

class AlphaVantageRateLimitError(Exception):
    """Exception raised when Alpha Vantage API rate limit is exceeded."""
    pass

def _make_api_request(function_name: str, params: dict, use_cache: bool = True) -> dict | str:
    """Helper function to make API requests with caching support.
    
    Args:
        function_name: Alpha Vantage API function name
        params: API parameters
        use_cache: Whether to use cache (default True)
    
    Raises:
        AlphaVantageRateLimitError: When API rate limit is exceeded
    """
    symbol = params.get("symbol", "")
    
    # Check cache first
    if use_cache and symbol:
        cache_path = _get_cache_path(function_name, symbol, params)
        cached_data = _check_cache(cache_path)
        if cached_data:
            print(f"Using cached data for {function_name} {symbol}")
            return cached_data
    
    # Create a copy of params to avoid modifying the original
    api_params = params.copy()
    api_params.update({
        "function": function_name,
        "apikey": get_api_key(),
        "source": "trading_agents",
    })
    
    # Handle entitlement parameter if present in params or global variable
    current_entitlement = globals().get('_current_entitlement')
    entitlement = api_params.get("entitlement") or current_entitlement
    
    if entitlement:
        api_params["entitlement"] = entitlement
    elif "entitlement" in api_params:
        # Remove entitlement if it's None or empty
        api_params.pop("entitlement", None)
    
    response = requests.get(API_BASE_URL, params=api_params)
    response.raise_for_status()

    response_text = response.text
    
    # Check if response is JSON (error responses are typically JSON)
    try:
        response_json = json.loads(response_text)
        # Check for rate limit error
        if "Information" in response_json:
            info_message = response_json["Information"]
            if "rate limit" in info_message.lower() or "api key" in info_message.lower():
                raise AlphaVantageRateLimitError(f"Alpha Vantage rate limit exceeded: {info_message}")
    except json.JSONDecodeError:
        # Response is not JSON (likely CSV data), which is normal
        pass
    
    # Save to cache
    if use_cache and symbol and response_text:
        cache_path = _get_cache_path(function_name, symbol, params)
        _save_cache(cache_path, response_text)
    
    return response_text



def _filter_csv_by_date_range(csv_data: str, start_date: str, end_date: str) -> str:
    """
    Filter CSV data to include only rows within the specified date range.

    Args:
        csv_data: CSV string from Alpha Vantage API
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format

    Returns:
        Filtered CSV string
    """
    if not csv_data or csv_data.strip() == "":
        return csv_data

    try:
        # Parse CSV data
        df = pd.read_csv(StringIO(csv_data))

        # Assume the first column is the date column (timestamp)
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col])

        # Filter by date range
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        filtered_df = df[(df[date_col] >= start_dt) & (df[date_col] <= end_dt)]

        # Convert back to CSV string
        return filtered_df.to_csv(index=False)

    except Exception as e:
        # If filtering fails, return original data with a warning
        print(f"Warning: Failed to filter CSV data by date range: {e}")
        return csv_data
