import glob
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-tpos','--n_cpus',required=True)
parser.add_argument('-pf','--phase_file',required=True)

io_args = parser.parse_args()

import os
import sys

tpos = int(io_args.n_cpus)
pf = io_args.phase_file

add = '/groups/cherkasvgrp/share/progressive_docking/pd_python/'

data = []
with open(add+'/'+pf+'_main.sh') as ref:
	for line in ref:
		data.append(line)

if tpos<=24:
   part = 'normal,gpu'
else:
   part = 'normal'


with open(add+'/'+pf+'.sh','w') as ref:
	for line in data:
		if 'cpus-per-task' in line:
			if pf=='phase_4':
				ref.write(line.rstrip()+str(3)+'\n')
			else:
				ref.write(line.rstrip()+str(tpos)+'\n')
		elif 'partition' in line:
                        #if part=='normal':
			if pf!='phase_4':
                            #continue
		            ref.write(line.rstrip()+part+'\n')
			else:
			    ref.write(line)
                        #else:
                        #    continue
		else:
			ref.write(line)
