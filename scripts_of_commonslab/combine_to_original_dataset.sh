#!/bin/bash

# Example to run:
# . splits_to_one_file.sh <folder_with_compounds_and_reactions> <inputfile_full>
# . ./scripts_of_commonslab/splits_to_one_file.sh /data/output/metacyc_generalized/20240601_lotus_generalized_n45/ ./example_data/230106_frozen_metadata_for_MINES.csv

# Description:
# splitt a MINES_file and add the header for MINES

#SBATCH --partition=pibu_el8
#SBATCH --mem=900G
#SBATCH --time=3:00:00
#SBATCH --job-name="combine"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/output_%j.out
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/error_%j.err

poetry run python scripts_of_commonslab/combine_to_original_dataset.py 