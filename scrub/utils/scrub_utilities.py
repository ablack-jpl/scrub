import re
import os
import sys
import shutil
import logging
import subprocess
import configparser
import argparse
from scrub.utils import translate_results


class CommandExecutionError(Exception):
    pass


def check_file(input_file, critical):
    """This function checks to ensure the given file is not empty.

    Inputs:
        - input_file: Full path to the file of interest [string]
        - critical: Indication of file criticality [binary]
            - 0: File is not critical and may be empty
            - 1: File is critical and should not be empty

    Output:
        - Warnings sent to standard output
    """

    # Check to make sure the file isn't empty
    file_size = os.path.getsize(input_file)
    if file_size == 0:
        if critical == 1:
            message = 'Output file \"' + input_file + '\" is empty. This file should not be empty.'
            raise UserWarning(message)
        if critical == 0:
            logging.warning('')
            logging.warning('\tOutput file %s is empty.', input_file)
            logging.warning('\tThis may or may not be a problem.')


def get_executable_path(executable):
    """This function returns the path of an executable.

    Inputs:
        - executable: Executable of interest [string]

    Outputs:
        - execution_path: Absolute path to the directory containing the executable [string]
    """

    # Initialize variables
    call_string = 'which ' + executable
    my_env = os.environ.copy()

    # Get the execution path
    # subprocess.call(call_string, shell=True, env=my_env)
    proc = subprocess.Popen(call_string, shell=True, env=my_env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    execution_path = os.path.dirname(proc.communicate()[0].strip())

    return execution_path


def split_results(baseline_file, subset_file, remainder_file, queries):
    """This function splits a baseline set of SCRUB results into two separate files based on a given query list.

    Inputs:
        - baseline_file: Absolute path to the baseline file containing SCRUB warnings [string]
        - subset_file: Absolute path to the output file to contain filtered warnings [string]
        - remainder_file: Absolute path to the output file to contain remaining warnings not filtered [string]
        - query_list: List of query strings to filter on [list of strings]
    """

    # Import the contents of the baseline input file
    with open(baseline_file, 'r') as input_fh:
        baseline_data = input_fh.readlines()

    try:
        # Open the output files
        subset_fh = open(subset_file, 'w')
        remainder_fh = open(remainder_file, 'w')

        # Iterate through every line of the baseline data
        for i in range(0, len(baseline_data)):
            line = baseline_data[i]

            # Check to see if the line contains a warning header
            if re.search(translate_results.WARNING_LINE_REGEX, line):
                # Get the current warning query
                warning_query = list(filter(None, re.split(":", line)))[-1].strip()

                # Get the full warning content
                current_warning = get_warning(baseline_data, i)

                # Check to see if the query is in the queries list of interest
                if warning_query in queries:
                    # Write the query to the output file
                    subset_fh.write('%s' % current_warning)

                else:
                    # If not, write the result to to remaining output file
                    remainder_fh.write('%s' % current_warning)

    finally:
        # Close the files
        subset_fh.close()
        remainder_fh.close()


def get_warning(warning_data, index):
    """This function gets a complete warning when passed the index of a warning header.

    Inputs:
        - warning_data: List of lines of warning file contents [list of strings]
        - index: Index of warning header of interest [int]

    Outputs:
        - warning_content: Full warnings contents including header data [string]
    """

    # Initialize variables
    warning_content = warning_data[index]

    # Get the warning content
    for i in range(index + 1, len(warning_data)):
        # Get the line content
        line = warning_data[i]

        # Make sure you haven't hit the next warning header
        if re.search(translate_results.WARNING_LINE_REGEX, line):
            break
        else:
            warning_content = warning_content + line

    return warning_content


def execute_command(call_string, my_env, output_file=None, interactive=False):
    """This function executes a command string and captures the results.

    Inputs:
        - call_string: Command to execute in the shell [string]
        - my_env: Environment to use during execution [dict]
        - output_file: Absolute path to output file for storing results [string] [optional]
        - interactive: Open command for user input? [bool] [optional]
    """

    # Initialize variables
    output_data = ''

    # Write out a logging message
    logging.info('')
    logging.info('\t>> Executing command: %s', call_string)
    logging.info('\t>> From directory: %s', os.getcwd())
    logging.debug('\tConsole output:')

    # Execute the call string and capture the output
    if interactive:
        proc = subprocess.Popen(call_string, shell=True, env=my_env, encoding='utf-8')
    else:
        proc = subprocess.Popen(call_string, shell=True, env=my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                encoding='utf-8')

        # Write the output to the logging file
        for stdout_line in iter(proc.stdout.readline, ''):
            logging.debug('\t\t%s', stdout_line.replace('\n', ''))
            output_data = output_data + stdout_line

        # Write results to the output file
        if output_file is not None:
            with open(output_file, 'w') as output_fh:
                output_fh.write(output_data)

    # Wait for the process to finish
    proc.wait(timeout=None)

    # Throw an exception if necessary
    if proc.poll() > 0:
        raise CommandExecutionError


def create_logger(log_file):
    """This function creates the logger to be used for logging SCRUB data.

    Inputs:
        - log_file: Absolute path to the location of the log file to be created [string]
    """

    # Clear any existing loggers
    logging.getLogger().handlers = []

    # Create the logger, if it doesn't already exist
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        filename=log_file,
                        filemode='w')

    # Start the console logger
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def create_conf_file(output_path=None):
    """
    This function generates a blank configuration file at the desired output location.

    Inputs:
        --output: Path to desired output location [string] [optional]
            Default value: ./scrub_template.cfg
    """

    # Parse arguments if necessary
    if output_path is None:
        # Create the parser
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description=create_conf_file.__doc__)

        # Add parser arguments
        parser.add_argument('--output', default='./scrub_template.cfg')

        # Parse the arguments
        args = vars(parser.parse_args(sys.argv[2:]))
        output_path = args['output']

    # Initialize variables
    default_config_file = os.path.dirname(__file__) + '/scrub_defaults.cfg'

    # Copy the default configuration file
    shutil.copyfile(default_config_file, output_path)


def parse_common_configs(user_conf_file, scrub_keys=[]):
    """This function parses a SCRUB configuration file and adds default values.

    Inputs:
        - conf_file: Absolute path to the SCRUB configuration file [string]
        - scrub_keys: List of configuration file sections to be retrieved [list of strings]

    Outputs:
        - scrub_conf_data: Dictionary of values read from configuration file [dict]
    """

    # Initialize the variables
    scrub_conf_data = {}
    scrub_init_path = os.path.dirname(__file__) + '/scrub_defaults.cfg'

    # Read in the default config data
    scrub_init_data = configparser.ConfigParser()
    scrub_init_data.read(scrub_init_path)

    # Set the keys, if necessary
    if not scrub_keys:
        scrub_keys = scrub_init_data.sections()

    # Convert to a dictionary
    for key in scrub_keys:
        scrub_conf_data.update(dict(scrub_init_data.items(key)))

    # Read in the values from the conf file
    user_conf_data = configparser.ConfigParser()
    user_conf_data.read(user_conf_file)

    # Update the dictionary
    for user_section in user_conf_data.sections():
        for section_key in user_conf_data.options(user_section):
            # Update the value only if there is a user value
            if user_conf_data.get(user_section, section_key):
                scrub_conf_data.update({section_key: user_conf_data.get(user_section, section_key)})

    # Update the configuration data
    for key in scrub_conf_data.keys():
        # Expand environment variables
        scrub_conf_data.update({key: os.path.expandvars(scrub_conf_data.get(key))})

        # Update boolean values
        if scrub_conf_data.get(key).lower() == 'true':
            scrub_conf_data.update({key: True})
        elif scrub_conf_data.get(key).lower() == 'false':
            scrub_conf_data.update({key: False})

    # Make the source root absolute
    scrub_conf_data.update({'source_dir': os.path.abspath(os.path.expanduser(scrub_conf_data.get('source_dir')))})

    # Set the SCRUB analysis directory
    scrub_conf_data.update({'scrub_analysis_dir': os.path.normpath(scrub_conf_data.get('source_dir') + '/.scrub')})

    # Set the default filtering file locations
    if scrub_conf_data.get('analysis_filters') == '':
        analysis_filters_file = os.path.normpath(os.path.dirname(os.path.abspath(user_conf_file)) + '/SCRUBFilters')
        scrub_conf_data.update({'analysis_filters': analysis_filters_file})
    if scrub_conf_data.get('query_filters') == '':
        analysis_filters_file = os.path.normpath(os.path.dirname(os.path.abspath(user_conf_file)) +
                                                 '/SCRUBExcludeQueries')
        scrub_conf_data.update({'query_filters': analysis_filters_file})

    # Set the SCRUB working directory
    if (scrub_conf_data.get('scrub_working_dir') is None) or (scrub_conf_data.get('scrub_working_dir') == ''):
        scrub_working_dir = scrub_conf_data.get('scrub_analysis_dir')
    else:
        scrub_working_dir = os.path.abspath(os.path.expanduser(scrub_conf_data.get('scrub_working_dir')))
    scrub_conf_data.update({'scrub_working_dir': scrub_working_dir})

    # Make every *path variable absolute and make every *build_dir variable absolute
    for key in scrub_conf_data.keys():
        if re.search(r'.+path', key) and (scrub_conf_data.get(key) != ''):
            path_value = scrub_conf_data.get(key)
            path_value = os.path.abspath(os.path.expanduser(path_value))
            scrub_conf_data.update({key: path_value})

        elif re.search(r'.+build_dir', key):
            if scrub_conf_data.get(key) == '':
                scrub_conf_data.update({key: scrub_conf_data.get('source_dir')})
            elif not scrub_conf_data.get(key).startswith(scrub_conf_data.get('source_dir')):
                path_value = scrub_conf_data.get(key)
                path_value = os.path.abspath(os.path.expanduser(path_value))
                scrub_conf_data.update({key: path_value})

    # Add SCRUB root path
    scrub_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/..')
    scrub_conf_data.update({'scrub_path': scrub_path})

    # Add the log directory
    scrub_log_dir = os.path.normpath(scrub_conf_data.get('scrub_analysis_dir') + '/log_files')
    scrub_conf_data.update({'scrub_log_dir': scrub_log_dir})

    # Add the raw results directory
    raw_results_dir = os.path.normpath(scrub_conf_data.get('scrub_analysis_dir') + '/raw_results')
    scrub_conf_data.update({'raw_results_dir': raw_results_dir})

    # Add the SARIF results directory
    sarif_results_dir = os.path.normpath(scrub_conf_data.get('scrub_analysis_dir') + '/sarif_results')
    scrub_conf_data.update({'sarif_results_dir': sarif_results_dir})

    # Add the filtering output file
    filtering_output_file = os.path.normpath(scrub_conf_data.get('scrub_analysis_dir') + '/SCRUBAnalysisFilteringList')
    scrub_conf_data.update({'filtering_output_file': filtering_output_file})

    return scrub_conf_data


def initialize_storage_dir(scrub_conf_data):
    """This function handles setting up the SCRUB analysis storage directory

    Inputs:
        - scrub_conf_data: Dictionary of values read from configuration file [dict]
    """

    # Create the .scrub analysis directory
    if not os.path.exists(scrub_conf_data.get('scrub_analysis_dir')):
        os.mkdir(scrub_conf_data.get('scrub_analysis_dir'))
        os.chmod(scrub_conf_data.get('scrub_analysis_dir'), 511)

    # Create the logging directory
    if not os.path.exists(scrub_conf_data.get('scrub_log_dir')):
        os.mkdir(scrub_conf_data.get('scrub_log_dir'))
        os.chmod(scrub_conf_data.get('scrub_log_dir'), 511)

    # Create the output directory
    if not os.path.exists(scrub_conf_data.get('raw_results_dir')):
        os.mkdir(scrub_conf_data.get('raw_results_dir'))
        os.chmod(scrub_conf_data.get('raw_results_dir'), 511)

    # Create the SARIF results directory
    if not os.path.exists(scrub_conf_data.get('sarif_results_dir')):
        os.mkdir(scrub_conf_data.get('sarif_results_dir'))
        os.chmod(scrub_conf_data.get('sarif_results_dir'), 511)

    # Create the analysis directory if it doesn't exist
    if scrub_conf_data.get('scrub_working_dir') != scrub_conf_data.get('scrub_analysis_dir'):
        if os.path.exists(scrub_conf_data.get('scrub_working_dir')):
            sys.exit('ERROR: SCRUB storage directory ' + scrub_conf_data.get('scrub_working_dir') +
                     ' already exists. Aborting analysis.')
        else:
            # Create the scrub working dir
            os.mkdir(scrub_conf_data.get('scrub_working_dir'))
            os.chmod(scrub_conf_data.get('scrub_working_dir'), 511)
