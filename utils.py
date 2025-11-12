"""
Utility helpers for the LinkedIn scraper project.

Contains helper functions for CSV persistence and resume logic.
"""

from __future__ import annotations

import os
from typing import Iterable, List, Dict, Set

import pandas as pd
from pandas.errors import EmptyDataError


def load_existing_profile_urls(csv_path: str) -> Set[str]:
    """
    Load previously scraped profile URLs from the CSV output file.

    Args:
        csv_path: Path to the CSV file containing prior results.

    Returns:
        A set of profile URLs that already exist in the output file. If the file
        does not exist, an empty set is returned.
    """

    if not os.path.isfile(csv_path):
        return set()

    try:
        dataframe = pd.read_csv(csv_path)
    except EmptyDataError:
        print(f"ℹ️ Existing CSV at {csv_path} is empty. Starting fresh.")
        return set()
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Failed to read existing CSV at {csv_path}") from exc

    if "Profile URL" not in dataframe.columns:
        return set()

    return set(dataframe["Profile URL"].dropna().astype(str).tolist())


def save_profiles_to_csv(records: Iterable[Dict[str, str]], csv_path: str) -> None:
    """
    Persist scraped profile records to a CSV file.

    Args:
        records: An iterable of dictionaries containing profile information.
        csv_path: Path where the CSV should be stored.
    """

    records_list: List[Dict[str, str]] = list(records)
    if not records_list:
        print("ℹ️ No new profiles to write to CSV.")
        return

    dataframe = pd.DataFrame(records_list)
    write_header = not os.path.isfile(csv_path)

    try:
        dataframe.to_csv(csv_path, mode="a", index=False, header=write_header)
    except Exception as exc:
        raise RuntimeError(f"Failed to save profiles to {csv_path}") from exc

    print(f"💾 Saved {len(records_list)} profiles to {csv_path}.")


def log_restricted_profile(csv_path: str, url: str, reason: str) -> None:
    """
    Append information about a restricted or inaccessible profile to a separate
    CSV log for follow-up.
    """

    dataframe = pd.DataFrame(
        [{"Profile URL": url, "Reason": reason}],
    )
    write_header = not os.path.isfile(csv_path)

    try:
        dataframe.to_csv(csv_path, mode="a", index=False, header=write_header)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Failed to log restricted profile to {csv_path}") from exc

    print(f"🚧 Logged restricted profile: {url} → {reason}")


