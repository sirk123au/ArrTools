import requests, json, csv
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['radarr']['baseurl']
api_key = config['radarr']['api_key']

with open('./radarr_backup.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    print("Downloading Data...")
    headers = {"Content-type": "application/json", "X-Api-Key": api_key }
    url = "{}/api/movie".format(baseurl)
    rsp = requests.get(url , headers=headers)
    if rsp.status_code == 200:
        RadarrData = json.loads(rsp.text)
        for d in RadarrData: csvwriter.writerow([d['title'],d['year'], d.get('imdbId'),d.get('tmdbId')])
    else:
        print("Failed to connect to Radar...")
print("Done...")