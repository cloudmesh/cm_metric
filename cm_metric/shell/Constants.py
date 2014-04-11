import os


class CMConst:
    DEFAULT_NIMBUS_VERSION = "2.9"
    DEFAULT_NIMBUS_DB = "sqlite3"
    DEFAULT_OPENSTACK_VERSION = "essex"

    DEFAULT_CONFIG_FILENAME = "cloudmesh.cfg"
    DEFAULT_CONFIG_FILEPATH = os.getenv("HOME") + "/.cloudmesh/"
