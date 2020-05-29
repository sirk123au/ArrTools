## Radarr and Sonarr Tools

*radarr_add_from_list.py* Add Movies from a csv formatted file.

*sonarr_add_from_list.py* Add Movies from a csv formatted file.

*radarr_remove_downloaded.py* Removes already downloaded movies and removes their entries from Radarr.

*backup_radarr_2csv.py* Creates a backup of the Radarr Database for easy importing.

*backup_sonarr_2csv.py* Creates a backup of the Sonarr Database for easy importing.

*get_imdbid.py* Matches the imdbd from a csv list MovieName/ShowName,Year for easy importing for the list import.

Using radarr_add_from_list/sonarr_add_from_list
The input list file has to have the format. 
It has to have MovieName/ShowName,Year,imdbid(Optional Makes it easer to find movie/TV show)

Use pip install -r requirments.txt to install the required python modules 

Movies CSV
```
title,year,imdbid
Ben-Hur,1959,tt0052618
Gone with the Wind,1939,tt0031381
Vreme na nasilie,1988,tt0096403

Without imdbid

The English Patient,1996
Schindler's List,1993
```
TV Shows CSV

```
13 Reasons Why,2017,tt1837492
50 Central,2017,tt7261310

Without imdbID

60 Days In,2016
9-1-1,2018
A Discovery of Witches,2018

```

when you run it use
```
$python3 radarr_add_from_list.py movielist.csv
$python3 sonarr_add_from_list.py showlist.csv
```
Rename config_example.ini and add your details

```
api_key = Radarr Api Key
baseurl = Radarr Base Url
urlbase = ; Include URL Base if you have it enabled
rootfolderpath = Movie Root Path
searchForMovie = Enable forced search
qualityProfileId = 
omdbapi_key =  sign up here for free api key http://www.omdbapi.com/apikey.aspx

[sonarr]
api_key = 
baseurl = 
urlbase = ; Include URL Base if you have it enabled
rootfolderpath = 
searchForShow = 
qualityProfileId = 
omdbapi_key = 
tvdb_api =  ; sign up here for a api key https://thetvdb.com/api-information
tvdb_userkey = 
tvdb_username = 

Standard Profile ID
1 Any
2 SD
3 HD-720p
4 HD-1080p
5 Ultra-HD
6 HD - 720p/1080p
```

Thanks for the support :)
<a href="https://www.buymeacoffee.com/Sirk123au" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>
