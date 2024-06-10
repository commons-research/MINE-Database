#!/bin/bash

# Example to run:
# . splits_to_one_file.sh <folder_with_compounds_and_reactions> <inputfile_full>
# . ../scripts_of_commonslab/splits_to_one_file.sh /data/output/metacyc_generalized/20240601_lotus_generalized_n45/ ./example_data/230106_frozen_metadata_for_MINES.csv

# Description:
# splitt a MINES_file and add the header for MINES

#SBATCH --partition=pibu_el8
#SBATCH --mem=250G
#SBATCH --time=1-1:00:00
#SBATCH --job-name="all MINEs"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/output_%j.out
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/error_%j.err

INPUT_FOLDER=$1
START_FILE=$2

START_FILE_PATH=$(pwd)/${START_FILE}
echo $START_FILE_PATH

cd ${INPUT_FOLDER}
mkdir -p results
FILE_REACTIONS=$(ls -1 reactions_*)


for FILE_REACTION in $FILE_REACTIONS;
do
    if [[ -f ${FILE_REACTION} ]]; 
    then 
        echo "File (reactions) exist: ${FILE_REACTION}"

        FILE_COMPOUND=$(echo $FILE_REACTION | sed 's/reactions/compounds/g')
        FILE_RESULT=$(echo $FILE_REACTION | sed 's/reactions/result/g')

        if [[ -f ${FILE_COMPOUND} ]]; 
        then 
            echo "File (compounds) exist: ${FILE_COMPOUND}"

            poetry run python /home/pamrein/2024_masterthesis/MINE-Database/scripts_of_commonslab/add_compounds_and_rules_to_dataframe.py -s ${START_FILE_PATH} -r ${FILE_REACTION} -c ${FILE_COMPOUND} -o ./results/${FILE_RESULT} -a "Reaction rules" -b "SMILES"

            echo "File wrote: ${FILE_RESULT}"
        fi
    fi
done