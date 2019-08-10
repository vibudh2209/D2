import numpy as np
import multiprocessing
from multiprocessing import Pool, Process, Array
from contextlib import closing
import glob
import time
from functools import partial
import pandas as pd
from keras.models import model_from_json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-fn','--fn',required=True)
parser.add_argument('-protein','--protein',required=True)
parser.add_argument('-it','--it',required=True)
parser.add_argument('-file_path','--file_path',required=True)
parser.add_argument('-mdd','--morgan_directory',required=True)

io_args = parser.parse_args()
fn = io_args.fn
protein = str(io_args.protein)
it = int(io_args.it)
file_path = io_args.file_path
mdd=io_args.morgan_directory

def prediction_morgan(fname,models,thresh):
    t=time.time()
    per_time = 1000000
    n_features = 1024
    z_id = []
    #thresh = tr
    X_set = np.zeros([per_time,n_features])
    total_passed = 0
    with open(add+'/'+fname,'r') as ref:
        no=0
        for line in ref:
            tmp=line.rstrip().split(',')
            on_bit_vector = tmp[1:]
            z_id.append(tmp[0])
            for elem in on_bit_vector:
                X_set[no,int(elem)] = 1
            no+=1
            if no == per_time:
                X_set = X_set[:no,:]
                pred = []
                for Progressive_docking in models:
                    pred.append(Progressive_docking.predict(X_set))
                with open(file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions/'+fname,'a') as ref:
                    for j in range(len(pred[0])):
                        is_pass = 0
                        for i,thr in enumerate(thresh):
                            if float(pred[i][j])>thr:
                                is_pass+=1
                        if is_pass>=1:
                            total_passed+=1
                            ref.write(z_id[j]+','+str(float(pred[i][j]))+'\n')
                X_set = np.zeros([per_time,n_features])
                z_id = []
                no = 0
        if no!=0:
            X_set = X_set[:no,:]
            pred = []
            for Progressive_docking in models:
                pred.append(Progressive_docking.predict(X_set))
            with open(file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions/'+fname,'a') as ref:
                for j in range(len(pred[0])):
                    is_pass = 0
                    for i,thr in enumerate(thresh):
                        if float(pred[i][j])>thr:
                            is_pass+=1
                    if is_pass>=1:
                        total_passed+=1
                        ref.write(z_id[j]+','+str(float(pred[i][j]))+'\n')
            X_set = np.zeros([per_time,n_features])
            z_id = []
    return total_passed


try:
    os.mkdir(file_path+'/'+protein+'/iteration_'+str(it)+'/morgan_1024_predictions')
except:
    pass

add = mdd

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
        
