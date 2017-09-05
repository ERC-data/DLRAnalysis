This repository should be cloned as the 'src' directory within a project parent directory. 
To run the scripts without a MSSQL database installation of the DLR project, access to a protected data repository is required. 
You can request access to this repo from @saintlyvi wiebke.toussaint@uct.ac.za

-----

Methodology for DLR DB data processing and anonymising

Check if /data/tables and /profiles folders exist in your home directory that contains the /src dir. If yes, check if they contain all the data you require. If no or if some data is missing, follow steps 1. and 2. below (only works with SQL database access).

1. use saveTables() in fetch_data.py to save tables as feather files (for working purposes only, not suitable for archiving)
2. use saveProfiles() in fetch_data.py to save load profiles as feather files (for working purposes only, not suitable for archiving)

Once the data has been extracted from the database and the tables and profiles directories are populated, you can use the remaining functions in the src directory to query the data.

For socio-demographic responses use the functions in answers.py to query the data.
