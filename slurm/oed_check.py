import glob
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-fp','--file_path',required=True)
parser.add_argument('-pf','--phase_file',required=True)
parser.add_argument('-ttime','--ttime',required=True)

io_args = parser.parse_args()

import os
import time
import sys

file_path = io_args.file_path
phase_file = io_args.phase_file
ttime = int(io_args.ttime)

tmm = file_path.split('/')
for i,name in enumerate(tmm):
	if 'iteration' in name:
		tmm = ('/').join(tmm[:i+1])
		break

def count_f(fn):
	ct=0
	with open(fn) as ref:
		for line in ref:
			ct+=1
	return ct


time.sleep(ttime)

rpt_file = []
for f in glob.glob(file_path+'/*.rpt'):
		rpt_file.append(f)
for f in glob.glob(file_path+'/*score.txt'):
		rpt_file.append(f)


ctv = []
for f in rpt_file:
	ctv.append(count_f(f))

time.sleep(300)

while 1==1:
	stop = True
	for i,f in enumerate(rpt_file):
		tmp = count_f(f)
		if tmp!=ctv[i]:
			ctv[i] = tmp
			stop=False
	if stop==True:
		with open(tmm+'/'+phase_file) as ref:
			fn = ref.readline().rstrip()
		sys.exit()
	else:
		time.sleep(300)


