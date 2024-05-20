import aiohttp
import logging

from solar_data.geolocator import get_location_coordinates


# Set up logger
LOGGERNAME = "fastapi_logger"
logger = logging.getLogger(LOGGERNAME)


async def api_request_solar_irr(
    lat: float,
    lon: float,
    year: int = 2019,
    pvcalc: int = 0,
    peakpower: float = 5,
    loss: float = 14.0,
    angle: float = 35.0,
    aspect: float = 0,
    opt: int = 0,
) -> dict:
    """
    API request to PVGIS
    Queries data for HOURLY SOLAR IRRADIANCE
    Response contains hourly data of
        Global irradiance on the inclined plane (plane of the array): G(i) in [W/m2]
        2-m air temperature: T2m in [degree Celsius]

    Args:
        Location: Latitude=lat, Longitude=lon
        Year for which data is required
        (Only required if pvcalc=1) System specifications: nominal power=peakpower [kW], system losses=loss [%]
        Inclination and azimuth angles can be set in input or calculated optimally by PVGIS

    Returns:
        Dict with response data
    """
    logger.info(
        f"\nPVGIS API: Request for lat={lat}, lon={lon}, year={year}, angle={angle}, aspect={aspect}."
    )

    # INPUTS Hourly radiation (minum example: https://re.jrc.ec.europa.eu/api/seriescalc?lat=45&lon=8)
    params = {  # type, obligatory, default, default, comment
        "lat": lat,  # float, y, - , Latitude, in decimal degrees, south is negative.
        "lon": lon,  # float, y, - , Longitude, in decimal degrees, west is negative.
        "usehorizon": 1,  # int,   n,	1 , Calculate taking into account shadows from high horizon.
        "startyear": year,  # int,   n, year_min(DB), First year of the output of hourly averages. Availability varies with the temporal coverage of the radiation DB chosen. The default value is the first year of the DB.
        "endyear": year,  # int,   n, year_max(DB), Final year of the output of hourly averages. Availability varies with the temporal coverage of the radiation DB chosen. The default value is the last year of the DB.
        "pvcalculation": pvcalc,  # int,   n, 0 , If "0" outputs only solar radiation calculations, if "1" outputs the estimation of hourly PV production as well.
        "peakpower": peakpower,  # float, y, - , Nominal power of the PV system, in kW.
        "mountingplace": "building",  # str, n , "free", Type of mounting of the PV modules. "free" for free-standing and "building" for building-integrated.
        "loss": loss,  # float, y, - , Sum of system losses, in percent.
        "trackingtype": 0,  # int,   n,	0 ,	Type of suntracking used, 0=fixed, 1=single horizontal axis aligned north-south, 2=two-axis tracking, 3=vertical axis tracking, 4=single horizontal axis aligned east-west, 5=single inclined axis aligned north-south.
        "angle": angle,  # float, n, 0 ,	Inclination angle from horizontal plane of the (fixed) PV system.
        "aspect": aspect,  # float, n, 0 ,	Orientation (azimuth) angle of the (fixed) PV system, 0=south, 90=west, -90=east.
        "optimalinclination": 0,  # int, n, 0 , Calculate the optimum inclination angle.
        "optimalangles": opt,  # int,   n, 0 , Calculate the optimum inclination AND orientation angles.
        "components": 0,  # int,   n, 0 , If "1" outputs beam, diffuse and reflected radiation components. Otherwise, it outputs only global values.
        "outputformat": "json",  # str, n, "csv", Type of output. "csv" normal csv output with text explanations, "basic" only data output with no text, "json".
        "browser": 1,  # int,   n , 0 , Use this with a value of "1" if you access the web service from a web browser and want to save the data to a file.
    }

    url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                logger.info(f"PVGIS API: Response code: {response.status}")
                if response.status != 200:
                    logger.error(
                        f"PVGIS API: An error occurred: {response.status} {response.reason}"
                    )
                    return None
                data = await response.json()
                return data
        except Exception as ex:
            logger.error(f"PVGIS API: An error occurred: {ex}")
            return None


async def get_solar_data_for_location(
    location: str, roof_azimuth: float, roof_incl: float
) -> tuple:
    """
    Get solar irradiance data from PVGIS API for a specified location.

    Args:
        location: str with the address of the location
        roof_azimuth: float with the azimuth angle of the roof
        roof_incl: float with the inclination angle of the roof

    Returns:
        Tuple of two lists with the temperature and solar irradiance data

    """
    coordinates = await get_location_coordinates(location)
    if coordinates is None:
        logger.error("No coordinates found for location")
        return None

    lat = coordinates["lat"]
    lon = coordinates["lon"]

    try:
        response_data = await api_request_solar_irr(
            lat=lat, lon=lon, angle=roof_incl, aspect=roof_azimuth
        )
    except Exception as ex:
        logger.error(f"Get Solar Data: An error occurred: {ex}")
        return None

    if response_data is None:
        logger.error("No data returned from PVGIS API request")
        return None

    hourly_data = response_data["outputs"]["hourly"]

    T_amb = [item["T2m"] for item in hourly_data]
    G_i = [item["G(i)"] for item in hourly_data]

    logger.info(f"Solar Data: {len(hourly_data)} data points\n")

    return T_amb, G_i, coordinates
