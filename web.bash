#!/bin/bash
function usage () {
    cat << EOS
Usage: $0
EOS
}

### TYPE MATCH ###
case "$2" in
    "start"|"build"|"delete"|"stop"|"run"|"do") echo "Web Bash Command: $2";;
    *) echo "Invalid Argument #2: $2"
       exit 1;;
esac

case "$1" in
    "dev"|"test"|"prod") echo "Environment: $1";;
    *) echo "Invalid Argument #1: $1"
       exit 1;;
esac

echo

docker_compose_config_file="docker-compose.$1.yml"
cmd="docker-compose -f $docker_compose_config_file"

function run () {
    echo -e "\033[1;4;34m> $*\033[m\n"
    eval "$*"
}

function debug () {
    echo -e "\033[21;1;4;31;47m$*\033[m\n"
}

function stop () {
    debug "[STOP]"
    run $cmd stop
}

function build () {
    debug "[BUILD]"
    case "$1" in
        "dev")
            run $cmd 'build';;
        "test")
            debug '[*] Build Images'
            run $cmd 'build'
            debug "[*] Database Migration"
            run $cmd 'run -e PYTHONPATH=".." --entrypoint "bash -c \"pip install alembic;cd app;alembic revision --autogenerate -m \"$(date +%Y_%m_%d_%H_%M_%S)\";alembic upgrade head\"" api'
            debug "[*] Build Frontend"
            run $cmd 'run --entrypoint "bash -c \"yarn install --production=false && yarn build\"" frontend'
            ;;
        "prod")
            debug '[*] Build Images'
            run $cmd build
            debug "[*] Database Migration"
            run $cmd 'run -e PYTHONPATH='..' --entrypoint "bash -c \"pip install alembic;cd app;alembic revision --autogenerate -m \"$(date +%Y_%m_%d_%H_%M_%S)\";alembic upgrade head\"" api'
            debug "[*] Build Frontend"
            run $cmd 'run --entrypoint "bash -c \"yarn install --production=false && yarn build\"" frontend'
            ;;
    esac
}

function start () {
    debug "[START]"
    case "$1" in
        "dev")
            run $cmd 'up -d frontend'
            run $cmd 'up -d mongo'
            run $cmd 'up -d api proxy'
            run $cmd 'exec frontend yarn serve'
            ;;
        "test")
            trap finally EXIT
            function finally {
                debug '[*] Remove Files'
                run $cmd 'down'
            }
            debug "[*] Start Database"
            run $cmd 'up -d mongo postgres'
            sleep 5
            debug "[*] Start Proxy"
            run $cmd 'up -d proxy'
            debug '[*] Test Start'
            run $cmd 'run --entrypoint "pytest -v --cov=app --cov-report xml --cov-report term-missing" api'
            debug '[*] Test Completed!'
            ;;
        "prod")
            debug '[*] Run Database'
            run $cmd 'up -d mongo postgres'
            sleep 5
            debug '[*] Run Services'
            run $cmd 'up -d --scale api=8 api proxy'
            ;;
    esac
}

function delete () {
    debug "[DELETE]"
    case "$1" in
        "dev")
            run $cmd 'down --remove-orphans'
            ;;
        "test")
            run $cmd 'down --remove-orphans'
            ;;
        "prod")
            run $cmd 'down --remove-orphans'
            ;;
    esac
}

set -e

case "$2" in
"do")
    shift
    shift
    run $cmd $*;;
"stop")
    stop $1;;
"start")
    start $1;;
"build")
    build $1;;
"delete")
    delete $1;;
"run")
    delete $1
    build $1
    start $1;;
esac

exit 0
