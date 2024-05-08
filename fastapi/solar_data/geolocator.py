import aiohttp
import logging

# Set up logger
LOGGERNAME = "fastapi_logger"
logger = logging.getLogger(LOGGERNAME)


async def get_location_coordinates(location: str):
    """
    Convert address from user input to lat/lon coordinates using aiohttp library
    with Nominatim geocoder. The coordinates are required to obtain the solar
    data from PVGIS for the specified address.

    Args:
        location: str, address provided by the user

    Returns:
        dict: dictionary with lat and lon coordinates

    """
    logger.info(f"\nGeolocator: Requesting coordinates for address: {location}")

    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                logger.info(f"Geolocator: Response code: {response.status}")
                if response.status != 200:
                    logger.error(
                        f"Geolocator: Failed to get coordinates for address: {location}"
                    )
                    return None
                data = await response.json()
                coordinates = {
                    key: data[0][key] for key in ["lat", "lon", "display_name"]
                }
                logger.info(f"Geolocator: Coordinates: {coordinates}")
                return coordinates
        except Exception as ex:
            logger.error(f"Geolocator: An error occurred: {ex}")
            return None


async def get_timezone(coordinates: dict):
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

    lat = coordinates["lat"]
    lon = coordinates["lon"]
    USERNAME = "felixtgd"

    url = (
        f"http://api.geonames.org/timezoneJSON?lat={lat}&lng={lon}&username={USERNAME}"
    )

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                logger.info(f"GeoNames API: Response code: {response.status}")
                if response.status != 200:
                    logger.error(f"GeoNames API: An error occurred: {response.status}")
                    return None
                data = await response.json()
                timezone = data["timezoneId"]
                logger.info(f"GeoNames API: Timezone: {timezone}")
                return timezone
        except Exception as ex:
            logger.error(f"GeoNames API: An error occurred: {ex}")
            return None
