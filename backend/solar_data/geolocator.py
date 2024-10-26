import aiohttp
import asyncio
import logging
from typing import Any, Optional

# Set up logger
LOGGERNAME = "fastapi_logger"
logger = logging.getLogger(LOGGERNAME)


async def get_location_coordinates(location: str) -> Optional[dict[str, str]]:
    """
    Convert address from user input to lat/lon coordinates using aiohttp library
    with Nominatim geocoder. The coordinates are required to obtain the solar
    data from PVGIS for the specified address.

    Args:
        location: str, address provided by the user

    Returns:
        dict: dictionary with lat and lon coordinates

    """

    # Create a rate limiter
    rate_limit: asyncio.Semaphore = asyncio.Semaphore(1)  # Allow 1 request at a time
    last_request_time: float = 0.0

    logger.info(f"\nGeolocator: Requesting coordinates for address: {location}")

    url: str = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    headers: dict[str, str] = {"User-Agent": "Ferntree/1.0 (contact@ferntree.dev)"}

    async with rate_limit:
        # Ensure at least 1 second between requests
        current_time = asyncio.get_event_loop().time()
        if current_time - last_request_time < 1:
            await asyncio.sleep(1 - (current_time - last_request_time))

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    last_request_time = asyncio.get_event_loop().time()
                    logger.info(f"Geolocator: Response code: {response.status}")
                    if response.status != 200:
                        logger.error(
                            f"Geolocator: Failed to get coordinates for address: {location}"
                        )
                        return None
                    data: list[dict[str, Any]] = await response.json()
                    if not data:
                        logger.error(
                            f"Geolocator: No results found for address: {location}"
                        )
                        return None
                    coordinates: dict[str, str] = {
                        key: data[0][key] for key in ["lat", "lon", "display_name"]
                    }
                    logger.info(f"Geolocator: Coordinates: {coordinates}")
                    return coordinates
            except Exception as ex:
                logger.error(f"Geolocator: An error occurred: {ex}")
                return None


async def get_timezone(coordinates: dict[str, str]) -> str:
    """
    Get the timezone for the specified coordinates using the GeoNames API.
    Important limits for the free GeoNames API:
    - 30,000 credits per day
    - 1 credit per request
    - 1 request per second

    Args:
        coordinates: dict, dictionary with lat and lon coordinates

    Returns:
        str: timezone string

    """
    logger.info(f"\nGeoNames API: Requesting timezone for coordinates: {coordinates}")

    lat: str = coordinates["lat"]
    lon: str = coordinates["lon"]
    USERNAME: str = "felixtgd"

    url: str = (
        f"http://api.geonames.org/timezoneJSON?lat={lat}&lng={lon}&username={USERNAME}"
    )

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                logger.info(f"GeoNames API: Response code: {response.status}")
                if response.status != 200:
                    logger.error(
                        f"GeoNames API: An error occurred: {response.status} {response.reason}"
                    )
                    raise RuntimeError("Failed to get timezone")
                data: dict[str, Any] = await response.json()
                timezone: str = data["timezoneId"]
                logger.info(f"GeoNames API: Timezone: {timezone}")
                return timezone
        except Exception as ex:
            logger.error(f"GeoNames API: An error occurred: {ex}")
            raise RuntimeError("Failed to get timezone")
