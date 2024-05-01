import ssl
import time
import certifi
import geopy.geocoders
import geopy.exc


# Set SSL context for verification of Nominatim API
ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx

# Instantiate Nominatim geocoder
geolocator = geopy.geocoders.Nominatim(user_agent="ferntree_locator")


def get_location_coordinates(address: str):
    """
    Convert address from user input to lat/lon coordinates using Geopy library
    with Nominatim geocoder. The coordinates are required to obtain the solar
    data from PVGIS for the specified address.

    Args:
        address: str, address provided by the user

    Returns:
        dict: dictionary with lat and lon coordinates

    """
    print(f"Requesting coordinates for address: {address}")

    try:
        location = geolocator.geocode(address)
    except geopy.exc.GeocoderQueryError:
        print("GeocoderQueryError: Request failed. Invalid input.")
        return None
    except geopy.exc.GeocoderQuotaExceeded:
        print("GeocoderQuotaExceeded: Request rejected due to exceeded quota.")
        return None
    except geopy.exc.GeocoderRateLimited as ex:
        print("GeocoderRateLimited: {ex.message}")
        if ex.retry_after is not None:
            time.sleep(ex.retry_after)
            print("Request failed. Retrying in {ex.retry_after} seconds ...")
        else:
            time.sleep(1)
            print("Request failed. Retrying in 1 second ...")
        return get_location_coordinates(address)
    except Exception as e:
        # Handle other exceptions
        print(f"An unexpected error occurred: {e}")
        return None

    if location is not None:
        return {"lat": location.latitude, "lon": location.longitude}
    else:
        print("Geopy request failed. Probably invalid input.")
        return None
