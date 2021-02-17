import os, time, requests, json, sys, re, configparser

config = configparser.ConfigParser()
config.read('./config.ini')
omdbapi_key = config['sonarr']['omdbapi_key']
add_count = 0
failed_count = 0
res = 0

def main():
    global add_count 
    global failed_count
    global res
    if len(sys.argv)<2: 
        print ("No list Specified... Bye!!")
        exit()
    f=open(sys.argv[1], "r")
    if f.mode == 'r':
        f1 = f.readlines()
    res = input("This list contains S) TV Shows or M) Movies [S/M]? : ")
    if res == "S": res = 'series'
    elif res == "M": res = 'movie'
    else: print("Invalid Entry"); sys.exit(0)

    for x in f1:
        r = requests.get("https://www.omdbapi.com/?t={}&type={}&apikey={}".format(x.rstrip(),res,omdbapi_key))
        if r.status_code == 200:
            item = json.loads(r.text)
            
            if item.get('Response') == "False": 
                failed_count +=1
                print("\u001b[31m{} Failed to be Matched\u001b[0m".format(x.rstrip()))
                continue
            else:
                year = item.get('Year')
                imdbid = item.get('imdbID')
                title = item.get('Title')
                title = re.sub('[(]\d{4}[)]','',title)
                print ("{},{},{}".format(title.rstrip(),year[:4],imdbid))
                add_count +=1
    print("\u001b[32mMatched {} of {}, {} Failed to match\u001b[0m".format(add_count,len(f1),failed_count))
if __name__ == "__main__":
    main()

