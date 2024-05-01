from pvgis_api import get_solar_data_for_coordinates
from geolocator import get_location_coordinates

address = "Ferntree Gully, Victoria, Australia"
coordinates = get_location_coordinates(address)
print(coordinates)

solar_data = get_solar_data_for_coordinates(coordinates)
print(solar_data.head())
