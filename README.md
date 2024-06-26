# MINE Databases
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Documentation](https://readthedocs.org/projects/mine-database/badge)

The MINE Database contains code for generating (through Pickaxe) and storing and retrieving compounds from a database.
Pickaxe applies reaction rules, representing reaction transformation patterns, to a list of user-specified compounds in order to predict reactions.  

## Documentation
For general information on MINE Databases, please consult [JJeffryes et al. 2015.](http://jcheminf.springeropen.com/articles/10.1186/s13321-015-0087-1).

Documentation is hosted at https://mine-database.readthedocs.io/en/latest/. It gives more detailed descriptions and example uses of the software.

## Installation (legacy)
If a conda environment is desired to be used:

`conda create -n mine`

`conda activate mine`


Then, use pip (with or without conda) to install minedatabase:

`pip install minedatabase`

## Installation (current)

You need Poetry (https://python-poetry.org/)

`poetry install`

Also be sure to install MongoDB (https://docs.mongodb.com/manual/installation/) if you are using the `write_db = True` option in Pickaxe.
Installation information on Ubuntu system https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
 

## Running Pickaxe (legacy)
### Running Pickaxe through a python file (recommended)
An example file, [pickaxe_run_template.py](https://github.com/tyo-nu/MINE-Database/blob/master/pickaxe_run_template.py), provides a framework for running pickaxe through a python file. Feel free to download it and change it to your needs. The starting compounds, rules and cofactors, optional database information, and Pickaxe run options are specified. After running the results are stored in a specified database or written to .tsv files.

This is all explained in more detail in the [documentation](https://mine-database.readthedocs.io/en/develop/pickaxe_run.html).

### Pickaxe command-line usage (not recommended - see above section)
Pickaxe.py can be called independently to generate predictions with or 
without database storage. To list all options call `python -m minedatabase.pickaxe -h`. Note that due to relative imports, it needs to be run as a module (-m flag) from the MINE-Database directory. To predict metacyc reactions for one generation on compounds in the iML1515 model one would call 

`python pickaxe.py -C ./data/metacyc_rules/metacyc_generalized_rules.tsv -r ./data/metacyc_rules/metacyc_coreactants.tsv -g 1 -c ../example_data/iML1515_ecoli_GEM.csv`

## Running Pickaxe (current)
### Running Pickaxe through the CLI (recommended)

Activate the poetry shell:

`poetry shell`

Then, run the following command:

```python
python pickaxe_run_template.py
```

For now you will need to edit all your parameters directly inside the corresponding script.


We now try to clean the previous messy command.

`python pickaxe.py -C ./data/metacyc_rules/metacyc_generalized_rules.tsv -r ./data/metacyc_rules/metacyc_coreactants.tsv -g 1 -c ../example_data/iML1515_ecoli_GEM.csv`

Should be

```python
python mine_database/pickaxe.py -C ./mine_database/data/metacyc_rules/metacyc_coreactants.tsv -r ./mine_database/data/metacyc_rules/metacyc_generalized_rules.tsv  -g 1 -c ./example_data/iML1515_ecoli_GEM.csv -o ./data/
```

```python
python mine_database/pickaxe.py -C ./mine_database/data/metacyc_rules/metacyc_coreactants.tsv -r ./mine_database/data/metacyc_rules/metacyc_generalized_rules.tsv  -g 1 -c ./example_data/iML1515_ecoli_GEM.csv -o ./data/
```


### Accessing the mongodb database

To access the mongodb database, you can use the following command:

```bash
mongosh
```

Then, you can use the following commands to access the database:

```bash
use example_db
db.compounds.find()
```

Optionally the DB can be observed using MongoDB Compass. See https://www.mongodb.com/docs/compass/current/install/


