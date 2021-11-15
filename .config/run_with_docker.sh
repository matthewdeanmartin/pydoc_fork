(
    export MSYS_NO_PATHCONV=1
    ./dockerw.sh run --rm --volume "$PWD":/output pydoc_fork:latest "$@" --output=/output --logs
)
