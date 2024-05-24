#!/bin/bash

# Example to run:
# sbatch pickaxe_run_on_cluster_onebyone.sh example_data/230106_frozen_metadata_for_MINES_split_ae.csv generalized

# for multiple runs:
# for n in $(ls -1 <files_to_predict>); do sbatch pickaxe_run_on_cluster_onebyone.sh ${n} generalized; done

#SBATCH --cpus-per-task=10
#SBATCH --partition=pibu_el8
#SBATCH --mem=250G
#SBATCH --time=3-1:00:00
#SBATCH --job-name="all MINEs"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/output_%j.out
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/error_%j.err



# run generalized rulset
cd /home/pamrein/2024_masterthesis/MINE-Database


FILE=$1
FILTER=$2

FILENAME=$(basename ${FILE})

fraction=1


file_name_compound="/compounds_"${fraction}"_generalized_"${FILENAME}
file_name_reaction="/reactions_"${fraction}"_generalized_"${FILENAME}
echo "$fraction | $file_name_compound | $file_name_reaction | ${FILE}"
poetry run python pickaxe_run_template.py ${FILTER} $fraction $file_name_compound $file_name_reaction ${FILE}
