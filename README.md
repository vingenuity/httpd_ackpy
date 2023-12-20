# httpd_ackpy
Python client to connect to an [httpd-ack](https://github.com/sega-dreamcast/httpd-ack) Dreamcast server to dump disc and console data.

## Usage
There are currently two methods of using these scripts on the command-line: Python and shell script.

### Python
`httpd_ack_client_cmd.py OPERATION OPTIONS`

**Available Operations:**
- `dump`: dump Dreamcast data via an httpd-ack server
- `read`: read and display httpd-ack HTML

#### Dump Operation
**Available Options:**
- `--url SERVER_URL, -u SERVER_URL`: URL for the httpd-ack server
- `--output OUTPUT_DIR, -o OUTPUT_DIR`: directory in which dumped files will be output
- `--bios, -b`: if set, the Dreamcast console's BIOS will be dumped
- `--flash, -f`: if set, the Dreamcast console's flash will be dumped
- `--gdi, -g`: if set, the GDI of the Dreamcast disc will be dumped.
- `--page, -p`: if set, the HTML page from httpd-ack will be dumped
- `--syscalls, -s`: if set, the Dreamcast console's syscalls will be dumped
- `--disc, -d`: if set, all tracks of the Dreamcast disc will be dumped
- `--track TRACKS_TO_DUMP, -t TRACKS_TO_DUMP`: individual track(s) of the Dreamcast disc to dump
**NOTE:** If both of the `-d` and `-t` arguments are provided, `-d` takes precedence.

#### Read Operation
**Available Options:**
- `--file FILE, -f FILE`:  path to httpd-ack HTML file
- `-url SERVER_URL, -u SERVER_URL`: URL for the httpd-ack server
**NOTE:** One of these two options _must_ be provided!

### Shell
The shell scripts have all of the same options as the Python script. However, each operation has its own shell script:
- "dump_dreamcast_data.sh": Equivalent to the `dump` command
- "read_httpd_html.sh": Equivalent to the `read` command

Each shell script provides the following additional functionality over the Python version:
- Prompts for required options for each command if they are not given on the command line
- Automatic creation and activation of a Python virtual environment
- Automatic installation of required Python packages
- Pauses for input post-execution to keep the console window open

Three additional options can be passed to each shell script to disable the additional functionality:
- `--noinstall` - Disables automatic required package installation
- `--nopause` - Disables pausing for input post-execution
- `--novenv` - Disable creation and activation of Python virtual environment
