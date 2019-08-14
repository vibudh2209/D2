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
(For more details please check the example folder)

1) Create a folder with the name of the protein and inside it create a text file with name "logs.txt"

    - logs file should look something like [this](temp/logs.txt), one example can be found [here](temp/logs_example.txt)

2) Next step is to start the phase 1 i.e. Random sampling a fixed number of molecules (e.g. 3M) from entire dataset, getting the morgan fingerprint and getting the smiles.

   - Here based on the computational power available change the logs file for number of molecules to be sampled (these same number of molecules will be docked later on). For iteration 1 try to keep the number as high as possible (you can decrease it for later iterations).
   - Run 'bash pd_python/phase_1.sh iteration_no n_cpus path_to_log_file path_to_tensorflow_venv
      
       - This will run all the steps mentioned phase 1.

3) Next is phase 2 which involve converting the smiles to sdf (2D to 3D optimization).
   - There are three files in the smile folder created (train, valid and test). All three needs to be converted to sdf.
   - In case you have openeye do the following:
       - First protonate the molecules using "fixpka -in in_file -out output_file" (will take 5 mins for 1 million molecules)
       - Then convert the file obtained to sdf by "oeomega classic -in file_after_protonation -out name_of_sdf_file.sdf -maxconfs 1 -strictstereo false -mpi_np number_of_cpus -log log_file_name.log -prefix prefix_name" (this will take >4-5 hours using 20 CPUs for one million molecules)

4) Now you have all the required sdf. Dock them with any program of your choice (phase 3).
   - After this you will have 3 docked files one for each training, validation and testing.
   - From these files get the csv file with column names: ZINC_ID, r_i_docking_score
       - ZINC_ID column will have ids of the molecule
       - r_i_docking_score will have docking score values of these molecules
   - name the csv files: training_labels.txt, validation_labels.txt, testing_labels.txt
   - place these three files in the respective iteration folder

5) Next is the phase 4, here we have to train simple NN models and chose the best one to predict on all.
   - First is to generate bash files that have different hyperparamaeters.
       - activate the tensorflow environemnt
       - run 'python simple_job_models_noslurm.py -n_it iteration_no -mdd morgan_directory_path -time training_time(1-2hrs) -protein protein_name -file_path path_to_protein_folder -pdfp pd_python_folder_path -tfp tensorflow_venv_path
   - Now go to the following path: protein_folder_path/protein/iteration_no/simple_job
   - There will be 12 bash scripts created here, run them

6) Next step is chose the best hyperparameter and predict on entire database:
   - For selecting the best hyperparameter run: 'python hyperparameter_result_evaluation.py -n_it iteration_no -protein protein_name -file_path path_to_protein -mdd morgan_directory_path
   - Next is to generate bash files for individual morgan files (for prediction):
       - run 'python simple_job_predictions.py -protein protein_name -file_path path_to_protein -n_it iteration_no -mdd morgan_directory
   - Now go to the following path: protein_folder_path/protein/iteration_no/simple_job_predictions
   - Run all the bash scripts

7) To check the number of molecules left after each iteration just load the: 'protein_folder_path/protein/iteration_no/morgan_1024_predictions/passed_file_ct.txt' and sum the last column. You can compare this number with predicted molecule left: 'protein_folder_path/protein/iteration_no/best_model_stats.txt' and verify whether they are close.

8) Repeat the abouve steps 1-7 for as many iterations as it takes to get some fixed number of final molecules (in our case we were running until final number is <=15 million)

9) In case you are in hurry and want to select top n molecules after some iteration (for example you are done with 3 iterations and 30 million molecules are left but you dont want to run another iteration but select the top 10 million compounds) run: 'python Prediction_morgan_1024_top_n.py -protein protein_name -it iteration_no -file_path path_to_protein -top_n top_n_molecules'

10) Now after the final iteration is done/you have selected top n molecules, to get the smiles for all the left do the following:
   - Out of the left we will segregate the ones which are already docked and the ones which needs to be docked.
   - Run: 'bash final_phase_noslurm.sh iteration_no number_of_cpus path_to_log_file path_to_tensorflow_venv'
   - This will create new folder after_iteration and put all the already docked files inside docked folder and all the smiles in to_dock folder.

11) You can dock the smiles using the same procedure as step 3  
