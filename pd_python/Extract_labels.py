import numpy as np
import pandas as pd
import glob
import time
from multiprocessing import Pool
from contextlib import closing
import gzip
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-if','--is_final',required=True)
parser.add_argument('-n_it','--iteration_no',required=True)
parser.add_argument('-protein','--protein',required=True)
parser.add_argument('-file_path','--file_path',required=True)
parser.add_argument('-t_pos','--tot_process',required=True)
parser.add_argument('-sof','--software',required=True)

io_args = parser.parse_args()

is_final = io_args.is_final
n_it = int(io_args.iteration_no)
protein = io_args.protein
file_path = io_args.file_path
tot_process = int(io_args.tot_process)
sof = io_args.software

if is_final=='False' or is_final=='false':
    is_final = False
elif is_final=='True' or is_final=='true':
    is_final = True

if sof=='GLIDE':
    key_word = 'r_i_docking_score'
elif sof=='OEDDOCKING':
    key_word = 'FRED Chemgauss4 score'

print(key_word)

def extract_glide_score(filen):
    scores = []
    try:
        with gzip.open(filen,'rt') as ref:
            for line in ref:
                if line[:4]=="ZINC":
                    zinc_id = line.rstrip()
                    for lines in ref:
                        tmp = lines.rstrip().split('<')[-1]
                        if key_word==tmp[:-1]:
                            tmpp = float(ref.readline().rstrip())
                            if tmpp>50 or tmpp<-50:
                                print(zinc_id,tmpp)
                                break
                            scores.append([zinc_id,tmpp])
                            break
    
    except:
        with open(filen,'r') as ref:
            for line in ref:
                if line[:4]=="ZINC":
                    zinc_id = line.rstrip()
                    for lines in ref:
                        tmp = lines.rstrip().split('<')[-1]
                        #print(tmp[:-1],key_word,tmp[:-1]==key_word)
                        if key_word==tmp[:-1]:
                            tmpp = float(ref.readline().rstrip())
                            if tmpp>50 or tmpp<-50:
                                print(zinc_id,tmpp)
                                break
                            scores.append([zinc_id,tmpp])
                            break
                    

    with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/'+filen.split('/')[-1].split('.')[0]+'_'+'labels.txt','w') as ref:
        ref.write('r_i_docking_score'+','+'ZINC_ID'+'\n')
        for z_id,gc in scores:
            ref.write(str(gc)+','+z_id+'\n')

if __name__=='__main__':
    files=[]
    if is_final:
       path = file_path+'/'+protein+'/after_iteration'+'/docked/*.sdf*'
    else:
       path = file_path+'/'+protein+'/iteration_'+str(n_it)+'/docked/*.sdf*'
       path1 = file_path+'/'+protein+'/iteration_'+str(n_it)+'/*labels*'
    for f in glob.glob(path):
        files.append(f)
    
    print(len(files))
    with closing(Pool(len(files))) as pool:
        pool.map(extract_glide_score,files)

    if not is_final:
        for f in glob.glob(path1):
            os.rename(f,file_path+'/'+protein+'/iteration_'+str(n_it)+'/'+f.split('/')[-1].split('_')[2]+'_'+'labels.txt')

