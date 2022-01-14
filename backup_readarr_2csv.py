import requests, json, csv, sys, configparser

if sys.version_info[0] < 3: raise Exception("Must be using Python 3")

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['readarr']['baseurl']
api_key = config['readarr']['api_key']

with open('./readarr_backup.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    print("Downloading Data...")
    headers = {"Content-type": "application/json", "X-Api-Key": api_key }
    url = "{}/api/v1/book".format(baseurl)
    rsp = requests.get(url , headers=headers)
    csvwriter.writerow(['AuthorID','AuthorName','BookID','BookName'])
    if rsp.status_code == 200:
        readarrData = json.loads(rsp.text)
        for d in readarrData: csvwriter.writerow([d['author']['foreignAuthorId'], d['author']['authorName'], d['foreignBookId'], d['title']])
    else:
        print("Failed to connect to readarr...")
print("Done...")