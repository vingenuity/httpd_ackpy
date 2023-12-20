#
# read_httpd_html.sh
#
# Reads an httpd-ack webpage that has been saved to an HTML file.
#
# This is primarily used for testing the HTML parsing.
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

is_arg_set "-f" "$@" || is_arg_set "--file" "$@"
if [ $? -ne 0 ]; then
    read -p "Please enter the path to an HTML file to read:" HTML_FILE
fi

# Pass any remaining arguments to the script directly.
python $SCRIPT_PATH read "$@" ${HTML_FILE:+-f "$HTML_FILE"}

echo_script_result $? "Reading http-ack HTML"
pause $SKIP_PAUSE
