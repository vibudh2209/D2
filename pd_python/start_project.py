import glob
import argparse
import os
from os.path import expanduser
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-fp','--file_path',required=True)
parser.add_argument('-pn','--protein',required=True)
io_args = parser.parse_args()
fp = io_args.file_path
pn = io_args.protein


home_path = expanduser("~")

#with open(home_path+'/new_project_details.txt','r') as ref:
#    file_path = ref.readline().rstrip()
#    protein = ref.readline().rstrip()

try:
    os.mkdir(fp+'/'+pn)
except:
    pass

try:
    os.mkdir(fp+'/'+pn+'/iteration_1')
except:
    pass
