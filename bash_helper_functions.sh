# bash_helper_functions.sh
#
# Contains helper functions to be sourced by other scripts.
#
# Version: 1.0.0
#
#!/usr/bin/env bash

# Activates a Python virtual environment (venv) at the given path.
# If that venv does not exist, it will be created.
# First argument should be the venv path.
# If set, the second argument will prevent venv activation (i.e. '--novenv').
function activate_python_venv {
    if [ -z "$2" ]; then
        local VENV_PATH=$1

        if [ ! -d "$VENV_PATH" ]; then
            echo "Creating Python virtual environment at '$VENV_PATH'..."
            python -m venv "$VENV_PATH"
        fi

        echo "Activating Python virtual environment at '$VENV_PATH'..."
        source "$VENV_PATH/bin/activate"
    fi
}

# Echos different messages based upon the passed error level.
# The first argument should be the error level.
# The second argument is the script operation to use in the report.
function echo_script_result {
    local SCRIPT_OPERATION=$2
    if [ -z "$SCRIPT_OPERATION" ]; then
        local SCRIPT_OPERATION="Script"
    fi
        
    if [ $1 -eq 0 ]; then
        echo "$SCRIPT_OPERATION completed successfully."
    else
        echo "$SCRIPT_OPERATION failed!"
        echo "Check the console logs for details about the failure."
    fi
}

# Installs any required packages defined in a given requirements.txt file.
# The first argument is the path to requirements.txt.
# If set, the second argument will prevent installation (i.e. '--noinstall').
function install_python_requirements {
    if [ -z "$2" ]; then
        echo "Installing required Python modules..."
        pip install -r "$1"
    fi
}

# Returns whether a given argument is set in a set of arguments.
# The first argument is the argument to find.
# All remaining arguments are the arguments to search.
# NOTE 1:  0 is success and 1 is failure. This allows chaining of the function.
#   `is_arg_set "-u" "$@" || is_arg_set "--url" "$@"`
# NOTE 2: Checking of the function should be done by checking the error level.
#   `if [ $? -ne 0 ]; then...`
function is_arg_set {
    local ARG_TO_FIND=$1
    shift

    while [[ $# -gt 0 ]]; do
        if [[ "${1,,}" == "$ARG_TO_FIND" ]]; then
            return 0
        else
            shift
        fi
    done

    return 1
}

# Sets some common helper environment variables from command-line args.
# Expected input is the full list of arguments from the calling script.
# If you want to remove the helper args after this call, execute:
# `set -- "${NON_HELPER_ARGS[@]}"`
function set_helper_vars_from_arguments {
    NON_HELPER_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            --noinstall)
            SKIP_INSTALL=1
            shift
            ;;

            --nopause)
            SKIP_PAUSE=1
            shift
            ;;

            --novenv)
            NO_VENV=1
            shift
            ;;

            *) # All remaining arguments
            NON_HELPER_ARGS+=("$1") # Save for later restoration
            shift
            ;;
        esac
    done
}

# Pauses the script for input.
# If the first argument to the script is set (i.e. '--nopause'), pausing will be skipped.
function pause {
    if [ -z "$1" ]; then
        read -p "Press any key to exit..."
    fi
}
