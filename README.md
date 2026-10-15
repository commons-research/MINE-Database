# MINE Databases
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Documentation](https://readthedocs.org/projects/mine-database/badge)

The MINE Database contains code for generating (through Pickaxe) and storing and retrieving compounds from a database.
Pickaxe applies reaction rules, representing reaction transformation patterns, to a list of user-specified compounds in order to predict reactions.  

## Documentation
For general information on MINE Databases, please consult [JJeffryes et al. 2015.](http://jcheminf.springeropen.com/articles/10.1186/s13321-015-0087-1).

Documentation is hosted at https://mine-database.readthedocs.io/en/latest/. It gives more detailed descriptions and example uses of the software.

## Installation (current)

You need the `uv` package manager. If you don't have it, install it with the following command:
```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Also be sure to install MongoDB (https://docs.mongodb.com/manual/installation/) if you are using the `write_db = True` option in Pickaxe.
Installation information on Ubuntu system https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/

## Running Pickaxe
### Example Running Pickaxe through the CLI

Using MetaCyc rules and coreactants.

```bash
uv run mine_database/pickaxe_commons.py -C ./mine_database/data/metacyc_rules/metacyc_coreactants.tsv -r ./mine_database/data/metacyc_rules/metacyc_generalized_rules.tsv  -g 1 -c ./example_data/lotus_10.csv -o ./data/
```

Using original rules and coreactants (Enzymatic)

```bash
uv run mine_database/pickaxe_commons.py \
    --coreactant_list ./mine_database/data/original_rules/EnzymaticCoreactants.tsv \
    --rule_list ./mine_database/data/original_rules/EnzymaticReactionRules.tsv \
    --generations 1 \
    --compound_file ./example_data/Solanum_1000.csv \
    --output_dir ./data/ \
    --processes 8 \
    --explicit_h \
    --database testing-mine
```

or 
```bash
uv run mine_database/pickaxe_commons.py -C ./mine_database/data/original_rules/EnzymaticCoreactants.tsv -r ./mine_database/data/original_rules/EnzymaticReactionRules.tsv  -g 1 -c ./example_data/lotus_1000.csv -o ./data/ -m 60
```

Complete command (writing to database):

```bash
uv run mine_database/pickaxe_commons.py --coreactant_list ./mine_database/data/original_rules/EnzymaticCoreactants.tsv --rule_list ./mine_database/data/original_rules/EnzymaticReactionRules.tsv --generations 1 --compound_file ./data/230106_lotus_inchikey_smiles.csv --output_dir ./data/ --processes 20  --explicit_h --database lotus_expanded --write_core
```

Command without writing to database:

```bash
uv run mine_database/pickaxe_commons.py --coreactant_list ./mine_database/data/original_rules/EnzymaticCoreactants.tsv --rule_list ./mine_database/data/original_rules/EnzymaticReactionRules.tsv --generations 1 --compound_file ./example_data/lotus_10.csv --output_dir ./data/ --processes 60 --verbose --explicit_h
```


Command with generalized rules and full LOTUS dataset without writing to database:

```bash
uv run mine_database/pickaxe_commons.py --coreactant_list ./mine_database/data/metacyc_rules/metacyc_coreactants.tsv --rule_list ./mine_database/data/metacyc_rules/metacyc_generalized_rules.tsv --generations 1 --compound_file ./data/LOTUS_inputfiles/230106_frozen_metadata_inchy_smiles.csv --output_dir ./data/ --processes 60 --verbose --explicit_h
```

Command loading target compounds and pruning the network to reactions that lead to them (`--target_file` needs an `id` column and a SMILES/InChI column; `--prune_to_targets` and `--react_targets` require `--target_file`). By default a generated compound that matches a target is not reacted further; add `--react_targets` to keep expanding it:

```bash
uv run mine_database/pickaxe_commons.py \
    --coreactant_list ./tests/data/test_coreactants.tsv \
    --rule_list ./tests/data/test_single_reaction_rule.tsv \
    --generations 2 \
    --smiles 'Cc1cc2c(cc1C)N(CC(O)C(O)C(O)COP(=O)(O)OP(=O)(O)OCC1OC(n3cnc4c(N)ncnc43)C(O)C1O)c1nc(O)nc(O)c1N2' \
    --target_file ./tests/data/test_targets.csv \
    --prune_to_targets \
    --output_dir ./data/ \
    --explicit_h
```

`--rule_list` can be repeated to load several rule files together. `mine_database/data/metacyc_rules/metacyc_custom_rules.tsv` holds hand-written rules that are not in the published generalized set: chalcone synthase (`rule_CHS`: acyl-CoA + 3 malonyl-CoA → chalcone + 4 CoA + 3 CO2) and flavonol synthase (`rule_FLS`: dihydroflavonol + 2-oxoglutarate + O2 → flavonol + succinate + CO2 + H2O). They need `metacyc_coreactants.tsv` (which defines `MALONYL-COA` and `SUCCINATE`) and run without `--explicit_h`:

```bash
uv run mine_database/pickaxe_commons.py \
    --coreactant_list ./mine_database/data/metacyc_rules/metacyc_coreactants.tsv \
    --rule_list ./mine_database/data/metacyc_rules/metacyc_generalized_rules.tsv \
    --rule_list ./mine_database/data/metacyc_rules/metacyc_custom_rules.tsv \
    --generations 1 \
    --compound_file ./example_data/start_building_blocks.tsv \
    --output_dir ./data/
```

### Filtering and pruning between generations

Filters run on every generation before it is expanded; compounds they reject are not expanded and are removed from the network when nothing else depends on them. `--prune_between_gens` additionally prunes the network after filtering to what leads to compounds that are still expanded (and targets).

| Option | Filter | Notes |
|---|---|---|
| `--similarity_cutoff 0.3` or `0,0.26,0.29` | Tanimoto (RDKit fingerprint) to the targets | One value, or one per generation (last value reused). Needs `--target_file`. |
| `--similarity_sample N` | Keep N compounds per generation, sampled weighted by similarity | Runs after all cutoff filters and samples only what they kept. Compounds with similarity ≤ 0.15 are never sampled. Needs `--target_file`. |
| `--mcs_cutoff 0.5` | Maximum common substructure with the targets (fraction of atoms + bonds) | One value or one per generation; slow on large molecules. Needs `--target_file`. |
| `--min_mw`, `--max_mw` | Molecular weight range | |
| `--atomic_composition 'C:5-30,N:0-0'` | Atom-count ranges | Empty bound is open (`C:5-`). |

Generation 0 (the starting compounds) is filtered too, so give per-generation cutoffs starting at `0` if early intermediates are dissimilar to the target. Example (naringenin chalcone → quercetin):

```bash
uv run mine_database/pickaxe_commons.py \
    --coreactant_list ./mine_database/data/metacyc_rules/metacyc_coreactants.tsv \
    --rule_list ./mine_database/data/metacyc_rules/metacyc_generalized_rules.tsv \
    --rule_list ./mine_database/data/metacyc_rules/metacyc_custom_rules.tsv \
    --smiles 'Oc1ccc(/C=C/C(=O)c2c(O)cc(O)cc2O)cc1' \
    --generations 4 --processes 8 \
    --target_file ./example_data/target_quercetin.tsv \
    --similarity_cutoff 0,0.26,0.29,0.30 --similarity_sample 200 \
    --prune_between_gens --prune_to_targets \
    --output_dir ./data/
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


