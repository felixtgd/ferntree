import pytest

from src.domains.loadprofiles.gaussian_profile import (
    DAYS_PER_YEAR,
    SECONDS_PER_DAY,
    generate_annual_profile,
    generate_daily_profile,
)


@pytest.mark.parametrize("timebase", [3600, 900])
def test_generate_annual_profile_matches_timebase(timebase: int) -> None:
    """Generate one annual value per simulation timestep."""
    profile = generate_annual_profile(timebase)

    assert len(profile) == DAYS_PER_YEAR * SECONDS_PER_DAY // timebase


def test_generate_annual_profile_is_non_negative_and_normalized() -> None:
    """Clamp noisy values and normalize the resulting profile."""
    profile = generate_annual_profile(3600)

    assert all(value >= 0.0 for value in profile)
    assert sum(profile) == pytest.approx(1.0, abs=1e-6)


def test_generate_annual_profile_is_deterministic() -> None:
    """Use the fixed random seed on every profile generation."""
    assert generate_annual_profile(3600) == generate_annual_profile(3600)


def test_daily_profile_evening_peak_is_higher_than_morning_peak() -> None:
    """Retain the specified higher evening Gaussian peak."""
    daily_profile = generate_daily_profile(24)

    assert daily_profile[19] > daily_profile[7]


@pytest.mark.parametrize("timebase", [0, -1, 1000])
def test_generate_annual_profile_rejects_invalid_timebase(timebase: int) -> None:
    """Require a positive timestep that evenly divides a day."""
    with pytest.raises(ValueError, match="positive divisor"):
        generate_annual_profile(timebase)
