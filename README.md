# Radarr Tools 
### radarr_add_from_list.py Add Movies from a csv formatted file
### radarr_remove_downloaded.py Removes already downloaded movies and removes there entries from Radarr 
 
The input list file has to have the format. It has to have MovieName,Year,imdbid(Optional Makes it easer to find movie)
```
Ben-Hur,1959,tt0052618
Gone with the Wind,1939,tt0031381
Vreme na nasilie,1988,tt0096403

# OR without imdbid #
The English Patient,1996
Schindler's List,1993
```
when you run it use
```
$python3 radarr_add_from_list.py movielist.csv
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
