import logging
from typing import Any, Optional, Union

import aiohttp

# from backend.solar_data.geolocator import get_location_coordinates


# Set up logger
LOGGERNAME = "fastapi_logger"
logger = logging.getLogger(LOGGERNAME)


async def api_request_solar_irr(
    lat: str,
    lon: str,
    year: int = 2019,
    pvcalc: int = 0,
    peakpower: float = 5,
    loss: float = 14.0,
    angle: float = 35.0,
    aspect: float = 0,
    opt: int = 0,
) -> dict[str, Any]:
    """Make an API request to PVGIS for hourly solar irradiance data.

    This function queries data for hourly solar irradiance and temperature.
    The response contains hourly data of global irradiance on the inclined plane
    (plane of the array) in W/m2 and 2-m air temperature in degrees Celsius.

    Args:
        lat (str): Latitude in decimal degrees (south is negative).
        lon (str): Longitude in decimal degrees (west is negative).
        year (int, optional): Year for which data is required. Default = 2019.
        pvcalc (int, optional): If 1, outputs PV production estimation. Default = 0.
        peakpower (float, optional): Nominal power of the PV system in kW. Default = 5.
        loss (float, optional): Sum of system losses in percent. Default = 14.0.
        angle (float, optional): Inclination angle from horizontal plane. Default=35.0.
        aspect (float, optional): Orient. angle (0=south, 90=west, -90=east). Default=0.
        opt (int, optional): If 1, calculates optimal incl. and orient. . Defaults = 0.

    Returns:
        dict[str, Any]: Dictionary containing the API response data.

    Raises:
        RuntimeError: If the API request fails or returns a non-200 status code.

    """
    logger.info(
        f"\nPVGIS API: Request for lat={lat}, lon={lon}, "
        f"year={year}, angle={angle}, aspect={aspect}."
    )

    # INPUTS Hourly radiation (minum example: https://re.jrc.ec.europa.eu/api/seriescalc?lat=45&lon=8)
    params: dict[
        str, Union[str, float, int]
    ] = {  # type, obligatory, default, default, comment
        "lat": lat,
        # float, y, - , Latitude, in decimal degrees, south is negative.
        "lon": lon,
        # float, y, - , Longitude, in decimal degrees, west is negative.
        "usehorizon": 1,
        # int,   n,	1 , Calculate taking into account shadows from high horizon.
        "startyear": year,
        # int,   n, year_min(DB), First year of the output of hourly averages.
        # Availability varies with the temporal coverage of the radiation DB chosen.
        # The default value is the first year of the DB.
        "endyear": year,
        # int,   n, year_max(DB), Final year of the output of hourly averages.
        # Availability varies with the temporal coverage of the radiation DB chosen.
        # The default value is the last year of the DB.
        "pvcalculation": pvcalc,
        # int,   n, 0 , If "0" outputs only solar radiation calculations,
        # if "1" outputs the estimation of hourly PV production as well.
        "peakpower": peakpower,
        # float, y, - , Nominal power of the PV system, in kW.
        "mountingplace": "building",
        # str, n , "free", Type of mounting of the PV modules. "free" for free-standing
        # and "building" for building-integrated.
        "loss": loss,
        # float, y, - , Sum of system losses, in percent.
        "trackingtype": 0,
        # int,   n,	0 ,	Type of suntracking used, 0=fixed, 1=single horizontal axis
        # aligned north-south, 2=two-axis tracking, 3=vertical axis tracking, 4=single
        # horizontal axis aligned east-west, 5=single inclined axis aligned north-south.
        "angle": angle,
        # float, n, 0 ,	Inclination angle from horizontal plane of the (fixed) PV system
        "aspect": aspect,
        # float, n, 0 ,	Orientation (azimuth) angle of the (fixed) PV system, 0=south,
        # 90=west, -90=east.
        "optimalinclination": 0,
        # int, n, 0 , Calculate the optimum inclination angle.
        "optimalangles": opt,
        # int,   n, 0 , Calculate the optimum inclination AND orientation angles.
        "components": 0,
        # int,   n, 0 , If "1" outputs beam, diffuse and reflected radiation components.
        # Otherwise, it outputs only global values.
        "outputformat": "json",
        # str, n, "csv", Type of output. "csv" normal csv output with text explanations,
        # "basic" only data output with no text, "json".
        "browser": 1,
        # int,   n , 0 , Use this with a value of "1" if you access the web service from
        # a web browser and want to save the data to a file.
    }

    url: str = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                logger.info(f"PVGIS API: Response code: {response.status}")
                if response.status != 200:
                    logger.error(
                        f"PVGIS API Error: {response.status} {response.reason}"
                    )
                    raise RuntimeError("PVGIS API request failed")
                data: dict[str, Any] = await response.json()
                return data
        except Exception as ex:
            logger.error(f"PVGIS API: An error occurred: {ex}")
            raise RuntimeError("PVGIS API request failed")


async def get_solar_data_for_location(
    location: str, roof_azimuth: float, roof_incl: float
) -> tuple[list[float], list[float], dict[str, str]]:
    """Retrieve solar irradiance data from PVGIS API for a specified location.

    This function fetches solar irradiance and temperature data for a given location,
    considering the roof's azimuth and inclination angles.

    Args:
        location (str): The address of the location.
        roof_azimuth (float): The azimuth angle of the roof.
        roof_incl (float): The inclination angle of the roof.

    Returns:
        tuple[list[float], list[float], dict[str, str]]: A tuple containing:
            - List of ambient temperatures (T_amb) in degrees Celsius.
            - List of global irradiance values (G_i) in W/m2.
            - Dictionary with location coordinates and display name.

    Raises:
        RuntimeError: If coordinates cannot be found for the location or
                        if the PVGIS API request fails.

    """
    # coordinates: Optional[dict[str, str]] = await get_location_coordinates(location)
    coordinates: Optional[dict[str, str]] = {
        "lat": "47.9960901",
        "lon": "7.8494005",
        "display_name": "Freiburg im Breisgau, Baden-Württemberg, Germany",
    }  # TODO: temporaray fix, Render currently blocks Nominatim requests for locations
    if coordinates is None:
        logger.error("No coordinates found for location")
        raise RuntimeError("No coordinates found for location")

    lat: str = coordinates["lat"]
    lon: str = coordinates["lon"]

    try:
        response_data: Optional[dict[str, Any]] = await api_request_solar_irr(
            lat=lat, lon=lon, angle=roof_incl, aspect=roof_azimuth
        )
    except Exception as ex:
        logger.error(f"Get Solar Data: An error occurred: {ex}")
        raise RuntimeError("Failed to get solar data")

    if response_data is None:
        logger.error("No data returned from PVGIS API request")
        raise RuntimeError("No data returned from PVGIS API request")

    hourly_data: list[dict[str, float]] = response_data["outputs"]["hourly"]

    T_amb: list[float] = [item["T2m"] for item in hourly_data]
    G_i: list[float] = [item["G(i)"] for item in hourly_data]

    logger.info(f"Solar Data: {len(hourly_data)} data points\n")

    return T_amb, G_i, coordinates
