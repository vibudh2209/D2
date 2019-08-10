# PD2.0
Speed virtual screening by >50X

Hi everyone! This repo contains all the required codes and step by step information on how to use PD2.0 that we developed to speed the process of virtual screening. With this you can use your desired docking tool and virtually screen entire ZINC15 data base (containing >1.3B molecules) in 1-2 weeks depending on the resources you have at your disposal. We were able to screen 570 million 3D ZINC15 molecules using 60 CPU cores and 4 GPUs in about 2 weeks. For further information please refer to our [paper](https://www.google.com).

Before you start there are certain files that are required:

- smiles for the entire database such as ZINC15. To get all the smiles of ZINC15 databae go [here](https://zinc15.docking.org/tranches/home/) and download 2D smiles (.smi).

- Now you need to get the Morgan descriptors for all the ZINC files. For this do the following:
   -  efjfrwjfn 

There are 5 phases to the method:

1) Random sampling a fixed number of molecules (e.g. 3M) from 
