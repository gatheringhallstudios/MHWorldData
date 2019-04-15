[![Build Status](https://travis-ci.org/gatheringhallstudios/MHWorldData.svg?branch=master)](https://travis-ci.org/gatheringhallstudios/MHWorldData)

# MHWorldData
A project used to generate a SQLite database file from Monster Hunter World data. Check the releases section for compiled db files.

There's currently no documentation for the db file. I recommend using a graphical tool like [SQliteBrowser](http://sqlitebrowser.org/) or figuring it out from the [mapping file](https://github.com/gatheringhallstudios/MHWorldData/blob/master/mhdata/sql/mappings.py). To see the data we build from, look at the [source_data](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data) folder.

## Purpose and goals
This project exists as a free and open collection of Monster Hunter World data for people to build cool things with. We use this data in the (also open source) [MHWorldDatabase](https://github.com/gatheringhallstudios/MHWorldDatabase) Android app.

There are very few open collections of Monster Hunter data out there, and assembling what we have added a significant amount of time to the app's development process. Hopefully this database can spare you some of that trouble.

The data collected is limited to observable or computable data. Handwritten guides and editorial content are not collected in the repository

## How to contribute
To contribute, create a pull request. All data is found in the [source_data/](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data) folder. If you want to contribute a code change, inspect build.py in the root folder and follow the import trail.

If you are unable to work Git but have data corrections or translations to contribute, you can create a Github Issue with the new file or share a link to a google drive spreadsheet.

### MISSING (Important Todo)
This is data we'd love to receive help towards.
- Gathering Data is incomplete (**Important**).
  - Normal gather data: Requires us to throughly examine areas in game for different items and manually insert them into a spreadsheet.
  - Ore/Bone data: We will need a copy of モンスターハンター:ワールド 公式データハンドブック フィールド＆アイテムの知識書, and anyone capable of reading it, to read data and insert into a spreadsheet. This includes rare vs non-rare nodes.
- Quest list. Not really useful all on its own but leads into unlock conditions.
- Unlock conditions for special items like mantles, and base camps, including deliveries.
- Weapon motion value data
- A refactor to schema validation to allow multi-stage validation. There are certain validations that we'd love to skip during merge routines but perform during database building. Right now we lack that degree of control and we need to add dummy data or not validate at all.

## Data Structure
The data files in [source_data/](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data) are used to build the final SQL file. The project is in the middle of a conversion from JSON to CSV, so some files are still JSON.

To edit the CSV files, I suggest using an office program like Excel or [LibreOffice](https://www.libreoffice.org/). Make sure to use UTF8 text encoding and comma separators when opening files. You can also import it to google drive.

Each subsystem (Monster/Armor/Weapons/etc) is stored in its own subdirectory. There are several types of data files:
- ***type*_base.csv**: A names and basic data registry containing the names of different objects of that type for each supported language, as well as any additional base data.
- ***type*_base_translations.csv**: An extension of a base file that adds translated names and potentially descriptions to the main base file.
- ***type*_*data*.csv**: Additional data key'd by the name of the owning type. These are used when the type can have many data, like a monster can have many hunting rewards.
- ***type*_ext.csv**: Extension data that adds additional data to the type. This is used when each type can be optionally extended, such as a weapon that may be a bowgun and has bowgun ammo.

## How to build
Make sure Python 3.6 or greater is installed on your system, and pipenv is installed (`pip install pipenv`). Afterwards, you can install all dependencies by running `pipenv install`.

Afterwards, run `pipenv run python build.py` in a terminal to generate an `mhw.sql` file. Alternatively, run `pipenv shell` and then run `python build.py`.

You can run the tests by executing `pipenv run pytest tests`.

### Merging ingame binaries
This project uses [fresch's mhw_armor_edit](https://github.com/fre-sch/mhw_armor_edit) to parse ingame binary data. To use it, follow the directions in fresch's repository to create a merged chunk data folder (make sure you own a copy of Monster Hunter World...), rename it to `mergedchunks`, and move it outside the project (to the same directory this project is contained in). Afterwards, run `pipenv run python merge.py binary update`.

The directory structure should approximately look like this:

```
-- any parent directory
 |-- mhworlddata/
  |-- mhdata/
  |-- mhw_armor_edit/
  |-- build.py
 |-- mergedchunks/
```

## Data Sources
The data collected by this project is an accumulation of various sources, including manual entry from the game itself, official guidebooks, and other collections like [LartTyler's API](https://github.com/LartTyler/MHWDB-Docs/wiki), Kiranico (raw data only), and Japanese wikis like [MHWG](http://mhwg.org/). .

We also use [fresch's mhw_armor_edit](https://github.com/fre-sch/mhw_armor_edit) for parsing ingame binaries.

## License
The build code is licensed under the [MIT License](http://opensource.org/licenses/mit-license.php). The data and images are from Monster Hunter World, which is owned by Capcom.

The `mhw_armor_edit/` folder and its contents are public domain. Instead of our silly little extraction, feel free to access the real deal [here](https://github.com/fre-sch/mhw_armor_edit).

You are free to use this database for any purpose.

## Special Credits
- [Hexhexhex](https://twitter.com/MHhexhexhex) - For releasing monster hitzone data.
- [LartTyler](https://github.com/LartTyler/MHWDB-Docs/wiki) - For creating a collection of data that allows others to pull from
- [Vocalonation](https://github.com/ahctang) - For helping with translating and crossvalidating data.
- [TanukiSharp](https://github.com/TanukiSharp/) - For creating a computer usable collection of sharpness data and allowing others to use it. His original project is [here](https://github.com/TanukiSharp/MHWSharpnessExtractor)
- DiscreetMath - For streaming the game to me as I copied data down, while I waited for the PC release.
