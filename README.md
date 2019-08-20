# Progressive Docking 2.0 – accelerate virtual screening by 50X 

Progressive docking 2.0 (PD2.0) is a deep learning-based tool that we developed to accelerate docking-based virtual screening. In this repository you can find all what you need to screen extra-large chemical libraries such as ZINC15 database (containing >1.3B molecules) using your favourite docking program in 1-2 weeks depending on the resources available to you. By using PD2.0 we were able to screen 570 million molecules from ZINC15 using 60 CPU cores and 4 GPUs in about 2 weeks. For further information please refer to our [paper](https://www.google.com/).

Prerequisites
-------------

The following are the minimal prerequisites needed for running PD2.0:
- Package installer for python [pip](https://pypi.org/project/pip/)
- [Anaconda](https://www.anaconda.com/distribution/)
- Virtual environment with python3. Within the environment install [rdkit](https://rdkit.readthedocs.io/en/latest/Install.html#how-to-get-conda) and wget (pip install wget)
- Virtual environment (different from previous one) with python3. Within the environment install tensorflow-gpu (pip install tensorflow_gpu), pandas (pip install pandas), numpy (pip install numpy), keras (pip install keras), matplotlib (pip install matplotlib) and sklearn (pip install scikit-learn)
- A program to create 3D conformations from SMILES (e.g. OpenEye [omega](https://www.eyesopen.com/omega), [openbabel](https://open-babel.readthedocs.io/en/latest/3DStructureGen/Overview.html)
- Docking program 

Download and prepare compounds for PD2.0
----------------------------------------

To run PD2.0 you need to download the SMILES of the compounds and calculate the Morgan fingerprints for all of them. 

**SMILES**

- Download the SMILES for all the molecules from the database. For large databases, SMILES are usually downloaded in url format. For example, to get all the SMILES of ZINC15 database go [here](https://zinc15.docking.org/tranches/home/) and download the 2D SMILES (.smi) in url format.
- Activate the rdkit environment (conda activate environment_name)
- Run the following command

         python pd_python/download_zinc15.py -up url_file_path -fp destination_path -fn name_of_smile_folder -tp num_cpus

- This step can take few hours, and ~84GB memory for 1.3 billion molecules

**MORGAN FINGERPRINTS**

- To calculate the Morgan descriptors for all the SMILES activate the rdkit environent (conda activate environment_name)
- Run the following command

              python pd_python/Morgan_fing.py -sfp path_to_smile_folder -fp path_where_you_want_morgan_folder -fn name_of_morgan_folder -tp num_cpus
- Use as many CPUs as possible to speed the process. It can take more than 1 day to finish (depending on the number of molecules)
- This step will take ~260GB memory for 1.3 billion molecules

Run PD2.0
---------

PD2.0 is divided in 5 sequential phases (for more details please check the example folder):
0.	Create a folder with the name of the target and a text file named "logs.txt" inside it
   - logs file should follow this format. An example can be found here
1.	Phase 1: random sampling of a fixed number of molecules (e.g. 3 millions) from the entire dataset, getting the Morgan fingerprint and the SMILES
•	Here based on the computational power available change the logs file for number of molecules to be sampled (these same number of molecules will be docked later on). For iteration 1 try to keep the number as high as possible (you can decrease it for later iterations)
•	Run 
bash pd_python/phase_1.sh iteration_no n_cpus path_to_log_file path_to_tensorflow_venv
	This will run all the steps mentioned phase 1
2.	Phase 2: conversion from SMILES to sdf (2D to 3D )
•	The three files created in the SMILES folder (train, valid and test) need to be converted to sdf 3D format for docking
•	Assign protonation states and generate 3D conformations. For example, with OpenEye program suite:
	Protonate the molecules using 
fixpka -in in_file.smi -out output_file.smi
	It will take 5 mins for 1 million molecules on one CPU
	Convert the smi file obtained to sdf by running
oeomega classic -in file_after_protonation.smi -out name_of_sdf_file.sdf -maxconfs 1 -strictstereo false -mpi_np number_of_cpus -log log_file_name.log -prefix prefix_name 
	This will take >4-5 hours using 20 CPUs for one million molecules)
	Depending on the docking program, you may want to generate more than 1 conformation per molecule
3.	Phase 3: molecular docking 
•	Perform docking of the three sets with your program of choice (training, validation and testing)
•	From the docking files get three csv files with column names: ZINC_ID, r_i_docking_score
	ZINC_ID column will have IDs of the molecule
	r_i_docking_score will have docking score values 
•	name the csv files as training_labels.txt, validation_labels.txt, testing_labels.txt
•	place these three files in the respective iteration folder
4.	Phase 4: training of simple neural networks models and choice of best model to predict all molecules
•	First, generate bash files that have different hyperparameters
	Activate the tensorflow environment
	Run 
python simple_job_models_noslurm.py -n_it iteration_no -mdd morgan_directory_path -time training_time(1-2hrs) -protein protein_name -file_path path_to_protein_folder -pdfp pd_python_folder_path -tfp tensorflow_venv_path
•	Now go to the following path: protein_folder_path/protein/iteration_no/simple_job
•	There will be 12 bash scripts created here, run them
5.	Next step is chose the best hyperparameter and predict on entire database:
•	For selecting the best hyperparameter run 
python hyperparameter_result_evaluation.py -n_it iteration_no -protein protein_name -file_path path_to_protein -mdd morgan_directory_path
•	Generate bash files for individual Morgan files (for prediction):
	Run 
python simple_job_predictions.py -protein protein_name -file_path path_to_protein -n_it iteration_no -mdd morgan_directory
•	Now go to the following path: protein_folder_path/protein/iteration_no/simple_job_predictions
•	Run all the bash scripts
6.	To check the number of molecules left after each iteration just load the: 'protein_folder_path/protein/iteration_no/morgan_1024_predictions/passed_file_ct.txt' and sum the last column. You can compare this number with predicted molecule left: 'protein_folder_path/protein/iteration_no/best_model_stats.txt' and verify whether they are close.
7.	Repeat the abouve steps 1-7 for as many iterations as it takes to get a fixed number of final molecules that can be docked (e.g. until final number is <=15 million)
8.	In case you are in hurry and want to select top n molecules after an iteration (for example you are done with 3 iterations and 30 million molecules are left but you do not want to run another iteration, selecting the top 10 million compounds) run:
python Prediction_morgan_1024_top_n.py -protein protein_name -it iteration_no -file_path path_to_protein -top_n top_n_molecules
9.	After the final iteration is done and you have selected top n molecules, to get the SMILES for all the left compounds in the database do the following:
•	Out of the left we will segregate the ones which are already docked and the ones which needs to be docked.
•	Run: 
bash final_phase_noslurm.sh iteration_no number_of_cpus path_to_log_file path_to_tensorflow_venv
•	This will create new folder after_iteration and put all the already docked files inside docked folder and all the SMILES in to_dock folder.
11.	You can dock the SMILES using the same procedure as step 3

