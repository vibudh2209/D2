#!/bin/bash
#SBATCH --cpus-per-task=64
#SBATCH --ntasks=3
#SBATCH --mem=0               # memory per node
#SBATCH --job-name=phase_3


t_nod=$2

if [ $t_nod == 64 ];then t_nod=48;fi

file_path=`sed -n '1p' $3/$4/logs.txt`
protein=`sed -n '2p' $3/$4/logs.txt`
grid_file=`sed -n '3p' $3/$4/logs.txt`

morgan_directory=`sed -n '4p' $3/$4/logs.txt`
smile_directory=`sed -n '5p' $3/$4/logs.txt`
sdf_directory=`sed -n '6p' $3/$4/logs.txt`

python jobid_writer.py -protein $protein -file_path $file_path -n_it $1 -jid phase_3 -jn phase_3.sh

local_path=/groups/cherkasvgrp/share/progressive_docking/pd_python

source tensorflow_gpu/bin/activate
cd $file_path/$protein/iteration_$1

mkdir $file_path/$protein/iteration_$1/docked

cd $file_path/$protein/iteration_$1/docked

for f in ../sdf/*.sdf
do
	tmp="$(cut -d'/' -f3 <<<"$f")"
	tmp="$(cut -d'_' -f1 <<<"$tmp")"
   (srun -n 1 -N 1 --jobid=$SLURM_JOBID --job-name=phase_3.sh  $openeye oeomega classic -in $f -out $tmp.oeb.gz -maxconfs 100 -rangeIncrement 5 -rmsrange "0.5,0.8" -strictstereo false -mpi_np $t_nod -log $tmp.log -prefix $tmp 2> $temp\_stderr.txt)&
done
python $local_path/oed_check.py -fp $file_path/$protein/iteration_$1/docked -pf phase_3.sh -ttime 30
scancel $SLURM_JOBID

