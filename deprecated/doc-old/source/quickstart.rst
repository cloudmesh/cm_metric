Quick Start
===========

Download 
---------------------------

Download CM Cloud Metric from PyPI. You can achieve this with::

        pip install cloudmesh-cloud-metric

Create A Log Backup of Eucalyptus
----------------------------------

This section explains how to make a log backup transaction of
eucalyptus using CM Metric tools.  The Cluster Controller (CC) of
eucalyptus generates a log file (named cc.log) which is a main
resource provider for the tools, so creating log backup of eucalyptus
is the most important start-up.

        1. Log into the management node of eucalyptus with access to the log files
        2. Create crontab::
           #Hourly
           0 * * * * cm-euca-gather-log-files -i <directory of log files> -o <directory of backup>

Parse the Log Backup 
-----------------------------------

Once we collected log backup by ``cm-euca-gather-log-files``, we need to
parse and store log files into database. MySQL configuration should be
set by ``.cloudmesh.cfg`` such as hostname, id, password, and port
number.

 ::

        cm-parser -i <directory of the backup>

Generate Results
-------------------

Now you can use the convenient cm-metric shell to create results::

        $ cm-metric
        ...
        (Cmd) analyze -Y 2012
        (Cmd) createreport -d 2012 

..


You can sore also the templates you use to create results with in a
file and input them to our cm-metric shell::

        cat examples/example2.txt | cm-metric


 
Additional Notes
----------------

We assume you have a valid python version (2.7.2 or higher) and all
the needed libraries on the system where you run the code. We also
assume you have installed a results database and populated it with
data from log files.

You will need the following python libraries::

    setuptools, pip, cmd2, pygooglechart, mysql-python

..


Now you just download the code from github::

   git clone git@github.com:cloudmesh/cloudmesh-cloud-metrics.git

..


Create a ~/.cloudmesh/cloudmesh.cfg file that includes the
following::

    [EucaLogDB]
    host=<yourhostname>
    port=<portnumber>
    user=<username>
    passwd=<password>
    db=<dbname>

Now you are ready to create results in a sphinx web page::

   cd cloudmesh-cloud-metric*/doc
   make force

If you met all the prerequisits, you will find the index file in::

   cloudmesh-cloud-metric*/doc/build/html/index.html


..

A live example of the data is available at

*  `http://portal.cloudmesh.org/doc/metric/results.html <http://portal.cloudmesh.org/doc/metric/results.html>`_

