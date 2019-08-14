#!/bin/bash

file_path=`sed -n '1p' $3`
protein=`sed -n '2p' $3`

grid_file=`sed -n '3p' $3`
morgan_directory=`sed -n '4p' $3`
smile_directory=`sed -n '5p' $3`
sdf_directory=`sed -n '6p' $3`

t_cpu=$2

mkdir $file_path/$protein/after_iteration

source $4/bin/activate

python final_step.py -pt $protein -fp $file_path -it $1 -t_pos $t_cpu

cd $file_path/$protein/after_iteration/to_dock

for f in *.txt
do
	tmp="$(cut -d'_' -f3 <<<"$f")"
	tmp="$(cut -d'.' -f1 <<<"$tmp")"
	python $local_path/Extracting_smiles.py -pt $protein -fp $file_path -it $1 -fn $tmp -smd $smile_directory -sd $sdf_directory -t_pos $t_cpu -if True
done


