import numpy as np
import multiprocessing
from multiprocessing import Pool, Process, Array
from contextlib import closing
import glob
import time
from functools import partial
import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-fn','--fn',required=True)
parser.add_argument('-protein','--protein',required=True)
parser.add_argument('-it','--it',required=True)
parser.add_argument('-file_path','--file_path',required=True)
parser.add_argument('-top_n','--top_n',required=True)
#parser.add_argument('-mdd','--morgan_directory',required=True)

io_args = parser.parse_args()
fn = io_args.fn
protein = str(io_args.protein)
it = int(io_args.it)
file_path = io_args.file_path
top_n = int(io_args.top_n)
#mdd=io_args.morgan_directory


try:
    os.mkdir(file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions_new')
except:
    pass

all_files = []
for f in glob.glob(file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions/*.txt'):
    all_files.append(f)
all_files.remove(file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions/passed_file_ct.txt')

ind_df = []
for f in all_files:
    ind_df = pd.read_csv(f,header=None)
all_molecules = pd.concat([*ind_df])
ind_df = []
all_molecules.columns= ['ZINC_ID','probability']
all_molecules = all_molecules.sort_values('probability')[::-1]
all_molecules = all_molecules.iloc[:top_n]

files_to_make = []
t_f = len(all_files)
for f in all_files:
    name = f.split('/')[-1]
    files_to_make.append(open(file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions_new/'+name,'w'))

per_file = int(top_n/t_f)

ct=0
fn=1
for zid in all_molecules.ZINC_ID:
    ct+=1
    if fn==t_f:
        files_to_make[fn-1].write(zid+'\n')
    elif ct==per_file:
        files_to_make[fn-1].write(zid+'\n')
        fn+=1
        ct=0
    else:
        files_to_make[fn-1].write(zid+'\n')

for f in files_to_make:
    f.close()

with open(file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions_new/passed_file_ct.txt','w') as ref:
    ct=0
    for f in files_to_make:
        ct+=1
        name = f.split('/')[-1]
        if ct==t_f:
            ref.write(name+','+str(top_n-per_file*(ct-1))+'\n')
        ref.write(name+','+str(per_file)+'\n')

os.system('mv '+file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions'+' '+file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions_old')
os.system('mv '+file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions_new'+' '+file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions')

#add = mdd

'''
thresholds = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(it)+'/best_models/thresholds.txt',header=None)
thresholds.columns = ['model_no','thresh','cutoff']

tr = []
models = []
for f in glob.glob(file_path+'/'+protein+'/iteration_'+str(it)+'/best_models/*.h5'):
    mn = int(f.split('/')[-1].split('_')[1])
    tr.append(thresholds[thresholds.model_no==mn].thresh.iloc[0])
    with open(file_path+'/'+protein+'/iteration_'+str(it)+'/best_models/model_'+str(mn)+'.json','r') as ref:
        models.append(model_from_json(ref.read()))
    models[-1].load_weights(f)
t=time.time()

returned = prediction_morgan(fn,models,tr)

print(time.time()-t)

with open(file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions/passed_file_ct.txt','a') as ref:
        ref.write(fn+','+str(returned)+'\n')
'''        
