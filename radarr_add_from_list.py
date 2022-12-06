import configparser
import csv
import json
import logging.handlers
import os
import requests
import sys
import urllib.parse

from colorlog import ColoredFormatter

movie_added_count = 0
movie_exist_count = 0



# Config ###############################################################################################################

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['radarr']['baseurl']
urlbase = config['radarr']['urlbase']
api_key = config['radarr']['api_key']
rootfolderpath = config['radarr']['rootfolderpath']
searchForMovie = config['radarr']['searchForMovie']
if searchForMovie == "1" or searchForMovie == "True":
    searchForMovie = True
else:
    searchForMovie = False
quality_profile_id = config['radarr']['qualityProfileId']
omdbapi_key = config['radarr']['omdbapi_key']

# Logging ##############################################################################################################

logging.getLogger().setLevel(logging.NOTSET)

formatter = ColoredFormatter(
    "%(log_color)s[%(levelname)s]%(reset)s %(white)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

logger = logging.StreamHandler()
logger.setLevel(logging.INFO)  # DEBUG To show all
logger.setFormatter(formatter)
logging.getLogger().addHandler(logger)
if not os.path.exists("./logs/"): os.mkdir("./logs/")
logFileName = "./logs/rafl.log"  # .format(datetime.now().strftime("%Y-%m-%d-%H.%M.%S"))
filelogger = logging.handlers.RotatingFileHandler(filename=logFileName)
filelogger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
filelogger.setFormatter(logFormatter)
logging.getLogger().addHandler(filelogger)

log = logging.getLogger("app." + __name__)


########################################################################################################################

def add_movie(title, year, imdbid):
    global movie_added_count
    global movie_exist_count
    global ProfileId

    if year == "" or year is None:
        year = get_year(title)
    if imdbid == "" or imdbid is None:
        imdbid = get_imdbid(title, year)

    # Store Radarr Server imdbid for faster matching
    current_movie_ids = [movie.get('imdbId') for movie in RadarrData]

    if quality_profile_id is None or quality_profile_id == '':
        log.warning("Quality profile not set in config file.")
        ProfileId = select_profile_id()
    elif match_profile_id(quality_profile_id):
        ProfileId = quality_profile_id

    if imdbid is None:
        # Search by Movie Title in Radarr
        headers = {"Content-type": "application/json", 'Accept': 'application/json'}
        url = "{}{}/api/v3/movie/lookup?term={}&apikey={}".format(baseurl, urlbase, title.replace(" ", "%20"), api_key)
        radarr_api_response = requests.get(url, headers=headers)
        data = json.loads(radarr_api_response.text)
        if radarr_api_response.text == "[]":
            log.error(f"\u001b[35mSorry. We couldn't find any movies matching {title} ({year})\u001b[0m")
            return
        if radarr_api_response.status_code == 200:
            tmdbid = data[0]["tmdbId"]
            title = data[0]["title"]
            year = data[0]['year']
            images = json.loads(json.dumps(data[0]["images"]))
            titleslug = data[0]["titleSlug"]
            movie_data = json.dumps({
                "title":               title,
                "qualityProfileId":    ProfileId,
                "year":                year,
                "tmdbId":              tmdbid,
                "titleslug":           titleslug,
                "monitored":           'true',
                "minimumAvailability": "released",
                "rootFolderPath":      rootfolderpath,
                "images":              images,
                "addOptions":          {"searchForMovie": searchForMovie}
            })
            # Add Movie To Radarr
            headers = {"Content-type": "application/json", 'Accept': 'application/json', "X-Api-Key": api_key}
            url = f'{baseurl}{urlbase}/api/v3/movie'
            radarr_api_response = requests.post(url, headers=headers, data=movie_data)
            if radarr_api_response.status_code == 201:
                movie_added_count += 1
                if searchForMovie:
                    log.info(
                        f"\u001b[36mtm{tmdbid}\t         \u001b[0m{title} ({year}) \u001b[32mAdded to Radarr :) "
                        f"\u001b[36;1mNowSearching.\u001b[0m\n")
                else:
                    log.info(
                        f"\u001b[36mtm{tmdbid}\t         \u001b[0m{title} ({year}) \u001b[32mAdded to Radarr :) "
                        f"\u001b[31mSearch Disabled.\u001b[0m\n")
            elif radarr_api_response.status_code == 400:
                movie_exist_count += 1
                log.info(
                    f"\u001b[36mtm{tmdbid}\t         \u001b[0m{title} ({year}) already Exists in Radarr.\n")
                return
        else:
            log.error(f"\u001b[35m{imdbid}\t {title} ({year}) Not found, Not added to Radarr.\u001b[0m\n")
            return

    elif imdbid not in current_movie_ids:
        # Build json Data to import into radarr
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        headers = {"Content-type": "application/json", 'Accept': 'application/json'}
        url = "{}{}/api/v3/movie/lookup/imdb?imdbId={}&apikey={}".format(baseurl, urlbase, imdbid, api_key)
        radarr_api_response = session.get(url, headers=headers)
        if len(radarr_api_response.text) == 0:
            log.error(f"\u001b[35mSorry. We couldn't find any movies matching {title} ({year})\u001b[0m")
            return
        if radarr_api_response.status_code == 200:
            data = json.loads(radarr_api_response.text)
            tmdbid = data["tmdbId"]
            title = data["title"]
            year = data['year']
            images = json.loads(json.dumps(data["images"]))
            titleslug = data["titleSlug"]
            movie_data = json.dumps({
                "title":               title,
                "qualityProfileId":    ProfileId,
                "year":                year,
                "tmdbId":              tmdbid,
                "titleslug":           titleslug,
                "monitored":           True,
                "minimumAvailability": "released",
                "rootFolderPath":      rootfolderpath,
                "images":              images,
                "addOptions":          {"searchForMovie": searchForMovie}})
        elif radarr_api_response.status_code == 404:
            log.error(f"\u001b[36m{imdbid}\t \u001b[0m{title} ({year}) Movie not found... unable to add to Radarr")
            return
        elif radarr_api_response.status_code == 500:
            log.error(f"\u001b[36m{imdbid}\t \u001b[0m{title} ({year}) Can't find TMDB ID - movie may have been removed!"
                      f"")
        else:
            log.error("Something else has happened.")
            return
        # Add Movie To Radarr
        headers = {"Content-type": "application/json", 'Accept': 'application/json', "X-Api-Key": api_key}
        url = '{}{}/api/v3/movie'.format(baseurl, urlbase)
        radarr_api_response = requests.post(url, headers=headers, data=movie_data)
        if radarr_api_response.status_code == 201:
            movie_added_count += 1
            if searchForMovie:  # Check If you want to force download search
                log.info(
                    f"\u001b[36m{imdbid}\t \u001b[0m{title} ({year}) \u001b[32mAdded to Radarr :) \u001b[36;1mNow "
                    f"Searching.\u001b[0m\n")
            else:
                log.info(
                    f"\u001b[36m{imdbid}\t \u001b[0m{title} ({year}) \u001b[32mAdded to Radarr :) \u001b[31mSearch "
                    f"Disabled.\u001b[0m\n")
    else:
        movie_exist_count += 1
        log.info("\u001b[36m{}\t \u001b[0m{} ({}) already Exists in Radarr.".format(imdbid, title, year))
        return


def get_quality_profiles() -> list:
    """
Parses local Radarr API to get the server's quality profiles and return them to calling
functions
    :return: The server's quality profiles as a list
    :rtype: list
    """
    log.info("Getting quality profiles...")
    headers = {"Content-type": "application/json", "X-Api-Key": "{}".format(api_key)}
    url = "{}{}/api/v3/qualityProfile".format(baseurl, urlbase)
    r = requests.get(url, headers=headers)
    profiles_json = json.loads(r.text)
    return profiles_json


def select_profile_id() -> int:
    """
Allows the user to select a quality profile ID at runtime using console input
    :return: Returns an integer that matches the specified quality profile Id
    :rtype: int

    """
    selected = False
    profile_choice = -1

    quality_profiles = get_quality_profiles()
    print("\nPlease enter a valid profile ID:")
    for profile in quality_profiles:
        print(f"{profile.get('id')}: {profile.get('name')}")
    while not selected:
        user_input = input("> ")
        selected = match_profile_id(user_input)
        if selected:
            profile_choice = int(user_input)
    return profile_choice


def match_profile_id(quality_id: str) -> bool:
    """
Checks if a given quality profile ID matches with one from the API.
    :rtype: bool
    :param quality_id: Quality profile ID as a string
    :return: Returns true if the quality profile is matched/found
    """
    profiles = get_quality_profiles()
    profile = next((p for p in profiles if p["id"] == int(quality_id)), False)
    if not profile:
        log.error(f'Could not find profile_id for instance profile ID f"{quality_id}"')
        sys.exit(0)
    return True


def get_imdbid(title: str, year: str) -> str | None:
    """
Uses OMDB to return the IMDB ID (ttXXXXXXX) of a movie
    :param title: Title of the movie
    :param year: Year the movie released
    :return: IMDB ID of the movie if found, or None if not.
    """
    # Get Movie imdbid
    log.info(f"Getting IMDbId for {title}")
    parsed_movie_title = urllib.parse.quote(title, "UTF-8")
    headers = {"Content-type": "application/json", 'Accept': 'application/json'}
    r = requests.get(f"https://www.omdbapi.com/?t={parsed_movie_title}&y={year}&type=movie&apikey={omdbapi_key}",
                     headers=headers)
    if r.status_code == 401:
        log.error("omdbapi Request limit reached!")
    d = json.loads(r.text)
    if r.status_code == 200:
        if d.get('Response') == "False":
            return None
        else:
            return d.get('imdbID')
    else:
        return None


def get_year(imdbid: str) -> str | None:
    """
Uses OMDB to check the year that a given movie released
    :param imdbid: The IMDB ID of a movie
    :return: Year the movie released if found, None if not
    """
    # Get Movie Year
    headers = {"Content-type": "application/json", 'Accept': 'application/json'}
    r = requests.get(f"https://www.omdbapi.com/?t={imdbid}&apikey={omdbapi_key}", headers=headers)
    if r.status_code == 401:
        log.error("omdbapi Request limit reached!")
    d = json.loads(r.text)
    if r.status_code == 200:
        if d.get('Response') == "False":
            return None
        else:
            return d.get('Year')
    else:
        return None


def main():
    global RadarrData

    print('\033c')
    if sys.version_info[0] < 3:
        log.error("Must be using Python 3")
        sys.exit(-1)
    if len(sys.argv) < 2:
        log.error("No list Specified... Bye!!")
        sys.exit(-1)
    if not os.path.exists(sys.argv[1]):
        log.error("{} Does Not Exist".format(sys.argv[1]))
        sys.exit(-1)

    log.info("Downloading Radarr Movie Data. :)")
    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    url = "{}{}/api/v3/movie".format(baseurl, urlbase)
    rsp = requests.get(url, headers=headers)
    if rsp.status_code == 200:
        RadarrData = json.loads(rsp.text)
    else:
        log.error("Failed to connect to Radarr...")

    with open(sys.argv[1], encoding="ISO-8859-1", errors='ignore') as csvfile:
        total_count = len(list(csv.DictReader(csvfile)))
    with open(sys.argv[1], encoding="ISO-8859-1", errors='ignore') as csvfile:
        movies_list = csv.DictReader(csvfile)
        if not total_count > 0:
            log.error("No movies found in CSV file.")
            exit()
        if movies_list.fieldnames != ["title", "year", "imdbid"]:
            log.error("Invalid CSV File, Header does not contain title,year,imdbid")
            sys.exit(-1)
        log.info("Found {} Movies in {}. :)".format(total_count, sys.argv[1]))
        for row in movies_list:
            title = row['title']
            year = row['year']
            imdbid = row['imdbid']
            try:
                add_movie(title, year, imdbid)
            except Exception as e:
                log.error(e)
                sys.exit(-1)
    log.info("Added {} of {} Movies, {} already exists. ;)".format(movie_added_count, total_count, movie_exist_count))


if __name__ == "__main__":
    main()
