#!/bin/bash

#SBATCH --cpus-per-task=10
#SBATCH --partition=pibu_el8
#SBATCH --mem=250G
#SBATCH --time=1-1:00:00
#SBATCH --job-name="all MINEs"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/output_%j_%A_%a.out
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/error_%j_%A_%a.err
##SBATCH --array=0-4



# run generalized rulset
cd /home/pamrein/2024_masterthesis/MINE-Database

# split the dataset to let pickaxe run in parallel (only do ones!)
# split -l 50000 ./example_data/230106_frozen_metadata_for_MINES.csv 230106_frozen_metadata_for_MINES_split_

FILES=($(ls -1 ./example_data/230106_frozen_metadata_for_MINES_split_a*))
FILENAME=$(basename ${FILES[$SLURM_ARRAY_TASK_ID]})

fraction=1


file_name_compound="/compounds_"${fraction}"_generalized"${FILENAME}
file_name_reaction="/reactions_"${fraction}"_generalized"${FILENAME}
echo "$fraction | $file_name_compound | $file_name_reaction | ${FILES[$SLURM_ARRAY_TASK_ID]}"
poetry run python pickaxe_run_template.py generalized $fraction $file_name_compound $file_name_reaction ${FILES[$SLURM_ARRAY_TASK_ID]}
