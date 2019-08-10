import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-sfp','--smile_folder_path',required=True)
parser.add_argument('-fp','--folder_path',required=True)
parser.add_argument('-fn','--folder_name',required=True)
parser.add_argument('-tp','--t_pos',required=True)

io_args = parser.parse_args()
sfp = io_args.smile_folder_path
fp = io_args.folder_path
fn = io_args.folder_name
t_pos = int(io_args.t_pos)

import glob
import time
import numpy as np
import pandas as pd
import pickle
from contextlib import closing
from multiprocessing import Pool
import multiprocessing
from rdkit.Chem import AllChem
from rdkit import DataStructs
from rdkit import Chem
from functools import partial
import os

def get_n_lines_2(file):
    ct=0
    with open(file,'r') as ref:
        ref.readline()
        for line in ref:
            ct+=1
    return file,ct

def morgan_fingp(fname):
    nbits=1024
    radius=2
    #fp = []
    fsplit = fname.split('/')[-1]
    #to_skip = done_dict[fsplit]
    ref2  = open(fp+'/'+fn+'/'+fsplit,'a')
    #print(fname,to_skip)
    with open(fname,'r') as ref:
        ref.readline()
        #for count in range(to_skip):
        #    ref.readline()
        for line in ref:
            smile,zin_id = line.rstrip().split()
            arg = np.zeros((1,))
            try:
                DataStructs.ConvertToNumpyArray(AllChem.GetMorganFingerprintAsBitVect(Chem.MolFromSmiles(smile),radius,nBits=nbits),arg)

                ref2.write((',').join([zin_id]+[str(elem) for elem in np.where(arg==1)[0]]))
                ref2.write('\n')
            except:
                print(line)
                pass

if __name__=='__main__':
	files = []
	for f in glob.glob(sfp+'/*.txt'):
	    files.append(f)

	try:
	    os.mkdir(fp+'/'+fn)
	except:
	    pass

	#all_morgan = []
	#for f in glob.glob(fp+'/'+fn+'/*.txt'):all_morgan.append(f)

	#t=time.time()
	#with closing(Pool(multiprocessing.cpu_count())) as pool:
	#    ct_per_file = pool.map(get_n_lines_2,all_morgan)
	#print(time.time()-t)

	#ct_per_file_dict = {}
	#for fn,ct in ct_per_file:
	#    ct_per_file_dict[fn.split('/')[-1]] = ct

	t_f = len(files)
	t=time.time()
	with closing(Pool(np.min([multiprocessing.cpu_count(),t_pos]))) as pool:
	    pool.map(morgan_fingp,files)
	print(time.time()-t)
