import glob
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-pf','--phase_file',required=True)
parser.add_argument('-itr','--iteration_directory',required=True)


io_args = parser.parse_args()

import os
import sys
import time
import numpy as np

pf = io_args.phase_file
itr = io_args.iteration_directory

pfd = itr


print(pf)
if pf=='phase_1.sh' or pf=='phase_2.sh':
	with open(pfd+'/'+pf,'w') as ref:
		ref.write('finished\n')
elif pf=='phase_3_alternate.sh' or pf=='phase_3_alternate_1.sh':
	with open(pfd+'/phase_3.sh','w') as ref:
		ref.write('finished\n')
elif pf=='phase_3.sh':
	while 1==1:
		fct = len(glob.glob(itr+'/docked/*.sdf*'))
		if fct==3:
			with open(pfd+'/'+pf,'w') as ref:
				ref.write('finished\n')
			break
		else:
			time.sleep(300)
elif pf=='phase_4.sh':
	while 1==1:
		t_jobs = len(glob.glob(itr+'/simple_job/*.sh'))
		t_done = len(glob.glob(itr+'/simple_job/*.out'))
		if t_done!=t_jobs:
			time.sleep(300)
		else:
			jobids = []
			for f in glob.glob(itr+'/simple_job/*.out'):
				tmp = f.split('/')[-1].split('-')[-1].split('.')[0]
				jobids.append(os.system('squeue|grep '+tmp))
			if np.sum(np.array(jobids)>0)==len(jobids):
				with open(pfd+'/'+pf,'w') as ref:
					ref.write('finished\n')
				break
			else:
				time.sleep(300)
elif pf=='phase_5.sh':
	while 1==1:
		t_jobs = len(glob.glob(itr+'/simple_job_predictions/*.sh'))
		t_done = len(glob.glob(itr+'/simple_job_predictions/*.out'))
		if t_done!=t_jobs:
			time.sleep(300)
		else:
			jobids = []
			for f in glob.glob(itr+'/simple_job_predictions/*.out'):
				tmp = f.split('/')[-1].split('-')[-1].split('.')[0]
				jobids.append(os.system('squeue|grep '+tmp))
			if np.sum(np.array(jobids)>0)==len(jobids):
				with open(pfd+'/'+pf,'w') as ref:
					ref.write('finished\n')
				break
			else:
				time.sleep(300)
elif pf=='final_phase.sh':
	while 1==1:
		fct = len(glob.glob(itr+'to_dock/docked/*.sdf*'))
		if fct==3:
			with open(pfd+'/phase_f.sh','w') as ref:
				ref.write('finished\n')
			break
		else:
			time.sleep(300)
elif pf=='final_phase_alternate.sh' or pf=='final_phase_alternate_1.sh':
	with open(pfd+'/phase_f.sh','w') as ref:
		ref.write('finished\n')



