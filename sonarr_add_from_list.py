import os, time, requests, logging, logging.handlers, json, sys, re, csv, configparser, base64
from colorlog import ColoredFormatter
from datetime import  datetime

show_added_count = 0
show_exist_count = 0
sonarrData = []
# Config ###############################################################################################################

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['sonarr']['baseurl']
urlbase = config['sonarr']['urlbase']
api_key = config['sonarr']['api_key']
rootfolderpath = config['sonarr']['rootfolderpath']
searchForShow = config['sonarr']['searchForShow']
qualityProfileId = config['sonarr']['qualityProfileId']
omdbapi_key = config['sonarr']['omdbapi_key']

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
    if imdbid == None : imdbid = get_imdbid(title,year)
    if imdbid == None : log.info("Not imdbid found for {}".format(title)); return
    imdbIds = []
    tvdbIds = []
    for shows_to_add in sonarrData:  imdbIds.append(shows_to_add.get('imdbId'))
    for shows_to_add in sonarrData:  tvdbIds.append(shows_to_add.get('tvdbId'))
   
    if imdbid not in imdbIds:
        tvdbId = get_tvdbId(title,imdbid)
        if tvdbId in tvdbIds: 
            show_exist_count +=1
            log.info("\033[1;36m{}\t {} ({}) already Exists in Sonarr.\u001b[0m".format(imdbid,title,year))
            return
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter) 

        if tvdbId == None: log.error("No tvdbId found for {}".format(title)); return
        if not qualityProfileId.isdigit(): 
            ProfileId = get_profile_from_id(qualityProfileId)
        elif qualityProfileId == None: 
            log.error("\u001b[35m qualityProfileId Not Set in the config correctly.\u001b[0m")
        else: 
            ProfileId = qualityProfileId
        
        headers = {"Content-type": "application/json"}
        url = "{}{}/api/v3/series/lookup?term=tvdb:{}&apikey={}".format(baseurl,urlbase,tvdbId, api_key )
        rsp = session.get(url, headers=headers)
        data = json.loads(rsp.text)
        if rsp.text =="[]":
            log.error("\u001b[35mSorry. We couldn't find {} ({})\u001b[0m".format(title,year))
            return 
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
        
        url = '{}{}/api/v3/series'.format(baseurl,urlbase)
        rsp = requests.post(url, headers=headers, data=data)
        data = json.loads(rsp.text)

        if rsp.status_code == 201:
            show_added_count +=1
            if searchForShow == "True":
                log.info("\033[0;32m{}\t {} ({}) Added to Sonarr :) Now Searching.\u001b[0m".format(imdbid,title,year))
            else:
                log.info("\033[0;32m{}\t {} ({}) Added to Sonarr :) \033[1;31mSearch Disabled.\u001b[0m".format(imdbid,title,year))
        elif rsp.status_code == 400:
            show_exist_count +=1
            log.info("\033[1;36m}\t {} ({}) already Exists in Sonarr.\u001b[0m".format(imdbid,title,year))
            return
        else:
            log.error("\u001b[32m{}\t {} ({}) Not found, Not added to Sonarr.\u001b[0m".format(imdbid,title,year))
            return
    
    else:
        show_exist_count+=1
        log.info("\033[1;36m{}\t {} ({}) already Exists in Sonarr.\u001b[0m".format(imdbid,title,year))
        return

def get_imdbid(title,year,imdbid):
    # Get TV Show imdbid 
    headers = {"Content-type": "application/json", 'Accept':'application/json'}
    r = requests.get("https://www.omdbapi.com/?t={}&y={}&apikey={}".format(title,year,omdbapi_key), headers=headers)
    if r.status_code == 401:
        log.error("omdbapi Request limit reached!")
        return None
     
    if r.status_code == 200: 
        d = json.loads(r.text)
        if d.get('Response') == "False": 
            return  None
        else: 
            return d.get('imdbID')
    else: 
        return None 

def get_tvdbId(title,imdbid):
    api = str(base64.b64decode('YWE2Yjc5YTBlZDdjM2Y3NWUyOWI1MjkyOTAyNjhmOGFkNzM0ZmE3MWUzYzA3Zjg2YmE2OTVlMzQzZDFmZmNjMw=='))
    bearer = str(base64.b64decode('NTQ2NTc4MTc0ODY4YTllODUxMTFhYzZkYjg2ODg2MmNkMTU0MjU3MmY4ODE2M2I4ODZjNmJiMWVlMWE2NmMzNA=='))
    title = title.replace(" ","-"); title = title.replace("'","-"); title = title.replace(":","")
    if title.find("&"): title = title.replace(" ",""); title = title.replace("&","-")
    headers = {'Content-Type': 'application/json', 'trakt-api-version': '2', 'trakt-api-key': api, 'Authorization': 'Bearer {}'.format(bearer)}
    rsp = requests.get('https://api.trakt.tv/search/imdb/{}?type=show'.format(imdbid), headers=headers)
    if rsp.status_code == 403: log.error("trakt Api Failed"); return None
    if rsp.status_code == 200:
        d = json.loads(rsp.text)
        if d == []: 
            rsp = requests.get('https://api.trakt.tv/shows/{}'.format(title), headers=headers)
            if rsp.status_code == 200:
                d = json.loads(rsp.text)
                if d == []: return None 
                return d['ids']['tvdb']
            else:
                return None
        else:
            return d[0]['show']['ids']['tvdb']
    else:
         return None

def get_profile_from_id(id): 
    headers = {"Content-type": "application/json", "X-Api-Key": "{}".format(api_key)}
    url = "{}{}/api/v3/profile".format(baseurl,urlbase)
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
    url = "{}{}/api/v3/series".format(baseurl,urlbase)
    rsp = requests.get(url , headers=headers)
    if rsp.status_code == 200:
        sonarrData = json.loads(rsp.text)
    else:
        log.error("Failed to connect to Radar...")
    with open(sys.argv[1], encoding="utf8") as csvfile: total_count = len(list(csv.DictReader(csvfile)))
    with open(sys.argv[1], encoding="utf8") as csvfile:
        s = csv.DictReader(csvfile)
        if not total_count>0: log.error("No TV Shows Found in file... Bye!!"); exit()
        log.info("Found {} TV Shows in {}. :)".format(total_count,sys.argv[1]))

        for row in s:
            if not (row): continue
            if len(row) >= 4: log.error("Invalid Format on line {} Data:{}".format(str(s.line_num),row)); continue
            try: row['title']
            except: log.error("Invalid CSV File, Header does not contain title,year,imdbid"); sys.exit(-1)
            title = row['title']; year = row['year']; imdbid = row['imdbid']
            try: add_show(title,year,imdbid)
            except Exception as e: log.error(e); sys.exit(-1)
    log.info("Added {} of {} Shows, {} Already Exist".format(show_added_count,total_count,show_exist_count))


if __name__ == "__main__":
    main()

