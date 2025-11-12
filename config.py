"""
Configuration module for the LinkedIn scraper project.

This file centralises all configuration items including login credentials,
profile URLs to visit, and optional proxy settings. Credentials are expected
to be supplied via environment variables for safety.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class Credentials:
    """
    Represents the login credentials required to authenticate with LinkedIn.

    Attributes:
        email: LinkedIn username or email address.
        password: LinkedIn password.
    """

    email: str
    password: str


def get_credentials() -> Credentials:
    """
    Retrieve credentials from environment variables.

    Returns:
        A Credentials instance populated with the user's login details.

    Raises:
        ValueError: If either the email or password is missing.
    """

    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")

    if not email or not password:
        raise ValueError(
            "Missing LinkedIn credentials. Please set LINKEDIN_EMAIL and "
            "LINKEDIN_PASSWORD environment variables."
        )

    return Credentials(email=email, password=password)


def get_profile_urls() -> List[str]:
    """
    Return the list of LinkedIn profile URLs to scrape.

    Returns:
        A list containing exactly 20 LinkedIn profile URLs. These are placeholder
        URLs and should be customised before running the scraper.
    """

    return [
    "https://www.linkedin.com/in/dummy-profile-1/",
    "https://www.linkedin.com/in/dummy-profile-2/",
    "https://www.linkedin.com/in/dummy-profile-3/",
    "https://www.linkedin.com/in/dummy-profile-4/",
    "https://www.linkedin.com/in/dummy-profile-5/",
    "https://www.linkedin.com/in/dummy-profile-6/",
    "https://www.linkedin.com/in/dummy-profile-7/",
    "https://www.linkedin.com/in/dummy-profile-8/",
    "https://www.linkedin.com/in/dummy-profile-9/",
    "https://www.linkedin.com/in/dummy-profile-10/",
    "https://www.linkedin.com/in/dummy-profile-11/",
    "https://www.linkedin.com/in/dummy-profile-12/",
    "https://www.linkedin.com/in/dummy-profile-13/",
    "https://www.linkedin.com/in/dummy-profile-14/",
    "https://www.linkedin.com/in/dummy-profile-15/",
    "https://www.linkedin.com/in/dummy-profile-16/",
    "https://www.linkedin.com/in/dummy-profile-17/",
    "https://www.linkedin.com/in/dummy-profile-18/",
    "https://www.linkedin.com/in/dummy-profile-19/",
    "https://www.linkedin.com/in/dummy-profile-20/",

       
    ]


def get_proxy_list() -> List[str]:
    """
    Return a list of HTTP proxies to support rotation.

    This is a placeholder implementation. Populate with your proxy pool in the
    format 'http://user:password@host:port' or 'http://host:port'.

    Returns:
        A list of proxy URLs. May be empty.
    """

    return []


def get_output_path() -> str:
    """
    Return the default path to the CSV output file.

    Returns:
        Path to the `profiles.csv` output file.
    """

    return os.path.join(os.path.dirname(__file__), "profiles.csv")


def should_resume() -> bool:
    """
    Determine whether the scraper should attempt to resume from previous runs.

    Returns:
        True if resume mode is enabled, False otherwise. Controlled via the
        RESUME_SCRAPE environment variable (any truthy value enables it).
    """

    return os.getenv("RESUME_SCRAPE", "true").lower() in {"1", "true", "yes"}


def get_chrome_driver_path() -> Optional[str]:
    """
    Optionally return a custom ChromeDriver path.

    Returns:
        A string path to ChromeDriver if provided via CHROMEDRIVER_PATH
        environment variable, otherwise None to fall back to system defaults.
    """

    return os.getenv("CHROMEDRIVER_PATH")


def get_delay_range() -> Tuple[float, float]:
    """
    Retrieve the minimum and maximum delay (in seconds) between profile visits.
    """

    minimum = float(os.getenv("SCRAPE_DELAY_MIN", "3.0"))
    maximum = float(os.getenv("SCRAPE_DELAY_MAX", "6.0"))
    if minimum > maximum:
        minimum, maximum = maximum, minimum
    return minimum, maximum


def get_login_wait_seconds() -> int:
    """
    Return the maximum number of seconds to wait for login confirmation.
    """

    return int(os.getenv("LOGIN_WAIT_SECONDS", "20"))


def get_retry_attempts() -> int:
    """
    Determine how many times to retry loading a restricted profile.
    """

    return max(0, int(os.getenv("SCRAPE_RETRY_ATTEMPTS", "1")))


def get_restricted_log_path() -> str:
    """
    Return the path where restricted profile attempts should be logged.
    """

    return os.path.join(os.path.dirname(__file__), "restricted_profiles.csv")


def should_rotate_user_agent() -> bool:
    """
    Determine whether to rotate the user-agent between profile visits.
    """

    return os.getenv("ROTATE_USER_AGENT", "false").lower() in {"1", "true", "yes"}


