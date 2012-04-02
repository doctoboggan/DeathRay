#!/bin/bash
if [ -f ./utils/buildInit.py ];
then 
  if [ -f ./interfaces/lib_m.py ];
  then 
    if [ -f ./interfaces/lib_GUI.py ];
    then 
      if [ -f ./interfaces/lib_f.py ];
      then 
        if [ -f ./interfaces/lib_u.py ];
        then 
          if [ -f ./interfaces/lib_i.py ];
          then 
            if [ -f ./interfaces/pythonlabtools/lib_pythonlabtools.py ];
            then 
              python ./utils/buildInit.py #make sure the __init__ file contains all the commands
              python ./utils/reloadFPGA.py  #reload the FPGA scripts
              python ./interfaces/lib_m.py install --record build_lib_m.txt
              python ./interfaces/lib_GUI.py install --record build_lib_GUI.txt
              python ./interfaces/lib_f.py install --record build_lib_f.txt
              python ./interfaces/lib_u.py install --record build_lib_u.txt
              python ./interfaces/lib_i.py install --record build_lib_i.txt
              python ./interfaces/pythonlabtools/lib_pythonlabtools.py install --record build_lib_pythonlabtools.txt
              echo -e "\e[00;32mInstallaion is done\e[00m"
            else
              echo -e "\e[00;31mWarning: \e[00;33mlib_pythonlabtools.py file is missing. It is under 'DeathRay/interfaces/pythonlabtools/'.\nBecause of that, The installation \e[00;35faild.\e[00m"
            fi
          else
            echo -e "\e[00;31mWarning: \e[00;33mlib_i.py file is missing. It is under 'DeathRay/interfaces/'.\nBecause of that, The installation \e[00;35faild.\e[00m"
          fi
        else
          echo -e "\e[00;31mWarning: \e[00;33mlib_u.py file is missing. It is under 'DeathRay/interfaces/'.\nBecause of that, The installation \e[00;35faild.\e[00m" 
        fi
      else
        echo -e "\e[00;31mWarning: \e[00;33mlib_f.py file is missing. It is under 'DeathRay/interfaces/'.\nBecause of that, The installation \e[00;35faild.\e[00m"  
      fi
    else
      echo -e "\e[00;31mWarning: \e[00;33mlib_GUI.py file is missing. It is under 'DeathRay/interfaces/'.\nBecause of that, The installation \e[00;35faild.\e[00m"    
    fi
  else
    echo -e "\e[00;31mWarning: \e[00;33mlib_m.py file is missing. It is under 'DeathRay/interfaces/'.\nBecause of that, The installation \e[00;35faild.\e[00m"   
  fi
else
  echo -e "\e[00;31mWarning: \e[00;33mbuildInit.py file is missing. It is under 'DeathRay/utils/'.\nBecause of that, The installation \e[00;35faild.\e[00m"
fi
#python main.py (I thinkwe need to add some kind of steps)
# Also, we need creat a shortcut for the program in user Desktop.
# we can not do above until we have one main file (contain FPGA and GPIB). 
