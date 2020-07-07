![build](https://github.com/gatheringhallstudios/MHWorldData/workflows/build/badge.svg)

# MHWorldData
A project used to generate a database from Monster Hunter World data. This database file is used to power the MHWorld Database Android app, but can be used for other purposes as well.

Check the releases section for compiled SQLite db files. There is no documentation for the db file, instead use a graphical tool like [SQliteBrowser](http://sqlitebrowser.org/) or figure it out from the [mapping file](https://github.com/gatheringhallstudios/MHWorldData/blob/master/mhdata/sql/mappings.py). The data we build from is in the [source_data](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data) folder.

Now that the game has launched for PC, the core maintainer has started in earnest. If you want to help speed up the process, please check out the help wanted section.

If you wish to chat with us, we also have a [discord server](https://discord.gg/k5rmEWh).

### Iceborne Update (Help Wanted)
I've started playing through the Iceborne PC launch, and while I'll have all data eventually, some help would definitely go a long way. Any help would be appreciated, but additions or corrections to these are some great examples:
- [Any monster data](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data/monsters) - Ailments, rewards, as well as corrections to weaknesses are all needed. Reward entries without a percentage value are ok at this stage.
- [Items and icon mappings](https://github.com/gatheringhallstudios/MHWorldData/blob/master/source_data/items/item_base.csv) - If any items are missing on that list, feel free to add them. We're also missing item icon names and colors. Note that item icons are a limited selection, so try to reuse existing names if possible. 
- Or really anything else you see.

## Purpose and goals
This project exists as a free and open collection of Monster Hunter World data for people to build cool things with. We use this data in the (also open source) [MHWorldDatabase](https://github.com/gatheringhallstudios/MHWorldDatabase) Android app.

There are very few open collections of Monster Hunter data out there, and assembling what we have added a significant amount of time to the app's development process. Hopefully this database can spare you some of that trouble.

The data collected is limited to observable or computable data. Handwritten guides and editorial content are not collected in the repository.

## How to contribute
This project sources most of its data from spreadsheets in the [source_data/](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data) folder. If you want to contribute a code change, inspect build.py in the root folder and follow the import trail.

If you are unable to work Git but have data corrections or translations to contribute, you can create a Github Issue with the new file or share a link to a google drive spreadsheet.

### MISSING (Important Todo)
This is data we'd love to receive help towards.
- Gathering Data is incomplete. Requires a thorough examination of in game for different items.
- Unlock conditions for special items like mantles, and base camps, including deliveries.
- Weapon motion value data
- (Developer) A refactor to schema validation to allow multi-stage validation. There are certain validations that we'd love to skip during merge routines but perform during database building. Right now we lack that degree of control and we need to add dummy data or not validate at all.

## Data Structure
The data files in [source_data/](https://github.com/gatheringhallstudios/MHWorldData/tree/master/source_data) are used to build the final SQL file. The project is in the middle of a conversion from JSON to CSV, so some files are still JSON.

To edit the CSV files, I suggest using an office program like Excel or [LibreOffice](https://www.libreoffice.org/). Make sure to use UTF8 text encoding and comma separators when opening files. You can also import it to google drive.

Each subsystem (Monster/Armor/Weapons/etc) is stored in its own subdirectory. There are several types of data files:
- ***type*_base.csv**: A names and basic data registry containing the names of different objects of that type for each supported language, as well as any additional base data.
- ***type*_base_translations.csv**: An extension of a base file that adds translated names and potentially descriptions to the main base file.
- ***type*_*data*.csv**: Additional data key'd by the name of the owning type. These are used when the type can have many data, like a monster can have many hunting rewards.
- ***type*_ext.csv**: Extension data that adds additional data to the type. This is used when each type can be optionally extended, such as a weapon that may be a bowgun and has bowgun ammo.

## How to build
Make sure Python 3.6 or greater is installed on your system, and pipenv is installed (`pip install pipenv`).
- Open a console window in the root project directory (shift+rightclick or `cd` to navigate to it)
- `pipenv install` to install all dependencies. Make sure its using python 3.6 or greater.
- `pipenv shell` to activate the environment

Afterwards, run `pipenv run python build.py` in a terminal to generate an `mhw.sql` file. You can run the tests by executing `pipenv run pytest tests`. 
You will need to use `pipenv shell` everytime you open a new console window.

### Merging ingame binaries
This project uses [fresch's mhw_armor_edit](https://github.com/fre-sch/mhw_armor_edit) to parse ingame binary data. To use it, follow the directions in fresch's repository to create a merged chunk data folder (make sure you own a copy of Monster Hunter World...), rename it to `mergedchunks`, and move it outside the project (to the same directory this project is contained in). Afterwards, run `pipenv run python binary.py update`.

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
The data collected by this project is an accumulation of various sources, including manual entry from the game itself, official guidebooks, and other collections.

- [fresch's mhw_armor_edit](https://github.com/fre-sch/mhw_armor_edit)
- [Decoration Drop Rates (by Asterisk)](https://docs.google.com/spreadsheets/d/1u9coasn-zyrBHKjcYedawr1A_bzPgrhjqMx6cMeqk_c/edit#gid=0)
- [Kiranico](https://mhworld.kiranico.com/)
- [Poedb](https://mhw.poedb.tw/eng/)
- [MHWG](http://mhwg.org/)
- [LartTyler's API](https://github.com/LartTyler/MHWDB-Docs/wiki)

## License
The build code is licensed under the [MIT License](http://opensource.org/licenses/mit-license.php). Data and images are from Monster Hunter World, which is owned by Capcom.

The `mhw_armor_edit/` folder and its contents are public domain. Instead of our silly little extraction, feel free to access the real deal [here](https://github.com/fre-sch/mhw_armor_edit).

You are free to use this database for any purpose.

## Special Credits
- Asterisk - For work in the modding community and completing Leshen Hitzones
- Deathcream - For figuring out many of the file formats
- MechE - For assembling an [awesome spreadsheet](https://docs.google.com/spreadsheets/d/1ttUaWtw2aaBFpz3NUp6izr-FgtQHSYJA_CjJA-xuets/edit#gid=730347439) of monster hitzones.
- Kurohonyon - Leshen Hitzones (except for ice weakness, which was missing)
- [Hexhexhex](https://twitter.com/MHhexhexhex) - For releasing certain monster hitzone data.
- Material - For releasing AT Kulve drop rates.
- [LartTyler](https://github.com/LartTyler/MHWDB-Docs/wiki) - For creating a collection of data that allows others to pull from
- [Vocalonation](https://github.com/ahctang) - For helping with translating and crossvalidating data.
- Fuzzle/David - Additional data from spreadsheets (items/monster breaks/etc)
- [TanukiSharp](https://github.com/TanukiSharp/) - For creating a computer usable collection of sharpness data and allowing others to use it. His original project is [here](https://github.com/TanukiSharp/MHWSharpnessExtractor)
- DiscreetMath - For streaming the game to me as I copied data down, while I waited for the PC release.

Additional help with verifying data was done by nikibobi and Jayson.
