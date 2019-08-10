import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n_it','--iteration_no',required=True)
parser.add_argument('-mdd','--morgan_directory',required=True)
parser.add_argument('-time','--time',required=True)
parser.add_argument('-protein','--protein',required=True)
parser.add_argument('-file_path','--file_path',required=True)
parser.add_argument('-nhp','--number_of_hyp',required=True)

io_args = parser.parse_args()
n_it = int(io_args.iteration_no)
mdd = io_args.morgan_directory
time = io_args.time
protein = io_args.protein
file_path = io_args.file_path
nhp = int(io_args.number_of_hyp)

import numpy as np
import pandas as pd
import glob

t_mol = pd.read_csv(mdd+'/Mol_ct_file.csv',header=None)[[0]].sum()[0]/1000000

cummulative = 0.25*n_it
num_units = [1000,1500,2000]
dropout = [0.7,0.9]
learn_rate = [0.0001]
bin_array = [2,3]
wt = [2,3]
if nhp<144:
   bs = [256]
else:
    bs = [128,256]
oss = [10]

try:
    os.mkdir(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job')
except:
    pass

for f in glob.glob(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job/*'):
    os.remove(f)

scores = []
with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/training_labels.txt','r') as ref:
    ref.readline()
    for line in ref:
        scores.append(float(line.rstrip().split(',')[0]))

scores_val = []
with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/validation_labels.txt','r') as ref:
    ref.readline()
    for line in ref:
        scores_val.append(float(line.rstrip().split(',')[0]))

scores_val = np.array(scores_val)

mean_score = np.mean(scores)
std_score = np.std(scores)

if nhp<48:
    cf = [mean_score - (1.75+cummulative)*std_score]
elif nhp<72:
    cf = [mean_score - (1.75+cummulative)*std_score,mean_score - (2+cummulative)*std_score]
else:
    cf = [mean_score - (1.75+cummulative)*std_score,mean_score - (2+cummulative)*std_score,mean_score - (2.25+cummulative)*std_score]

print(cf)

scores_val = []
with open(file_path+'/'+protein+'/iteration_'+str(1)+'/validation_labels.txt','r') as ref:
    ref.readline()
    for line in ref:
        scores_val.append(float(line.rstrip().split(',')[0]))

scores_val = np.array(scores_val)

for i,c in enumerate(cf):
    t_avail = len(scores_val[scores_val<c])
    print(c,t_avail)
    if t_avail<200:
        for j in range(100):
            new_c = c+0.05*(j+1)
            t_avail = len(scores_val[scores_val<new_c])
            if t_avail>200:
                cf[i] = new_c
                break

new_cf = cf

print(new_cf)

if len(new_cf)==3:
    if np.abs(new_cf[-1]-new_cf[-2])<0.1:
        cf.remove(cf[-1])
    elif np.abs(new_cf[-2]-new_cf[-3])<0.1:
        cf.remove(cf[-2])
elif len(new_cf)==2:
    if np.abs(new_cf[-1]-new_cf[-2])<0.1:
        cf.remove(cf[-1])


print(cf)
for c in cf:
    t_avail = len(scores_val[scores_val<c])
    print(c,t_avail)


all_hyperparas = []

for o in oss:
    for batch in bs:
        for nu in num_units:
            for do in dropout:
                for lr in learn_rate:
                    for ba in bin_array:
                        for w in wt:
                            for c in cf:
                                all_hyperparas.append([o,batch,nu,do,lr,ba,w,c])

print(len(all_hyperparas))
#hyper_division = []
#temp = []
#for i in range(len(all_hyperparas)):
#    if i%4==0 and i!=0:
#       hyper_division.append(temp)
#       temp = []
#    temp.append(all_hyperparas[i])
#if len(temp)!=0:
#   hyper_division.append(temp)


#print(len(hyper_division))
#ct = 0
#for i in range(len(hyper_division)):
#    ct+=len(hyper_division[i])
#print(ct)

ct=1
#for i in range(len(hyper_division)):
for i in range(len(all_hyperparas)):
    with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job/simple_job_'+str(ct)+'.sh','w') as ref:
        ref.write('#!/bin/bash\n')
        ref.write('#SBATCH --ntasks=1\n')
        #ref.write('#SBATCH --nodes=1\n')
        ref.write('#SBATCH --gres=gpu:1\n')
        ref.write('#SBATCH --cpus-per-task=1\n')
        ref.write('#SBATCH --job-name=phase_4\n')
        ref.write('#SBATCH --mem=0               # memory per node\n')
        ref.write('#SBATCH --time='+time+'            # time (DD-HH:MM)\n')
        ref.write('\n')
        ref.write('cd /groups/cherkasvgrp/share/progressive_docking/pd_python\n')
        ref.write('source tensorflow_gpu/bin/activate\n')
        #for j in range(len(hyper_division[i])):
        o,batch,nu,do,lr,ba,w,c = all_hyperparas[i]
        ref.write('python '+'progressive_docking.py'+' '+'-num_units'+' '+str(nu)+' '+'-dropout'+' '+str(do)+' '+'-learn_rate'+' '+str(lr)+' '+'-bin_array'+' '+str(ba)+' '+'-wt'+' '+str(w)+' '+'-cf'+' '+str(c)+' '+'-n_it'+' '+str(n_it)+' '+'-t_mol'+' '+str(t_mol)+' '+'-os'+' '+str(o)+' '+'-bs'+' '+str(batch)+' '+'-protein'+' '+protein+' '+'-file_path'+' '+file_path+'\n')
        #ref.write('srun'+' '+'-N 1 -n 1 --gres=gpu:1 '+'python '+'progressive_docking.py'+' '+'-num_units'+' '+str(nu)+' '+'-dropout'+' '+str(do)+' '+'-learn_rate'+' '+str(lr)+' '+'-bin_array'+' '+str(ba)+' '+'-wt'+' '+str(w)+' '+'-cf'+' '+str(c)+' '+'-n_it'+' '+str(n_it)+' '+'-t_mol'+' '+str(t_mol)+' '+'-os'+' '+str(o)+' '+'-bs'+' '+str(batch)+' '+'-protein'+' '+protein+' '+'-file_path'+' '+file_path+' &\n')
        #ref.write('wait')
    ct+=1

