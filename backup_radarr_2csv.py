import requests, json, csv, sys, configparser

if sys.version_info[0] < 3: raise Exception("Must be using Python 3")

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['radarr']['baseurl']
api_key = config['radarr']['api_key']
urlbase = config['radarr']['urlbase']

with open('./radarr_backup.csv', 'w', encoding="utf-8",  newline='' ) as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    print("Downloading Data...")
    headers = {"Content-type": "application/json", "X-Api-Key": api_key }
    url = f"{baseurl}{urlbase}/api/v3/movie"
    rsp = requests.get(url , headers=headers)
    csvwriter.writerow(['title','year','imdbid', 'tmdbId'])
    if rsp.status_code == 200:
        RadarrData = json.loads(rsp.text)
        for d in RadarrData: csvwriter.writerow([d.get('title'),d.get('year'), d.get('imdbId'),d.get('tmdbId')])
    else:
        print("Failed to connect to Radar...")
print("Done...")