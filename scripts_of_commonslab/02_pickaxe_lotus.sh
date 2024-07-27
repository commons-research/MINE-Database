#!/bin/bash

# Example to run:
# sbatch pickaxe_lotus.sh example_data/230106_frozen_metadata_for_MINES_split_ae.csv generalized data/output/my_folder_to_save

# for multiple runs:
# for file in $(ls -1 <files_to_predict>); do sbatch pickaxe_lotus.sh ${file} generalized <folderpath_to_save>; done

# Description:
# explore new molecules with help of the given ruleset and input_file (SMILES).
# 1000 SMILES ~1h


#SBATCH --cpus-per-task=20
#SBATCH --partition=pibu_el8
#SBATCH --mem=500G
#SBATCH --time=4-1:00:00
#SBATCH --job-name="all MINEs"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/expand_%j.out
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/expand_%j.err



# run generalized rulset
cd /home/pamrein/2024_masterthesis/MINE-Database

# Inputfiles can be choosed with wildcards (exp.: folder/*)
FILE=$(pwd $1)/$1


# generalized or intermediate
FILTER=$2

# location to save results
OUTPUT_FOLDER=$3
mkdir -p ${OUTPUT_FOLDER}

# Remove any known extension
FILENAME="${FILE%.*}"

fraction=1

file_name_compound="/compounds_"${fraction}"_generalized_"${FILENAME}
file_name_reaction="/reactions_"${fraction}"_generalized_"${FILENAME}
echo "$fraction | $file_name_compound | $file_name_reaction | ${FILE}.csv"
poetry run python pickaxe_run_template.py ${FILTER} $fraction $file_name_compound $file_name_reaction ${FILE} ${OUTPUT_FOLDER}
