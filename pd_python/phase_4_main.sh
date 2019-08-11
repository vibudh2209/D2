#!/bin/bash
#SBATCH --cpus-per-task=
#SBATCH --ntasks=1
#SBATCH --mem=0               # memory per node
#SBATCH --job-name=phase_4
#SBATCH --partition=gpu

file_path=`sed -n '1p' $3/$4/logs.txt`
protein=`sed -n '2p' $3/$4/logs.txt`

morgan_directory=`sed -n '4p' $3/$4/logs.txt`
smile_directory=`sed -n '5p' $3/$4/logs.txt`
sdf_directory=`sed -n '6p' $3/$4/logs.txt`
nhp=`sed -n '8p' $3/$4/logs.txt`
sof=`sed -n '7p' $3/$4/logs.txt`

local_path=/groups/cherkasvgrp/share/progressive_docking/pd_python

python jobid_writer.py -protein $protein -file_path $file_path -n_it $1 -jid $SLURM_JOB_NAME -jn $SLURM_JOB_NAME.sh

source tensorflow_gpu/bin/activate

t_pos=$2

python Extract_labels.py -if False -n_it $1 -protein $protein -file_path $file_path -t_pos $t_pos -sof $sof
python simple_job_models.py -n_it $1 -mdd $morgan_directory -time 00-04:00 -protein $protein -file_path $file_path -nhp $nhp

cd $file_path/$protein/iteration_$1/simple_job

for f in *;do sbatch $f;done
python $local_path/phase_changer.py -pf phase_4.sh -itr $file_path/$protein/iteration_$1
