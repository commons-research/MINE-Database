#!/bin/bash

# Example to run:
# . splitter.sh <file_to_be_splitted> <output_folder> <lines_per_file>
# . ../scripts_of_commonslab/splitter.sh 230106_frozen_metadata_for_MINES.csv 230106_frozen_metadata_splitted_n100 2500

# Description:
# splitt a MINES_file and add the header for MINES
# lines of Lotus: 220834

#SBATCH --partition=pibu_el8
#SBATCH --mem=250G
#SBATCH --time=3-1:00:00
#SBATCH --job-name="all MINEs"
#SBATCH --mail-user=pascal.amrein@unifr.ch
#SBATCH --mail-type=begin,end,fail
#SBATCH --output=/home/pamrein/2024_masterthesis/MINE-Database/data/log/output_%j.out
#SBATCH --error=/home/pamrein/2024_masterthesis/MINE-Database/data/log/error_%j.err



FILE_TO_SPLIT=$(pwd $1)/$1
OUTPUT=$2
FILE_AMOUNT=$3

HOME_FOLDER=$(pwd)

# Check if n is not zero to avoid division by zero error
if [ "${FILE_AMOUNT}" -eq 0 ] 
then
    echo "Error: Division by zero is not allowed."
    exit 1
fi

# Calculate 220834 / n using bc
LINES_PER_FILE=$(echo "scale=2; 220834 / ${FILE_AMOUNT}" | bc | awk '{printf("%d\n", ($1 == int($1)) ? $1 : int($1)+1)}')

mkdir -p ${OUTPUT}
cd ${OUTPUT}

# get the filename without suffix (generally it is *.csv)
FILE_NAME=$(basename ${FILE_TO_SPLIT} .csv)

# split the dataset to let pickaxe run in parallel
split -d --additional-suffix=".csv" -l ${LINES_PER_FILE} ${FILE_TO_SPLIT} ${FILE_NAME}_split_

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

cd ${HOME_FOLDER}
