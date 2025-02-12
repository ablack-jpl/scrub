import re
import os
import glob
import logging
import traceback
import importlib
from scrub.utils.filtering import create_file_list
from scrub.utils.filtering import filter_results
from scrub.utils.filtering import move_warnings
from scrub.utils import scrub_utilities
from scrub.utils import translate_results
from scrub.utils import do_clean


def initialize_analysis(scrub_conf_data):
    """This function prepares the tool to perform analysis.

    Inputs:
        - scrub_conf_data: Dictionary of scrub.cfg input variables [dict]
    """

    scrub_conf_data.update({'filter_warnings': True})
    scrub_conf_data.update({'filtering_log_file': scrub_conf_data.get('scrub_log_dir') + '/filtering.log'})

    return scrub_conf_data


def get_valid_tags(scrub_root):
    """This function gets the valid tags from every tool module.

    Inputs:
        - scrub_root: Absolute path to the SCRUB root directory [string]

    Outputs:
        - valid_warning_tags: A dictionary of valid warning tags for each tool [dict]
    """

    # Initialize variables
    valid_warning_types = []

    # Find all of the tool modules
    for tool_module in glob.glob(scrub_root + '/tools/**/do*.py'):
        module_name = 'scrub.' + re.split('\\.py', os.path.relpath(tool_module, scrub_root))[0].replace('/', '.')

        # Import the module
        module_object = importlib.import_module(module_name)

        # Add the tags
        valid_warning_types.append(getattr(module_object, "VALID_TAGS"))

    return valid_warning_types


def distribute_scrub_results(scrub_conf_data):
    """This function distributes the filtered SCRUB output files

    Inputs:
        - scrub_conf_data: Dictionary of SCRUB configuration variables [dict]
    """

    # Get a list of the filtered SCRUB output files
    filtered_output_files = glob.glob(scrub_conf_data.get('scrub_analysis_dir') + '/*.scrub')

    # Move the warnings to the appropriate directories
    for filtered_output_file in filtered_output_files:
        move_warnings.move_warnings(filtered_output_file,
                                    scrub_conf_data.get('source_dir'))


def filter_scrub_results(scrub_conf_data):
    """This function filters the raw SCRUB output files.

    Inputs:
        - scrub_conf_data: Dictionary of SCRUB configuration variables [dict]
    """

    # Get a list of valid tags
    valid_warning_types = get_valid_tags(scrub_conf_data.get('scrub_path'))

    # Create a filtering list
    create_file_list.create_file_list(scrub_conf_data.get('source_dir'),
                                      scrub_conf_data.get('filtering_output_file'),
                                      scrub_conf_data.get('analysis_filters'))

    # Get the list of SCRUB files
    results_files = glob.glob(scrub_conf_data.get('raw_results_dir') + '/*.scrub')

    # Sort the files into groups
    raw_compiler_files = []
    raw_p10_files = []
    raw_generic_files = []
    for results_file in results_files:
        if re.search(r'compiler_raw\.scrub', results_file):
            raw_compiler_files.append(results_file)
        elif re.search(r'p10_raw\.scrub', results_file):
            raw_p10_files.append(results_file)
        else:
            raw_generic_files.append(results_file)

    # Filter compiler results
    if raw_compiler_files:
        try:
            # Set the compiler output file path
            filtered_compiler_results_file = scrub_conf_data.get('scrub_analysis_dir') + '/compiler.scrub'

            # Parse all of the input files
            compiler_results = []
            for results_file in raw_compiler_files:
                # Append the results file
                compiler_results = (compiler_results +
                                    translate_results.parse_scrub(results_file,
                                                                  scrub_conf_data.get('source_dir')))

            # filtered_compiler_results_file = scrub_conf_data.get('scrub_analysis_dir') + '/compiler.scrub'
            filter_results.filter_results(compiler_results, filtered_compiler_results_file,
                                          scrub_conf_data.get('filtering_output_file'),
                                          scrub_conf_data.get('query_filters'),
                                          scrub_conf_data.get('source_dir'),
                                          scrub_conf_data.get('enable_micro_filter'),
                                          scrub_conf_data.get('enable_ext_warnings'),
                                          valid_warning_types)

        except:      # lgtm [py/catch-base-exception]
            # Print a status message
            logging.warning("Could not generate output file %s", filtered_compiler_results_file)

            # Print the exception traceback
            logging.debug(traceback.format_exc())

    # Filter P10 results
    if raw_p10_files:
        try:
            # Set the output file path
            filtered_p10_results = scrub_conf_data.get('scrub_analysis_dir') + '/p10.scrub'

            # Parse all of the input files
            p10_results = []
            for results_file in raw_p10_files:
                # Append the results file
                p10_results = (p10_results + translate_results.parse_scrub(results_file,
                                                                           scrub_conf_data.get('source_dir')))

            filter_results.filter_results(p10_results, filtered_p10_results,
                                          scrub_conf_data.get('filtering_output_file'),
                                          scrub_conf_data.get('query_filters'),
                                          scrub_conf_data.get('source_dir'),
                                          scrub_conf_data.get('enable_micro_filter'),
                                          scrub_conf_data.get('enable_ext_warnings'),
                                          valid_warning_types)

        except:     # lgtm [py/catch-base-exception]
            # Print a status message
            logging.warning("Could not generate output file %s", filtered_p10_results)

            # Print the exception traceback
            logging.debug(traceback.format_exc())

    # Filter everything else
    if raw_generic_files:
        for raw_generic_file in raw_generic_files:
            try:
                # Import the warning data
                raw_generic_warnings = translate_results.parse_scrub(raw_generic_file,
                                                                     scrub_conf_data.get('source_dir'))

                # Get the output file name
                tool_name = list(filter(None, re.split('_raw.scrub', os.path.basename(raw_generic_file))))[0]
                filtered_generic_results = scrub_conf_data.get('scrub_analysis_dir') + '/' + tool_name + '.scrub'

                filter_results.filter_results(raw_generic_warnings, filtered_generic_results,
                                              scrub_conf_data.get('filtering_output_file'),
                                              scrub_conf_data.get('query_filters'),
                                              scrub_conf_data.get('source_dir'),
                                              scrub_conf_data.get('enable_micro_filter'),
                                              scrub_conf_data.get('enable_ext_warnings'),
                                              valid_warning_types)

            except:     # lgtm [py/catch-base-exception]
                # Print a status message
                logging.warning("Could not generate output file %s", filtered_generic_results)

                # Print the exception traceback
                logging.debug(traceback.format_exc())

    # Execute the custom filtering command if it exists
    if scrub_conf_data.get('custom_filter_cmd'):
        scrub_utilities.execute_command(scrub_conf_data.get('custom_filter_cmd'), os.environ.copy())


def generate_sarif(scrub_conf_data):
    """This function converts SCRUB formatted output files into SARIF.

    Inputs:
        - scrub_conf_data: Dictionary of SCRUB configuration variables [dict]
    """

    # Find all of the SCRUB output files
    scrub_files = glob.glob(scrub_conf_data.get('scrub_analysis_dir') + '/*.scrub')

    for scrub_file in scrub_files:
        # Create the SARIF output file path
        sarif_output_file = (scrub_conf_data.get('sarif_results_dir') + '/' +
                             os.path.splitext(os.path.basename(scrub_file))[0] + '.sarif')

        # Create a SARIF output file
        translate_results.perform_translation(scrub_file, sarif_output_file, scrub_conf_data.get('source_dir'),
                                              'sarifv2.1.0')


def run_analysis(scrub_conf_data, override=False):
    """This function calls Coverity to perform analysis.

    Inputs:
        - baseline_conf_data: Dictionary of raw scrub.cfg configuration parameters [dict]
        - override: Force tool execution? [optional] [bool]

    Outputs:
        - log_file/filtering.log: SCRUB log file for the filtering analysis
        - <tool>.scrub: SCRUB-formatted results file after filtering
    """

    # Initialize the analysis
    filtering_conf_data = initialize_analysis(scrub_conf_data)

    # Initialize variables
    filtering_exit_code = 2
    attempt_analysis = filtering_conf_data.get('filter_warnings') or override

    # Perform filtering?
    if attempt_analysis:
        try:
            # Create the logger
            scrub_utilities.create_logger(filtering_conf_data.get('filtering_log_file'))

            # Print a status message
            logging.info('')
            logging.info('Perform filtering and distribution...')

            # Remove distributed results
            do_clean.clean_subdirs(scrub_conf_data.get('source_dir'))

            # Filter the results
            filter_scrub_results(scrub_conf_data)

            # Convert the results into SARIF format
            generate_sarif(scrub_conf_data)

            # Distribute the results
            distribute_scrub_results(scrub_conf_data)

            # Set the exit code
            filtering_exit_code = 0

        except scrub_utilities.CommandExecutionError:
            # Print a warning message
            logging.warning('Filtering and distribution could not be completed. '
                            'Please see log file %s for more information.',
                            filtering_conf_data.get('filtering_log_file'))

            # Print the exception traceback
            logging.warning(traceback.format_exc())

            # Set the exit code
            filtering_exit_code = 100

        except:     # lgtm [py/catch-base-exception]
            # Print a warning message
            logging.warning('Filtering and distribution could not be completed. '
                            'Please see log file %s for more information.',
                            filtering_conf_data.get('filtering_log_file'))

            # Print the exception traceback
            logging.warning(traceback.format_exc())

            # Set the exit code
            filtering_exit_code = 100

        finally:
            # Close the loggers
            logging.getLogger().handlers = []

    # Return the exit code
    return filtering_exit_code
