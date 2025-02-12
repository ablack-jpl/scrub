==========================
Frequently Asked Questions
==========================

**What are the system requirements for running SCRUB?**

SCRUB requires Python version 3.6 or greater and a Linux or Mac operating system. SCRUB does not work on Windows
systems because the static analysis tools require different command structure on Windows.

**What static analysis tools does SCRUB support?**

The list of supported analysis tools can be found on the :ref:`Usage` page.

**What languages does SCRUB support?**

SCRUB currently supports C/C++ and Java.

**How do I configure SCRUB for my project?**

All the information that SCRUB needs to run is contained in the ``scrub.cfg`` file. Each value in the scrub.cfg file has
detailed instructions on what should be provided. More information on how to complete the scrub.cfg file can be found
on the :ref:`Detailed Configuration` page.

**How do I run SCRUB?**

After the ``scrub.cfg`` file for your project is completed, SCRUB can be executed by any tool or operation that is
capable of making the call ``scrub run-all --config scrub.cfg``. For more detailed information on running SCRUB, refer
to the :ref:`Usage` page.

**Do I have to use every static analysis tool?**

No. Users may enable analysis for whichever tools they want using ``scrub.cfg``.

**Where are SCRUB results located?**

SCRUB results are stored in a hidden directory (``.scrub``) within the source code root directory provided in the
``scrub.cfg`` file.

**Why does each tool require a different build and clean command?**

Each of the static analysis tools support different compilers. While one make command may work for one of the
analyzers, it may not work for all of them. For instance, Semmle does not support the Green Hills compilers, but
Coverity does. In this case a user may want to run both tools using different compilers and different build commands.

**Where are SCRUB log files located?**

SCRUB log files are stored along with the results in the hidden ``.scrub`` directory. The structure of this directory
can be found on the :ref:`SCRUB Output` page

**How long does it take to run SCRUB?**

SCRUB execution time depends primarily on the number of analyzers being used and the size of the source code being
analyzed. A good rule of thumb is 2-3 time longer than the non-analysis build time for each tool, but this time can
vary greatly.

**Which static analyzers should I use?**

This depends almost entirely on the needs of a project. The baseline recommendation is to only produce as many results
as the team can realistically review. More results will introduce more noise, but false positives and preferable to
false negatives.

**How do I filter out results I don't care about?**

SCRUB provides several filtering options: regex-based filtering, query-based filtering, and false positive filtering.
Details on how to use each of these filtering options can be found on the :ref:`Filtering` page.

**How do I view SCRUB results?**

There are a few different options. Please refer to the :ref:`Reviewing Results` page for more information.

**How can I push reviews to Collaborator?**

The Collaborator review creation utility can be called automatically as part of normal SCRUB execution or called
directly after static analysis has been completed. Please refer to the :ref:`Reviewing Results` page.

**How can I add a new analysis tool to SCRUB?**

A new module can be added to the analysis chain by making the following modifications. More information can be found
in the :ref:`Contributing` page.

- A new section in ``scrub.cfg`` file must be created for inputs for the new analysis module
- A new module for handling reading in values from scrub.cfg and running the analysis tool
- A new module for parsing raw results from the analysis tool into the SCRUB defined format

**Can I preview results before pushing them to Collaborator for formal review?**

Yes. Please refer to the :ref:`Reviewing Results` page for more information.

**What analysis tools support the Power of 10 rules?**

Both Semmle and CodeSonar support the Power of 10 checks. Usage information is covered on the
:ref:`Detailed Configuration` wiki page.

**How can I perform DoubleCheck analysis?**

DoubleCheck analysis can be performed by the gbuild compiler analysis. DoubleCheck warnings will automatically be
parsed as part of this process. Users must first enable the DoubleCheck analysis option via the GHS compilation
options. For more information, please refer to the GHS documentation.

**Can I upload a subset of results to Collaborator?**

Yes. For more information on defining which files are included in Collaborator uploads please refer to the
:ref:`Filtering` wiki page.

**Is it possible to rerun a single tool without rerunning all of SCRUB?**

Yes. It is possible to call any tool module individually. Please refer to the :ref:`Usage` page for more information.

**Can I run P10 analysis with Semmle and CodeSonar?**

Yes. Refer to the :ref:`Detailed Configuration` page for more information on how to enable P10 for both tools.
The output file ``p10.scrub`` will contain results from both analysis tools.

**Can I run multiple compilers when analyzing my code?**

It is possible to perform gcc and gbuild analysis as long different build commands are provided to each tool. The
output file ``compiler.scrub`` will contain results from both compilers.

**Do I need to provide the analysis tool location if it's already included in my PATH variable?**

If the tool location is not provided in the configuration file and the run flag is set to True, SCRUB will attempt to
perform analysis with the assumption that the tool has been properly initialized before executing SCRUB.

**Do I need to fill out every field in the configuration file?**

No. Minimally, the fields marked as required for each tool on the :ref:`Detailed Configuration` page must be provided.
Any optional fields do not have to be present in the configuration file.

**SCRUB seems to be taking a long time to execute. How can I monitor progress?**

SCRUB will continuously print results to the log files. The best way to monitor analysis progress is to examine the
tool log files.