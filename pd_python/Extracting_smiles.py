import glob
import pickle
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-pt','--protein_name',required=True)
parser.add_argument('-fp','--file_path',required=True)
parser.add_argument('-it','--n_iteration',required=True)
parser.add_argument('-fn','--file_no',required=True)
parser.add_argument('-smd','--smile_directory',required=True)
parser.add_argument('-sd','--sdf_directory',required=True)
parser.add_argument('-t_pos','--tot_process',required=True)
parser.add_argument('-if','--is_final',required=True)

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


protein = io_args.protein_name
file_path = io_args.file_path
n_it =  int(io_args.n_iteration)
file_no = int(io_args.file_no)
sdf_directory = io_args.sdf_directory
smile_directory = io_args.smile_directory
tot_process = int(io_args.tot_process)
is_final = io_args.is_final

if is_final=='False' or is_final=='false':
    is_final = False
elif is_final=='True' or is_final=='true':
    is_final = True
    
def no_molecules_txt(f_name):
    with open(f_name,'r') as ref:
        ct = 0
        for line in ref:
            if line.rstrip()[:4]=="ZINC":
                ct+=1
    return ct

def get_mol_final(fname):
    #final_dict = {}
    try:
        with open(file_path+'/'+protein+"/after_iteration/to_dock/to_dock_"+str(file_no)+".pickle",'rb') as ref:
            final_dict = pickle.load(ref)
    except:
        with open(file_path+'/'+protein+"/after_iteration/to_dock/to_dock_"+str(file_no)+".txt",'r') as ref:
            for line in ref:
                final_dict[line.rstrip()] = 0
    to_return = {}
    with open(sdf_directory+"/zinc_ids_each_file/"+fname.split('/')[-1]+'.txt','r') as ref:
        for line in ref:
            tmp = line[:16]
            if tmp in final_dict:
                to_return[tmp] = 0
    return to_return

def get_mol(fname):
    train= {}
    test = {}
    valid = {}
    with open(file_path+'/'+protein+"/iteration_"+str(n_it)+"/train_set.txt",'r') as ref:
        for line in ref:
            train[line.rstrip()] = 0
    with open(file_path+'/'+protein+"/iteration_"+str(n_it)+"/valid_set.txt",'r') as ref:
        for line in ref:
            valid[line.rstrip()] = 0
    with open(file_path+'/'+protein+"/iteration_"+str(n_it)+"/test_set.txt",'r') as ref:
        for line in ref:
            test[line.rstrip()] = 0
    
    to_return_train = {}
    to_return_valid = {}
    to_return_test = {}
    
    with open(sdf_directory+"/zinc_ids_each_file/"+fname.split('/')[-1]+'.txt','r') as ref:
        for line in ref:
            tmp = line[:16]
            if tmp in train:
                to_return_train[tmp] = 0
            if tmp in valid:
                to_return_valid[tmp] = 0
            if tmp in test:
                to_return_test[tmp] = 0
            
    return to_return_train,to_return_valid,to_return_test

def extract_smile(file_name,train,valid,test):
    #for file_name in file_names:
    ref1 = open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/smile/'+'train_'+file_name.split('/')[-1],'w')
    ref2 = open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/smile/'+'valid_'+file_name.split('/')[-1],'w')
    ref3 = open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/smile/'+'test_'+file_name.split('/')[-1],'w')
    with open(file_name,'r') as ref:
        ref.readline()
        flag=0
        for line in ref:
            if line[-17:-1] in train.keys():
                train[line[-17:-1]]+=1
                fn = 1
                if train[line[-17:-1]]==1: flag=1
            elif line[-17:-1] in valid.keys():
                valid[line[-17:-1]]+=1
                fn = 2
                if valid[line[-17:-1]]==1: flag=1
            elif line[-17:-1] in test.keys():
                test[line[-17:-1]]+=1
                fn = 3
                if test[line[-17:-1]]==1: flag=1
            if flag==1:
                if fn==1:
                    ref1.write(line)
                if fn==2:
                    ref2.write(line)
                if fn==3:
                    ref3.write(line)
            flag = 0

def extract_smile_final(all_mols,file_name):
    #for file_name in file_names:
    #all_total_mols = {}
    #with open(file_path+'/'+protein+"/after_iteration/to_dock/to_dock_"+str(file_no)+".pickle",'rb') as ref:
    #    all_mols  = pickle.load(ref)
    fn = file_name.split('/')[-1]
    ref1 = open(file_path+'/'+protein+'/after_iteration/to_dock/smile/'+fn,'w')    
    with open(file_name,'r') as ref:
        ref.readline()
        flag=0
        for line in ref:
            if line[-17:-1] in all_mols.keys():
                all_mols[line[-17:-1]]+=1
                if all_mols[line[-17:-1]]==1: flag=1
            if flag==1:
                ref1.write(line)
            flag = 0

def alternate_concat(files):
    to_return = []
    with open(files,'r') as ref:
        for line in ref:
            to_return.append(line)
    return to_return
        
def delete_all(files):
    os.remove(files)
            
def smile_duplicacy(f_name):
    flag=0
    mol_list = {}
    ref1 = open(f_name[:-4]+'_updated.smi','a')
    with open(f_name,'r') as ref:
        for line in ref:
            if line[-17:-1] not in mol_list:
                mol_list[line[-17:-1]] = 1
                flag=1
            if flag==1:
                ref1.write(line)
                flag = 0
    os.remove(f_name)

def delete_all(files):
    os.remove(files)
    
if __name__=='__main__':
    if is_final==False:
        try:
            os.mkdir(file_path+'/'+protein+'/iteration_'+str(n_it)+'/smile')
        except:
            pass
    else:
        try:
            os.mkdir(file_path+'/'+protein+'/after_iteration/to_dock/smile')
        except:
            pass

    files = []
    for f in glob.glob(sdf_directory+"/*.gz"):
        files.append(f)

    files_z_id = []
    for f in glob.glob(sdf_directory+"/zinc_ids_each_file/*"):
        files_z_id.append(f)
    
    files_smiles = []
    for f in glob.glob(smile_directory+"/*.txt"):
        files_smiles.append(f)
    
    print(len(files_smiles))

    if is_final==True:
        print('is final')
        t=time.time()
        if len(files)==0:
            return_mols_per_file = []
        else:
            with closing(Pool(np.min([tot_process,len(files)]))) as pool:
                return_mols_per_file = pool.map(get_mol_final,files)
            print(time.time()-t)
   
        ct = 0
        for i in range(len(return_mols_per_file)):
            ct+=len(return_mols_per_file[i])
        print(ct)
        
        t=time.time()
        for i in range(len(return_mols_per_file)):
            for j in range(i+1,len(return_mols_per_file)):
                for keys in return_mols_per_file[i].keys():
                    if keys in return_mols_per_file[j]:
                        return_mols_per_file[j].pop(keys)
        print(time.time()-t)
        
        ct = 0
        for i in range(len(return_mols_per_file)):
            ct+=len(return_mols_per_file[i])
        print(ct)
        
        total_mols = {}
        for mini_dict in return_mols_per_file:
            for keys in mini_dict.keys():
                total_mols[keys] = 0

        all_total_mols = {}
        try:
            with open(file_path+'/'+protein+"/after_iteration/to_dock/to_dock_"+str(file_no)+".pickle",'rb') as ref:
                all_total_mols = pickle.load(ref)
        except:
            with open(file_path+'/'+protein+"/after_iteration/to_dock/to_dock_"+str(file_no)+".txt",'r') as ref:
                for line in ref:
                    all_total_mols[line.rstrip()] = 0

        for keys in total_mols.keys():
            all_total_mols.pop(keys)
        
        print(len(all_total_mols))
        t=time.time()
        with closing(Pool(np.min([tot_process,len(files_smiles)]))) as pool:
            #pool.map(extract_smile_final,files_smiles)
            pool.map(partial(extract_smile_final,all_total_mols),files_smiles)
        print(time.time()-t)
        t=time.time()
        files = []
        for f in glob.glob(file_path+'/'+protein+'/after_iteration/to_dock/smile/*.txt'):
            files.append(f)
        print(len(files))
        if len(files)==0:
            print("Error in address above")
        with closing(Pool(np.min([tot_process,len(files)]))) as pool:
            to_print = pool.map(alternate_concat,files)
            
        with open(file_path+'/'+protein+'/after_iteration/to_dock/smile/to_dock_'+str(file_no)+'_smile.txt','w') as ref:
            for file_data in to_print:
                for line in file_data:
                    ref.write(line)
        to_print = []
        print(time.time()-t)
        t=time.time()
        smile_duplicacy(file_path+'/'+protein+'/after_iteration/to_dock/smile/to_dock_'+str(file_no)+'_smile.txt')
        print(time.time()-t)
        with closing(Pool(np.min([tot_process,len(files)]))) as pool:
            pool.map(delete_all,files)
            
    else:
        print('not final')
        t=time.time()
        if len(files)==0:
            return_mols_per_file = []
        else:
            with closing(Pool(np.min([tot_process,len(files)]))) as pool:
                return_mols_per_file = pool.map(get_mol,files)
            print(time.time()-t)
       
        for j in range(3):
            ct = 0
            for i in range(len(return_mols_per_file)):
                ct+=len(return_mols_per_file[i][j])
            print(ct)
        
        for k in range(3):
            t=time.time()
            for i in range(len(return_mols_per_file)):
                for j in range(i+1,len(return_mols_per_file)):
                    for keys in return_mols_per_file[i][k].keys():
                        if keys in return_mols_per_file[j][k]:
                            return_mols_per_file[j][k].pop(keys)
            print(time.time()-t)
        
        for j in range(3):
            ct = 0
            for i in range(len(return_mols_per_file)):
                ct+=len(return_mols_per_file[i][j])
            print(ct)
        
        train = {}
        valid = {}
        test = {}
        for j in range(3):
            for i in range(len(return_mols_per_file)):
                for keys in return_mols_per_file[i][j]:
                    if j==0:
                        train[keys] = 0
                    elif j==1:
                        valid[keys] = 0
                    elif j==2:
                        test[keys] = 0
        
        all_train = {}
        all_valid = {}
        all_test = {}
        with open(file_path+'/'+protein+"/iteration_"+str(n_it)+"/train_set.txt",'r') as ref:
            for line in ref:
                all_train[line.rstrip()] = 0

        with open(file_path+'/'+protein+"/iteration_"+str(n_it)+"/valid_set.txt",'r') as ref:
            for line in ref:
                all_valid[line.rstrip()] = 0
        
        with open(file_path+'/'+protein+"/iteration_"+str(n_it)+"/test_set.txt",'r') as ref:
            for line in ref:
                all_test[line.rstrip()] = 0
        
        for keys in train.keys():
            all_train.pop(keys)

        for keys in valid.keys():
            all_valid.pop(keys)

        for keys in test.keys():
            all_test.pop(keys)
        
        print(len(all_train),len(all_valid),len(all_test))

        t=time.time()
        with closing(Pool(np.min([tot_process,len(files_smiles)]))) as pool:
            pool.map(partial(extract_smile,train=all_train,valid=all_valid,test=all_test),files_smiles)
        print(time.time()-t)
        
        
        all_to_delete = []
        for type_to in ['train','valid','test']:
            t=time.time()
            files = []
            for f in glob.glob(file_path+'/'+protein+'/iteration_'+str(n_it)+'/smile/'+type_to+'*'):
                files.append(f)
                all_to_delete.append(f)
            print(len(files))
            if len(files)==0:
                print("Error in address above")
                break
            with closing(Pool(np.min([tot_process,len(files)]))) as pool:
                to_print = pool.map(alternate_concat,files)
            with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/smile/'+type_to+'_smiles_final.csv','w') as ref:
                for file_data in to_print:
                    for line in file_data:
                        ref.write(line)
            to_print = []
            print(type_to,time.time()-t)
        
        f_names = []
        for f in glob.glob(file_path+'/'+protein+'/iteration_'+str(n_it)+'/smile/*final*'):
            f_names.append(f)

        t=time.time()
        with closing(Pool(np.min([tot_process,len(f_names)]))) as pool:
            pool.map(smile_duplicacy,f_names)
        print(time.time()-t)

        with closing(Pool(np.min([tot_process,len(all_to_delete)]))) as pool:
            pool.map(delete_all,all_to_delete)
        
