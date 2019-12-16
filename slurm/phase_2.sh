#!/bin/bash
#SBATCH --cpus-per-task=19
#SBATCH --partition=normal,gpu
#SBATCH --ntasks=3
#SBATCH --mem=0               # memory per node
#SBATCH --job-name=phase_2

t_nod=$2

file_path=`sed -n '1p' $3/$4/logs.txt`
protein=`sed -n '2p' $3/$4/logs.txt`

morgan_directory=`sed -n '4p' $3/$4/logs.txt`
smile_directory=`sed -n '5p' $3/$4/logs.txt`
sdf_directory=`sed -n '6p' $3/$4/logs.txt`

python jobid_writer.py -protein $protein -file_path $file_path -n_it $1 -jid $SLURM_JOB_NAME -jn $SLURM_JOB_NAME.sh

local_path=/groups/cherkasvgrp/share/progressive_docking/pd_python
source tensorflow_gpu/bin/activate
cd $file_path/$protein/iteration_$1
mkdir smile_ph
cd smile
ct=0
for f in *.smi
do
   ($openeye fixpka -in $f -out ../smile_ph/$f)&
done
wait
cd ..
mkdir sdf
for f in smile_ph/*
do
   tmp="$(cut -d'/' -f2 <<<"$f")"
   tmp="$(cut -d'_' -f1 <<<"$tmp")"
   if [ $tmp = train ];then name=training;node=gn02;fi
   if [ $tmp = valid ];then name=validation;node=gn03;fi
   if [ $tmp = test ];then name=testing;node=gn04;fi
   (srun -n 1 -N 1 --jobid=$SLURM_JOBID --job-name=$SLURM_JOB_NAME  $openeye oeomega classic -in $f -out sdf/$name\_sdf.sdf -maxconfs 1 -strictstereo false -mpi_np $t_nod -log $name.log -prefix $name)&
done
python $local_path/oed_check.py -fp $file_path/$protein/iteration_$1 -pf $SLURM_JOB_NAME.sh -ttime 30
python $local_path/phase_changer.py -pf phase_2.sh -itr $file_path/$protein/iteration_$1
scancel $SLURM_JOBID
