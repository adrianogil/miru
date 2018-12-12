
function set-miru-python-path()
{
    if [ -z "$MIRU_PYTHON_PATH" ]
    then
        export MIRU_PYTHON_PATH=$MIRU_PROJ_PATH/
        export PYTHONPATH=$MIRU_PYTHON_PATH:$PYTHONPATH
    fi
}

function miru-raymarching-cubes()
{
    set-miru-python-path
    python2 -m raymarching.scenes.cubes
}