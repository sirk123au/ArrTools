import os, time, requests, logging, logging.handlers, json, sys
from colorlog import ColoredFormatter

# Config ###############################################################################################################

api_key = 'a6db7a0ddf18311f7b97d78ee6d8806ff'
baseurl = 'http://cloud.kdata.net.au/radarr'
rootfolderpath = '/home/hd15/sirk123au/mnt/gdrive/Media/Movies/'
searchForMovie = "False"

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

filelogger = logging.handlers.RotatingFileHandler(filename='./rafl.log')
filelogger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
filelogger.setFormatter(logFormatter)
logging.getLogger().addHandler(filelogger)

log = logging.getLogger("app." + __name__)

########################################################################################################################

def add_movie(title, year):
	imdbid = get_imdb_id(title,year)
	headers = {"Content-type": "application/json", 'Accept':'application/json'}
	url = "{}/api/movie/lookup/imdb?imdbId={}&apikey={}".format(baseurl, imdbid, api_key)
	rsp = requests.get(url, headers=headers)
	if rsp.status_code == 200:
		if imdbid == None:
			url = "{}/api/movie/lookup?term={}&apikey={}".format(baseurl, title.replace(" ","%20"), api_key)
			rsp = requests.get(url, headers=headers)
			data = json.loads(rsp.text)
			if rsp.status_code == 200:
				tmdbid = data[0]["tmdbId"]
				title = data[0]["title"]
				year = data[0]['year']
				images = json.loads(json.dumps(data[0]["images"]))
				titleslug = data[0]["titleSlug"]
				Rdata = json.dumps({
					"title": title , 
					"qualityProfileId": '6' , 
					"year": year ,
					"tmdbId": tmdbid ,
					"titleslug":titleslug, 
					"monitored": 'true' , 
					"minimumAvailability": "released",
					"rootFolderPath": rootfolderpath ,
					"images": images,
					"addOptions" : {"searchForMovie" : searchForMovie}
					})
			else:
				log.info("{} ({}) Not found, Not added to Radarr..".format(title,year))
				return
				
		else:
			data = json.loads(rsp.text)
			tmdbid = data["tmdbId"]
			title = data["title"]
			year = data['year']
			images = json.loads(json.dumps(data["images"]))
			titleslug = data["titleSlug"]
			Rdata = json.dumps({
				"title": title , 
				"qualityProfileId": '6' , 
				"year": year ,
				"tmdbId": tmdbid ,
				"titleslug":titleslug, 
				"monitored": 'true' , 
				"minimumAvailability": "released",
				"rootFolderPath": rootfolderpath ,
				"images": images,
				"addOptions" : {"searchForMovie" : searchForMovie}})

	elif rsp.status_code == 404:
		log.info("{} ({}) Not found, Not added to Radarr..".format(title,year))
		return 
	elif rsp.status_code == 500:
		log.error("Unauthorized Access..")
		return
	else:
		log.error ("Failed to connect to Radarr.")
		return

	headers = {"Content-type": "application/json", 'Accept':'application/json', "X-Api-Key": api_key}
	url = '{}/api/movie'.format(baseurl)
	try:
		rsp = requests.post(url, headers=headers, data=Rdata)
	except requests.exceptions.RequestException as e:
		log.error ("Opps this error {} has just happend".format(e))

	if rsp.status_code == 201:
		if searchForMovie ==  "True":
			log.info("{}\t {} ({}) Added to Radarr, Now Searching...".format(imdbid,title,year))
		else:
			log.info("{}\t {} ({}) Added to Radarr, Search Disabled...".format(imdbid,title,year))
	elif rsp.status_code == 400:
		if searchForMovie ==  "True":
			movie_download(imdbid)
			return
		else:
			log.info("{}\t {} ({}) already Exists in Radarr, Search Disabled...".format(imdbid,title,year))
			return

def get_imdb_id(title,year):
	headers = {"Content-type": "application/json", 'Accept':'application/json'}
	r = requests.get("http://www.omdbapi.com/?t={}&y={}&apikey=43a1c303".format(title,year), headers=headers)
	if r.status_code == 200: return json.loads(r.text).get('imdbID')
	else: return None

def movie_download(imdbid):
	
	if not os.path.exists('data.json'):
		headers = {"Content-type": "application/json", "X-Api-Key": api_key }
		url = "{}/api/movie".format(baseurl)
		rsp = requests.get(url, headers=headers)
		data = json.loads(rsp.text)
		with open('data.json', 'w') as json_file: json.dump(data, json_file)
	else:
		with open('data.json') as json_file:
			data = json.load(json_file)
 
	for i in data:
			if i.get('imdbId','') == imdbid:
				if i['downloaded'] == False:
					headers = {"Content-type": "application/json"}
					url = "{}/api/command?apikey={}".format(baseurl, api_key)
					data = json.dumps({"name": "MoviesSearch", "movieIds": [i['id']]})
					rsp = requests.post(url, headers=headers , data=data)
					log.info("{} ({}) already Exists in Radarr, But Not Downloaded Now Searching...".format(i['title'],i['year']))
				else:
					log.info("{} ({}) already Exists in Radarr and has been Downloaded...".format(i['title'], i['year'])) 
					return

def main():
	print('\033c')
	movies_count = 0
	if len(sys.argv)<2:
		log.error("No list Specified... Bye!!")
		exit()
	if os.path.exists('data.json'): os.remove('data.json')
	if not os.path.exists(sys.argv[1]):
		log.info("{} Does Not Exist".format(sys.argv[1]))
		exit()
	with open(sys.argv[1]) as m: count = len(m.readlines())
	f=open(sys.argv[1], "r")
	if f.mode == 'r':
		f1 = f.readlines()
		if len(f1) == 0:
			log.error("No Movies Found in file... Bye!!")
			exit()
		log.info("Found {} Movies... :)".format(count))
		try:
			for x in f1:
				movies_count +=1
				title, year = x.split(',', 1)
				year = year.rstrip()
				add_movie(title, year)
		except Exception as e:
				log.error(e)
		log.info("Added {} of {} Movies".format(movies_count,count))

if __name__ == "__main__":
	main()