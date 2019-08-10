import glob
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-pt','--protein_name',required=True)
parser.add_argument('-it','--n_iteration',required=True)
parser.add_argument('-cdd','--data_directory',required=True)
parser.add_argument('-t_pos','--tot_process',required=True)
parser.add_argument('-t_samp','--tot_sampling',required=True)

io_args = parser.parse_args()

import os
from multiprocessing import Pool 
import time
from contextlib import closing
import pandas as pd
import numpy as np



protein = io_args.protein_name
n_it = int(io_args.n_iteration)
data_directory = io_args.data_directory
tot_process = int(io_args.tot_process)
tot_sampling = int(io_args.tot_sampling)

#if iteration_done==0:
#    add = clustered_data_directory
#else:
#    add = protein+'/iteration_'+str(iteration_done+1)+'/cluster_ZINC_id_after_iteration'

def write_mol_count_list(file_name,mol_count_list):
    with open(file_name,'w') as ref:
        for ct,file_name in mol_count_list:
            ref.write(str(ct)+","+file_name.split('/')[-1])
            ref.write("\n")

def molecule_count(file_name):
    temp = 0
    with open(file_name,'r') as ref:
        ref.readline()
        for line in ref:
            temp+=1
    return temp,file_name



if __name__=='__main__':
    files = []
    print(data_directory)
    for f in glob.glob(data_directory+'/*.txt'):
        files.append(f)
    print(len(files))
    t=time.time()
    with closing(Pool(np.min([tot_process,len(files)]))) as pool:
        rt = pool.map(molecule_count,files)
    print(time.time()-t)

    write_mol_count_list(data_directory+'/Mol_ct_file.csv',rt)

    mol_ct = pd.read_csv(data_directory+'/Mol_ct_file.csv',header=None)

    mol_ct.columns = ['Number_of_Molecules','file_name']

    Total_sampling = tot_sampling
    Total_mols_available = np.sum(mol_ct.Number_of_Molecules)

    mol_ct['Sample_for_million'] = [int(Total_sampling/Total_mols_available*elem) for elem in mol_ct.Number_of_Molecules]

    mol_ct.to_csv(data_directory+'/Mol_ct_file_updated.csv',sep=',',index=False)

