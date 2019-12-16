import argparse
import os
import glob

parser = argparse.ArgumentParser()
parser.add_argument('-protein','--protein',required=True)
parser.add_argument('-file_path','--file_path',required=True)
parser.add_argument('-n_it','--iteration_no',required=True)
parser.add_argument('-jid','--job_id',required=True)
parser.add_argument('-jn','--job_name',required=True)

io_args = parser.parse_args()
protein = io_args.protein
file_path = io_args.file_path
n_it = int(io_args.iteration_no)
job_id = io_args.job_id
job_name = io_args.job_name

if n_it!=-1:
        try:
           os.mkdir(file_path+'/'+protein+'/iteration_'+str(n_it))
        except:
           pass
	with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/'+job_name,'w') as ref:
		ref.write(job_id+'\n')
else:
        try:
           os.mkdir(file_path+'/'+protein+'/after_iteration')
        except:
           pass
	with open(file_path+'/'+protein+'/after_iteration'+'/'+job_name,'w') as ref:
		ref.write(job_id+'\n')

