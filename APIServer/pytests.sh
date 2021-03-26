#!/bin/sh
# if downloading to Windows, watch for end-of-line character changing.
export user_type="test"
export test_dir="tests"
export ignore_files="scheduler"  # dummy file!
export ignore_dir="utils"

cd ..
export PYTHONPATH=$PWD

if [ -z $1 ]
then
    export capture=""
else
    export capture="--nocapture"
fi

echo "MESSAGING_HOME: $MESSAGING_HOME"
nosetests --ignore-files=$ignore_files --exe --verbose --with-coverage --cover-package=APIServer $capture --exclude=$ignore_dir
