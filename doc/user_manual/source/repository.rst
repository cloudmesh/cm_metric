Directory Structure
======================================================================

We have designed a directory layout as follows:


.. csv-table:: Main directory structure of cloud metric 
   :header: Directory, Description
   :widths: 10, 50
                  
                  data, png files
                  doc , Documentation
                  draft, Software development plans
                  misc, miscellaneous files
                  examples, Examples for CloudMetrics CLI
                  fghpc, HPC Real-time monitoring
                  cm_metric, Main development
                  fgmonitor, Real-time monitoring
                  fgweb, CherryPy of CloudMetrics
                  fgws, Flask WSGI service
                  lighttpd, lighttpd
                  results, Sphinx for statistics
                  todo, outdated
                  doc-old, outdated documentation
		  deprecated, outdated


File contents
=============

::

  | CMAnalyzer.py - old version of metric analyzer
  | CMCollectFiles.py - log backup tool
  | CMConverter.py - data converting tool from Nimbus, Openstack to Cloud Metrics
  | CMEucaMetricsDB.py - old version of metrics db
  | CMHighcharts.py - Highcharts API
  | CMInstall.py - Initializer of Cloud Metrics (db configuration, etc)
  | CMLogParser.py - Eucalyptus log parser
  | CMMetricsCli.py - fg-metric-cli command tool
  | CMNovaDB.py - outdated OpenStack API
  | CMParser.py - old version of VM instance class
  | CMSearch.py - New version of 
  | CMTimeZone.py - TimeZone helper for managing timestamp in logs
  | CMCharts.py - Chart library API
  | CMConstants.py - Constants class
  | CMDatabase.py - New version of database class
  | CMGoogleMotionChart.py - Old version of Google Chart API
  | CMHighchartsTemplate.py - outdated Highcharts API
  | CMInstances.py - New version of VM instance class
  | CMMetricsAPI.py - New version of Metrics API class
  | CMMetrics.py - New version of main class of Cloud Metrics
  | CMNovaMetric.py - outdated OpenStack class for metric
  | CMPygooglechart.py - outdated python google chart API
  | CMTester.py - outdated Tester
  | CMUtility.py - Utility libraries
