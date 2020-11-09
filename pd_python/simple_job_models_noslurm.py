import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n_it','--iteration_no',required=True)
parser.add_argument('-mdd','--morgan_directory',required=True)
parser.add_argument('-time','--time',required=True)
parser.add_argument('-protein','--protein',required=True)
parser.add_argument('-file_path','--file_path',required=True)
#parser.add_argument('-nhp','--number_of_hyp',required=True)
parser.add_argument('-pdfp','--pd_folder_path',required=True)
parser.add_argument('-tfp','--tf_venv_path',required=True)
parser.add_argument('-min_last','--min_mols_last',required=True)

io_args = parser.parse_args()
n_it = int(io_args.iteration_no)
mdd = io_args.morgan_directory
time = io_args.time
protein = io_args.protein
file_path = io_args.file_path
#nhp = int(io_args.number_of_hyp)
pd_folder_path = io_args.pd_folder_path 
tf_venv_path = io_args.tf_venv_path
min_last = int(io_args.min_mols_last)

import numpy as np
import pandas as pd
import glob

t_mol = pd.read_csv(mdd+'/Mol_ct_file.csv',header=None)[[0]].sum()[0]/1000000

num_units = [1000,1500,2000]
dropout = [0.7]
learn_rate = [0.0001]
bin_array = [2,3]
wt = [2,3]
bs = [256]
oss = [10]

try:
    os.mkdir(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job')
except:
    pass

for f in glob.glob(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job/*'):
    os.remove(f)

scores = []
with open(file_path+'/'+protein+'/iteration_'+str(1)+'/training_labels.txt','r') as ref:
    ref.readline()
    for line in ref:
        scores.append(float(line.rstrip().split(',')[0]))

scores_val = []
with open(file_path+'/'+protein+'/iteration_'+str(1)+'/validation_labels.txt','r') as ref:
    ref.readline()
    for line in ref:
        scores_val.append(float(line.rstrip().split(',')[0]))

scores_val = np.array(scores_val)

if n_it==1:
    good_mol = int(min_last*t_mol/15)
else:
    with open(file_path+'/'+protein+'/iteration_'+str(n_it-1)+'/best_model_stats.txt','r') as ref:
        ref.readline()
        left_mol = float(ref.readline().rstrip().split(',')[-1])/1000000
    good_mol = int(min_last*left_mol/15)

cf_start = np.mean(scores_val)
while 1==1:
    t_good = len(scores_val[scores_val<cf_start])
    if t_good<=good_mol:
        break
    cf_start = cf_start - 0.005

cf = [cf_start]


print(cf)



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


ct=1
#for i in range(len(hyper_division)):
for i in range(len(all_hyperparas)):
    with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job/simple_job_'+str(ct)+'.sh','w') as ref:
        ref.write('#!/bin/bash\n')
        ref.write('\n')
        ref.write('cd '+pd_folder_path+'\n')
        ref.write('source '+tf_venv_path+'/bin/activate\n')
        #for j in range(len(hyper_division[i])):
        o,batch,nu,do,lr,ba,w,c = all_hyperparas[i]
        ref.write('python '+'progressive_docking.py'+' '+'-num_units'+' '+str(nu)+' '+'-dropout'+' '+str(do)+' '+'-learn_rate'+' '+str(lr)+' '+'-bin_array'+' '+str(ba)+' '+'-wt'+' '+str(w)+' '+'-cf'+' '+str(c)+' '+'-n_it'+' '+str(n_it)+' '+'-t_mol'+' '+str(t_mol)+' '+'-os'+' '+str(o)+' '+'-bs'+' '+str(batch)+' '+'-protein'+' '+protein+' '+'-file_path'+' '+file_path+'-run_time'+' '+time+'\n')
    ct+=1

