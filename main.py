"""
Entry point for the LinkedIn scraper.

This script orchestrates configuration loading and scraper execution.
"""

from __future__ import annotations

from config import (
    get_chrome_driver_path,
    get_credentials,
    get_delay_range,
    get_login_wait_seconds,
    get_profile_urls,
    get_proxy_list,
    get_restricted_log_path,
    get_retry_attempts,
    should_rotate_user_agent,
    should_resume,
)
from scraper import run_scraper


def main() -> None:
    """
    Execute the full scraping workflow.
    """

    credentials = get_credentials()
    profile_urls = get_profile_urls()
    proxy_pool = get_proxy_list()
    driver_path = get_chrome_driver_path()
    resume = should_resume()
    delay_range = get_delay_range()
    login_wait_seconds = get_login_wait_seconds()
    retry_attempts = get_retry_attempts()
    restricted_log_path = get_restricted_log_path()
    rotate_user_agent = should_rotate_user_agent()

    run_scraper(
        credentials=credentials,
        profile_urls=profile_urls,
        driver_path=driver_path,
        proxy_pool=proxy_pool,
        resume=resume,
        delay_range=delay_range,
        login_wait_seconds=login_wait_seconds,
        retry_attempts=retry_attempts,
        restricted_log_path=restricted_log_path,
        rotate_user_agent=rotate_user_agent,
    )


if __name__ == "__main__":
    main()


