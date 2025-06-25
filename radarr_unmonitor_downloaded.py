import os, requests, json, logging, logging.handlers, sys
from colorlog import ColoredFormatter
import configparser

# Config ###############################################################################################################

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['radarr']['baseurl']
urlbase  = config['radarr']['urlbase']
api_key = config['radarr']['api_key']
if urlbase != "": baseurl = "{}{}".format(baseurl,urlbase)

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
log = logging.getLogger("app." + __name__)

########################################################################################################################

print('\033c')
if sys.version_info[0] < 3: log.error("Must be using Python 3"); sys.exit(-1)
log.info("Downloading Radarr Movie Data...")
headers = {"Content-type": "application/json", "X-Api-Key": api_key }
url = "{}/api/v3/movie".format(baseurl)
rsp = requests.get(url, headers=headers)
data = json.loads(rsp.text)
count = 0
for i in data:
    headers = {"Content-type": "application/json", "X-Api-Key": api_key }
    url = "{}/api/v3/movie/{}".format(baseurl,i['id'])
    rsp = requests.get(url, headers=headers)
    if rsp.status_code == 200:
        if i['hasFile']: 
            if os.path.exists(i['path']):
                if i['monitored'] == True:
                    # print(json.dumps(i, indent=4, sort_keys=True))
                    data = json.loads(json.dumps(i))
                    data['monitored'] = False
                    data = json.dumps(data, indent=4, sort_keys=True)
                    headers = {"Content-type": "application/json", 'Accept':'application/json', "X-Api-Key": api_key}
                    url = '{}/api/movie'.format(baseurl)
                    rsp = requests.put(url, headers=headers, data=data)
                    if rsp.status_code == 201:
                        count += count
                        log.info ("\u001b[36m{} ({})\u001b[0m Has been downloaded, \u001b[31mUnmonitoring....\u001b[0m".format(i['title'],i['year']))
log.info ("Unmonitored {} Movies.".format(count))
