import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-up','--url_path',required=True)
parser.add_argument('-fp','--folder_path',required=True)
parser.add_argument('-fn','--folder_name',required=True)
parser.add_argument('-tp','--t_pos',required=True)

io_args = parser.parse_args()
up = io_args.url_path
fp = io_args.folder_path
fn = io_args.folder_name
t_pos = int(io_args.t_pos)

import wget
import multiprocessing
from multiprocessing import Pool, Process, Array
from contextlib import closing
from functools import partial
import urllib, time
import os
import numpy as np

def down_file(url):
    if os.path.isfile(fp+'/'+fn+'/'+url.split('/')[-1]):
        return 0
    else:
        try:
            wget.download(url,fp+'/'+fn+'/'+url.split('/')[-1])
        except urllib.error.HTTPError:
            with open(fp+'/'+fn+'/'+'files_not_found.csv','a') as ref:
                ref.write(url+'\n')

if __name__=='__main__':
    url_links = []
    with open(up,'r') as ref:
        for line in ref:
            url_links.append(line.rstrip())
    try:
        os.mkdir(fp+'/'+fn)
    except:
        pass
    t=time.time()
    with closing(Pool(np.min([multiprocessing.cpu_count(),t_pos]))) as pool:
        pool.map(down_file,url_links)
    print(time.time()-t)
