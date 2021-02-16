import os, time, requests, json, sys, re, configparser


config = configparser.ConfigParser()
config.read('./config.ini')
omdbapi_key = config['sonarr']['omdbapi_key']

def main():
    if len(sys.argv)<2: 
        print ("No list Specified... Bye!!")
        exit()
    f=open(sys.argv[1], "r")
    if f.mode == 'r':
        f1 = f.readlines()
    for x in f1:
        r = requests.get("https://www.omdbapi.com/?t={}&type=movie&apikey={}".format(x.rstrip(),omdbapi_key))
        if r.status_code == 200:
            item = json.loads(r.text)
            if item.get('Response') == "False": 
                continue
            else:
                year = item.get('Year')
                imdbid = item.get('imdbID')
                title = item.get('Title')
                title = re.sub('[(]\d{4}[)]','',title)
                print ("{},{},{}".format(title.rstrip(),year[:4],imdbid))

if __name__ == "__main__":
    main()

