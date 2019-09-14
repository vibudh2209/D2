import multiprocessing
from multiprocessing import Pool, Process, Array, Manager
from contextlib import closing
import glob
import time
from functools import partial
#import gzip
import numpy as np
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-sfp','--smile_folder',required=True)
parser.add_argument('-tp','--t_pos',required=True)
parser.add_argument('-tn','--t_no',required=True)
io_args = parser.parse_args()


sf = io_args.smile_folder
t_pos = int(io_args.t_pos)
t_no = int(io_args.t_no)
name = 'smile_all_'

def zid_molecules(f_name):
    ct=0
    with open(f_name,'r') as ref:
        for line in ref:
            ct+=1
    return f_name,ct

def delete_all(files):
    os.remove(files)
    
def concat_morgan_files(file_data):
    file_no = file_data[0]
    files = file_data[1:]
    print(len(files))
    ref1 = open(sf+'/'+name+str(file_no)+'.txt','w')
    for f in files:
        with open(f,'r') as ref:
            for line in ref:
                ref1.write(line)
        os.remove(f)
    ref1.close()
    
def get_ct(to_list):
    return np.array([to_list[i][0] for i in range(len(to_list))])

def concat_for_equal(list_files,to_list):
    for i in range(len(list_files)):
        to_list[0].append(list_files[-1-i][-1])
        to_list[0][0] = to_list[0][0] + list_files[-1-i][0]
        ct = get_ct(to_list)
        to_list = [to_list[i] for i in ct.argsort()]
    
if __name__=='__main__':
    files = []
    for f in glob.glob(sf+"/*.smi"):
        files.append(f)
    t=time.time()
    with closing(Pool(np.min([multiprocessing.cpu_count(),len(files),t_pos]))) as pool:
        molecule_ct = pool.map(zid_molecules,files)
    print(time.time()-t)
    ct=[]
    for i in range(len(molecule_ct)):
        ct.append(molecule_ct[i][1])
    print(np.sum(ct))
    file_ct_list=[]
    for i in range(len(molecule_ct)):
        file_ct_list.append([molecule_ct[i][1],molecule_ct[i][0]])

    file_ct_list = [file_ct_list[i] for i in np.array(ct).argsort()]
    
    to_list = file_ct_list[-t_no:]
    list_files = file_ct_list[:-t_no]

    concat_for_equal(list_files,to_list)

    ct=0
    for i in range(len(to_list)):
        ct+=to_list[i][0]

    print(ct)
    
    files = {}
    for i in range(len(to_list)):
        for j in range(1,len(to_list[i])):
            files[to_list[i][j]] = 1

    print(len(files))

    for i in range(len(to_list)):
        to_list[i][0] = i+1
        
    t=time.time()
    with closing(Pool(np.min([multiprocessing.cpu_count(),len(to_list),t_pos]))) as pool:
        pool.map(concat_morgan_files,to_list)
    print(time.time()-t)
    
    files_morgan = []
    for f in glob.glob(sf+'/*.txt'):
        files_morgan.append(f)
        
    t=time.time()
    with closing(Pool(t_no)) as pool:
        molecule_ct = pool.map(zid_molecules,files_morgan)
    print(time.time()-t)
    
    ct=[]
    for i in range(len(molecule_ct)):
        ct.append(molecule_ct[i][1])
    print(np.sum(ct))




