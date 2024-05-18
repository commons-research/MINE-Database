#!/bin/bash

#SBATCH --cpus-per-task=10
#SBATCH --partition=pibu_el8
#SBATCH --mem-per-cpu=10G
#SBATCH --time=3-2:00:00
#SBATCH --job-name="1000 MINEs"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/output_%j.o
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/error_%j.e



# run generalized rulset
cd /home/pamrein/2024_masterthesis/MINE-Database

fraction=1

file_name_compound="/compounds_"$fraction"_generalized"
file_name_reaction="/reactions_"$fraction"_generalized"
echo "$fraction | $file_name_compound | $file_name_reaction"
poetry run python pickaxe_run_template.py generalized $fraction $file_name_compound $file_name_reaction
