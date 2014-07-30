import os


class CMConst:
    DEFAULT_NIMBUS_VERSION = "2.9"
    DEFAULT_NIMBUS_DB = "sqlite3"
    DEFAULT_OPENSTACK_VERSION = "essex"

    # We still use old names but at some point, we will replace it with
    # cloudmesh - July 30, 2014
    #DEFAULT_CONFIG_FILENAME = "cloudmesh.cfg"
    DEFAULT_CONFIG_FILENAME = "futuregrid.cfg"
    DEFAULT_CONFIG_FILEPATH = os.getenv("HOME") + "/.futuregrid/"
    #DEFAULT_CONFIG_FILEPATH = os.getenv("HOME") + "/.cloudmesh/"
