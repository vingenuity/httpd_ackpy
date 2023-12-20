#
# dump_dreamcast_data.sh
#
# Dumps Dreamcast console and disc data via an httpd-ack server.
#
# Version: 2.0.0
#
#!/usr/bin/env bash

### Static environment variables
SCRIPT_ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
HELPER_SOURCE_PATH="$SCRIPT_ROOT/bash_helper_functions.sh"
SCRIPT_PATH="$SCRIPT_ROOT/src/httpd_ack_client_cmd.py"
VENV_PATH=".venv"

source $HELPER_SOURCE_PATH

### Main execution
set_helper_vars_from_arguments "$@"
set -- "${NON_HELPER_ARGS[@]}" # Overwrite args with non-helpers only

activate_python_venv $VENV_PATH $NO_VENV
install_python_requirements "$SCRIPT_ROOT/requirements.txt" $SKIP_INSTALL

is_arg_set "-u" "$@" || is_arg_set "--url" "$@"
if [ $? -ne 0 ]; then
    read -p "Please enter the URL of the httpd-ack server:" SERVER_ADDRESS
fi

is_arg_set "-o" "$@" || is_arg_set "--output" "$@"
if [ $? -ne 0 ]; then
    read -p "Please enter the output directory for the dumped files:" OUTPUT_DIR
fi

# Pass any remaining arguments to the script directly.
python $SCRIPT_PATH dump "$@" ${SERVER_ADDRESS:+-u "$SERVER_ADDRESS"} ${OUTPUT_DIR:+-o "$OUTPUT_DIR"}

echo_script_result $? "Dumping Dreamcast data"
pause $SKIP_PAUSE
