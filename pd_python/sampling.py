import glob
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-pt','--protein_name',required=True)
parser.add_argument('-fp','--file_path',required=True)
parser.add_argument('-it','--n_iteration',required=True)
parser.add_argument('-dd','--data_directory',required=True)
parser.add_argument('-t_pos','--tot_process',required=True)

io_args = parser.parse_args()

import os
from multiprocessing import Pool 
import time
from contextlib import closing
import pandas as pd
import numpy as np



protein = io_args.protein_name
file_path = io_args.file_path
n_it =  int(io_args.n_iteration)
data_directory = io_args.data_directory
tot_process = int(io_args.tot_process)


def train_valid_test(file_name,iteration=0):
    f_name = file_name.split('/')[-1]
    mol_ct = pd.read_csv(data_directory+"/Mol_ct_file_updated.csv",index_col=1)
    To_sample = int(mol_ct.loc[f_name].Sample_for_million/3)
    Total_len = int(mol_ct.loc[f_name].Number_of_Molecules)
    shuffle_array = np.linspace(0,Total_len-1,Total_len)
    seed = np.random.randint(0,2**32)
    np.random.seed(seed=seed)
    np.random.shuffle(shuffle_array)
    train_ind = shuffle_array[:To_sample]
    valid_ind = shuffle_array[To_sample:To_sample*2]
    test_ind = shuffle_array[To_sample*2:To_sample*3]
    train_ind_dict = {}
    valid_ind_dict = {}
    test_ind_dict = {}
    train_set = open(file_path+'/'+protein+"/iteration_"+str(n_it)+"/train_set.txt",'a')
    test_set = open(file_path+'/'+protein+"/iteration_"+str(n_it)+"/test_set.txt",'a')
    valid_set = open(file_path+'/'+protein+"/iteration_"+str(n_it)+"/valid_set.txt",'a')
    for i,j,k in zip(train_ind,valid_ind,test_ind):
        train_ind_dict[i] = 1
        valid_ind_dict[j] = 1
        test_ind_dict[k] = 1
    with open(file_name,'r') as ref:
        for ind,line in enumerate(ref):
            if ind in train_ind_dict.keys():
                train_set.write(line[:16]+'\n')
            elif ind in valid_ind_dict.keys():
                valid_set.write(line[:16]+'\n')
            elif ind in test_ind_dict.keys():
                test_set.write(line[:16]+'\n')
    train_set.close()
    valid_set.close()
    test_set.close()
    
if __name__=='__main__':
    print(file_path,protein,data_directory)
    try:
        os.mkdir(file_path+'/'+protein+"/iteration_"+str(n_it))
    except:
        pass
    f_names = []
    for f in glob.glob(data_directory+'/*.txt'):
        f_names.append(f)

    t=time.time()
    with closing(Pool(np.min([tot_process,len(f_names)]))) as pool:
        pool.map(train_valid_test,f_names)
    print(time.time()-t)
