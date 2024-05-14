#!/bin/bash

#SBATCH --cpus-per-task=10
#SBATCH --partition=pibu_el8
#SBATCH --mem-per-cpu=10G
#SBATCH --time=25:00:00
#SBATCH --job-name="performancetest MINEs"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/output_%j.o
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/error_%j.e



# run generalized rulset
cd /home/pamrein/2024_masterthesis/MINE-Database

for fraction in $(seq 0.1 0.1 1);
do
    file_name_compound="/compounds_"$fraction"_generalized"
    file_name_reaction="/reactions_"$fraction"_generalized"
    echo "$fraction | $file_name_compound | $file_name_reaction"
    poetry run python pickaxe_run_template.py generalized $fraction $file_name_compound $file_name_reaction
done

# run intermediate rulset
for fraction in $(seq 0.1 0.1 1);
do
    file_name_compound="/compounds_"$fraction"_intermediate"
    file_name_reaction="/reactions_"$fraction"_intermediate"
    echo "$fraction | $file_name_compound | $file_name_reaction"
    poetry run python pickaxe_run_template.py intermediate $fraction $file_name_compound $file_name_reaction
done
