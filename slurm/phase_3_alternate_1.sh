#!/bin/bash
#SBATCH --cpus-per-task=19
#SBATCH --partition=normal,gpu
#SBATCH --ntasks=3
#SBATCH --mem=0               # memory per node
#SBATCH --job-name=phase_3_new


t_nod=$2


file_path=`sed -n '1p' $3/$4/logs.txt`
protein=`sed -n '2p' $3/$4/logs.txt`
grid_file=`sed -n '3p' $3/$4/logs.txt`

morgan_directory=`sed -n '4p' $3/$4/logs.txt`
smile_directory=`sed -n '5p' $3/$4/logs.txt`
sdf_directory=`sed -n '6p' $3/$4/logs.txt`

local_path=/groups/cherkasvgrp/share/progressive_docking/pd_python

#python jobid_writer.py -protein $protein -file_path $file_path -n_it $1 -jid phase_3_new -jn phase_3.sh

source tensorflow_gpu/bin/activate
cd $file_path/$protein/iteration_$1

cd $file_path/$protein/iteration_$1/docked

for f in *.oeb.gz
do
	temp=${f%.*}
	(srun -n 1 -N 1 --jobid=$SLURM_JOBID --job-name=phase_3_new.sh $openeye fred -receptor $grid_file -dbase $f -docked_molecule_file phase_3_${temp%.*}\_docked.sdf -hitlist_size 0 -mpi_np $t_nod -prefix ${temp%.*} 2> ${temp%.*}\_fred_stderr.txt)&
done
python $local_path/oed_check.py -fp $file_path/$protein/iteration_$1/docked -pf phase_3.sh -ttime 600
python $local_path/phase_changer.py -pf phase_3_alternate_1.sh -itr $file_path/$protein/iteration_$1
scancel $SLURM_JOBID
