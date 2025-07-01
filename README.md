## Radarr and Sonarr Tools

*radarr_add_from_list.py* Add Movies from a csv formatted file.

*sonarr_add_from_list.py* Add Shows from a csv formatted file.

*lidarr_add_from_list.py* Add Artists from a csv formatted file.

*radarr_remove_downloaded.py* Removes already downloaded movies and removes their entries from Radarr.

*backup_radarr_2csv.py* Creates a backup of the Radarr Database for easy importing.

*backup_sonarr_2csv.py* Creates a backup of the Sonarr Database for easy importing.

*backup_lidarr_2csv.py* Creates a backup of the Lidarr Database for easy importing.

*get_imdbid.py* Matches the imdbd from a csv list MovieName/ShowName,Year for easy importing for the list import.

*arr_gui.py* Standalone GUI to import or export data for Radarr, Sonarr or Lidarr.

Using radarr_add_from_list/sonarr_add_from_list
The input list file has to have the format. 
It has to have MovieName/ShowName,Year,imdbid   **imdbid is Optional Makes it easer to find movie/TV show

Use pip install -r requirements.txt to install the required python modules 

Movies CSV
```
title,year,imdbid (This header has to be included in the csv for it to work correctly)
Ben-Hur,1959,tt0052618
Gone with the Wind,1939,tt0031381

Without imdbid

title,year,imdbid (This header has to be included in the csv for it to work correctly)
The English Patient,1996
Schindler's List,1993
```
TV Shows CSV

```
title,year,imdbid (This header has to be included in the csv for it to work correctly)
13 Reasons Why,2017,tt1837492
50 Central,2017,tt7261310

Without imdbID

title,year,imdbid (This header has to be included in the csv for it to work correctly)
60 Days In,2016
9-1-1,2018
A Discovery of Witches,2018

```
Artist CSV

```
artist,foreignArtistId
10cc
2 DJ's and One
3 Doors Down
3-11 Porter

With foreignArtistId

artist,foreignArtistId
Weird Al Yankovic,7746d775-9550-4360-b8d5-c37bd448ce01
Adele,cc2c9c3c-b7bc-4b8b-84d8-4fbd8779e493
Alanis Morissette,4bdcee62-4902-4773-8cd1-e252e2e31225
Arctic Monkeys,ada7a83c-e3e1-40f1-93f9-3e73dbc9298a
Augie March,29070ba5-c3df-41d9-bed0-8e2f1e1c22ad
BABYMETAL,27e2997f-f7a1-4353-bcc4-57b9274fa9a4
Backstreet Boys,2f569e60-0a1b-4fb9-95a4-3dc1525d1aad

```

If `foreignArtistId` is omitted, `lidarr_add_from_list.py` will attempt to
retrieve the MusicBrainz ID automatically.

Run the GUI with
```
$ python3 arr_gui.py
```
The CLI scripts remain for advanced usage, but the GUI handles common import
and export operations without calling them.
Rename config_example.ini and add your details

```
[radarr]
api_key = Radarr Api Key
baseurl = http://localhost:7878 Radarr Base Url
urlbase = ; Include URL Base if you have it enabled
rootfolderpath = Movie Root Path (trailing slash is needed eg. /media/Movies/ or d:\media\Movies\)
searchForMovie = Enable forced search
qualityProfileId = 
omdbapi_key =  sign up here for free api key http://www.omdbapi.com/apikey.aspx

[sonarr]
api_key = Sonarr Api Key 
baseurl = http://localhost:8989
urlbase = ; Include URL Base if you have it enabled
rootfolderpath = Show Root Path (trailing slash is needed eg. /media/shows/ or d:\media\shows\)
searchForShow = 
qualityProfileId = 
omdbapi_key = 
tvdb_api =  ; sign up here for a api key https://thetvdb.com/api-information
tvdb_userkey = 
tvdb_username = 

[lidarr]
api_key =
baseurl = http://localhost:8686
rootfolderpath =

[gui]
# Optional default CSV path used by arr_gui.py
default_csv =


Standard Profile ID
1 Any
2 SD
3 HD-720p
4 HD-1080p
5 Ultra-HD
6 HD - 720p/1080p
```

Thanks for the support :)

[![Github Sponsorship](https://img.shields.io/badge/support-me-red.svg)](https://github.com/users/sirk123au/sponsorship)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/M4M25DUMM)
