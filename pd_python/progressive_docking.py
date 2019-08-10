import pandas as pd
import time
import numpy as np
import tensorflow as tf
from keras.layers import Input,Dense,Activation,BatchNormalization,Dropout
from keras.models import Model,Sequential
from keras import optimizers
from keras.callbacks import EarlyStopping,Callback
import matplotlib
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import keras.backend as K
import tensorflow as tf
import argparse
from keras.utils.training_utils import multi_gpu_model
from tensorflow.python.client import device_lib
from keras import regularizers
from keras import metrics
#import keras_metrics
from keras.models import model_from_json
from sklearn.metrics import auc
from sklearn.metrics import precision_recall_curve,roc_curve,fbeta_score
from keras.layers.normalization import BatchNormalization
import random
import glob
import os,sys

parser = argparse.ArgumentParser()
parser.add_argument('-num_units','--nu',required=True)
parser.add_argument('-dropout','--df',required=True)
parser.add_argument('-learn_rate','--lr',required=True)
parser.add_argument('-bin_array','--ba',required=True)
parser.add_argument('-wt','--wt',required=True)
parser.add_argument('-cf','--cf',required=True)
parser.add_argument('-n_it','--n_it',required=True)
parser.add_argument('-t_mol','--t_mol',required=True)
parser.add_argument('-bs','--bs',required=True)
parser.add_argument('-os','--os',required=True)
parser.add_argument('-protein','--protein',required=True)
parser.add_argument('-file_path','--file_path',required=True)

io_args = parser.parse_args()


nu = int(io_args.nu)
df=float(io_args.df)
lr=float(io_args.lr)
ba=int(io_args.ba)
wt=float(io_args.wt)
cf=float(io_args.cf)
n_it=int(io_args.n_it)
bs=int(io_args.bs)
oss=int(io_args.os)
t_mol=float(io_args.t_mol)
protein = io_args.protein
file_path = io_args.file_path
print(nu,df,lr,ba,wt,cf,bs,oss,protein,file_path)

def get_x_data(Oversampled_zid,fname):
    #train_set = np.zeros([1000000,1024])
    #train_id = []
    with open(fname,'r') as ref:
        no=0
        for line in ref:
            tmp=line.rstrip().split(',')
            if tmp[0] in Oversampled_zid.keys():
                if type(Oversampled_zid[tmp[0]])!=np.ndarray:
                    train_set = np.zeros([1,1024])
                    on_bit_vector = tmp[1:]
                    for elem in on_bit_vector:
                        train_set[0,int(elem)] = 1
                    Oversampled_zid[tmp[0]] = np.repeat(train_set,Oversampled_zid[tmp[0]],axis=0)
                    
def get_all_x_data(fname,y):
    train_set = np.zeros([1000000,1024])
    train_id = []
    with open(fname,'r') as ref:
        no=0
        for line in ref:
            tmp=line.rstrip().split(',')
            train_id.append(tmp[0])
            on_bit_vector = tmp[1:]
            for elem in on_bit_vector:
                train_set[no,int(elem)] = 1
            no+=1
        train_set = train_set[:no,:]
    train_pd = pd.DataFrame(data=train_set)
    train_pd['ZINC_ID'] = train_id
    if len(y.columns)!=2:
        y.reset_index(level=0,inplace=True)
    else:
        print('already 2 columns: ',fname)
    score_col = y.columns.difference(['ZINC_ID'])[0]
    #y['ZINC_ID'] = y.index
    train_data = pd.merge(y,train_pd,how='inner',on=['ZINC_ID'])
    X_train = train_data[train_data.columns.difference(['ZINC_ID',score_col])].values
    y_train = train_data[[score_col]].values
    return X_train,y_train




prefix = ['_morgan_1024_updated.csv']
prefix_label = ['']
n_iteration = n_it
total_mols = t_mol

try:
    os.mkdir(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/all_models')
except:
    pass

is_v2 = False
#X_old_full = []
#y_old_full = []
for i in range(1,n_iteration):
    try:
        train_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(i)+'/morgan/train'+prefix[0],header=None,usecols=[0])
    except:
        train_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(i)+'/morgan/train'+prefix[0],header=None,usecols=[0],engine='python')
        try:
            if 'ZINC' in train_pd.index[0]:
                train_pd = pd.DataFrame(data=train_pd.index)
        except:
            pass
    train_pd.columns= ['ZINC_ID']
    try:
        valid_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(i)+'/morgan/valid'+prefix[0],header=None,usecols=[0])
    except:
        valid_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(i)+'/morgan/valid'+prefix[0],header=None,usecols=[0],engine='python')
        try:
            if 'ZINC' in valid_pd.index[0]:
                valid_pd = pd.DataFrame(data=valid_pd.index)
        except:
            pass
    valid_pd.columns= ['ZINC_ID']
    try:
        test_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(i)+'/morgan/test'+prefix[0],header=None,usecols=[0])
    except:
        test_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(i)+'/morgan/test'+prefix[0],header=None,usecols=[0],engine='python')
        try:
            if 'ZINC' in test_pd.index[0]:    
                test_pd = pd.DataFrame(data=test_pd.index)
        except:
            pass
    test_pd.columns= ['ZINC_ID']
    
    test_label = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(i)+'/testing_labels'+prefix_label[0]+'.txt',sep=',',header=0)
    train_label = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(i)+'/training_labels'+prefix_label[0]+'.txt',sep=',',header=0)
    valid_label = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(i)+'/validation_labels'+prefix_label[0]+'.txt',sep=',',header=0)


    train_data = pd.merge(train_label,train_pd,how='inner',on=['ZINC_ID'])
    validation_data = pd.merge(valid_label,valid_pd,how='inner',on=['ZINC_ID'])
    train_data.set_index('ZINC_ID',inplace=True)
    validation_data.set_index('ZINC_ID',inplace=True)
    test_data = pd.merge(test_label,test_pd,how='inner',on=['ZINC_ID'])
    test_data.set_index('ZINC_ID',inplace=True)
    #test_set = []
    #test_id = []
    test_pd = []
    test_label = []
    #train_set = []
    #valid_set = []
    #train_id = []
    #valid_id = []
    train_pd = []
    valid_pd = []
    train_label = []
    valid_label = []
    
    y_train = train_data<cf
    y_valid = validation_data<cf
    y_test = test_data<cf
    
    train_data = []
    validation_data = []
    test_data = []
    
    print(y_train.shape,y_valid.shape,y_test.shape)
    if i==1:
        y_test_fn = y_test
        y_valid_fn = y_valid
        print(int(y_valid.sum()))
        if int(y_valid.sum())<=10000:
            y_test_fn_2 = y_train
            is_v2 = True
            y_old = []
        else:
            y_old = y_train
    else:
        y_old = pd.concat((y_train,y_valid,y_test),axis=0)
    try:
        y_old_full = pd.concat([y_old,y_old_full],axis=0)
        print(y_old_full.shape)
    except:
        y_old_full = y_old
    y_train = []
    y_valid = []
    y_test = []
    y_old = []

try:
    train_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/morgan/train'+prefix[0],header=None,usecols=[0])
except:
    train_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/morgan/train'+prefix[0],header=None,usecols=[0],engine='python')
    try:
        if 'ZINC' in train_pd.index[0]:
            train_pd = pd.DataFrame(data=train_pd.index)
    except:
        pass
train_pd.columns= ['ZINC_ID']
try:
    valid_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/morgan/valid'+prefix[0],header=None,usecols=[0])
except:
    valid_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/morgan/valid'+prefix[0],header=None,usecols=[0],engine='python')
    try:
        if 'ZINC' in valid_pd.index[0]:
            valid_pd = pd.DataFrame(data=valid_pd.index)
    except:
        pass
valid_pd.columns= ['ZINC_ID']
try:
    test_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/morgan/test'+prefix[0],header=None,usecols=[0])
except:
    test_pd = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/morgan/test'+prefix[0],header=None,usecols=[0],engine='python')
    try:
        if 'ZINC' in test_pd.index[0]:
            test_pd = pd.DataFrame(data=test_pd.index)
    except:
        pass
test_pd.columns= ['ZINC_ID']
train_label = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/training_labels'+prefix_label[0]+'.txt',sep=',',header=0)
valid_label = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/validation_labels'+prefix_label[0]+'.txt',sep=',',header=0)
test_label = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/testing_labels'+prefix_label[0]+'.txt',sep=',',header=0)
train_data = pd.merge(train_label,train_pd,how='inner',on=['ZINC_ID'])
validation_data = pd.merge(valid_label,valid_pd,how='inner',on=['ZINC_ID'])
train_data.set_index('ZINC_ID',inplace=True)
validation_data.set_index('ZINC_ID',inplace=True)
test_data = pd.merge(test_label,test_pd,how='inner',on=['ZINC_ID'])
test_data.set_index('ZINC_ID',inplace=True)

train_pd = []
valid_pd = []
test_pd = []
train_label = []
valid_label = []
test_label = []

print(train_data.shape,validation_data.shape,test_data.shape)

y_train = train_data<cf
y_valid = validation_data<cf
y_test = test_data<cf

train_data = []
validation_data = []
test_data = []

if n_iteration==1:
    y_train = y_train
    y_valid = y_valid
    y_test = y_test
else:
    y_train = pd.concat([y_train,y_test,y_valid],axis=0)
    y_valid = y_valid_fn
    y_test = y_test_fn

t_train_mol = len(y_train)
pos_ct_orig = y_train.r_i_docking_score.sum()

print(y_train.shape)

if y_valid.sum().values<=10:
    sys.exit()

if y_test.sum().values<=10:
    sys.exit()

try:
    y_train = pd.concat([y_train,y_old_full])
except:
    pass

print(y_train.shape)

y_pos = y_train[y_train.r_i_docking_score==1]
y_neg = y_train[y_train.r_i_docking_score==0]


neg_ct = y_neg.shape[0]
pos_ct = y_pos.shape[0]

print(pos_ct,pos_ct_orig,neg_ct)

#sample_size = np.min([neg_ct,pos_ct*oss])

sample_size = np.min([neg_ct,125000,pos_ct*oss])

print(sample_size)

Oversampled_zid = {}
Oversampled_zid_y = {}
for i in range(sample_size):
    idx = random.randint(0,pos_ct-1)
    idx_neg = random.randint(0,neg_ct-1)
    try:
        Oversampled_zid[y_pos.index[idx]] +=1
    except:
        Oversampled_zid[y_pos.index[idx]] = 1
        Oversampled_zid_y[y_pos.index[idx]] = 1
    try:
        Oversampled_zid[y_neg.index[idx_neg]] +=1
    except:
        Oversampled_zid[y_neg.index[idx_neg]] = 1
        Oversampled_zid_y[y_neg.index[idx_neg]] = 0
y_pos = []
y_neg = []

#y_valid_temp = y_valid
print(y_valid.shape)
for i in range(n_iteration):
    for f in glob.glob(file_path+'/'+protein+'/iteration_'+str(i+1)+'/morgan/*'):
        if i==0:
            if f.split('/')[-1].split('_')[0]=='valid':
                X_valid,y_valid = get_all_x_data(f,y_valid)
            elif f.split('/')[-1].split('_')[0]=='test':
                X_test,y_test = get_all_x_data(f,y_test)
            else:
                if is_v2:
                    print('Its V2')
                    X_test_2,y_test_2 = get_all_x_data(f,y_test_fn_2) 
                else:
                    get_x_data(Oversampled_zid,f)
        else:
            get_x_data(Oversampled_zid,f)

#if is_v2:
#    print(X_valid.shape,X_valid_2.shape)
#    X_valid = np.concatenate([X_valid,X_valid_2])
#    y_valid = np.concatenate([y_valid,y_valid_2])
#    print(y_valid.shape)

#y_valid_temp = []
#X_valid_2 = []
#y_valid_2 = []

ct= 0 
Oversampled_X_train = np.zeros([sample_size*2,1024])
Oversampled_y_train = np.zeros([sample_size*2,1])
for keys in Oversampled_zid.keys():
    tt = len(Oversampled_zid[keys])
    Oversampled_X_train[ct:ct+tt] = Oversampled_zid[keys]
    Oversampled_y_train[ct:ct+tt] = Oversampled_zid_y[keys]
    ct +=tt
    
try:
    print(Oversampled_X_train.shape,Oversampled_y_train.shape,X_valid.shape,y_valid.shape,X_test.shape,y_test.shape)
except:
    print(Oversampled_X_train.shape,Oversampled_y_train.shape,X_valid.shape,y_valid.shape)
    

from keras.callbacks import Callback
class TimedStopping(Callback):
    '''Stop training when enough time has passed.
    # Arguments
        seconds: maximum time before stopping.
        verbose: verbosity mode.
    '''
    def __init__(self, seconds=None, verbose=1):
        super(Callback, self).__init__()

        self.start_time = 0
        self.seconds = seconds
        self.verbose = verbose

    def on_train_begin(self, logs={}):
        self.start_time = time.time()

    def on_epoch_end(self, epoch, logs={}):
        print('epoch done')
        if time.time() - self.start_time > self.seconds:
            self.model.stop_training = True
            if self.verbose:
                print('Stopping after %s seconds.' % self.seconds)
    

def Progressive_Docking(input_shape,num_units=32,bin_array=[0,1,0],dropoutfreq=0.8):
    X_input = Input(input_shape)
    X = X_input
    for j,i in enumerate(bin_array):
        if i==0:
            X = Dense(num_units,name="Hidden_Layer_%i"%(j+1))(X)
            X = BatchNormalization()(X)
            X = Activation('relu')(X)
        else:
            X = Dropout(dropoutfreq)(X)
    X = Dense(1,activation='sigmoid',name="Output_Layer")(X)
    model = Model(inputs = X_input,outputs=X,name='Progressive_Docking')
    return model

progressive_docking = Progressive_Docking(Oversampled_X_train.shape[1:],num_units=nu,bin_array=ba*[0,1],dropoutfreq=df)

adam_opt = tf.train.AdamOptimizer(learning_rate=lr,epsilon=1e-06)
progressive_docking.compile(optimizer=adam_opt,loss='binary_crossentropy',metrics=['accuracy'])

es = EarlyStopping(monitor='val_loss',min_delta=0,patience=10,verbose=0,mode='auto')
es1 = TimedStopping(seconds=10800)
cw = {0:wt,1:1}

progressive_docking.fit(Oversampled_X_train,Oversampled_y_train,epochs=500,batch_size=bs,shuffle=True,class_weight=cw,verbose=1,validation_data=[X_valid,y_valid],callbacks=[es,es1])

#prediction_train = progressive_docking.predict(X_train)
if is_v2:
    print('using train as validation')
    prediction_valid = progressive_docking.predict(X_test_2)
    precision_vl, recall_vl, thresholds_vl = precision_recall_curve(y_test_2,prediction_valid)
    fpr_vl, tpr_vl, thresh_vl = roc_curve(y_test_2, prediction_valid)
    auc_vl = auc(fpr_vl,tpr_vl)
    pr_vl = precision_vl[np.where(recall_vl>0.9)[0][-1]]
    pos_ct_orig = np.sum(y_test_2)
    Total_left = 0.9*total_mols/pr_vl*pos_ct_orig/len(y_test_2)*1000000
    tr = thresholds_vl[np.where(recall_vl>0.90)[0][-1]]
else:
    print('using valid as validation')
    prediction_valid = progressive_docking.predict(X_valid)
    precision_vl, recall_vl, thresholds_vl = precision_recall_curve(y_valid,prediction_valid)
    fpr_vl, tpr_vl, thresh_vl = roc_curve(y_valid, prediction_valid)
    auc_vl = auc(fpr_vl,tpr_vl)
    pr_vl = precision_vl[np.where(recall_vl>0.9)[0][-1]]
    pos_ct_orig = np.sum(y_valid)
    Total_left = 0.9*pos_ct_orig/pr_vl*total_mols*1000000/len(y_valid)
    tr = thresholds_vl[np.where(recall_vl>0.90)[0][-1]]

try:
    with open(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/model_no.txt','r') as ref:
        mn = int(ref.readline().rstrip())+1
    with open(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/model_no.txt','w') as ref:
        ref.write(str(mn))
except:
    mn = 1
    with open(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/model_no.txt','w') as ref:
        ref.write(str(mn))


with open(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/all_models/model_'+str(mn)+'.json','w') as ref:
    ref.write(progressive_docking.to_json())
progressive_docking.save_weights(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/all_models/model_'+str(mn)+'_weights.h5')

prediction_test = progressive_docking.predict(X_test)
precision_te, recall_te, thresholds_te = precision_recall_curve(y_test,prediction_test)
fpr_te, tpr_te, thresh_te = roc_curve(y_test, prediction_test)
auc_te = auc(fpr_te,tpr_te)
pr_te = precision_te[np.where(thresholds_te>tr)[0][0]]
re_te = recall_te[np.where(thresholds_te>tr)[0][0]]
pos_ct_orig = np.sum(y_test)
Total_left_te = re_te*pos_ct_orig/pr_te*total_mols*1000000/len(y_test)
with open(file_path+'/'+protein+'/iteration_'+str(n_iteration)+'/hyperparameter_morgan_with_freq_v3.csv','a') as ref:
    ref.write(str(mn)+','+str(oss)+','+str(bs)+','+str(lr)+','+str(ba)+','+str(nu)+','+str(df)+','+str(wt)+','+str(cf)+','+str(auc_vl)+','+str(pr_vl)+','+str(Total_left)+','+str(auc_te)+','+str(pr_te)+','+str(re_te)+','+str(Total_left_te)+','+str(pos_ct_orig)+'\n')

