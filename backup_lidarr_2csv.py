import requests, json, csv, sys, configparser, re

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
        csvwriter.writerow(['artist','foreignArtistId'])
        for d in lidarrData:
            artist = re.sub(r'[^a-zA-Z0-9 ]',r'', d['artistName']) 
            csvwriter.writerow([artist, d.get('foreignArtistId')])
    else:
        print("Failed to connect to Radar...")
print("Done...")