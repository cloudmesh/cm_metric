#from fgmetric.FGDatabase import FGDatabase
from fgmetric.FGSearch import FGSearch
from fgmetric.FGInstances import FGInstances

class FGMetricsAPI:
    """ FG Metric Python API

    This API supports usage statistics in FG Metric way, but rely on database query.

    In a nutshell, 
    FG Metric retrieves all records on the database and collects matching records on Python programmatically.
    However, FG Metric API retrieves records on the database with search condition, especially 'ownerid' is required field to search.
    Mainly, this API calls database with a query look like " select * from instance where start >= date and end <= date and ownerid = id "
    Other than that, rest of processes are same as FG Metric.

    return value is python 'dict' type

    Description
    ===========
    FG Metric Python API to provide usage data like FG Metric's cmd tool but through python API.
    
    Requirement
    ^^^^^^^^^^^
    set_user(ownerid) should be set
    get_stats() returns selected statistics

    Sample Usage
    ^^^^^^^^^^^^
    api = FGMetricsAPI()
    api.set_user('hrlee')
    api.set_date('2012-01-01', '2012-12-31')
    api.set_metric('vmcount')
    res = api.get_stats()
    print res

    Development Status :: 2 - Pre-Alpha

    """

    def __init__(self):
        self.search = FGSearch()
        self.instances = FGInstances()
        self.init_db()

    def init_db(self):
        self.instances.db.conf()
        self.instances.db.connect()

    def set_date(self, s_date, e_date):
        self.start_date = s_date
        self.end_date = e_date

    def set_metric(self, name):
        self.metric = name

    def set_user(self, name):
        self.username = name

    def set_cloud(self, name):
        self.cloud = name

    def set_hostname(self, name):
        self.hostname = name

    def get_metric(self):
        # TBD
        return

    def get_cloud(self):
        # TBD
        return

    def set_period(self, name):
        self.period = name

    def get_period(self):
        # TBD
        return

    def get_stats(self):
        ownerids = self._get_ownerids()
        self._get_instances(ownerids)
        self.search.init_stats()
        self._set_search_vars()
        self.calculate_stats()

    def _set_search_vars(self):
        self.search.set_date([self.start_date, self.end_date])
        self.search.set_metric(self.metric)
        self.search.set_platform(self.cloud)
        self.search.set_nodename(self.hostname)

    def calculate_stats(self):
        for i in range(0, self.instances.count()):
            instance = self.instances.get_data(i, self.search._is_userinfo_needed())[0]
            if not self.search._is_in_date(instance):
                continue
            if not self.search._is_filtered(instance):
                continue
            res = self.search.collect(instance)
        print self.search.get_metric()

    def _get_ownerids(self):
        self.instances.read_userinfo({"username":self.username})
        userinfo = self.instances.userinfo
        ownerids = [element['ownerid'] for element in userinfo]
        return ownerids

    def _get_instances(self, ownerids):
        res = []
        self.instances.read_instances({}, " and ownerid in " + str(tuple(ownerids)) + "")
        #instances = self.instances.instance
        #return instances

