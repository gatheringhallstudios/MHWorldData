# MHWorldData
A project used to generate a SQLite database file from Monster Hunter World data.

## How to build
Make sure Python 3.6 is installed on your system, as well as SQLAlchemy. Afterwards, run build.py.

## Data Structure
Each subsystem (like Monster, or Armor) is stored in its own subdirectory. There are 3 kinds of data files:
- ***type*_names.json**: A names registry containing the names of different objects of that type for each supported language.
- ***type*_data.json**: A data registry indexed by the english name (name_en) of that object. These are pulled to populate table data during the build process.
- ***type*\_*value*/*type*\_*value*\_*lang*.json**: An example translation file contained in a translation directory.
Lang is a translation code like en or jp. For an example, look up the monster descriptions.

## How to contribute
To contribute, create a pull request adding the data or translation you wish to add. 
If the translation is for a language that is not supported, 
feel free to create an issue and I will populate the *names* data files with dummy data.

## License
The build code is licensed under the [MIT License](http://opensource.org/licenses/mit-license.php). The data itself is unlicensed data pertaining to Monster Hunter World, which is owned by Capcom.
