## Radarr and Sonarr Tools

*radarr_add_from_list.py* Add Movies from a csv formatted file.

*sonarr_add_from_list.py* Add Movies from a csv formatted file.

*radarr_remove_downloaded.py* Removes already downloaded movies and removes there entries from Radarr.

*backup_radarr_2csv.py* Creates a backup of the Radarr Database for easy importing.

*backup_sonarr_2csv.py* Creates a backup of the Sonarr Database for easy importing.

*get_imdbid.py* Matches the imdbid from a csv list MovieName/ShowName,Year for easy importing for the list import.

Using radarr_add_from_list/sonarr_add_from_list
The input list file has to have the format. It has to have MovieName/ShowName,Year,imdbid(Optional Makes it easer to find movie/TV show)

Movies CSV
```
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
rootfolderpath = Movie Root Path
searchForMovie = Enable forced search
qualityProfileId = 
omdbapi_key =  sign up here for free api key http://www.omdbapi.com/apikey.aspx
```
```
Standard Profile ID
1 Any
2 SD
3 HD-720p
4 HD-1080p
5 Ultra-HD
6 HD - 720p/1080p
```
