# suite_cascade1p
Automated Calcium imaging detection (using suite2p) and deconvolution (using cascade) for primary neuronal cultures using widefield microscopy
- added simple GUI to both interact with the configurations file and start suite2p and cascade
- no need to manually change environments
- needed: seperate environments for suite2p, cascade and plotting, an already existing gui_configurations.py file
- additionally to suite2p/cascade packages: seaborn, statannotations 
- filepaths in the following files will have to be adjusted before first usage: run_default_ops.bat, run_plots.bat, run_s2p_gui.bat, run_sequence.bat (need to find a way to streamline)
- the GUI needs an already existing gui_configurations file 
- call the GUI by executing jd_gui_test.py (plan to adjust so it can be launched by doubleclick)