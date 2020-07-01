# Deep Docking – Accelerate Virtual Screening by 50X 


Deep docking (DD) is a deep learning-based tool developed to accelerate docking-based virtual screening. In this repository you can find all what you need to screen ultra-large chemical libraries such as ZINC15 database (containing >1.3 billion molecules) using your favourite docking program. For further information please refer to our [paper](https://pubs.acs.org/doi/10.1021/acscentsci.0c00229). The dataset used for building the models reported in the paper can be found at this [link](https://drive.google.com/file/d/1w86NqUk7brjDIGCxD65tFLNeQ5IgLeHZ/view?usp=sharing).


About this repository
-------------

The *pd_python* folder contains all the scripts that you need to run DD. Copy the folder to your machine prior to start. The *slurm* folder contains some examples of scripts to automate DD on clusters using slurm queueing system. The *temp* folder contains templates and examples of files that need to be created for running DD.


Prerequisites
-------------

To run DD you need to install the following packages:
- Package installer for python ([pip](https://pypi.org/project/pip/))
- [Anaconda](https://www.anaconda.com/distribution/)
- A program to create 3D conformations from SMILES
- Docking program

Then you need to set up the following virtual environments:
- Python3 virtual environment. Install [rdkit](https://rdkit.readthedocs.io/en/latest/Install.html#how-to-get-conda)

- Activate the rdkit conda environment if not already activated

          conda activate environment_name

- Install Wget package (to download the smiles for later)

          pip install wget

- Python3 virtual environment (different from previous one).

          virtualenv -p python3 tensorflow_gpu 

- Activate the virtual environment

          source /path/to/tensorflow_gpu/bin/activate

- Install tensorflow-gpu, pandas, numpy, keras, matplotlib and sklearn

          pip install -r requirements.txt

 
Preparing molecules for DD
----------------------------------------

To run the code you need to download the SMILES of the molecules and calculate their Morgan fingerprint with size of 1024 bits and radius of 2 as QSAR descriptors. 

**DOWNLOAD AND PREPARE SMILES**

- You can skip the next three points if you have already the database in SMILES format, or if you want to use a different database than ZINC15
- Go [here](https://zinc15.docking.org/tranches/home/) and download the 2D SMILES (.smi) in url format
- Activate the virtual environment where rdkit was installed
- Run

          python download_zinc15.py -up path_url_file/url_file -fp path_smile_folder -fn smile_folder -tp num_cpus
          
  This will create a *path_to_smile_folder/smile_folder* folder and download the SMILES within it. This step can take few hours, and ~84GB memory for 1.36 billion molecules.
- Reorganize the SMILES files into a number of evenly populated files equal to the number of CPUs used for phase 1 (see below). Activate the tensorflow environment and run

          python smile_simplification.py -sfp path_smile_folder/smile_folder -tp num_cpus -tn final_number_of_files

**CALCULATION OF MORGAN FINGERPRINTS**

- Activate the rdkit environment
- Run the following command

          python Morgan_fing.py -sfp path_smile_folder/smile_folder -fp path_morgan_folder -fn morgan_folder -tp num_cpus

  This will create a *path_to_morgan_folder/morgan_folder* folder, and generate the Morgan fingerprints of 1024 bits of size and radius of 2 within it. It is recommended as many CPUs as possible to speed up the process. This step takes ~260GB memory for 1.36 billion molecules


Run DD
---------

**Create the project**

Before starting DD, create a project folder and create a text file named "logs.txt" within it, following this [format](temp/logs.txt). An overview of logs lines:

| Line number | Value | Explanation |
|:---|:---|:---|
| 1 | path_project_folder | Path to the project folder |              
| 2 | project_folder | Name of project folder |                             
| 3 | path_grid_file/grid_file | Path and name of docking grid file; write a random line if you do not use a grid |                  
| 4 | path_morgan_folder/morgan_folder | Path to files containing the previously calculated QSAR descriptors (Morgan fingerprints) |           
| 5 | path_smile_folder/smile_folder | Path to files containing SMILES of molecules |             
| 6 | path_3dsdf_folder/3dsdf_folder | Path to precalculated 3D sdf conformations of molecules; write a random line if you do not have them |            
| 7 | number_of_molecules_to_sample | Number of molecules sampled at each iteration. In the first iteration, this number of molecules will be split in three to form initial training, validation and testing, from the second iteration it will be the number of molecules added to the training set |

DD pipeline is divided in 5 sequential phases to be repeated over multiple iterations until a desired number of final predicted virtual hits is reached:

**Phase 1.** *Random sampling of molecules*
1. The number of molecules to be sampled is defined in the logs.txt file and can be modified any time during the runs (for example, to keep constant the number of molecules added to the training set between iteration 1 and the other iterations). Choose the number according with the computational resources that are available (for the paper we sampled 3 million molecules for iteration 1 (so that can be divided into 1 million each for training, validation and test) and 1 million from iteration 2 onwards, all for training), as these molecules will be docked later on. During iteration 1 this sample of molecules will be splitted in three to build initial training, validation and test set. From iteration 2 it will correspond to the number of molecules that are used for augmenting the training set (so do not worry about the naming convention from iteration 2 onwards).
2. Run phase 1
    
          bash pd_python/phase_1.sh iteration_no n_cpus path_to_log_file path_tensorflow_venv
    
3. This step will create few folders and files inside the *iteration* folder relative to your current iteration. First, it will create three *txt* files containing the names of molecules that were randomly sampled. Note that the name of these files will always start with train, valid and test, even after iteration 1 (when molecules are added only to the training set). Then, a *morgan* folder will be generated, containing three *csv* files with Morgan fingerprints for the sampled molecules. Finally, phase 1 will generate three *smi* files in a *smile* folder, with the SMILES of the sampled molecules, to be used as input for docking (phase 2). 

**Phase 2.** *Prepare molecules for docking*\
Convert SMILES from phase 1 to 3D sdf format for docking (if it is not done internally by the docking software). This step includes assigning tautomer and protonation states and generating conformers, and can be done with different free (e.g. [openbabel](https://openbabel.org/docs/dev/Command-line_tools/babel.html)) or licensed programs (e.g. [omega](https://www.eyesopen.com/omega)).

**Phase 3.** *Molecular docking*
1. Run docking using the created sdf files
2. From the docking results create three *csv* files with two columns, *ZINC_ID*, *r_i_docking_score* (use these exact headings):
    - Populate the *ZINC_ID* column with the IDs of molecules (use the same heading even if you are not screening ZINC)
    - Add the corresponding scores in the *r_i_docking_score* column
3. Name the *csv* files as training_labels.txt, validation_labels.txt, testing_labels.txt, according with to the original *smi* file used to create files for docking. Follow this [format](temp/labels_example.txt)
4. Put these files in the *iteration_no* folder

**Phase 4.** *Neural network training*
1. Training neural network models with different sets of hyperparameters (12 combinations of hyperparameter values will be evaluated). Activate the tensorflow environment and run
     
          python simple_job_models_noslurm.py -n_it iteration_no -mdd path_morgan_folder/morgan_folder -time training_time -protein project_folder_name -file_path path_to_project_folder -pdfp path_to_pd_python/pd_python -tfp path_tensorflow_venv -min_last minimum_molecules_at_last_iteration

2. Training time should be set between 1 and 2 (hours)
3. The minimum_molecules_at_last_iteration defines the number of top scoring molecules considered as virtual hits in the validation set during the last iteration. For example, setting this value to 100 for a validation set of 1 million molecules corresponds to consider the top 0.01% molecules as virtual hits, and so on. Default value is 200.
4. Execute all the bash scripts in *path_project_folder/project_folder/iteration_no/simple_job*
    
**Phase 5.** *Selection of best model and prediction of the entire database*
1. For chosing the best model run 
                 
          python hyperparameter_result_evaluation.py -n_it iteration_no -protein project_folder_name -file_path path_project_folder -mdd path_morgan_folder/morgan_folder
                
2. Generate bash files for prediction:

          python simple_job_predictions_noslurm.py -protein project_folder_name -file_path path_project_folder -n_it iteration_no -mdd path_morgan_folder/morgan_folder
                
3. Execute all the bash scripts in *path_project_folder/project_folder/iteration_no/simple_job_predictions*
4. To check the number of molecules that are left after each iteration, sum the last column of the passed_file_ct.txt created in *path_project_folder/project_folder/iteration_no/morgan_1024_predictions*. You can compare this number with the number of left molecules predicted from the test set (total_pred_left) in *path_project_folder/project_folder/iteration_no/best_model_stats.txt*, and verify whether they are close.

Repeat the above phases 1-5 for as many iterations as needed to reach a desired number of left molecules. You will just need to change the *iteration_no* value every time you start from phase 1 again (sometimes the number of molecules will plateu after a point i.e. the decrease will become very small after each iteration, at that point you can use the useful tip mentioned below).


After DD
---------------

 After the final iteration is completed, the final set can be directly docked to remove residual low scoring molecules. Some molecules could have been randomly sampled and docked during the previous iterations, and therefore do not need to be docked again:
- Run 

          bash final_phase_noslurm.sh iteration_no number_of_cpus path_logs_file path_tensorflow_venv

  This will create a new folder in the project called *after_iteration* and put all the molecules that have been already docked inside the *docked* folder within it, and all the remaining SMILES in the *to_dock* folder
- You can dock the SMILES using the same procedure as step 2 and 3


Useful tips
-----------
You can select a subset of top predicted virtual hits instead of all of them to dock after the final iteration, using the rank provided by the model probabilities of being virtual hits (for example you completed 3 iterations after which 30 million molecules are remaining, and you want to dock only the top 10 million compounds). Run

          python Prediction_morgan_1024_top_n.py -protein protein_name -it iteration_no -file_path path_to_protein -top_n top_n_molecules

Executing this command will rename the original *morgan_1024_predictions* folder to *morgan_1024_predictions_old*, and create a new *morgan_1024_predictions* folder inside *iteration_no*, with all the files generated by phase 5 for the top n compounds only. 
