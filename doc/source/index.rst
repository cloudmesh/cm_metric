**********************************************************************
Welcome to CloudMesh Metric's documentation!
**********************************************************************


.. sidebar:: Table of Contents

    .. toctree::
       :maxdepth: 5

       manual
       metrics
       developer
       highchart
       todo
       repository
       ubmod
       lighttpd

..
       modules

**Screenshots**::
 
 set date 2012-10-01 2013-02-01
 set metric runtime
 set platform openstack
 set nodename india
 analyze

.. raw:: html

   <table>
   <tr>
   <td> 
   <img width="30%" src="_static/examples/daily_active_user_count.png"/>
   </td>
   <td>
   <img width="30%" src="_static/examples/vms_count_by_project.png"/>
   </td>
   </tr>
   </table>
    <hr>

CloudMesh Metric is an open source code project that analyzes resource allocation from
several IaaS platforms. OpenStack, Nimbus, and Eucalyptus are supported. 
It will include

* a framework to explore the data via a shell 
* a framework to display the data
* a mechanism to replace the charting library
* a web framework (currently based on sphinx and flask)

CloudMesh Metric aims to enable the following capabilities

* integration of multiple centers (regions)
* integration of multiple cloud deployments within each center
* integraton of OpenStack
* Integration of HPC services
* integration of Nimbus
* integration of OpenNebula

Relevant data will be merged into a database.  
We have several convenient mechanisms to deal with the
data.  We can create summary of the data and can export in a variety
of formats. This summary is especially important for administrators
who like to find out what is happening on their clouds, but also for
users to see with who they compete for resources. 

..
  Figure 1 provides an overview of the main components that
  are communication as part of the clout metric framework.


Together thes components provide the following functionality: (a) various clouds produce
many log files, (b) the log files will be moved to a backup directory,
(c) the log files that have been recently moved will be inspected and
their contents will be added to the database, (d) the database is
queried by a cm-metric command which is a simple shell that allows to
quey for some very elementary iformation. It also allows to generate
graphics for this information and place them in a web server (e) a
sphinx portal framework - no login required (f) a flask portal
framework - login required, (g) the output format
includes png, googlecharts, and cvs tables.  


.. 
   We are also collaborating with the TAS project that developd
   XDMod. Once this project has open sourced their code we intend to
   leverage from their user interface. However, at this time the
   metics we collect are not yet integrated. Hence we can not yet use
   XDMod. We anticipate that modifications to XDMod will be conducted
   over the next year to accomplish this goal.


Authors (Alphabetical)
--------------------------------------

* Lee, Hyungro (lee212@indiana.edu)   
* von Laszewski, Gregor (laszewski@gmail.com)
* Wang, Fugang (kevinwangfg@gmail.com)

Please contact laszewski@gmail.com for mor information. Please insert
the prefix: "METRICS: " in the subject of email messages.

The contribution impact is recorded at

* https://github.com/cloudmesh/cloud-metrics/graphs
* https://github.com/cloudmesh/cloud-metrics/contributors

The original database integration was contributed by Fugang Wang and
was not tracked.

If you like to join the development efforts, please e-mail us. We can
than discuss how best you can contribute. You may have enhanced our
code already or used it in your system. If so, please let us know.

If you run into problems when using the cloud metric framework, please use our 
help form at `https://portal.cloudmesh.org/help <https://portal.cloudmesh.org/help>`_.


Production Deployment
----------------------

`Cloud Metrics <https://portal.cloudmesh.org/metrics>`_ is our main
monitoring system for clouds on FuturegGrid. In addition we also
deployed other monitoring systems such as `Inca <https://portal.cloudmesh.org/monitoring/cloud>`_ which does
monitoring at specific time intervals, and `Nimbus
<http://inca.cloudmesh.org/nimbus-stats/>`_ which offers a less
sophisticated and less comprehensive set of monitoring tools than our
framework provides. However we integrate the data from Nimbus in our
framework.

..
     default_fontsize = 20;

.. 
   WE DO NOT DISLAY IMAGE WE WILL USE PPT
   blockdiag::

      blockdiag {
	 default_node_color = lightyellow;
	 default_shape = roundedbox;
	 user_a [shape = actor];
	 user_b [shape = actor];
	 user_c [shape = actor];
	 Database [shape = flowchart.database];
	 Backup [shape = flowchart.database];

	  "Log OpenStack" -> Backup;
	  "Log Eucalyptus" -> Backup; 
	  "Log Nimbus" ->  Backup;
	  Backup -> Database;

	  Database <-> "Shell";
	  Database <-> "Sphinx Portal";
	  Database <-> "Flask Portal";

	  "Sphinx Portal" -> user_a
	  "Flask Portal" -> user_b
	  "Shell" -> user_c
       }

    **Figure 1:** cloud metrics components. 
    

Indices and tables
======================================================================

:ref:`genindex`
:ref:`modindex`
:ref:`search`

Modules
======================================================================
