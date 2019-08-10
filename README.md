# PD2.0
Speed virtual screening by >50X

Hi everyone! This repo contains all the required codes and step by step information on how to use PD2.0 that we developed to speed the process of virtual screening. With this you can use your desired docking tool and virtually screen entire ZINC15 data base (containing >1.3B molecules) in 1-2 weeks depending on the resources you have at your disposal. We were able to screen 570 million 3D ZINC15 molecules using 60 CPU cores and 4 GPUs in about 2 weeks. For further information please refer to our [paper](https://www.google.com).

Before you start there are certain files that are required:

- Virtual environment with python3, [RDKIT](https://www.rdkit.org/docs/Install.html) and wget (inside the environment: pip install wget) installed
- Virtual environment with python3, tensorflow-gpu (pip install tensorflow_gpu), pandas (pip install pandas), numpy (pip install numpy), keras (pip install keras), matplotlib (pip install matplotlib) and sklearn (pip install scikit-learn) installed 
- smiles for the entire database such as ZINC15. To get all the smiles of ZINC15 databae go [here](https://zinc15.docking.org/tranches/home/) and download 2D smiles (.smi) in url format. Ones you have all the urls in a text file do the following:
    - activate the rdkit environent (conda activate environment_name)
    - run "python pd_python/download_zinc15.py -up url_file_path -fp path_where_you_want_smile_folder -fn name_of_smile_folder -tp num_cpus"
    - This can take few hours.
    - This will take ~84GB memory for 1.3 billion molecules.

- Now you need to get the Morgan descriptors for all the ZINC files. For this do the following:
   -  activate the rdkit environent (conda activate environment_name)
   -  run "python pd_python/Morgan_fing.py -sfp path_to_smile_folder -fp path_where_you_want_morgan_folder -fn name_of_morgan_folder -tp num_cpus"
   - Use as many CPUs as possible to speed the process, it can take more than 1 day to finish (depending on the number of molecules).
   - It will take ~260GB memory for 1.3 billion molecules.

There are 5 phases to the method:

1) Random sampling a fixed number of molecules (e.g. 3M) from 
