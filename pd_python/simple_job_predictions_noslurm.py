import os
import glob
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-protein','--protein',required=True)
parser.add_argument('-file_path','--file_path',required=True)
parser.add_argument('-n_it','--n_it',required=True)
parser.add_argument('-mdd','--morgan_directory',required=True)
parser.add_argument('-pdfp','--pd_folder_path',required=True)
parser.add_argument('-tfp','--tf_venv_path',required=True)

io_args = parser.parse_args()

protein = io_args.protein
file_path = io_args.file_path
n_it=int(io_args.n_it)
mdd=io_args.morgan_directory


add = mdd

try:
    os.mkdir(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job_predictions')
except:
    pass

for f in glob.glob(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job_predictions/*'):
    os.remove(f)

ct = 1

#temp = []
part_files = []

#for i,f in enumerate(glob.glob(add+'/*.txt')):
#    if i%4==0 and i!=0:
#       part_files.append(temp)
#       temp = []
#    temp.append(f)
#if len(temp)!=0:
#   part_files.append(temp)

#ct=0
#for i in range(len(part_files)):
#    ct+=len(part_files[i])
#print(ct)

for i,f in enumerate(glob.glob(add+'/*.txt')):
    part_files.append(f)

ct=1
for f in part_files:
    with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job_predictions/simple_job_'+str(ct)+'.sh','w') as ref:
        ref.write('#!/bin/bash\n')
        #ref.write('#SBATCH --ntasks=1\n')
        #ref.write('#SBATCH --nodes=1\n')
        #ref.write('#SBATCH --gres=gpu:1\n')
        #ref.write('#SBATCH --cpus-per-task=1\n')
        #ref.write('#SBATCH --job-name=phase_5\n')
        #ref.write('#SBATCH --mem=0               # memory per node\n')
        #ref.write('#SBATCH --time='+time+'            # time (DD-HH:MM)\n')
        ref.write('\n')
        ref.write('cd '+pd_folder_path+'\n')
        ref.write('source '+tf_venv_path+'/bin/activate\n')
        ref.write('python '+'Prediction_morgan_1024.py'+' '+'-fn'+' '+f.split('/')[-1]+' '+'-protein'+' '+protein+' '+'-it'+' '+str(n_it)+' '+'-mdd'+' '+str(mdd)+' '+'-file_path'+' '+file_path+'\n')
    ct+=1
      
