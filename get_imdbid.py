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
    if len(sys.argv)<2: print ("No list Specified... Bye!!"); sys.exit(-1)
    f=open(sys.argv[1], "r")
    if f.mode == 'r': f1 = f.readlines()
    print('\033c')
    res = input("This list contains S) TV Shows or M) Movies [S/M]? : ")
    if res == "S" or "s": res = 'series'
    elif res == "M" or "m": res = 'movie'
    else: print("Invalid Entry"); sys.exit(0)
    fo = open("{}.csv".format(res), "a")
    fo.write("title,year,imdbid\n")
    for x in f1:
        r = requests.get("https://www.omdbapi.com/?t={}&type={}&apikey={}".format(x.rstrip(),res,omdbapi_key))
        if r.status_code == 200:
            item = json.loads(r.text)
            if item.get('Response') == "False": 
                failed_count +=1
                ff = open("{}_failed".format(res), "a")
                ff.write("{} Failed to be Matched\n".format(x.rstrip()))
                ff.close()
                continue
            else:
                year = item.get('Year')
                imdbid = item.get('imdbID')
                title = item.get('Title')
                title = re.sub('[(]\d{4}[)]','',title)
                fo.write("{},{},{}\n".format(title.rstrip(),year[:4],imdbid))
                #print ("{},{},{}".format(title.rstrip(),year[:4],imdbid))
                print('\033c')
                print("Matching {} {}.".format(title,year[:4]))
                add_count +=1
    print("\u001b[32mMatched {} of {}, {} Failed to match. {} file was created.\u001b[0m".format(add_count,len(f1),failed_count,res))
    fo.close()

if __name__ == "__main__":
    main()

