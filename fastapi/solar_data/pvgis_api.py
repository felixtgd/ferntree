import pandas as pd
import requests
import time

from solar_data.geolocator import get_location_coordinates


def api_request_solar_irr(
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
        Response object containing status_code, response content etc.

    """

    # INPUTS Hourly radiation (minum example: https://re.jrc.ec.europa.eu/api/seriescalc?lat=45&lon=8)
    irr_inputs = {  # type, obligatory, default, default, comment
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

    print(f"API request to PVGIS_seriescalc for lat={lat} lon={lon} year={year}")
    response = requests.get(
        "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc", params=irr_inputs
    )

    if response.status_code == 200:
        # Continue processing returned data
        print("Request successful.")
        return response.json()
    elif response.status_code == 429 or response.status_code == 529:
        # Retry after waiting for a moment
        print(f"Received status code {response.status_code}. Retrying in 2 seconds...")
        time.sleep(2)
        # Recursive call to retry
        return api_request_solar_irr(
            lat=lat,
            lon=lon,
            year=year,
            pvcalc=pvcalc,
            peakpower=peakpower,
            loss=loss,
            angle=angle,
            aspect=aspect,
            opt=opt,
        )
    else:
        # Raise an error for other status code
        response.raise_for_status()


def get_solar_data_for_location(
    location: str, roof_azimuth: float, roof_incl: float
) -> pd.DataFrame:
    """
    Get solar irradiance data from PVGIS API for a specified location.

    Args:
        location: str with the address of the location
        roof_azimuth: float with the azimuth angle of the roof
        roof_incl: float with the inclination angle of the roof

    Returns:
        sol_irr_df: dataframe with solar irradiance data and timestamps

    """
    coordinates = get_location_coordinates(location)
    lat = coordinates["lat"]
    lon = coordinates["lon"]
    try:
        response_sol_irr = api_request_solar_irr(
            lat=lat, lon=lon, angle=roof_incl, aspect=roof_azimuth
        )
    except requests.exceptions.HTTPError as e:
        print(
            f"API request failed with status code {e.response.status_code}: {e.response.text}"
        )
    except Exception as e:
        print(f"Alarm! An unexpected error occurred: {e}")

    hourly_data = response_sol_irr["outputs"]["hourly"]

    T_amb = []
    G_i = []

    for item in hourly_data:
        T_amb.append(item["T2m"])
        G_i.append(item["G(i)"])

    # for item in hourly_data:
    #     # Convert 'time' to datetime
    #     item["time"] = datetime.strptime(item["time"], "%Y%m%d:%H%M").isoformat()

    #     # Ensure 'G(i)' and 'T2m' are floats
    #     item["G_i"] = float(item.pop("G(i)"))
    #     item["T2m"] = float(item["T2m"])

    #     # Remove unwanted fields
    #     item.pop("H_sun", None)
    #     item.pop("WS10m", None)
    #     item.pop("Int", None)

    print(f"{len(hourly_data)} data points")

    return T_amb, G_i  # hourly_data
