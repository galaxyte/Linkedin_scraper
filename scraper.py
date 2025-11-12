"""
Core scraping logic for LinkedIn profiles.

This module encapsulates Selenium interactions, login automation, scraping
workflows, and robustness measures (user-agent rotation, throttling, resume
support). It is designed for production-grade usage with emphasis on
maintainability and readability.
"""

from __future__ import annotations

import random
import time
from contextlib import suppress
from typing import Dict, Iterable, List, Optional, Tuple

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import (
    Credentials,
    get_output_path,
)
from utils import load_existing_profile_urls, save_profiles_to_csv, log_restricted_profile

LOGIN_URL = "https://www.linkedin.com/login"


class LinkedInScraper:
    """
    A LinkedIn profile scraper that authenticates via Selenium and scrapes
    public profile information.

    Attributes:
        credentials: Login credentials for LinkedIn.
        profile_urls: A list of profile URLs to scrape.
        driver_path: Optional path to the ChromeDriver executable.
        proxy_pool: A list of proxy URLs for rotation.
        resume: Enables resume mode when True.
    """

    def __init__(
        self,
        credentials: Credentials,
        profile_urls: Iterable[str],
        driver_path: Optional[str] = None,
        proxy_pool: Optional[List[str]] = None,
        resume: bool = True,
        delay_range: Optional[Tuple[float, float]] = None,
        login_wait_seconds: int = 20,
        retry_attempts: int = 1,
        restricted_log_path: Optional[str] = None,
        rotate_user_agent: bool = False,
    ) -> None:
        self.credentials = credentials
        self.profile_urls = list(profile_urls)
        self.driver_path = driver_path
        self.proxy_pool = proxy_pool or []
        self.resume = resume
        self.ua = self._initialise_user_agent()
        self.driver = self._create_driver()
        self.output_path = get_output_path()
        self.scraped_records: List[Dict[str, str]] = []
        self.minimum_delay, self.maximum_delay = delay_range or (3.0, 6.0)
        self.login_wait_seconds = login_wait_seconds
        self.retry_attempts = max(0, retry_attempts)
        self.restricted_log_path = restricted_log_path
        self.rotate_user_agent = rotate_user_agent

    @staticmethod
    def _initialise_user_agent() -> Optional[UserAgent]:
        """
        Instantiate UserAgent with graceful degradation if the upstream service
        is unavailable.
        """

        try:
            return UserAgent()
        except Exception:
            print("⚠️ Failed to initialise fake_useragent. Falling back to default user-agent.")
            return None

    def _get_random_user_agent(self) -> str:
        """
        Safely fetch a random user-agent string.
        """

        default_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.0.0 Safari/537.36"
        )
        if not self.ua:
            return default_agent

        for _ in range(5):
            try:
                candidate = self.ua.random
            except Exception:
                break
            lowered = candidate.lower()
            if any(keyword in lowered for keyword in ("mobile", "android", "iphone", "ipad")):
                continue
            return candidate

        return default_agent

    def _create_driver(self) -> webdriver.Chrome:
        """
        Initialise a Selenium Chrome WebDriver with sensible defaults.

        Returns:
            A configured Chrome WebDriver instance.
        """

        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")

        user_agent = self._get_random_user_agent()
        options.add_argument(f"user-agent={user_agent}")

        proxy = self._get_proxy()
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
            print(f"🔁 Using proxy: {proxy}")

        print(f"🧭 Initialising ChromeDriver with UA: {user_agent}")

        try:
            if self.driver_path:
                service = ChromeService(executable_path=self.driver_path)
            else:
                service = ChromeService()
            driver = webdriver.Chrome(service=service, options=options)
        except WebDriverException as exc:  # pragma: no cover - runtime dependency
            raise RuntimeError("Failed to initialise ChromeDriver") from exc

        driver.set_page_load_timeout(60)
        return driver

    def _get_proxy(self) -> Optional[str]:
        """
        Retrieve a proxy from the proxy pool if available.

        Returns:
            A proxy string suitable for Selenium's --proxy-server flag.
        """

        if not self.proxy_pool:
            return None
        return random.choice(self.proxy_pool)

    def _human_pause(self) -> None:
        """
        Sleep for a random duration to mimic human browsing behaviour.
        """

        delay = random.uniform(self.minimum_delay, self.maximum_delay)
        print(f"⏳ Sleeping for {delay:.2f} seconds to mimic human behaviour.")
        time.sleep(delay)

    def _refresh_user_agent(self) -> None:
        """
        Refresh the user-agent for the webdriver to reduce bot detection risk.
        """

        if not self.rotate_user_agent:
            return

        user_agent = self._get_random_user_agent()
        try:
            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
            print(f"🔄 Updated user-agent to: {user_agent}")
        except Exception:
            print("⚠️ Failed to update user-agent via CDP; continuing with existing UA.")

    def login(self) -> None:
        """
        Log into LinkedIn using supplied credentials.
        """

        print("🚀 Navigating to LinkedIn login page.")
        self.driver.get(LOGIN_URL)

        wait = WebDriverWait(self.driver, self.login_wait_seconds)
        try:
            email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        except TimeoutException as exc:
            raise RuntimeError("Login page did not load as expected.") from exc

        email_input.clear()
        email_input.send_keys(self.credentials.email)
        password_input.clear()
        password_input.send_keys(self.credentials.password)

        with suppress(NoSuchElementException):
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()

        time.sleep(random.uniform(2.0, 3.0))

        try:
            wait.until(EC.presence_of_element_located((By.ID, "global-nav-search")))
            print("✅ Successfully logged into LinkedIn.")
        except TimeoutException:
            print("⚠️ Login confirmation timeout. Verify credentials or check for MFA prompts.")

    def scrape_profiles(self) -> None:
        """
        Iterate over profile URLs, scrape data, and save the results.
        """

        processed_urls = load_existing_profile_urls(self.output_path) if self.resume else set()
        print(f"📂 Resume mode {'enabled' if self.resume else 'disabled'}.")
        if processed_urls:
            print(f"🔁 Detected {len(processed_urls)} previously scraped profiles. Skipping duplicates.")

        for url in self.profile_urls:
            if self.resume and url in processed_urls:
                print(f"⏭️ Skipping already-scraped profile: {url}")
                continue

            record = self._scrape_with_retries(url)
            if record:
                self.scraped_records.append(record)
                save_profiles_to_csv([record], self.output_path)

        print("🏁 Scraping run complete.")

    def _scrape_with_retries(self, url: str) -> Optional[Dict[str, str]]:
        """
        Attempt to scrape a profile with retry support for restricted access.
        """

        attempts = max(1, self.retry_attempts + 1)
        for attempt in range(1, attempts + 1):
            try:
                record = self._scrape_profile(url)
            except Exception as exc:
                print(f"❌ Failed to scrape {url}: {exc}")
                return None

            if record is not None:
                return record

            if attempt < attempts:
                print(f"🔁 Retrying {url} (attempt {attempt + 1}/{attempts}) after pause.")
                self._human_pause()

        reason = "Restricted or inaccessible after retries"
        if self.restricted_log_path:
            log_restricted_profile(self.restricted_log_path, url, reason)
        else:
            print(f"🚧 Unable to access {url}: {reason}")
        return None

    def _scrape_profile(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape a single LinkedIn profile page.

        Args:
            url: LinkedIn profile URL.

        Returns:
            A dictionary containing profile information, or None on failure.
        """

        print(f"🌐 Visiting profile: {url}")
        self._refresh_user_agent()
        try:
            self.driver.get(url)
        except TimeoutException:
            print(f"⚠️ Timeout while loading {url}. Retrying once.")
            self.driver.get(url)

        self._human_pause()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        if not self._is_profile_accessible(soup):
            print(
                "🚫 LinkedIn served a restricted or marketing page. "
                "Verify the profile URL, account permissions, or throttling limits."
            )
            return None

        profile_data: Dict[str, Optional[str]] = {
            "Full Name": None,
            "Headline": None,
            "Location": None,
            "Current Company": None,
            "Profile URL": url,
        }

        profile_data["Full Name"] = self._extract_text(
            soup,
            [
                "h1.text-heading-xlarge",
                "section[data-view-name='profile-top-card'] h1",
                "main h1",
            ],
        )
        profile_data["Headline"] = self._extract_text(
            soup,
            [
                "div.text-body-medium.break-words",
                "section[data-view-name='profile-top-card'] div.inline-show-more-text",
                "main section div.text-body-medium",
            ],
        )
        profile_data["Location"] = self._extract_text(
            soup,
            [
                "span.text-body-small.inline.t-black--light.break-words",
                "section[data-view-name='profile-top-card'] span.inline.t-black--light",
                "main section span.text-body-small",
            ],
        )

        profile_data["Current Company"] = self._extract_current_company(soup)

        if any(value for key, value in profile_data.items() if key != "Profile URL"):
            print(f"✅ Scraped: {profile_data.get('Full Name', 'Unknown')}")
        else:
            print(f"⚠️ No visible data extracted for {url}. You may need to check selectors.")

        return profile_data

    def _extract_text(self, soup: BeautifulSoup, selectors: Iterable[str]) -> Optional[str]:
        """
        Iterate through CSS selectors and return the first non-empty text match.
        """

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return None

    def _extract_current_company(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Attempt to extract the current company from the profile page.

        Args:
            soup: Parsed BeautifulSoup object for the profile page.

        Returns:
            The current company string if available, otherwise None.
        """

        selectors = [
            "div.pv-entity__summary-info h2 span[aria-hidden='true']",
            "section[data-view-name='profile-experience'] li span[aria-hidden='true']",
            "section#experience-section li .pv-entity__summary-info h2 span:not(.visually-hidden)",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return None

    def _is_profile_accessible(self, soup: BeautifulSoup) -> bool:
        """
        Detect whether LinkedIn has served a restricted/marketing page instead of
        the requested profile.
        """

        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            blocked_titles = {
                "LinkedIn: Log In or Sign Up",
                "LinkedIn Login, Sign in | LinkedIn",
            }
            if any(blocked in title_text for blocked in blocked_titles):
                return False

        heading = soup.find("h1")
        if heading:
            heading_text = heading.get_text(strip=True)
            marketing_markers = {
                "Join LinkedIn",
                "Build your professional brand & network",
                "Sign in",
            }
            if any(marker in heading_text for marker in marketing_markers):
                return False

        auth_wall = soup.select_one(".authwall-join-form__form-toggle, .authwall-join-form__title")
        if auth_wall:
            return False

        return True

    def close(self) -> None:
        """
        Cleanly close the Selenium WebDriver instance.
        """

        if self.driver:
            print("🛑 Closing ChromeDriver.")
            self.driver.quit()


def run_scraper(
    credentials: Credentials,
    profile_urls: Iterable[str],
    driver_path: Optional[str] = None,
    proxy_pool: Optional[List[str]] = None,
    resume: bool = True,
    delay_range: Optional[Tuple[float, float]] = None,
    login_wait_seconds: int = 20,
    retry_attempts: int = 1,
    restricted_log_path: Optional[str] = None,
    rotate_user_agent: bool = False,
) -> None:
    """
    Convenience function to run the scraper in a single call.
    """

    scraper = LinkedInScraper(
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

    try:
        scraper.login()
        scraper.scrape_profiles()
    finally:
        scraper.close()


