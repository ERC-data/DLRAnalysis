# SA Domestic Load Research 
## Data Access & Analysis

### Setup DLR_DB src environment
1. Make a parent directory and call it DLR_DB.
2. Clone the src repository from git: `git clone https://github.com/ERC-data/DLRAnalysis.git src`

### Setup DLR_DB data environment
To run the scripts without a MSSQL database installation of the DLR project, access to a protected data repository is required. You can request access to this repo from [\@saintlyvi](https://github.com/SaintlyVi)

3. Clone the data repository from git into DLR_DB : `git clone https://github.com/SaintlyVi/DLR_data.git data`

### Explore socio-demographic and timeseries data

-----

### Raw data processing and anonymising

If you have access to an MSSQL installation of the DLR database, you can access the raw survey and profile data.

1. Follow the src environment setup instructions
2. Use `saveTables()` in fetch_data.py to save tables as feather files * 
3. Use `saveProfiles()` in fetch_data.py to save load profiles as feather files *
4. Use `reduceRawProfiles()` and `saveHourlyProfiles()` in tswrangler.py to reduce and save 5min data to hourly timeseries

\* feather is a fast and efficient file format for storing and retrieving data frames. It is compatible with both R and python. Feather files should be stored for working purposes only and are not a suitable file format for archiving.

Once the data has been extracted from the database and saved in the appropriate directories, you can follow the instructions above to explore 
