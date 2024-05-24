#!/bin/bash

# Example to run:
# . splitter.sh <file_to_be_splitted> <output_folder> <lines_per_file>

# Description:
# splitt a MINES_file and add the header for MINES

#SBATCH --partition=pibu_el8
#SBATCH --mem=250G
#SBATCH --time=3-1:00:00
#SBATCH --job-name="all MINEs"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/output_%j.out
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/error_%j.err



FILE=$1
OUTPUT=$2
LINES_PER_FILE=$3

mkdir ${OUTPUT}
cd ${OUTPUT}

# get the filename without suffix (generally it is *.csv)
FILENAME=$(basename ${FILE} .csv)

# split the dataset to let pickaxe run in parallel
split -d --additional-suffix=".csv" -l ${LINES_PER_FILE} ../${FILE} ${FILENAME}_split_

# add to each file a header for SMILE
for file in $(ls -1);
do
    # get 1st line
    inline=$(head -n 1 ${file}) 
    result=$(echo "$inline" |grep -c "id,smiles") # count

    if [ $result -lt 1 ]; then
        sed -i 1i"id,smiles" ${file}
    fi
done

cd ..