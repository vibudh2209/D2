#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --mem=0               # memory per node
#SBATCH --job-name=phase_5

file_path=`sed -n '1p' $2/$3/logs.txt`
protein=`sed -n '2p' $2/$3/logs.txt`

morgan_directory=`sed -n '4p' $2/$3/logs.txt`
smile_directory=`sed -n '5p' $2/$3/logs.txt`
sdf_directory=`sed -n '6p' $2/$3/logs.txt`

local_path=/groups/cherkasvgrp/share/progressive_docking/pd_python

python jobid_writer.py -protein $protein -file_path $file_path -n_it $1 -jid $SLURM_JOB_NAME -jn $SLURM_JOB_NAME.sh

source tensorflow_gpu/bin/activate

python hyperparameter_result_evaluation.py -n_it $1 -protein $protein -file_path $file_path -mdd $morgan_directory

python simple_job_predictions.py -protein $protein -file_path $file_path -n_it $1 -mdd $morgan_directory

cd $file_path/$protein/iteration_$1/simple_job_predictions

for f in *;do sbatch $f;done
python $local_path/phase_changer.py -pf phase_5.sh -itr $file_path/$protein/iteration_$1
