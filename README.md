[![Build Status](https://travis-ci.org/CarlosFdez/MHWorldData.svg?branch=master)](https://travis-ci.org/CarlosFdez/MHWorldData)

# MHWorldData
A project used to generate a SQLite database file from Monster Hunter World data.

## How to build
Make sure Python 3.6 or greater is installed on your system, and pipenv is installed (`pip install pipenv`). Afterwards, you can install all dependencies by running `pipenv install`.

Afterwards, run `pipenv run python build.py` in a terminal to generate an `mhw.sql` file. Alternatively, run `pipenv shell` and then run `python build.py`.

You can run the tests by executing `pipenv run pytest tests`.

## Data Structure
The data files in /data are used to build the final SQL file. If you want to contribute data, this is where you'd do it.

Each subsystem in (like Monster, or Armor) is stored in its own subdirectory in /source_data. There are two kinds of data files:
- ***type*_base.json**: A names registry containing the names of different objects of that type for each supported language, as well as any additional base data.
- ***type*_data.json**: A data registry key'd by the english name of that object. These are pulled to populate table data during the build process.

## How to contribute
To contribute, create a pull request adding the data or translation you wish to add. If the translation is for a language that is not supported, feel free to create a Github Issue and I will populate the *names* data files with dummy data.

Good visual git clients include `Git Kraken` and `SourceTree`. If you are unable to work with JSON or Git, but have data corrections or translations to contribute, feel free to create a Github Issue and I'll try my best to accomodate you.

## Data Sources
The data collected by this project is an accumulation of various sources, including the game itself, [LartTyler's API](https://github.com/LartTyler/MHWDB-Docs/wiki), Kiranico, and multiple Japanese sites. Only data that came from the game itself (includes reverse engineering) and official booklets are collected. Handwritten tips and tricks do not come from the game and are currently not accepted in the repository to avoid copyright violations.

If any data added here is your copyright, create an issue and I'll make sure to remove it.

## License
The build code is licensed under the [MIT License](http://opensource.org/licenses/mit-license.php). The data itself pertains to Monster Hunter World, which is owned by Capcom.
