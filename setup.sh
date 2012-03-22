python ./utils/buildInit.py #make sure the __init__ file contains all the commands
python ./interfaces/lib_m.py install --record build_lib_m.txt
python ./interfaces/lib_GUI.py install --record build_lib_GUI.txt
python ./interfaces/lib_f.py install --record build_lib_f.txt
python ./interfaces/lib_u.py install --record build_lib_u.txt
python ./interfaces/lib_i.py install --record build_lib_i.txt
python ./interfaces/pythonlabtools/lib_pythonlabtools.py install --record build_lib_pythonlabtools.txt

#python main.py (I thinkwe need to add some kind of steps)
# Also, we need creat a shortcut for the program in user Desktop.
# we can not do above until we have one main file (contain FPGA and GPIB). 


