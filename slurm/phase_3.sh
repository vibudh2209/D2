#!/bin/bash
#SBATCH --job-name=phase_3
#SBATCH --cpus-per-task=1
#SBATCH --partition=normal

file_path=`sed -n '1p' $3/$4/logs.txt`
protein=`sed -n '2p' $3/$4/logs.txt`
grid_file=`sed -n '3p' $3/$4/logs.txt`

morgan_directory=`sed -n '4p' $3/$4/logs.txt`
smile_directory=`sed -n '5p' $3/$4/logs.txt`
sdf_directory=`sed -n '6p' $3/$4/logs.txt`

local_path=/groups/cherkasvgrp/share/progressive_docking/pd_python

python jobid_writer.py -protein $protein -file_path $file_path -n_it $1 -jid phase_3 -jn phase_3.sh

source tensorflow_gpu/bin/activate
python input_glide.py -protein $protein -file_path $file_path -gf $grid_file -n_it $1
cd $file_path/$protein/iteration_$1/docked
for f in *.in;do $SCHRODINGER/glide -HOST slurm-compute -NJOBS $2 -OVERWRITE -JOBNAME phase_3_${f%.*} $f;done
python $local_path/phase_changer.py -pf phase_3.sh -itr $file_path/$protein/iteration_$1
