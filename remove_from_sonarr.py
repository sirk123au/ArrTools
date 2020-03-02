import os, requests, json, logging, logging.handlers, sys
from colorlog import ColoredFormatter
import configparser

# Config ###############################################################################################################

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['sonarr']['baseurl']
api_key = config['sonarr']['api_key']


# Logging ##############################################################################################################

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

logging.getLogger().setLevel(logging.NOTSET)

logger = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO) # DEBUG To show all
# logFormatter = logging.Formatter("\033[1;31;32m[%(levelname)s]  \u001b[0m%(message)s")
logger.setFormatter(formatter)
logging.getLogger().addHandler(logger)


rotatingHandler = logging.handlers.RotatingFileHandler(filename='./rfs.log')
rotatingHandler.setLevel(logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
rotatingHandler.setFormatter(logFormatter)
logging.getLogger().addHandler(rotatingHandler)

log = logging.getLogger("app." + __name__)

########################################################################################################################

print('\033c')
if sys.version_info[0] < 3: log.error("Must be using Python 3"); sys.exit(-1)
log.info("Downloading Sonarr Series Data...")
headers = {"Content-type": "application/json", "X-Api-Key": api_key }
url = "{}/sonarr/api/series".format(baseurl)
rsp = requests.get(url, headers=headers)
data = json.loads(rsp.text)
count = 0
for i in data:
	headers = {"Content-type": "application/json", "X-Api-Key": api_key }
	url = "{}/sonarr/api/series/{}?deleteFiles=false".format(baseurl,i['id'])
	# if 'Documentary' in i['genres']:
	# 	print('{} has these genres {}'.format(i['title'],i['genres']))
	if i['episodeFileCount'] == 0:
		# print(json.dumps(i, indent=4, sort_keys=True))
		rsp = requests.delete(url, headers=headers)
		if rsp.status_code == 200:
			count +=1
			log.info ("Removing {} from Sonarr...".format(i['title']))
log.info ("Removed {} Shows.".format(count))