import glob
import pickle
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-pt','--protein_name',required=True)
parser.add_argument('-fp','--file_path',required=True)
parser.add_argument('-it','--n_iteration',required=True)
parser.add_argument('-t_pos','--tot_process',required=True)

io_args = parser.parse_args()

import os
from multiprocessing import Pool 
import time
from contextlib import closing
import pandas as pd
import numpy as np
from functools import partial
import gzip
import pickle
import sys


protein = io_args.protein_name
file_path = io_args.file_path
n_it =  int(io_args.n_iteration)
tot_process = int(io_args.tot_process)


def get_z_ids(data):
	sdfname,i,fname = data
	zids = {}
	for key in pd.read_csv(fname).ZINC_ID:
		zids[key] = 0
	return [sdfname,i,zids]

def get_pred_zids(fname):
	zids = {}
	with open(fname,'r') as ref:
		for line in ref:
			zids[line.rstrip()] = 1
	return zids

def get_mol_from_zid(data):
	sdfname,i,zids = data
	name = sdfname.split('/')[-1].split('.')[0]
	ref1 = gzip.open(file_path+'/'+protein+'/after_iteration/already_docked/'+name+'_'+str(i)+'.sdf.gz','wb')
	with gzip.open(sdfname,'rb') as ref:
		for line in ref:
			if line.decode('utf-8')[:4] == 'ZINC':
				tmp = line.decode('utf-8').strip()
				#print(tmp)
				if tmp in zids:
					#print(tmp)
					if zids[tmp] == 0:
						zids[tmp] +=1
						ref1.write(line)
						for lines in ref:
							ref1.write(lines)
							if lines.decode('utf-8')[:4]=='$$$$':
								break
	ref1.close()


if __name__=='__main__':
	
	all_predocked = []
	for i in range(1,n_it+1):
		for f in glob.glob(file_path+'/'+protein+'/'+'iteration_'+str(i)+'/docked/*.sdf*'):
			name = f.split('/')[-1].split('_')[2]
			g = file_path+'/'+protein+'/'+'iteration_'+str(i)+'/'+name+'_labels.txt'
			all_predocked.append([f,i,g])

	#print(all_predocked[0])
	#sys.exit()

	with closing(Pool(np.min([len(all_predocked),tot_process]))) as pool:
		returned = pool.map(get_z_ids,all_predocked)

	for i in range(len(returned)):
		for j in range(i+1,len(returned)):
			for keys in returned[i][-1].keys():
				if keys in returned[j][-1].keys():
					returned[j][-1].pop(keys)

	all_files_predicted = []
	for f in glob.glob(file_path+'/'+protein+'/'+'iteration_'+str(n_it)+'/morgan_1024_predictions/*.txt'):
		all_files_predicted.append(f)

	with closing(Pool(np.min([len(all_files_predicted),tot_process]))) as pool:
		returned_predicted = pool.map(get_pred_zids,all_files_predicted)
	all_predicted = {}
	for i in range(len(returned_predicted)):
		for key in returned_predicted[i].keys():
			all_predicted[key] = 0
	returned_predicted = []

	print(len(all_predicted))

	for i in range(len(returned)):
		tmp = {}
		for keys in returned[i][-1].keys():
			if keys in all_predicted:
				all_predicted.pop(keys)
				tmp[keys] = 0
		returned[i][-1] = tmp

	tmp = []
	print(len(all_predicted))
	try:
		os.mkdir(file_path+'/'+protein+'/after_iteration')
	except:
		pass

	try:
		os.mkdir(file_path+'/'+protein+'/after_iteration/to_dock')
	except:
		pass

	try:
		os.mkdir(file_path+'/'+protein+'/after_iteration/already_docked')
	except:
		pass

	with closing(Pool(np.min([len(returned),tot_process]))) as pool:
		pool.map(get_mol_from_zid,returned)

	returned = []

	cnt = 1
	ref = open(file_path+'/'+protein+'/after_iteration/to_dock/to_dock_'+str(cnt)+'.txt','w')
	for i,keys in enumerate(all_predicted):
		ref.write(keys+'\n')
		if i%999999==0 and i!=0:
			ref.close()
			cnt+=1
			ref = open(file_path+'/'+protein+'/after_iteration/to_dock/to_dock_'+str(cnt)+'.txt','w')
	try:
		ref.close()
	except:
		pass







