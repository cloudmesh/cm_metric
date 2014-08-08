import sys
import os
import datetime
from flask import Flask, jsonify
from flask.views import View
from Mimerender import mimerender
from cm_metric.shell.Database import Database
from dateutil import parser

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def get_index_page():
    print "The server is running"
    return "The server is running\n"

@app.route('/<path:filename>')
def send_foo(filename):
    return app.send_static_file(filename)

@app.route('/metric/<cloudname>/<hostname>/<userid>/<metric>/<timestart>/<timeend>/<period>')
@app.route('/metric/<cloudname>/<hostname>/<userid>/<metric>/<timestart>/<timeend>/<period>/<projectid>')
def get_metric(cloudname, hostname, userid, metric, timestart, timeend, period,
               projectid=None):

    # Setting search options (first step)

    search = SearchSettings()

    search.set_cloud(cloudname)
    search.set_date(timestart,timeend)
    search.set_metric(metric)
    search.set_userid(userid)
    search.set_period(period)
    search.set_host(hostname)
    search.set_projectid(projectid)

    # Getting values regarding selected metric (Second step)
    #
    # - Each metric such as e.g. VMCount, WallTime, or UserCount
    # - can be collected by creating its own class instance.
    # - VMCount, WallTime, and UserCount are inherited by
    # - CloudMetricBase()

    l_metric = metric.lower()
    if l_metric == "vmcount": # or metric == "None":
        metrics = VMCount()
        metrics.set_search_settings(search)
    elif l_metric in ["walltime", "runtime", "wallclock"]:
        metrics = WallTime()
        metrics.set_search_settings(search)
    elif l_metric in ["usercount", "user"]:
        metrics = UserCount()
        metrics.set_search_settings(search)
    elif l_metric in ['top-ten-projects']:
        metrics = TopTenProjects()
        metrics.set_search_settings(search)
    elif l_metric in ['top-ten-users']:
        metrics = TopTenUsers()
        metrics.set_search_settings(search)
    else:
        if projectid and projectid != "None":
            metrics = ProjectSummary()
            metrics.set_search_settings(search)
        else:
            metrics = SummaryAll()
            metrics.set_search_settings(search)

    result = metrics.dispatch_request()
    #print result
    return result

@app.route('/metric-summary/')
@app.route('/metric-summary/<timeline>/')
@app.route('/project-summary/<projectid>/')
def get_metric_summary(cloudname="None", hostname="None", userid="None",
                       metric="None", timeline="None", timestart="None", timeend="None",
                       period="None", projectid="None"):

    return get_metric(cloudname, hostname, userid, metric,
                      timestart, timeend, period, projectid)

@app.route('/top-ten-projects/')
def get_top_ten_projects(cloudname="None", hostname="None", userid="None",
                       metric="None", timestart="None", timeend="None",
                       period="None", projectid="None"):

    return get_metric(cloudname, hostname, userid, "top-ten-projects",
                      timestart, timeend, period, projectid)

@app.route('/top-ten-users/')
def get_top_ten_users():
    return get_metric("None","None","None", "top-ten-users", "None", "None",
                      "None", "None")

@app.route('/metric/list_vms')
def get_list_vms():

    lvms = ListVMs()
    result = lvms.dispatch_request()
    print result
    return result

################################
# classes for metric api
################################

class SearchSettings:
    '''
    SearchSettings class
    collects user inputs to refine results
    '''
    def __init__(self):
        self.from_date = None # datetime
        self.to_date = None # datetime
        self.period = None
        self.metric = None
        self.host = None
        self.iaas = None
        self.userid = None
        self.projectid = None

    def __str__(self):
        result = ""
        result += "from_date: %s\n" % self.from_date
        result += "to_date:   %s\n" % self.to_date
        result += "period:    %s\n" % self.period
        result += "metric:    %s\n" % self.metric
        result += "host:    %s\n" % self.host
        result += "iaas:      %s\n" % self.iaas
        result += "userid:      %s\n" % self.userid
        result += "projectid:      %s\n" % self.projectid
        return result

    def set_date(self, from_date, to_date):
        if from_date != "None":
            self.from_date = parser.parse(from_date)
        if to_date != "None":
            self.to_date = parser.parse(to_date)

    def set_period(self, period):
        self.period = period

    def set_metric(self, metric):
        self.metric = metric

    def set_host(self, host):
        self.host = host

    def set_iaas(self, cloud):
        self.iaas = cloud

    def set_cloud(self, cloud):
        ''' link to set_iaas '''
        self.set_iaas(cloud)

    def set_userid(self, userid):
        self.userid = userid

    def set_projectid(self, name):
        self.projectid = name

class CloudMetricBase(View):

    def __init__(self):
        self.db = Database()
        self.db.conf()
        self.db.connect()
        self.cloudservice = None
        self.data = { "default": None }
        self.where_clause = ""
        self.where_clause_extra = ""
        #self.search = SearchSettings()

    @mimerender
    def dispatch_request(self):
        self.read_cloud_service()
        self.read_project_info()
        self.read_vms()
        message = {"message" : self.data }
        return message

    def set_result(self, data):
        self.data['default'] = data

    def add_result(self, data):
        # data (dict) addes to the current data
        # data (other types) replaces 'message'
        try:
            for k,v in data.iteritems():
                self.data[k] = v
        except:
            self.data['default'] = data

    def get_result(self, keyname='default'):
        return self.data[keyname]

    def read_cloud_service(self):
        res = self.db.read_cloudplatform()
        new_res = {}
        for cloud in res:
            new_res[cloud['cloudPlatformId']] = cloud
            self.cloudservice = new_res

    def read_project_info(self):
        if self.search.projectid == "None" or not self.search.projectid:
            return

        self._read_project_basic()
        ids = self._read_project_userids()
        self._add_columns_to_where("ownerid", ids)
        self._read_project_summary()

    def _read_project_basic(self):
        ''' Basic project info such as title, id, and leader '''
        column = ", ".join(['title', 'projectid', 'projectlead'])
        table = self.db.projectinfo_table
        where_clause = " where projectid=%s " % self.search.projectid
        query = "select %(column)s from %(table)s %(where_clause)s " % vars()
        res = self._execute_query(query)
        self.add_result({"project": res})

    def _read_project_summary(self):
        t_instance = self.db.instance_table
        t_platform = self.db.cloudplatform_table
        t_userinfo = self.db.userinfo_table
        projectid = self.search.projectid

        """ Summary for host or platform """

        column = (" cloudplatformidref, hostname, %(t_platform)s.platform," \
                + " version, count(*) as count ") % vars()

        t_ownerids = (" (select distinct ownerid from %(t_userinfo)s where " \
                + " project='fg%(projectid)s') as table_for_userids ") % vars()

        where_clause = (" where %(t_instance)s.ownerid=table_for_userids.ownerid " \
                        + " and %(t_platform)s.cloudplatformid=cloudplatformidref " \
                       ) % vars()

        groupby = "hostname" # Or platform
        extra = " group by %(t_platform)s.%(groupby)s " % vars()
        table = " %(t_instance)s, %(t_platform)s, %(t_ownerids)s " % vars()
        query = " select %(column)s from %(table)s %(where_clause)s %(extra)s " % vars()

        res = self._execute_query(query)
        self.add_result({"project-summary": 
                         {"meta": { "groupby" : groupby },
                          "objects": res}})
        
        """ Summary for other clouds which don't have project account. """

        '''
        # Extra for nimbus and other which don't have project accounts
        select cloudplatformidref, hostname, cloudplatform.platform,version,count(*) from instance, cloudplatform,
        (select distinct username from userinfo where project='fg82' and
         username!='admin') as b where instance.ownerid=b.username and
        cloudplatform.cloudplatformid = cloudplatformidref group by
        cloudplatformidref;
        '''
        column = column # same as before
        t_ownerids = (" (select distinct username from %(t_userinfo)s where " \
                      + " project='fg%(projectid)s' and username!='admin') as "\
                      + " table_for_userids ") % vars()

        where_clause = (" where " \
                        + " %(t_instance)s.ownerid=table_for_userids.username " \
                        + " and %(t_platform)s.cloudplatformid=cloudplatformidref " \
                       ) % vars()

        extra = extra # same as before
        table = " %(t_instance)s, %(t_platform)s, %(t_ownerids)s " % vars()
        query = " select %(column)s from %(table)s %(where_clause)s %(extra)s " % vars()

        res = self._execute_query(query)
        self.add_result({"project-summary-extra": 
                         { "meta": { "groupby" : groupby },
                           "objects": res}})

        """ Summary for users """
        column = " first_name, last_name, count(*) as count " 
        t_ownerids = (" (select distinct ownerid, username, first_name, " \
                      + " last_name from %(t_userinfo)s where " \
                      + " project='fg%(projectid)s') as table_for_userids ") \
                      % vars()
        where_clause = "where %(t_instance)s.ownerid=table_for_userids.ownerid"\
                % vars()
        groupby = "username"
        orderby = "count"
        extra = " group by %(groupby)s order by %(orderby)s " \
                % vars()
        table = " %(t_instance)s, %(t_ownerids)s " % vars()
        query = " select %(column)s from %(table)s %(where_clause)s %(extra)s " % vars()

        print query
        res = self._execute_query(query)
        self.add_result({"user-summary": 
                         {"meta": { "groupby" : groupby,
                                    "orderby" : orderby },
                          "objects": res}})

    def _read_project_userids(self):
        column = " distinct ownerid "
        table = self.db.userinfo_table
        where_clause = " where project='fg%s' " % self.search.projectid
        query = "select %(column)s from %(table)s %(where_clause)s " % vars()
        res = self._execute_query(query)
        return res

    def _execute_query(self, query):
        cursor = self.db.cursor
        results = None
        try:
            cursor.execute(query)
            results = cursor.fetchall()
        except:
            print sys.exc_info()
        return results

    def _add_columns_to_where(self, column_name, results):
        ids = map(lambda x: x[column_name], results)
        ids = "'" + "', '".join(map(str, ids)) + "'"
        res = "%s in (%s)" % (column_name, ids)
        self.add_where_clause(res)

    def get_where_clause(self):
        self.generate_where_clause()
        return self.where_clause

    def add_where_clause(self, extra):
        self.where_clause_extra = extra

    def generate_where_clause(self):
        where = []

        # basic for join table
        where.append("cloudplatform.cloudplatformid = \
                     instance.cloudplatformidref")

        if self.search.metric.lower() == "usercount":
            where.append("(userinfo.ownerid = instance.ownerid \
                         or userinfo.username = instance.ownerid)")

        if self.search.iaas != "None":
            iaas_ids = self.get_iaas_ids(self.search.iaas)
            if iaas_ids:
                ids = ', '.join(map(str, iaas_ids))
            else:
                ids = "'" + self.search.iaas + "'"
            where.append("cloudplatformidref in (%s)" % ids)

        if self.search.host != "None":
            host_ids = self.get_host_ids(self.search.host)
            if host_ids:
                ids = ', '.join(map(str, host_ids))
            else:
                ids = "'" + self.search.host + "'"
            where.append("cloudplatformidref in (%s)" % ids)

        # user id is a bit different.
        # To include nimbus, userid should be included in the search
        if self.search.userid != "None":
            owner_ids = self.get_owner_ids(self.search.userid)
            if owner_ids:
                owner_ids.append(self.search.userid)
                ids = "'" + "', '".join(map(str, owner_ids)) + "'"
            else: # there is no such user
                ids = "'" + self.search.userid + "'"
            where.append("ownerid in (%s)" % ids)

        if self.search.from_date:
            where.append("t_start >= '%s'" % str(self.search.from_date))
        if self.search.to_date:
            where.append("t_end <= '%s'" % str(self.search.to_date))

        if self.where_clause_extra:
            where.append(self.where_clause_extra)

        self.where_clause = " where " + " and ".join(map(str,where))
        return self.where_clause

    def get_owner_ids(self, name):
        ids = []
        self.db.cursor.execute("select ownerid from %s where username='%s'" \
                               % (self.db.userinfo_table, name))
        results = self.db.cursor.fetchall()
        ids = map(lambda x: x['ownerid'],results)
        return ids
    
    def get_host_ids(self, name):

        ids = []

        self.db.cursor.execute("select cloudPlatformId from %s where hostname="\
                               + "'%s'" % (self.db.cloudplatform_table, name))
        results = self.db.cursor.fetchall()
        for row in results:
            ids.append(row['cloudPlatformId'])
        return ids

    def get_iaas_ids(self, name):
        ids = []

        self.db.cursor.execute("select cloudPlatformId from %s where platform="\
                                + "'%s'" % (self.db.cloudplatform_table, name))
        results = self.db.cursor.fetchall()
        for row in results:
            ids.append(row['cloudPlatformId'])
        return ids

    def set_search_settings(self, searchObject):
        self.search = searchObject

    def map_cloudname(self):
        for record in self.get_result():
            try: 
                cloudname = self.cloudservice[record['cloudplatformidref']]
            except:
                print record

    def read_vms(self):
        # not implemented
        pass

class ProjectSummary(CloudMetricBase):
    def __init__(self):
        CloudMetricBase.__init__(self)

class TopTenUsers(CloudMetricBase):
    def __init__(self):
        CloudMetricBase.__init__(self)

    def _top10_users(self):

        cursor = self.db.cursor
        t_instance = self.db.instance_table
        t_userinfo = self.db.userinfo_table
        t_projectinfo = self.db.projectinfo_table
        last_3_months = str(get_last_3_months())
        groupby = 'username'
        orderby = 'count desc'
        extra = 'limit 10'

        query = "select first_name, last_name, count(*) as count from \
                %(t_instance)s inner join %(t_userinfo)s on \
                %(t_instance)s.ownerid=%(t_userinfo)s.ownerid \
                where t_start > '%(last_3_months)s' group by %(groupby)s \
                order by %(orderby)s %(extra)s" % vars()

        try:
            cursor.execute(query)
            self.add_result({self.search.metric: { 
                "meta": {
                    "groupby": groupby,
                    "orderby": orderby},
                "objects": cursor.fetchall()}})
        except:
            print sys.exc_info()

    def read_vms(self):
        self._top10_users()


class TopTenProjects(CloudMetricBase):
    def __init__(self):
        CloudMetricBase.__init__(self)

    def _top10_projects(self):

        cursor = self.db.cursor
        t_instance = self.db.instance_table
        t_userinfo = self.db.userinfo_table
        t_projectinfo = self.db.projectinfo_table
        last_3_months = str(get_last_3_months())
        groupby = 'projectid'
        orderby = 'count desc'
        extra = 'limit 10'

        query = "select projectid, title, count(*) as count from \
                %(t_instance)s inner join %(t_userinfo)s on \
                %(t_instance)s.ownerid=%(t_userinfo)s.ownerid \
                inner join %(t_projectinfo)s on \
                concat('fg',%(t_projectinfo)s.projectid)=%(t_userinfo)s.project\
                where t_start > '%(last_3_months)s' group by %(groupby)s \
                order by %(orderby)s %(extra)s" % vars()

        try:
            cursor.execute(query)
            self.add_result({"10-projects": { 
                "meta": {
                    "groupby": groupby,
                    "orderby": orderby},
                "objects": cursor.fetchall()}})
        except:
            print sys.exc_info()

    def read_vms(self):
        self._top10_projects()

class SummaryAll(CloudMetricBase):
    def __init__(self):
        CloudMetricBase.__init__(self)

    def _top10_projects(self):

        cursor = self.db.cursor
        t_instance = self.db.instance_table
        t_userinfo = self.db.userinfo_table
        t_projectinfo = self.db.projectinfo_table
        last_3_months = str(get_last_3_months())
        groupby = 'projectid'
        orderby = 'count desc'
        extra = 'limit 10'

        query = "select projectid, title, count(*) as count from \
                %(t_instance)s inner join %(t_userinfo)s on \
                %(t_instance)s.ownerid=%(t_userinfo)s.ownerid \
                inner join %(t_projectinfo)s on \
                concat('fg',%(t_projectinfo)s.projectid)=%(t_userinfo)s.project\
                where t_start > '%(last_3_months)s' group by %(groupby)s \
                order by %(orderby)s %(extra)s" % vars()

        try:
            cursor.execute(query)
            self.add_result({"10-projects": { 
                "meta": {
                    "groupby": groupby,
                    "orderby": orderby},
                "objects": cursor.fetchall()}})
        except:
            print sys.exc_info()

    def read_vms(self):
        self._platform_usage()
        self._top10_projects()

    def _platform_usage(self):
        cursor = self.db.cursor
        table = self.db.instance_table
        table2 = self.db.cloudplatform_table
        where_clause = self.get_where_clause()
        last_3_months = str(get_last_3_months())
        groupby = "%(table2)s.platform, hostname" % vars()
        orderby = ""

        query = "select %(table2)s.platform, hostname, count(*) as count from \
        %(table)s, %(table2)s where t_start > '%(last_3_months)s' and \
        %(table2)s.cloudplatformid=%(table)s.cloudplatformidref group by \
        %(groupby)s" % vars()
        
        try:
            cursor.execute(query)
            #self.set_result(cursor.fetchall())
            self.add_result({"platform-summary": { 
                "meta": {
                    "groupby": groupby,
                    "orderby": orderby},
                "objects": cursor.fetchall()}})
        except:
            print sys.exc_info()


class VMCount(CloudMetricBase):

    def __init__(self):
        CloudMetricBase.__init__(self)

    def read_vms(self):
        cursor = self.db.cursor
        table = self.db.instance_table
        table2 = self.db.cloudplatform_table
        where_clause = self.get_where_clause()
        query = "select DATE_FORMAT(date,'%%Y %%b') as 'YEAR MONTH', \
                %(table2)s.platform as 'CLOUDNAME', \
                count(*) as 'VMCOUNT' \
                from %(table)s, %(table2)s \
                %(where_clause)s \
                group by %(table2)s.platform, \
                YEAR(date), MONTH(date)" % vars()
        try:
            cursor.execute(query)
            self.set_result(cursor.fetchall())
        except:
            print sys.exc_info()

class WallTime(CloudMetricBase):

    def __init__(self):
        CloudMetricBase.__init__(self)

    def read_vms(self):
        cursor = self.db.cursor
        table = self.db.instance_table
        table2 = self.db.cloudplatform_table
        where_clause = self.get_where_clause()
        query = "select DATE_FORMAT(date,'%%Y %%b') as 'YEAR MONTH', \
                %(table2)s.platform as 'CLOUDNAME', \
                FORMAT(SUM(time_to_sec(timediff(t_end,t_start))/60/60),2) \
                as 'WallTime (Hrs)' \
                from %(table)s, %(table2)s \
                %(where_clause)s \
                group by %(table2)s.platform, \
                YEAR(date), MONTH(date)" % vars()
        try:
            cursor.execute(query)
            self.set_result(cursor.fetchall())
        except:
            print sys.exc_info()

class UserCount(CloudMetricBase):

    def __init__(self):
        CloudMetricBase.__init__(self)

    def read_vms(self):
        cursor = self.db.cursor
        table = self.db.instance_table
        table2 = self.db.cloudplatform_table
        table3 = self.db.userinfo_table
        where_clause = self.get_where_clause()
                #CONCAT(first_name, " ", last_name) as 'NAME', \
        query = "select DATE_FORMAT(date,'%%Y %%b') as 'YEAR MONTH', \
                %(table2)s.platform as 'CLOUDNAME', \
                COUNT(userinfo.username) as 'USERCOUNT' \
                from %(table)s, %(table2)s, %(table3)s \
                %(where_clause)s \
                group by %(table2)s.platform, \
                YEAR(date), MONTH(date)" % vars()
        try:
            print "Be patient, it takes about 10 to 30 seconds ..."
            cursor.execute(query)
            self.set_result(cursor.fetchall())
        except:
            print sys.exc_info()

# utility function
def get_last_3_months():
    return get_last_months(3)

def get_last_months(month):
    m = int(month)
    return (datetime.date.today() - datetime.timedelta(m*365/12)).isoformat()

#app.add_url_rule('/list_vms.json', view_func = ListVMs.as_view('list_vms'))

if __name__ == "__main__":
    app.run(host=os.environ["FG_HOSTING_IP"],
            port=int(os.environ["FG_HOSTING_PORT"]),debug=True)
