==================
cm-euca-log-parser
==================

NAME
====
 **cm-euca-log-parser** - Parse log files and store values into database (MySQL)

DESCRIPTION
===========

 cat filename.log | cm-euca-log-parser <parameters>

 All log entries are included through a pipe into the program

      --nodb

        does not use the internal database, but just files

      --conf filename
        
	configuraton file of the database to be used. The
        configuration file has the following format::

          [EucaLogDB]
      	  host=HOST
      	  port=PORT
      	  user=USER
      	  passwd=PASS
      	  db=DB

        if this parameter is not specified and a database is used the
        default location for this file is in::

          ~/.cloudmesh/cloudmesh.cfg
      
      --cleardb

        This command without any parameter deletes the entire database.
        Be careful with this.

      --backup filename

      	backups the database into a named file

      --restore filename

        restores the database from the named file

      --parse type1 type2 ...

        if one of more types separated with space ar used, those types
        are parsed and included into the database, this parameter is
        optional and by default all types of interest are parsed. they
        are case insensitive

        types are print_ccInstance, refresh_resources

        BUG: Note the code does not yet analyse or store data
            from refresh resources. This was not our highest priority
       
        types we have not yet included include
           terminate_instances
           ...
           put all the other once we ignore here

      --from date_from --to date_to

        If a from and to date are specified in the following format:
        2011-11-06 00:13:15 all entries outside of these dates are
        ignored as part of the parsing step If no from and to are
        specified, all data is parsed

  
Usage tip:
==========

 Using fgrep to search for the types before piping it into this program could
 speed up processing. multiple files, can be concatenated simply with cat.

EXAMPLES
========

AUTHOR
======

 Written by H. Lee, Fugang Wang and Gregor von Laszewski. 

REPORTING BUGS
==============

 Report cm-cleanup-table bugs to laszewski@gmail.com
 Github home page: <https://github.com/cloudmesh/cloudmesh-cloud-metrics>

COPYRIGHT
=========

SEE ALSO
========
