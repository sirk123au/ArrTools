import requests, json, csv, sys, configparser

if sys.version_info[0] < 3: raise Exception("Must be using Python 3")

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['sonarr']['baseurl']
api_key = config['sonarr']['api_key']

with open('./sonarr_backup.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    print("Downloading Data...")
    headers = {"Content-type": "application/json", "X-Api-Key": api_key }
    url = "{}/api/series".format(baseurl)
    rsp = requests.get(url , headers=headers)
    csvwriter.writerow(['title','year','imdbid'])
    if rsp.status_code == 200:
        RadarrData = json.loads(rsp.text)
        for d in RadarrData: csvwriter.writerow([d['title'],d['year'], d.get('imdbId')])
    else:
        print("Failed to connect to Radar...")
print("Done...")