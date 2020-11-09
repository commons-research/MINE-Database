from minedatabase.pickaxe import Pickaxe
import pymongo
import datetime
import time

###############################################################################
##### pickaxe_run.py
# This python script provides a skeleton to build Pickaxe runs around
# The general format of a script will be:
#   1. Connect to mongoDB (if desired)
#   2. Load reaction rules and cofactors
#   3. Load starting compounds
#   4. Load Tanimoto filtering options
#   5. Transform Compounds
#   6. Write results
###############################################################################

start = time.time()

###############################################################################
##### Database and output information
# The default mongo is localhost:27017
# Connecting remotely requires the location of the database 
# as well as username/password if security is being used. 
# Username/password are stored in credentials.csv
# in the following format: username

# Database to write results to
write_db = True
database_overwrite = True
database = "KEGG_200_int"
# Message to insert into metadata
message = "Text to describe reaction."

# mongo DB information
use_local = True
if use_local:
    mongo_uri = 'mongodb://localhost:27017'
else:
    # load file of form user,pass
    creds = open('credentials.csv').readline().split(',')
    creds = [cred.strip('\n') for cred in creds]
    # URI of remote mongo instance
    mongo_uri = f"mongodb://{creds[0]}:{creds[1]}@minedatabase.ci.northwestern.edu:27017/?authSource=admin"

# Write output .csv files locally
write_local = False
output_dir = '.'
###############################################################################

###############################################################################
##### Cofactors, rules and inputs
# Original rules derived from BNICE
# coreactant_list = './minedatabase/data/EnzymaticCoreactants.tsv'
# rule_list = './minedatabase/data/EnzymaticReactionRules.tsv'

# Rules from Joseph Ni
coreactant_list = './minedatabase/data/MetaCyc_Coreactants.tsv'
# rule_list = './minedatabase/data/intermediate_rules_uniprot.tsv'
rule_list = './minedatabase/data/metacyc_generalized_rules_500.tsv'

# Input compounds
input_cpds = 'kegg_200.csv'

# Partial operators
# Partial operators allow use of multiple compounds in an any;any expansion
partial_rules = False
mapped_rxns = 'minedatabase/data/metacyc_mapped.tsv'
###############################################################################

###############################################################################
##### Core Pickaxe Run Options
generations = 1
num_workers = 12     # Number of processes for parallelization
verbose = False     # Display RDKit warnings and errors
explicit_h = False
kekulize = True
neutralise = True
image_dir = None
quiet = True
indexing = False
###############################################################################

###############################################################################
##### Tanimoto Filtering options
target_cpds = 'APAH.csv'
tani_filter = False
# Prune results to only give expanded compounds/rxns
tani_prune = False
# Tanimito filter threshold. Can be single number of a list
# of length generations. 
crit_tani = 0.2
# crit_tani = [0, 0.5] # expands first with no filter then a 0.5 filter

# TODO: fingerprint options
###############################################################################

###############################################################################
##### Running pickaxe
# Initialize the Pickaxe class 
if write_db == False:
    database = None

pk = Pickaxe(coreactant_list=coreactant_list,
            rule_list=rule_list,
            errors=verbose, explicit_h=explicit_h,
            kekulize=kekulize, neutralise=neutralise,
            image_dir=image_dir, database=database,
            database_overwrite=database_overwrite,
            mongo_uri=mongo_uri, quiet=quiet)

# Load compounds
pk.load_compound_set(compound_file=input_cpds)

# Load partial operators
if partial_rules:
    pk.load_partial_operators(mapped_reactions)

# Initialize tanimoto filter
if tani_filter:
    pk.load_target_set(target_compound_file=target_cpds, crit_tani=crit_tani)

# Transform compounds
pk.transform_all(num_workers, generations)

# Remove cofactor redundancies 
pk.remove_cofactor_redundancy()

# Write results to database
if write_db:
    if tani_filter and tani_prune:
        pk.prune_network_to_targets()
    pk.save_to_mine(num_workers=num_workers, indexing=indexing)
    client = pymongo.MongoClient(mongo_uri)
    db = client[database]
    db.meta_data.insert_one({"Timestamp": datetime.datetime.now(),
                                    "Generations": f"{generations}",
                                    "Operator file": f"{rule_list}",
                                    "Coreactant file": f"{coreactant_list}",
                                    "Input compound file": f"{input_cpds}",
                                    "Tanimoto filter": f"{crit_tani}"}
                                    )
    db.meta_data.insert_one({"Timestamp": datetime.datetime.now(),
                            "Message": message})

if write_local:
    pk.assign_ids()
    pk.write_compound_output_file(output_dir + '/compounds.tsv')
    pk.write_reaction_output_file(output_dir + '/reactions.tsv')

print(f'----------------------------------------')
print(f'Overall run took {round(time.time() - start, 2)} seconds.')
print(f'----------------------------------------')