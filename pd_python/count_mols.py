import glob
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-pt','--protein_name',required=True)
parser.add_argument('-it','--n_iteration',required=True)
parser.add_argument('-fp','--file_path',required=True)
parser.add_argument('-t_pos','--tot_process',required=True)

io_args = parser.parse_args()

import os
from multiprocessing import Pool 
import time
from contextlib import closing

protein = io_args.protein_name
n_it = int(io_args.n_iteration)
file_path = io_args.file_path
tot_process = int(io_args.tot_process)

def molecule_count(file_name):
    temp = 0
    with open(file_name,'r') as ref:
        ref.readline()
        for line in ref:
            temp+=1
    return temp,file_name

if __name__=='__main__':
    files = []
    data_directory = file_path+'/'+protein+'/iteration_'+str(n_it)+'/morgan_1024_predictions/'
    print(data_directory)
    for f in glob.glob(data_directory+'/*.txt'):
        files.append(f)
    print(len(files))
    t=time.time()
    if len(files)<tot_process:
    	tot_process=len(files)
    with closing(Pool(tot_process)) as pool:
        rt = pool.map(molecule_count,files)
    print(time.time()-t)

    ct = 0
    for i in rt:
    	ct+=i

    with open(data_directory+'/molecule_count.csv','w') as ref:
    	ref.write(ct)