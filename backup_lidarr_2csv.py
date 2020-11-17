import requests, json, csv, sys, configparser

if sys.version_info[0] < 3: raise Exception("Must be using Python 3")

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['lidarr']['baseurl']
api_key = config['lidarr']['api_key']

with open('./lidarr_backup.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    print("Downloading Data...")
    headers = {"Content-type": "application/json", "X-Api-Key": api_key }
    url = "{}/api/v1/artist".format(baseurl)
    rsp = requests.get(url , headers=headers)
    if rsp.status_code == 200:
        lidarrData = json.loads(rsp.text)
        for d in lidarrData: csvwriter.writerow([d['artistName'], d.get('foreignArtistId')])
    else:
        print("Failed to connect to Radar...")
print("Done...")