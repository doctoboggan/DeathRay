if [ -f ./build_lib_m.txt ];
then
  cat build_lib_m.txt | xargs rm -rf
  rm build_lib_m.txt
else
  echo "build_lib_m file is missing. The uninstallation is not totally complete"
  echo "To get this file, you should make a fresh install by running setup.sh with permission"
fi
if [ -f ./build_lib_GUI.txt ];
then 
  cat build_lib_GUI.txt | xargs rm -rf
  rm build_lib_GUI.txt
else
  echo "build_lib_GUI file is missing. The uninstallation is not totally complete"
  echo "To get this file, you should make a fresh install by running setup.sh with permission"
fi  
if [ -f ./build_lib_f.txt ];
then 
  cat build_lib_f.txt | xargs rm -rf
  rm build_lib_f.txt
else
  echo "build_lib_f file is missing. The uninstallation is not totally complete"
  echo "To get this file, you should make a fresh install by running setup.sh with permission"
fi  
if [ -f ./build_lib_u.txt ];
then 
  cat build_lib_u.txt | xargs rm -rf
  rm build_lib_u.txt
else
  echo "build_lib_u file is missing. The uninstallation is not totally complete"
  echo "To get this file, you should make a fresh install by running setup.sh with permission"
fi  
if [ -f ./build_lib_i.txt ];
then 
  cat build_lib_i.txt | xargs rm -rf
  rm build_lib_i.txt
else
  echo "build_lib_i file is missing. The uninstallation is not totally complete"
  echo "To get this file, you should make a fresh install by running setup.sh with permission"
fi  
if [ -f ./build_lib_pythonlabtools.txt ];
then 
  cat build_lib_pythonlabtools.txt | xargs rm -rf
  rm build_lib_pythonlabtools.txt
else
  echo "build_lib_pythonlabtools file is missing. The uninstallation is not totally complete"
  echo "To get this file, you should make a fresh install by running setup.sh with permission"
fi  






