#!/bin/bash
#SBATCH --cpus-per-task=
#SBATCH --partition=
#SBATCH --ntasks=5
#SBATCH --mem=0               # memory per node
#SBATCH --job-name=phase_f

file_path=`sed -n '1p' $3/$4/logs.txt`
protein=`sed -n '2p' $3/$4/logs.txt`

grid_file=`sed -n '3p' $3/$4/logs.txt`
morgan_directory=`sed -n '4p' $3/$4/logs.txt`
smile_directory=`sed -n '5p' $3/$4/logs.txt`
sdf_directory=`sed -n '6p' $3/$4/logs.txt`

local_path=/groups/cherkasvgrp/share/progressive_docking/pd_python

t_cpu=$2

mkdir $file_path/$protein/after_iteration
python jobid_writer.py -protein $protein -file_path $file_path -n_it \-1 -jid phase_f -jn phase_f.sh

source tensorflow_gpu/bin/activate

python final_step.py -pt $protein -fp $file_path -it $1 -t_pos $t_cpu

cd $file_path/$protein/after_iteration/to_dock

ct=0
for f in *.txt
do
	((++ct))
	tmp="$(cut -d'_' -f3 <<<"$f")"
	tmp="$(cut -d'.' -f1 <<<"$tmp")"
	(srun -n 1 -N 1 --jobid=$SLURM_JOBID --job-name=$SLURM_JOB_NAME python $local_path/Extracting_smiles.py -pt $protein -fp $file_path -it $1 -fn $tmp -smd $smile_directory -sd $sdf_directory -t_pos $t_cpu -if True)&
	if (($ct % 1 ==0));then wait;fi
done
wait

mkdir smile_ph

cd smile

for f in *.smi
do
   ($openeye fixpka -in $f -out ../smile_ph/$f)&
done
wait

cd ..

mkdir sdf
ct=0
for f in smile_ph/*
do
	((++ct))
	tmp="$(cut -d'/' -f2 <<<"$f")"
	tmp="$(cut -d'_' -f3 <<<"$tmp")"
	(srun -n 1 -N 1 --jobid=$SLURM_JOBID --job-name=$SLURM_JOB_NAME  $openeye oeomega classic -in $f -out sdf/to_dock_$tmp.sdf -maxconfs 1 -strictstereo false -mpi_np $t_cpu -log to_dock_$tmp.log -prefix to_dock_$tmp)&
	if (($ct % 5 ==0));then wait;fi
done
wait

cd $local_path
python input_glide.py -protein $protein -file_path $file_path -gf $grid_file -n_it \-1

nj=$(($5/ct))

cd $file_path/$protein/after_iteration/to_dock/docked
for f in *.in
do
	$SCHRODINGER/glide -HOST slurm-compute -NJOBS $nj -OVERWRITE -JOBNAME phase_f_${f%.*} $f
done
python $local_path/phase_changer.py -pf final_phase.sh -itr $file_path/$protein/after_iteration
