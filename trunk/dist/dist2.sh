dirname="blenderaid-$pythonversionshort-$version"
tarname="$dirname.tar.gz"
zipname="$dirname.zip"

echo === $dirname ===
echo == remove old tar and zip file and directory ==
rm $tarname
rm $zipname
rm -Rf $dirname
echo == make $dirname ==
mkdir $dirname
echo == copy sources ==
cp -r ../src/* $dirname

echo == clean up unwanted resources ==
cd $dirname
rm *~
rm *.pyc
rm blendfileprofiler.*
rm blendfile
rm test*
rm .svn -Rf
cd www
rm *~
rm .svn -Rf
cd script
rm *~
rm .svn -Rf
cd ..
cd images
rm *~
rm .svn -Rf
cd ..
cd ..
echo == compile code ==
$pythonversion ../compile.py
echo == remove unwanted sources ==
mv settings.py settings.tmp
rm *.py
mv settings.tmp settings.py
chmod +x server.py

cd ..
echo == make archives ==
zip -r $dirname $dirname
tar -czf $tarname $dirname

echo == upload archive to googlecode ==
python googlecode_upload.py -s "Blender-aid (svn)" -p "blender-aid" -u "j.bakker@atmind.nl" -w $password -l Type-Archive,OpSys-Linux,OpSys-OSX,$pythonversion $zipname
python googlecode_upload.py -s "Blender-aid (svn)" -p "blender-aid" -u "j.bakker@atmind.nl" -w $password -l Type-Archive,OpSys-Linux,OpSys-OSX,$pythonversion $tarname

