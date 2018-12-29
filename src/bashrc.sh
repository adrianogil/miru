
if [ -z "$MIRU_PYTHON_PATH" ]
then
    export MIRU_PYTHON_PATH=$MIRU_PROJ_PATH/python/
    export PYTHONPATH=$MIRU_PYTHON_PATH:$PYTHONPATH
fi

function miru-raytracing()
{
    target_scene_file=$1
    target_render_image=$2

    python2 -m miru.raytracing.scene $target_scene_file $target_render_image
}

function miru-raymarching-py()
{
    target_scene_file=$1
    target_render_image=$2

    python2 -m miru.raymarching.scene $target_scene_file $target_render_image
}

function miru-raymarching-cpp()
{
    target_scene_file=$1
    target_render_image=$2

    $MIRU_PROJ_PATH/cpp/build/test_raymarching_sphere
}

function miru-raymarching-cpp-build()
{
    target_scene_file=$1
    target_render_image=$2

    current_dir=$PWD
    cd $MIRU_PROJ_PATH/cpp/build/
    make clean
    make build-test-raymarching
    cd $current_dir
}

alias miru-raymarching="miru-raymarching-py"

function miru-raymarching-cubes()
{
    python2 -m miru.raymarching.scenes.cubes
}