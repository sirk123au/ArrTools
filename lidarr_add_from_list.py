"""Add artists from a CSV list into Lidarr."""

import csv
import json
import logging
import logging.handlers
import os
import sys

import configparser
import requests
from requests.adapters import HTTPAdapter, Retry
from colorlog import ColoredFormatter

LidarrData: list = []

artist_added_count = 0
artist_exist_count = 0

# Config ###############################################################################################################

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['lidarr']['baseurl']
# urlbase = config['lidarr']['urlbase']
api_key = config['lidarr']['api_key']
rootfolderpath = config['lidarr']['rootfolderpath']

# Logging ######################################################################

logging.getLogger().setLevel(logging.NOTSET)

formatter = ColoredFormatter(
    "%(log_color)s[%(levelname)s]%(reset)s %(white)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style="%",
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

if not os.path.exists("./logs"):
    os.mkdir("./logs")
log_file_name = "./logs/lafl.log"
filelogger = logging.handlers.RotatingFileHandler(filename=log_file_name)
filelogger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
filelogger.setFormatter(log_formatter)
logging.getLogger().addHandler(filelogger)

log = logging.getLogger("app." + __name__)

########################################################################################################################

def create_session() -> requests.Session:
    """Return a session with retry and backoff configured."""

    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504], allowed_methods=["GET", "POST"])
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def add_artist(artist_name: str, foreign_artist_id: str, session: requests.Session) -> None:
    """Add an artist to Lidarr if it does not already exist."""

    
    payload = {
        "artistName": artist_name,
        "foreignArtistId": foreign_artist_id,
        "QualityProfileId": 1,
        "MetadataProfileId": 1,
        "Path": os.path.join(rootfolderpath, artist_name),
        "albumFolder": True,
        "RootFolderPath": rootfolderpath,
        "monitored": True,
        "addOptions": {"searchForMissingAlbums": False},
    }
    url = f"{baseurl}/api/v1/artist"
    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    try:
        rsp = session.post(url, headers=headers, json=payload, timeout=10)
    except requests.RequestException as exc:
        log.error(f"Error adding {artist_name}: {exc}")
        return
    if rsp.status_code == 201:
        artist_added_count += 1
        log.info(f"{artist_name} added to Lidarr :)")
    elif rsp.status_code == 400:
        artist_exist_count += 1
        log.info(f"{artist_name} already exists in Lidarr.")
    else:
        log.error(f"{artist_name} not found. Status: {rsp.status_code}")

def get_artist_id(artist: str, session: requests.Session) -> str | None:
    """Query Lidarr's search API to resolve an artist's MBID."""

    url = f"https://api.lidarr.audio/api/v0.4/search?type=artist&query=\"{artist}\""
    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    try:
        rsp = session.get(url, headers=headers, timeout=10)
    except requests.RequestException as exc:
        log.error(f"Error searching for {artist}: {exc}")
        return None

    if rsp.text == "[]":
        log.error(f"Sorry. We couldn't find {artist}")
        with open("not_found.txt", "a+", encoding="utf-8") as fo:
            fo.write(f"{artist}\n")
        return None

    data = json.loads(rsp.text)
    if rsp.status_code == 200:
        try:
            return data[0]["id"]
        except Exception:
            return data.get("id")
    return None


def lookup_musicbrainz(artist: str, session: requests.Session) -> str | None:
    """Query MusicBrainz directly for the artist MBID."""

    url = "https://musicbrainz.org/ws/2/artist/"
    params = {"query": f'artist:"{artist}"', "fmt": "json"}
    headers = {
        "User-Agent": "ArrTools (https://github.com/sirk123au/ArrTools)",
    }

    try:
        rsp = session.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException as exc:
        log.error(f"Error searching MusicBrainz for {artist}: {exc}")
        return None

    if rsp.status_code != 200:
        log.error(
            f"MusicBrainz search failed for {artist}. Status: {rsp.status_code}"
        )
        return None

    data = rsp.json()
    artists = data.get("artists")
    if not artists:
        log.error(f"Sorry. We couldn't find {artist} on MusicBrainz")
        with open("not_found.txt", "a+", encoding="utf-8") as fo:
            fo.write(f"{artist}\n")
        return None

    return artists[0].get("id")

def main() -> None:
    """Entry point for the script."""

    global LidarrData, artist_exist_count, artist_added_count

    if sys.version_info[0] < 3:
        log.error("Must be using Python 3")
        sys.exit(-1)
    if len(sys.argv) < 2:
        log.error("No list specified... bye!!")
        sys.exit(-1)
    if not os.path.exists(sys.argv[1]):
        log.error(f"{sys.argv[1]} does not exist")
        sys.exit(-1)

    session = create_session()

    log.info("Downloading Lidarr data...")
    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    url = f"{baseurl}/api/v1/artist"
    try:
        rsp = session.get(url, headers=headers, timeout=10)
    except requests.RequestException as exc:
        log.error(f"Error connecting to Lidarr: {exc}")
        sys.exit(-1)
    if rsp.status_code == 200:
        LidarrData = json.loads(rsp.text)
    elif rsp.status_code == 401:
        log.error("Failed to connect to Lidarr - unauthorized. Check API key in config.")
        sys.exit(-1)
    else:
        log.error(f"URL -> {url} Status Code -> {rsp.status_code}")
        log.error("Failed to connect to Lidarr...")
        sys.exit(-1)

    with open(sys.argv[1], encoding="utf-8") as csvfile:
        rows = list(csv.DictReader(csvfile))
    total_count = len(rows)
    if total_count == 0:
        log.error("No artists found in file... bye!!")
        sys.exit(0)
    if rows and "artist" not in rows[0]:
        log.error("Invalid CSV file - header must contain artist and foreignArtistId")
        sys.exit(-1)
    log.info(f"Found {total_count} artists in {sys.argv[1]} :)")

    for row in rows:
        artist = row.get("artist")
        foreign_artist_id = row.get("foreignArtistId")
        if not artist:
            continue
        if not foreign_artist_id:
            foreign_artist_id = get_artist_id(artist, session)
        if not foreign_artist_id:
            foreign_artist_id = lookup_musicbrainz(artist, session)
        if not foreign_artist_id:
            continue
        try:
            existing_ids = [artist.get("foreignArtistId") for artist in LidarrData]
            if foreign_artist_id in existing_ids:
                artist_exist_count += 1
                log.info(f"{artist} already exists in Lidarr Data.")
            else:
                add_artist(artist, foreign_artist_id, session)
        except Exception as err:
            log.error(err)
            sys.exit(-1)

    log.info(
        f"Added {artist_added_count} of {total_count} artists, {artist_exist_count} already exist"
    )

if __name__ == "__main__":
    main()