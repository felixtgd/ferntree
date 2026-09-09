"""Generate the deterministic simplified Gaussian household load profile."""

from typing import TypeAlias

import numpy as np
import numpy.typing as npt

FloatArray: TypeAlias = npt.NDArray[np.float64]

SIMPLE_PROFILE_ID: int = 1
SIMPLE_PROFILE_TYPE: str = "simplified gaussian loadprofile"

MORNING_PEAK_CENTER_HOURS: float = 7.0
MORNING_PEAK_SIGMA_HOURS: float = 2.0
MORNING_PEAK_SCALE_KW: float = 0.8
EVENING_PEAK_CENTER_HOURS: float = 19.0
EVENING_PEAK_SIGMA_HOURS: float = 2.5
EVENING_PEAK_SCALE_KW: float = 1.0

NOISE_STD_KW: float = 0.05
RNG_SEED: int = 20260909
SECONDS_PER_DAY: int = 24 * 60 * 60
DAYS_PER_YEAR: int = 365


def _gaussian(
    hours: FloatArray,
    center_hours: float,
    sigma_hours: float,
    scale_kw: float,
) -> FloatArray:
    """Evaluate a Gaussian load peak at each time of day.

    Args:
        hours: Hour-of-day values at which to evaluate the curve.
        center_hours: Time of the peak center in hours after midnight.
        sigma_hours: Standard deviation of the peak in hours.
        scale_kw: Peak scale of the unnormalized curve in kW.

    Returns:
        Gaussian power values in kW for each supplied hour.

    """
    return scale_kw * np.exp(-((hours - center_hours) ** 2) / (2 * sigma_hours**2))


def generate_daily_profile(steps_per_day: int) -> FloatArray:
    """Generate one daily profile sampled at the requested resolution.

    Args:
        steps_per_day: Number of equally spaced samples across one 24-hour day.

    Returns:
        Unnormalized load values in kW containing the morning and evening peaks.

    Raises:
        ValueError: If ``steps_per_day`` is not positive.

    """
    if steps_per_day <= 0:
        raise ValueError("steps_per_day must be positive")

    hours: FloatArray = np.arange(steps_per_day, dtype=float) * 24 / steps_per_day
    morning_peak: FloatArray = _gaussian(
        hours,
        MORNING_PEAK_CENTER_HOURS,
        MORNING_PEAK_SIGMA_HOURS,
        MORNING_PEAK_SCALE_KW,
    )
    evening_peak: FloatArray = _gaussian(
        hours,
        EVENING_PEAK_CENTER_HOURS,
        EVENING_PEAK_SIGMA_HOURS,
        EVENING_PEAK_SCALE_KW,
    )
    return morning_peak + evening_peak


def generate_annual_profile(timebase: int) -> list[float]:
    """Generate a normalized, non-negative annual load profile.

    The pre-normalization curve represents kW. Its physical scale is removed by
    normalization so the returned profile can be scaled to annual consumption.

    Args:
        timebase: Simulation timestep duration in seconds. It must evenly divide
            one day.

    Returns:
        A deterministic, non-negative annual profile with one value per timestep
        and a sum of ``1.0``.

    Raises:
        ValueError: If ``timebase`` is not positive or does not evenly divide one
            day.

    """
    if timebase <= 0 or SECONDS_PER_DAY % timebase != 0:
        raise ValueError("timebase must be a positive divisor of 86400 seconds")

    steps_per_day: int = SECONDS_PER_DAY // timebase
    profile_kw: FloatArray = np.tile(
        generate_daily_profile(steps_per_day), DAYS_PER_YEAR
    )

    rng: np.random.Generator = np.random.default_rng(RNG_SEED)
    profile_kw += rng.normal(0.0, NOISE_STD_KW, size=profile_kw.size)
    profile_kw = np.clip(profile_kw, 0.0, None)

    return [float(value) for value in profile_kw / profile_kw.sum()]
