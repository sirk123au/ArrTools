import os, time, requests, logging, logging.handlers, json, sys, re, csv
from colorlog import ColoredFormatter
import configparser
from datetime import datetime 

movie_added_count=0
movie_exist_count=0

# Config ###############################################################################################################

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['radarr']['baseurl']
urlbase = config['radarr']['urlbase']
api_key = config['radarr']['api_key']
rootfolderpath = config['radarr']['rootfolderpath']
searchForMovie = config['radarr']['searchForMovie']
if searchForMovie is None: searchForMovie = 'False'
qualityProfileId = config['radarr']['qualityProfileId']
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
logger.setLevel(logging.INFO) # DEBUG To show all
logger.setFormatter(formatter)
logging.getLogger().addHandler(logger)
if not os.path.exists("./logs/"): os.mkdir("./logs/")
logFileName =  "./logs/rafl.log"#.format(datetime.now().strftime("%Y-%m-%d-%H.%M.%S"))
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
	if year == '': year = get_year(imdbid)
	if imdbid == '': imdbid = get_imdbid(title,year)

	# Store Radarr Server imdbid for faster matching
	movieIds = []
	for movie_to_add in RadarrData: movieIds.append(movie_to_add.get('imdbId')) 
	if imdbid not in movieIds:
		# Build json Data to inport into radarr	
		session = requests.Session()
		adapter = requests.adapters.HTTPAdapter(max_retries=20)
		session.mount('https://', adapter)
		session.mount('http://', adapter)
		if not qualityProfileId.isdigit(): 
			ProfileId = get_profile_from_id(qualityProfileId) 
		else: 
			ProfileId = qualityProfileId
		headers = {"Content-type": "application/json", 'Accept':'application/json'}
		url = "{}{}/api/movie/lookup/imdb?imdbId={}&apikey={}".format(baseurl,urlbase, imdbid, api_key)
		rsp = session.get(url, headers=headers)
		if len(rsp.text)==0: 
			log.error("\u001b[35mSorry. We couldn't find any movies matching {} ({})\u001b[0m".format(title,year))
			return 
		if rsp.status_code == 200:
			data = json.loads(rsp.text)
			tmdbid = data["tmdbId"]
			title = data["title"]
			year = data['year']
			images = json.loads(json.dumps(data["images"]))
			titleslug = data["titleSlug"]
			Rdata = json.dumps({
				"title": title , 
				"qualityProfileId": ProfileId , 
				"year": year ,
				"tmdbId": tmdbid ,
				"titleslug":titleslug, 
				"monitored": 'true' , 
				"minimumAvailability": "released",
				"rootFolderPath": rootfolderpath ,
				"images": images,
				"addOptions" : {"searchForMovie" : searchForMovie}})
		elif rsp.status_code == 404:
			log.error("\u001b[36m{}\t \u001b[0m{} ({}) Not found, Not added to Radarr.".format(imdbid,title,year))
			return
		else:
			log.error("Something else has happend.")
			return
		# Add Movie To Radarr
		headers = {"Content-type": "application/json", 'Accept':'application/json', "X-Api-Key": api_key}
		url = '{}{}/api/movie'.format(baseurl,urlbase)
		rsp = requests.post(url, headers=headers, data=Rdata)
		if rsp.status_code == 201:
			movie_added_count +=1
			if searchForMovie == "True": # Check If you want to force download search
				log.info("\u001b[36m{}\t \u001b[0m{} ({}) \u001b[32mAdded to Radarr :) \u001b[36;1mNow Searching.\u001b[0m".format(imdbid,title,year))
			else:
				log.info("\u001b[36m{}\t \u001b[0m{} ({}) \u001b[32mAdded to Radarr :) \u001b[31mSearch Disabled.\u001b[0m".format(imdbid,title,year))
	
	elif imdbid == None:
		# Search by Movie Title in Radarr
		url = "{}{}/api/movie/lookup?term={}&apikey={}".format(baseurl,urlbase, title.replace(" ","%20"), api_key)
		rsp = requests.get(url, headers=headers)
		data = json.loads(rsp.text)
		if rsp.text =="[]":
			log.error("\u001b[35mSorry. We couldn't find any movies matching {} ({})\u001b[0m".format(title,year))
			return 
		if rsp.status_code == 200:
			tmdbid = data[0]["tmdbId"]
			title = data[0]["title"]
			year = data[0]['year']
			images = json.loads(json.dumps(data[0]["images"]))
			titleslug = data[0]["titleSlug"]
			Rdata = json.dumps({
				"title": title , 
				"qualityProfileId": ProfileId , 
				"year": year ,
				"tmdbId": tmdbid ,
				"titleslug":titleslug, 
				"monitored": 'true' , 
				"minimumAvailability": "released",
				"rootFolderPath": rootfolderpath ,
				"images": images,
				"addOptions" : {"searchForMovie" : searchForMovie}
				})
			# Add Movie To Radarr
			headers = {"Content-type": "application/json", 'Accept':'application/json', "X-Api-Key": api_key}
			url = '{}{}/api/movie'.format(baseurl,urlbase)
			rsp = requests.post(url, headers=headers, data=Rdata)
			if rsp.status_code == 201:
				movie_added_count +=1
				if searchForMovie == "True": # Check If you want to force download search
					log.info("\u001b[36mtm{}\t         \u001b[0m{} ({}) \u001b[32mAdded to Radarr :) \u001b[36;1mNow Searching.\u001b[0m".format(tmdbid,title,year))
				else:
					log.info("\u001b[36mtm{}\t         \u001b[0m{} ({}) \u001b[32mAdded to Radarr :) \u001b[31mSearch Disabled.\u001b[0m".format(tmdbid,title,year))
			elif rsp.status_code == 400:
				movie_exist_count +=1
				log.info("\u001b[36mtm{}\t         \u001b[0m{} ({}) already Exists in Radarr.".format(tmdbid,title,year))
				return
		else:
			log.error("\u001b[35m{}\t {} ({}) Not found, Not added to Radarr.\u001b[0m".format(imdbid,title,year))
			return
	else:
		movie_exist_count +=1
		log.info("\u001b[36m{}\t \u001b[0m{} ({}) already Exists in Radarr.".format(imdbid,title,year))
		return


def get_profile_from_id(id): 
    headers = {"Content-type": "application/json", "X-Api-Key": "{}".format(api_key)}
    url = "{}{}/api/profile".format(baseurl,urlbase)
    r = requests.get(url, headers=headers)
    d = json.loads(r.text)
    profile = next((item for item in d if item["name"].lower() == id.lower()), False)
    if not profile:
        log.error('Could not find profile_id for instance profile {}'.format(id))
        sys.exit(0)
    return  profile.get('id')

def get_imdbid(title,year):
	# Get Movie imdbid 
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

def get_year(imdbid):
	# Get Movie Year 
	headers = {"Content-type": "application/json", 'Accept':'application/json'}
	r = requests.get("https://www.omdbapi.com/?i={}&apikey={}".format(imdbid,omdbapi_key), headers=headers)
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
	print('\033c')
	if sys.version_info[0] < 3: log.error("Must be using Python 3"); sys.exit(-1)
	global RadarrData
	if len(sys.argv)<2: log.error("No list Specified... Bye!!"); sys.exit(-1)
	if not os.path.exists(sys.argv[1]): log.info("{} Does Not Exist".format(sys.argv[1])); sys.exit(-1)
	log.info("Downloading Radarr Movie Data. :)")
	headers = {"Content-type": "application/json", "X-Api-Key": api_key }
	url = "{}{}/api/movie".format(baseurl,urlbase)
	rsp = requests.get(url , headers=headers)
	if rsp.status_code == 200:
		RadarrData = json.loads(rsp.text)
	else:
		log.error("Failed to connect to Radarr...")
	with open(sys.argv[1], encoding="utf8") as csvfile: total_count = len(list(csv.DictReader(csvfile)))
	with open(sys.argv[1], encoding="utf8") as csvfile:
		m = csv.DictReader(csvfile)
		if not total_count>0: log.error("No Movies Found in file... Bye!!"); exit()
		log.info("Found {} Movies in {}. :)".format(total_count,sys.argv[1]))
		for row in m:
			if not (row): continue
			title = row['title']; year = row['year']; imdbid = row['imdbid']
			try: add_movie(title, year,imdbid)
			except Exception as e: log.error(e); sys.exit(-1)
	log.info("Added {} of {} Movies, {} already exists. ;)".format(movie_added_count,total_count,movie_exist_count))

if __name__ == "__main__":
	main()