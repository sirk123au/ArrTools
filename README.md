# Add Movies from a csv formatted file

Add Movies to radarr from a csv list

The input list file has to have the format. It has to have MovieName,Year or it won't match correctly.
```
The Matrix,1999
The King,2005
Michael Clayton,2007
Fletch,1985
Roxanne,1987
Kingpin,1996
Stakeout,1987
```
when you run it use
```
$python3 radarr_add_from_list.py movielist.txt
```
Rename config_example.ini and add your details

```
api_key = Radarr Api Key
baseurl = Radarr Base Url
rootfolderpath = Movie Root Path
searchForMovie = Enable forced search
qualityProfileId = 
```
```
; Standard Profile ID
; 1 Any
; 2 SD
; 3 HD-720p
; 4 HD-1080p
; 5 Ultra-HD
; 6 HD - 720p/1080p
```
