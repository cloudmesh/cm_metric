
class CMStats(Object):
    ''' Provide usage statistics based on projects.
    The statistics include hpc data and cloud data.

    Use case is
        - getting a list of active projects last 3 months.
           e.g. fg1, fg3 are active projects last 3 months

        - getting a list of resource distribution per a project.
           e.g. fg1 uses hpc on india, openstack on sierra

    Service types:
        - command line
        - web user interface

    Options:
        - Date: from date and to date
        - metric: active projects or resource distribution

    '''

    def set_date(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date

    def usage_cloud(self):
        pass

    def usage_hpc(self):
        self.usage_ubmod()
        self.get_prj_ids()

    def usage_ubmod(self):
        pass

    def usage_all(self):
        self.usage_cloud()
        self.usage_ubmod()
        return

    def get_prj_ids(self):
        pass

if __name__ == "__main__":
    obj = CMStats()
    obj.set_date("2014-01-01","2014-03-31")
    obj.usage_all()
