"""Export Lidarr artist information to a CSV file."""

import argparse
import csv
import json
import sys
import re
import configparser
from pathlib import Path

import requests


if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")


def backup_lidarr(config_path: str, output_path: str) -> None:
    """Backup Lidarr artists to ``output_path`` using ``config_path``."""

    config = configparser.ConfigParser()
    config.read(config_path)
    baseurl = config['lidarr']['baseurl']
    api_key = config['lidarr']['api_key']

    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    url = f"{baseurl}/api/v1/artist"

    print("Downloading Data...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    lidarr_data = response.json()

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["artist", "foreignArtistId"])
        for artist_info in lidarr_data:
            artist = re.sub(r"[^a-zA-Z0-9 ]", "", artist_info["artistName"])
            csvwriter.writerow([artist, artist_info.get("foreignArtistId")])


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup Lidarr artists to CSV")
    parser.add_argument(
        "-c",
        "--config",
        default="./config.ini",
        help="Path to config.ini",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./lidarr_backup.csv",
        help="Output CSV file",
    )

    args = parser.parse_args()

    try:
        backup_lidarr(args.config, args.output)
        print("Done...")
    except Exception as exc:  # keep CLI simple
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()

