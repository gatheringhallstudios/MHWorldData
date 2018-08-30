[![Build Status](https://travis-ci.org/gatheringhallstudios/MHWorldData.svg?branch=master)](https://travis-ci.org/gatheringhallstudios/MHWorldData)

# MHWorldData
A project used to generate a SQLite database file from Monster Hunter World data.

There's currently no documentation for the db file. I recommend using a graphical tool like [SQliteBrowser](http://sqlitebrowser.org/) or figuring it out from the [mapping file](https://github.com/gatheringhallstudios/MHWorldData/blob/master/mhdata/sql/mappings.py). To see the data we build from, look at the [source_data](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data) folder.

## Purpose and goals
This project exists as a free and open collection of Monster Hunter World data for people to build cool things with. While the data has to be manually built right now, once we approach a stable version they will be available without the need to build.

We use the data generated here for the [MHWorldDatabase](https://github.com/gatheringhallstudios/MHWorldDatabase) Android app, which is also open source. 

## How to contribute
To contribute, create a pull request adding the data or translation you wish to add to the [source_data/](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data) folder. If the translation is for a language that is not supported, then add a name_code column using the [ISO language code](https://en.wikipedia.org/wiki/ISO_639-1). 

If you are unable to work Git but have data corrections or translations to contribute, you can create a Github Issue with new file or share a link to a google drive spreadsheet.

### MISSING (Important Todo)
This is data we'd love to receive help towards.
- Gathering Data is incomplete (**Important**).
  - Normal gather data: Requires us to throughly examine areas in game for different items and manually insert them into a spreadsheet.
  - Ore/Bone data: We will need a copy of モンスターハンター:ワールド 公式データハンドブック フィールド＆アイテムの知識書, and anyone capable of reading it, to read data and insert into a spreadsheet. This includes rare vs non-rare nodes.
- Proper Sharpness Data  (**Important**). Sharpness data needs to max to 400 units, and exist for sharpness+5 entries. Once we have max sharpness entries, we can derive non-max sharpness mathematically. Current existing sharpness data is wrong units and for sharpness+0 (cannot derive the other way).
- Quest list. Not really useful all on its own but leads into unlock conditions.
- Unlock conditions for special items like mantles, and base camps, including deliveries.
- Weapon motion value data

## Data Structure
The data files in [source_data/](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data) are used to build the final SQL file. The project is in the middle of a conversion from JSON to CSV, so some files are still JSON.

To edit the CSV files, I suggest using an office program like Excel or [LibreOffice](https://www.libreoffice.org/). Make sure to use UTF8 text encoding and comma separators when opening files. You can also import it to google drive.

Each subsystem (Monster/Armor/Weapons/etc) is stored in its own subdirectory. There are several types of data files:
- ***type*_base.csv**: A names and basic data registry containing the names of different objects of that type for each supported language, as well as any additional base data.
- ***type*_*data*.csv**: Additional data key'd by the name of the owning type. These are used when the type can have many data, like a monster can have many hunting rewards.
- ***type*_ext.csv**: Extension data that adds additional data to the type. This is used when each type can be optionally extended, such as a weapon that may be a bowgun and has bowgun ammo.

## How to build
Make sure Python 3.6 or greater is installed on your system, and pipenv is installed (`pip install pipenv`). Afterwards, you can install all dependencies by running `pipenv install`.

Afterwards, run `pipenv run python build.py` in a terminal to generate an `mhw.sql` file. Alternatively, run `pipenv shell` and then run `python build.py`.

You can run the tests by executing `pipenv run pytest tests`.

## Data Sources
The data collected by this project is an accumulation of various sources, including manual entry from the game itself, official guidebooks, and other collections like [LartTyler's API](https://github.com/LartTyler/MHWDB-Docs/wiki), Kiranico (raw data only), and multiple Japanese wikis. Handwritten guides are not collected in the repository.

If we accidently anything added here is yours, create an issue and I'll make sure to remove it.

## License
The build code is licensed under the [MIT License](http://opensource.org/licenses/mit-license.php). The data and images are from Monster Hunter World, which is owned by Capcom. You are free to use it, but I'd really appreciate it if you let me know what you're working on, and would be even more stoked if you let other people know where you got the data from in a note somewhere (although that's not required).

## Special Credits
- DiscreetMath - For streaming the game to me as I copied data down, while I lamented my wait for the PC release.
- [Vocalonation](https://github.com/ahctang) - For helping with translating and crossvalidating data.
