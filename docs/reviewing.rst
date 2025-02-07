.. _Reviewing Results:

=================
Reviewing Results
=================

Viewing the results of SCRUB can be performed in three different ways: viewing the results directly in text format,
utilizing the SCRUB GUI, or pushing the results to Collaborator for peer review. The following sections will provide
more information about the SCRUB GUI and Collaborator review options.

SARIF Viewers
*************
SCRUB is capable of export results directly to the SARIF output format. Any tools that are capable of ingesting SARIF
files can be used to view SCRUB results. For more information please review the `SARIF specification`_.

Collaborator
************
Users can also push results to Collaborator directly from SCRUB. This can occur in two different ways:

- Direct invocation of the module for pushing results to Collaborator (targets/collaborator/do_collaborator.py)
- Automated invocation via SCRUB configuration file

.. Note:: The Collaborator command line utility is required for pushing results to Collaborator. This utility can be
          found on the `Collaborator download page`_.

.. Note:: User credentials are required for all Collaborator uploads. After analysis has been completed and before the
          Collaborator upload has begun, SCRUB will prompt users to enter their Collaborator login password.

Direct Invocation
-----------------
Results can be pushed to Collaborator manually by executing the following command from the same location as you
performed your SCRUB analysis::

    python3 <SCRUB root>/module_helper.py scrub.targets.collaborator.do_collaborator scrub.cfg

Please refer to the :ref:`Detailed Configuration` page for more information about Collaborator configuration inputs.

Automated Invocation
--------------------
There is a section of the scrub.cfg file that can be used for pushing results to Collaborator automatically. For more
information about the expected inputs for this process, please refer to the :ref:`Detailed Configuration` page. SCRUB
analysis will be performed normally, but before execution is completed SCRUB will create a new Collaborator review that
is initialized with all of the SCRUB results.


.. _`Collaborator download page`: https://support.smartbear.com/collaborator/downloads/
.. _`SARIF specification`: https://sarifweb.azurewebsites.net/