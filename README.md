# benchmarktu1402

A structural dynamics benchmark problem which is generated as part of COST Action TU1402 on 
Quantifying the Value of Information and is intended to serve as a reference case 
study for validation of Structural Health Monitoring (SHM) methods and decision-making tools 
relying on the Value of Information.

## Getting started

- Pull down a copy of the code by cloning or downloading the repository
- Open a terminal and change the current directory to the benchmark folder
- Run the benchmark through the terminal by typing
```
python main.py
```

## Analysis


## Results

Upon running the analysis, a file named "Output_nodes.dat" is firstly generated, containing the information
of output nodes and consisting of three columns:
- Column 1 stores the labels of output nodes
- Columns 2-3 store the corresponding nodal coordinates

Depending on the type of analysis, Modal or Dynamic, the following files are further generated:

- Modal 
  - *Job_name*_frequencies.dat
  - *Job_name*_modes.dat
 
- Dynamic
  - *Job_name*_displacements.dat
  - *Job_name*_accelerations.dat
  - *Job_name*_strains.dat

## Notes

- The backend and frontend are currently not connected
- The code can be configured and executed through main.py script
- All python dependencies are included in [Anaconda](https://www.anaconda.com/distribution/) installations
