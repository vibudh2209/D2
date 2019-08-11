#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --mem=0               # memory per node
#SBATCH --job-name=morgan_fing


conda init bash
conda activate my-rdkit-env

python Morgan_fing.py -sfp $1 -fp $2 -fn $3  -tp $4


