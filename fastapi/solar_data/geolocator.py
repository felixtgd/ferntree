import aiohttp
import json
import logging

# Set up logger
LOGGERNAME = "fastapi_logger"
logger = logging.getLogger(LOGGERNAME)


async def get_location_coordinates(address: str):
    """
    Convert address from user input to lat/lon coordinates using aiohttp library
    with Nominatim geocoder. The coordinates are required to obtain the solar
    data from PVGIS for the specified address.

    Args:
        address: str, address provided by the user

    Returns:
        dict: dictionary with lat and lon coordinates

    """
    logger.info(f"\nGeolocator: Requesting coordinates for address: {address}")

    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                logger.info(f"Geolocator: Response code: {response.status}")
                if response.status != 200:
                    logger.error(
                        f"Geolocator: Failed to get coordinates for address: {address}"
                    )
                    return None
                data = await response.text()
                location = json.loads(data)[0]
                return location
        except Exception as ex:
            logger.error(f"Geolocator: An error occurred: {ex}")
            return None
