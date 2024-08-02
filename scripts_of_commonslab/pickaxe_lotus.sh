
Copy code
#!/bin/bash

# Example to run:
# sbatch pickaxe_lotus.sh example_data/230106_frozen_metadata_for_MINES_split_ae.csv data/output/my_folder_to_save

# for multiple runs:
# for file in $(ls -1 <files_to_predict>); do sbatch pickaxe_lotus.sh ${file} <folderpath_to_save> <database_name>; done

# Description:
# explore new molecules with help of the given ruleset and input_file (SMILES).
# 1000 SMILES ~1h

#SBATCH --cpus-per-task=60
#SBATCH --partition=pibu_el8
#SBATCH --mem=500G
#SBATCH --time=4-1:00:00
#SBATCH --job-name="all MINEs"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/expand_%j.out
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/expand_%j.err

# Run generalized ruleset
cd /home/pamrein/2024_masterthesis/MINE-Database

# Input files can be chosen with wildcards (e.g., folder/*)
FILE=$(pwd $1)/$1

# Location to save results
OUTPUT_FOLDER=$2
mkdir -p ${OUTPUT_FOLDER}

# Check if a database is provided as the 3rd argument
DATABASE=$3

if [ -z "$DATABASE" ]; then
    # No database provided, run the original command
    poetry run python mine_database/pickaxe_commons.py \
    --coreactant_list ./mine_database/data/metacyc_rules/metacyc_coreactants.tsv \
    --rule_list ./mine_database/data/metacyc_rules/metacyc_generalized_rules.tsv \
    --generations 1 \
    --compound_file ${FILE} \
    --output_dir ${OUTPUT_FOLDER} \
    --processes 60 \
    --verbose \
    --explicit_h
else
    # Database provided, run the alternative command
    poetry run python mine_database/pickaxe_commons.py \
    --coreactant_list ./mine_database/data/original_rules/EnzymaticCoreactants.tsv \
    --rule_list ./mine_database/data/original_rules/EnzymaticReactionRules.tsv \
    --generations 1 \
    --compound_file ${FILE} \
    --output_dir ${OUTPUT_FOLDER} \
    --processes 60 \
    --verbose \
    --explicit_h \
    --database ${DATABASE}
fi

# Rename output files with current date and time
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
COMPOUNDS_FILE="${OUTPUT_FOLDER}/compounds.tsv"
REACTIONS_FILE="${OUTPUT_FOLDER}/reactions.tsv"
NEW_COMPOUNDS_FILE="${OUTPUT_FOLDER}/${TIMESTAMP}_compounds.tsv"
NEW_REACTIONS_FILE="${OUTPUT_FOLDER}/${TIMESTAMP}_reactions.tsv"

# Function to rename files
rename_file() {
    local old_file=$1
    local new_file=$2
    if [ -e "$new_file" ]; then
        new_file="${new_file%.tsv}_new.tsv"
    fi
    mv "$old_file" "$new_file"
}

# Rename if the files exist
if [ -e "$COMPOUNDS_FILE" ]; then
    rename_file "$COMPOUNDS_FILE" "$NEW_COMPOUNDS_FILE"
fi

if [ -e "$REACTIONS_FILE" ]; then
    rename_file "$REACTIONS_FILE" "$NEW_REACTIONS_FILE"
fi
