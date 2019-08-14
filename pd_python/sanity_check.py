import glob
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-pt','--protein_name',required=True)
parser.add_argument('-fp','--file_path',required=True)
parser.add_argument('-it','--n_iteration',required=True)

io_args = parser.parse_args()
import os
import time
import pandas as pd
import numpy as np



protein = io_args.protein_name
file_path = io_args.file_path
n_it =  int(io_args.n_iteration)

old_dict = {}
for i in range(1,n_it):
    with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(i)+'/training_labels*')[-1]) as ref:
        ref.readline()
        for line in ref:
            old_dict[line[-16:]] = 1
    with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(i)+'/validation_labels*')[-1]) as ref:
        ref.readline()
        for line in ref:
            old_dict[line[-16:]] = 1
    with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(i)+'/testing_labels*')[-1]) as ref:
        ref.readline()
        for line in ref:
            old_dict[line[-16:]] = 1

t=time.time()
new_train = {}
new_valid = {}
new_test = {}
with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(n_it)+'/train_set*')[-1]) as ref:
    for line in ref:
        new_train[line[:16]] = 1
with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(n_it)+'/valid_set*')[-1]) as ref:
    for line in ref:
        new_valid[line[:16]] = 1
with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(n_it)+'/test_set*')[-1]) as ref:
    for line in ref:
        new_test[line[:16]] = 1
print(time.time()-t)

t=time.time()
for keys in new_train.keys():
    if keys in new_valid.keys():
        new_valid.pop(keys)
    if keys in new_test.keys():
        new_test.pop(keys)
for keys in new_valid.keys():
    if keys in new_test.keys():
        new_test.pop(keys)
print(time.time()-t)

for keys in old_dict.keys():
    if keys in new_train.keys():
        new_train.pop(keys)
    if keys in new_valid.keys():
        new_valid.pop(keys)
    if keys in new_test.keys():
        new_test.pop(keys)
        
with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/train_set.txt','w') as ref:
    for keys in new_train.keys():
        ref.write(keys+'\n')
with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/valid_set.txt','w') as ref:
    for keys in new_valid.keys():
        ref.write(keys+'\n')
with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/test_set.txt','w') as ref:
    for keys in new_test.keys():
        ref.write(keys+'\n')