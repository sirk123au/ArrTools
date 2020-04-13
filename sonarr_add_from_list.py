import os, time, requests, logging, logging.handlers, json, sys, re, csv, configparser
from colorlog import ColoredFormatter
from datetime import  datetime

show_added_count = 0
show_exist_count = 0
sonarrData = []
# Config ###############################################################################################################

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['sonarr']['baseurl']
api_key = config['sonarr']['api_key']
rootfolderpath = config['sonarr']['rootfolderpath']
searchForShow = config['sonarr']['searchForShow']
qualityProfileId = config['sonarr']['qualityProfileId']
omdbapi_key = config['sonarr']['omdbapi_key']
tvdb_api = config['sonarr']['tvdb_api']
tvdb_userkey = config['sonarr']['tvdb_userkey']
tvdb_username = config['sonarr']['tvdb_username']

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
logger.setLevel(logging.INFO) # DEBUG To show all
logger.setFormatter(formatter)
logging.getLogger().addHandler(logger)

if not os.path.exists("./logs/"): os.mkdir("./logs/")
logFileName =  "./logs/safl.log"
filelogger = logging.handlers.RotatingFileHandler(filename=logFileName)
filelogger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
filelogger.setFormatter(logFormatter)
logging.getLogger().addHandler(filelogger)

log = logging.getLogger("app." + __name__)

########################################################################################################################

def add_show(title,year,imdbid):
    
    # Add Missing to sonarr Work in Progress
    global show_added_count
    global show_exist_count
    if imdbid =='' : imdbid = get_imdbid(title,year)
    if imdbid =='': log.info("Not imdbid found for {}".format(title)); return
    imdbIds = []
    tvdbIds = []
    for shows_to_add in sonarrData:  imdbIds.append(shows_to_add.get('imdbId'))
    for shows_to_add in sonarrData:  tvdbIds.append(shows_to_add.get('tvdbId'))
   
    if imdbid not in imdbIds:
        tvdbId = get_tvdbId(imdbid,title)
        if tvdbId in tvdbIds: 
            show_exist_count +=1
            log.info("{}\t {} ({}) already Exists in Sonarr.".format(imdbid,title,year))
            return
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter) 

        if tvdbId is None: log.error("Not tvdbId found for {}".format(title)); return
        if not qualityProfileId.isdigit(): 
            ProfileId = get_profile_from_id(qualityProfileId)
        else: 
            ProfileId = qualityProfileId
        headers = {"Content-type": "application/json"}
        url = "{}/api/series/lookup?term=tvdb:{}&apikey={}".format(baseurl,tvdbId, api_key )
        rsp = session.get(url, headers=headers)
        data = json.loads(rsp.text)
        if len(rsp.text)==0: 
            log.error("Sorry. We couldn't find any Shows matching {} ({})".format(title,year))
            return 
        tvdbId = data[0]["tvdbId"]
        title = data[0]["title"]
        year = data[0]["year"]
        images = json.loads(json.dumps(data[0]["images"]))
        titleslug = data[0]["titleSlug"] 
        seasons = json.loads(json.dumps(data[0]["seasons"]))
        headers = {"Content-type": "application/json", "X-Api-Key": "{}".format(api_key)}
        data = json.dumps({
            "title": title ,
            "year": year ,
            "tvdbId": tvdbId ,
            "titleslug": titleslug,
            "monitored": 'true' ,
            "seasonFolder": 'true',
            "qualityProfileId": ProfileId,
            "rootFolderPath": rootfolderpath ,
            "images": images,
            "seasons": seasons,
            "addOptions":
                        {
                        "ignoreEpisodesWithFiles": "true",
                        "ignoreEpisodesWithoutFiles": "false",
                        "searchForMissingEpisodes": searchForShow
                        }

            })
        
        url = '{}/api/series'.format(baseurl)
        rsp = requests.post(url, headers=headers, data=data)
        data = json.loads(rsp.text)
        if rsp.status_code == 201:
            show_added_count +=1
            if searchForShow == "True":
                log.info("{}\t {} ({}) Added to Sonarr :) Now Searching.".format(imdbid,title,year))
            else:
                log.info("{}\t {} ({}) Added to Sonarr :) Search Disabled.".format(imdbid,title,year))
        elif rsp.status_code == 400:
            show_exist_count +=1
            log.info("{}\t {} ({}) already Exists in Sonarr.".format(imdbid,title,year))
            return
        else:
            log.error("{}\t {} ({}) Not found, Not added to Sonarr.".format(imdbid,title,year))
            return
    
    else:
        show_exist_count+=1
        log.info("{}\t {} ({}) already Exists in Sonarr.".format(imdbid,title,year))
        return

def get_imdbid(title,year):
    # Get TV Show imdbid 
    headers = {"Content-type": "application/json", 'Accept':'application/json'}
    r = requests.get("https://www.omdbapi.com/?t={}&y={}&apikey={}".format(title,year,omdbapi_key), headers=headers)
    if r.status_code == 401:
        log.error("omdbapi Request limit reached!")
    d = json.loads(r.text)
    if r.status_code == 200: 
        if d.get('Response') == "False": 
            return  None
        else: 
            return d.get('imdbID')
    else: 
        return None 

def get_tvdbId(imdbid,title):
    JWT_token = get_token()
    if JWT_token == '':
        log.error("Failed to get thetvdb token")
        sys.exit(-1)   
    headers = {"Content-type": "application/json",  "Authorization": "Bearer {}".format(JWT_token)}
    url = "https://api.thetvdb.com/search/series?imdbId={}".format(imdbid)
    rsp = requests.get(url, headers=headers)
    if rsp.status_code == 200:
        tmdb_data = json.loads(rsp.text)
        return tmdb_data['data'][0]['id']
    elif rsp.status_code == 404:
<<<<<<< HEAD
         
        headers = {"Content-type": "application/json",  "Authorization": "Bearer {}".format(JWT_token)}
        url = "https://api.thetvdb.com/search/series?name={}".format(title)
        rsp = requests.get(url, headers=headers)
        if rsp.status_code == 200:
            tmdb_data = json.loads(rsp.text)
            return tmdb_data['data'][0]['id']
        elif rsp.status_code == 404:

            return None
    else: 
        log.error("Failed with status {}\n".format(rsp.status_code))
        return None

def get_token():
    data = {
        "apikey": tvdb_api,
        "userkey": tvdb_userkey, 
        "username": tvdb_username 
        }
    url = "https://api.thetvdb.com/login"
    rsp = requests.post(url, json=data)
    if rsp.status_code == 200:
        data = json.loads(rsp.text)
        return data['token']
    else:
        log.error("Failed to get TvDB JWT Token"); sys.exit(-1)

def get_profile_from_id(id): 
    headers = {"Content-type": "application/json", "X-Api-Key": "{}".format(api_key)}
    url = "{}/api/profile".format(baseurl)
    r = requests.get(url, headers=headers)
    d = json.loads(r.text)
    profile = next((item for item in d if item["name"].lower() == id.lower()), False)
    if not profile:
        log.error('Could not find profile_id for instance profile {}'.format(id))
        sys.exit(0)
    return  profile.get('id')


def main():
    print('\033c')
    if sys.version_info[0] < 3: log.error("Must be using Python 3"); sys.exit(-1)
    global sonarrData
    if len(sys.argv)<2: log.error("No list Specified... Bye!!"); sys.exit(-1)
    if not os.path.exists(sys.argv[1]): log.info("{} Does Not Exist".format(sys.argv[1])); sys.exit(-1)
    log.info("Downloading Sonarr Show Data. :)")
    headers = {"Content-type": "application/json", "X-Api-Key": api_key }
    url = "{}/api/series".format(baseurl)
    rsp = requests.get(url , headers=headers)
    if rsp.status_code == 200:
        sonarrData = json.loads(rsp.text)
    else:
        log.error("Failed to connect to Radar...")

    with open(sys.argv[1]) as csvfile:
        m = csv.reader(csvfile)
        s = sorted(m, key=lambda row:(row), reverse=False)
        total_count = len(s)
        if not total_count>0: log.error("No TV Shows Found in file... Bye!!"); exit()
        log.info("Found {} TV Shows in {}. :)".format(total_count,sys.argv[1]))

        for row in s:
            if not (row): continue
            num_cols = len(row)
            if num_cols == 2: title, year = row; imdbid = ''
            elif num_cols == 3: title, year, imdbid = row
            else: log.error("There was an error reading {} Details".format(title))
            try: add_show(title, year,imdbid)
            except Exception as e: log.error(e); sys.exit(-1)
    log.info("Added {} of {} Shows, {} Already Exist".format(show_added_count,total_count,show_exist_count))


if __name__ == "__main__":
    main()

