
if [ -z "$MIRU_PYTHON_PATH" ]
then
    export MIRU_PYTHON_PATH=$MIRU_PROJ_PATH/
    export PYTHONPATH=$MIRU_PYTHON_PATH:$PYTHONPATH
fi

function miru-raytracing()
{
    target_scene_file=$1
    target_render_image=$2

    python2 -m miru.raytracing.scene $target_scene_file $target_render_image
}

function miru-raymarching()
{
    target_scene_file=$1
    target_render_image=$2

    python2 -m miru.raymarching.scene $target_scene_file $target_render_image
}

function miru-raymarching-cubes()
{
    python2 -m miru.raymarching.scenes.cubes
}