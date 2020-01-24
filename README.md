# Add Movies from a csv formatted file

Add Movies to radarr from a csv list
The input list file has to have the format. It has to have MovieName,Year or it won't match correctly.

The Matrix,1999
The King,2005
Michael Clayton,2007
Fletch,1985
Roxanne,1987
Kingpin,1996
Stakeout,1987

when you run it use

$python radarr_add_from_list.py movielist.txt

which you add to the top of the radarr_add_from_list where it says config

api_key = 'Radarr Api Key'

baseurl = 'Radarr Base Url'

rootfolderpath = 'Movie Root Path'
