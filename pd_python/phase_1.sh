#!/bin/bash

file_path=`sed -n '1p' $3`
protein=`sed -n '2p' $3`
n_mol=`sed -n '8p' $3`

pr_it=$(($1-1)) 

t_cpu=$2

#if [ $t_cpu == 64 ];then t_cpu=48;fi

echo $t_cpu

morgan_directory=`sed -n '4p' $3`
smile_directory=`sed -n '5p' $3`
sdf_directory=`sed -n '6p' $3`

if [ $1 == 1 ];then pred_directory=$morgan_directory;else pred_directory=$file_path/$protein/iteration_$pr_it/morgan_1024_predictions;fi

source $4/bin/activate
python molecular_file_count_updated.py -pt $protein -it $1 -cdd $pred_directory -t_pos $t_cpu -t_samp $n_mol
python sampling.py -pt $protein -fp $file_path -it $1 -dd $pred_directory -t_pos $t_cpu
python sanity_check.py -pt $protein -fp $file_path -it $1
python Extracting_morgan.py -pt $protein -fp $file_path -it $1 -md $morgan_directory -t_pos $t_cpu
python Extracting_smiles.py -pt $protein -fp $file_path -it $1 -fn 0 -smd $smile_directory -sd $sdf_directory -t_pos $t_cpu -if False
