rm -rf build dist
python macsetup.py py2app
cp -R gpib_commands dist/DeviceControl.app/Contents/Resources
mv dist/DeviceControl.app ./DeathRay.app
rm -rf build dist
