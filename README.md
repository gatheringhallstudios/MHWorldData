[![Build Status](https://travis-ci.org/CarlosFdez/MHWorldData.svg?branch=master)](https://travis-ci.org/CarlosFdez/MHWorldData)

# MHWorldData
A project used to generate a SQLite database file from Monster Hunter World data.

## Purpose and goals
This project exists as a free and open collection of Monster Hunter World data. I feel that by opening up this repository, more people would be able to create cool things. While the data has to be manually built right now, once we approach a stable version they will be available without the need to build.

We use the data generated here for the [MHWorldDatabase](https://github.com/gatheringhallstudios/MHWorldDatabase) Android app, which is also open source. 

## Data Structure
The data files in /source_data are used to build the final SQL file. If you want to contribute data, this is where you'd do it. The project is in the middle of a conversion from JSON to CSV, so some files are still JSON.

To edit the CSV files, I suggest using an office program like Excel or Libreoffice. Make sure to use UTF8 text encoding and comma separators. You can also import it to google drive.

Each subsystem in (like Monster, or Armor) is stored in its own subdirectory in /source_data. There are two kinds of data files:
- ***type*_base.csv**: A names and basic data registry containing the names of different objects of that type for each supported language, as well as any additional base data.
- ***type*_data.csv**: A data registry key'd by the english name of that object. These are pulled to populate table data during the build process.

## How to contribute
To contribute, create a pull request adding the data or translation you wish to add. If the translation is for a language that is not supported, feel free to create a Github Issue and I will populate the *names* data files with dummy data.

Good visual git clients include `Git Kraken` and `SourceTree`. If you are unable to work with JSON or Git, but have data corrections or translations to contribute, feel free to create a Github Issue and send me the new file or link to a google drive spreadsheet.

## How to build
Make sure Python 3.6 or greater is installed on your system, and pipenv is installed (`pip install pipenv`). Afterwards, you can install all dependencies by running `pipenv install`.

Afterwards, run `pipenv run python build.py` in a terminal to generate an `mhw.sql` file. Alternatively, run `pipenv shell` and then run `python build.py`.

You can run the tests by executing `pipenv run pytest tests`.

## Data Sources
The data collected by this project is an accumulation of various sources, including the game itself, official guidebooks, and other collections like [LartTyler's API](https://github.com/LartTyler/MHWDB-Docs/wiki), Kiranico (raw data only), and multiple Japanese wikis. Only data that came from the game itself and official booklets are collected. Handwritten tips and tricks do not come from the game and are currently not accepted in the repository to avoid copyright violations.

If any data added here is your copyright, create an issue and I'll make sure to remove it.

## License
The build code is licensed under the [MIT License](http://opensource.org/licenses/mit-license.php). The data itself pertains to Monster Hunter World, which is owned by Capcom. You are free to use it, but I'd really appreciate it if you let me know what you're working on, and would be even more stoked if you let other people know where you got the data from in a note somewhere (although its not required).

## Special Credits
- DiscreetMath - For streaming the game to me as I copied data down, while I lamented my wait for the PC release.
- [Vocalonation](https://github.com/ahctang) For helping me with translating and crossvalidating data.
