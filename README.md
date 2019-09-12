# Progressive Docking 2.0 – Accelerate Virtual Screening by 50X 

Progressive docking 2.0 (PD2.0) is a deep learning-based tool that we developed to accelerate docking-based virtual screening. In this repository you can find all what you need to screen extra-large chemical libraries such as ZINC15 database (containing >1.3B molecules) using your favourite docking program in 1-2 weeks depending on the resources available to you. By using PD2.0 we were able to screen 570 million molecules from ZINC15 using 60 CPU cores and 4 GPUs in about 2 weeks. For further information please refer to our [paper](https://www.google.com/).

Prerequisites
-------------

The following are the minimal prerequisites needed for running PD2.0:
- Package installer for python [pip](https://pypi.org/project/pip/)
- [Anaconda](https://www.anaconda.com/distribution/)
- Virtual environment with python3. Within the environment install [rdkit](https://rdkit.readthedocs.io/en/latest/Install.html#how-to-get-conda) and wget (pip install wget)
- Virtual environment (different from previous one) with python3. Within the environment install tensorflow-gpu (pip install tensorflow_gpu), pandas (pip install pandas), numpy (pip install numpy), keras (pip install keras), matplotlib (pip install matplotlib) and sklearn (pip install scikit-learn)
- A program to create 3D conformations from SMILES
- Docking program 

Download and prepare compounds for PD2.0
----------------------------------------

To run PD2.0 you need to download the SMILES of the compounds and calculate the Morgan fingerprints for all of them. 

**SMILES**

- Download the SMILES for all the molecules from database. For large databases, SMILES are usually downloaded in url format. For example, to get all the SMILES of ZINC15 database go [here](https://zinc15.docking.org/tranches/home/) and download the 2D SMILES (.smi) in url format
- Activate the rdkit environment (conda activate environment_name)
- Run the following command

          python pd_python/download_zinc15.py -up url_file_path -fp destination_path -fn name_of_smile_folder -tp num_cpus

This step can take few hours, and ~84GB memory for 1.3 billion molecules. Please not that this step will download SMILES from ZINC15. You can skip this step if you have already the database in SMILES format, or if you want to use a different database than ZINC15.


**SMILES simplification**

- In case there are too many smile files and you want to decrease the number and have similar number of molecules in each file
- Activate tensorflow environment
- Run the following command

          python pd_python/smile_simplification.py -sfp smile_folder -tp num_cpus -tn total_number_of_files


**MORGAN FINGERPRINTS**

- To calculate the Morgan descriptors for all the SMILES activate the rdkit environment (conda activate environment_name)
- Run the following command

          python pd_python/Morgan_fing.py -sfp path_to_smile_folder -fp path_where_you_want_morgan_folder -fn name_of_morgan_folder -tp num_cpus

- Use as many CPUs as possible to speed the process. It can take more than 1 day to finish (depending on the number of molecules)
This step will take ~260GB memory for 1.3 billion molecules.

Run PD2.0
---------

Before starting PD2.0, create a folder with the name of the target. Create a text file named "logs.txt" inside it, following this [format](temp/logs.txt). PD2.0 is divided in 5 sequential phases to be repeated over multiple iterations until a desired number of final predicted good molecules is reached (for more details please check the example folder):

**Phase 1.** *Random sampling of a fixed number of molecules (e.g. 3 millions) from the entire dataset, getting the Morgan fingerprint and the SMILES*
1. The number of molecules to be sampled is defined in the logs.txt file. As these molecules will be docked later, set the number of molecules based on the computational power available to you. For iteration 1 try to keep the number as high as possible (you can decrease it for later iterations)
2. Run phase 1:
    
          bash pd_python/phase_1.sh iteration_no n_cpus path_to_log_file path_to_tensorflow_venv

**Phase 2.** *2D to 3D conversion from SMILES to sdf*\
The three files created in the SMILES folder in phase 1 (train, valid and test) need to be converted to 3D sdf format for docking. This includes assigning protonation states and generate 3D conformations, and can be done with different free (e.g. [openbabel](https://openbabel.org/docs/dev/Command-line_tools/babel.html)) or licensed programs (e.g. [omega](https://www.eyesopen.com/omega)). For example, with OpenEye omega program protonate the molecules using 
        
          fixpka -in in_file.smi -out output_file.smi

and convert the obtained smi file to sdf by running
                                        
          oeomega classic -in file_after_protonation.smi -out name_of_sdf_file.sdf -maxconfs 1 -strictstereo false -mpi_np number_of_cpus -log log_file_name.log -prefix prefix_name
                                       
This phase will take >4-5 hours using 20 CPUs for 1 million molecules. Note that you may want to create more than 1 conformation per molecule depending on the docking software.

**Phase 3.** *Molecular docking*
1. Run docking for the three compound sets (training, validation and testing)
2. From the docking results create three **csv** files with two columns, *ZINC_ID*, *r_i_docking_score* (use these exact headings):
    - ZINC_ID column will have IDs of the molecules (use the same heading even if you are not screening ZINC)
    - r_i_docking_score will have the docking score values 
3. Name the csv files as training_labels.txt, validation_labels.txt, testing_labels.txt
4. Put the three files in the respective iteration folder

**Phase 4.** *Training of neural networks models*
1. To generate bash files with different hyperparameters activate the tensorflow environment and run
     
          python simple_job_models_noslurm.py -n_it iteration_no -mdd morgan_directory_path -time training_time -protein protein_name -file_path path_to_protein_folder -pdfp pd_python_folder_path -tfp tensorflow_venv_path -min_last minimum_molecules_at_last_iteration

2. For training time, specify a value between 1 and 2 (1 to 2 hours)
3. For minimum_molecules_at_last_iteration put something like 100-200 (for details please read the paper, default 200)
4. Execute the 12 bash scripts created in protein_folder_path/protein/iteration_no/simple_job
    
**Phase 5.** *Choice of best hyperparameter and prediction of the entire database*
1. For selecting the best hyperparameter run 
                 
          python hyperparameter_result_evaluation.py -n_it iteration_no -protein protein_name -file_path path_to_protein -mdd morgan_directory_path
                
2. Generate bash files for individual Morgan files (for prediction):

          python simple_job_predictions_noslurm.py -protein protein_name -file_path path_to_protein -n_it iteration_no -mdd morgan_directory
                
3. Execute all the bash scripts in protein_folder_path/protein/iteration_no/simple_job_predictions
4. To check the number of molecules left after each iteration just load the protein_folder_path/protein/iteration_no/morgan_1024_predictions/passed_file_ct.txt and sum the last column. You can compare this number with predicted molecule left: 'protein_folder_path/protein/iteration_no/best_model_stats.txt' and verify whether they are close.

Final iteration
---------------

Repeat the above phases 1-5 for as many iterations as it takes to get a fixed number of final molecules that can be docked (e.g. until final number is <=15 million). You will just need to change the iteration_no value. After the final iteration is done you will dock the molecules predicted by PD2.0. Some of these molecules could have been randomly sampled during the previous iterations and do not need to be docked again:
- Run 

          bash final_phase_noslurm.sh iteration_no number_of_cpus path_to_log_file path_to_tensorflow_venv

- This will create a new folder called after_iteration and put all the already docked molecules inside the docked folder and all the remaining SMILES in to_dock folder
- You can dock the SMILES using the same procedure as step 3

Useful tips
-----------

- In case you are in hurry and want to select top n molecules after an iteration (for example you completed 3 iterations and 30 million molecules are left but you do not want to run another iteration, thus you want to select the predicted top 10 million compounds) run


          python Prediction_morgan_1024_top_n.py -protein protein_name -it iteration_no -file_path path_to_protein -top_n top_n_molecules
