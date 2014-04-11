import datetime
from cloudmesh.cloud.metric.Utility import Utility
import os

class html:

    tab = "\t"
    newline = "\n"

    
    def heading_c(self,title, c):
        return "\n" + title + "\n" + 70 * c + "\n\n"


    def heading(self,n=1, title=""):
        if n == 1:
            return self.heading_c(title, "=")
        if n == 2:
            return self.heading_c(title, "-")
        if n == 3:
            return self.heading_c(title, "^")
        if n == 4:
            return self.heading_c(title, '"')
        else:
            return self.heading_c(title, "=")


class HtmlReportsRSTs:

    ''' HtmlReportsRSTs class generates cloud usage reports in 
    reStructuredText files. Simple run the script without
    options will generate .rst files in results directory
    from 'start_date' date to 't_end_date' date which is 
    the day when you execute the script.
    In case that you want to change period of reports, 
    changing (start_date) and (t_end_date) variables in code
    is required at this time.
    '''

    
    def __init__(self):
        '''Initialize variables'''

        self.default_start_date = datetime.date(2011, 11, 01)
        self.default_end_date = datetime.date.today()

        self._set_filename()
        self._set_date()
        self._set_vars()
        self._set_template()

    def _set_filename(self):
        '''Set a default filename and a directory path'''
        self.name = "results"
        self.docs_ext = ".rst"
        self.source_path = "source"
        self.docs_path = self.source_path + "/" + self.name + "/"

        self.index_filename = "index" + self.docs_ext
        self.index_txt = None

    def _set_date(self, start_date=None, end_date=None):
        self.start_date = start_date or self.default_start_date
        self.end_date = end_date or self.default_end_date

        self.start_date_plus_six = self.start_date + datetime.timedelta(days=6)
        self.start_date_for_weekly = self.start_date
        self.week = datetime.timedelta(weeks=1)

    def _set_vars(self):
        self.count = 0

    def _set_template(self):
        self.template_path = "template"
        self.template_index = "index.rst"
        self.template_month = "YYYY-MM.rst"
        self.template_quarter = "YYYY-QQ.rst"

    def generate_index_rst(self):
        self.get_index_rst()
        self.write_index_rst()

    def get_index_template(self):
        return self.get_template(self.template_index)

    def get_monthly_template(self):
        return self.get_template(self.template_month)

    def get_quarterly_template(self):
        return self.get_template(self.template_quarter)

    def get_template(self, filename):
        filepath = self.template_path + "/" + filename
        with open(filepath, 'r') as content_file:
            content = content_file.read()
        return content

    def get_index_rst(self):
        '''Fill in the index template with the list variable'''
        index = self.get_index_template()
        toctree_list = self._get_toctree_list()
        self.index_txt = index % {"main_list": toctree_list}

    def _get_toctree_list(self):

        index_txt = ""
        start_date = self.start_date
        end_date = self.end_date

        while(1):
            if start_date > end_date:
                break

            # results.rst (index file)
            each_month = html.tab + self.docs_path + \
                start_date.strftime("%Y-%m") + html.newline
            index_txt = each_month + index_txt
            year, month, day = start_date.timetuple()[:3]
            if month % 3 == 0:
                quarter = html.tab + self.docs_path + \
                    str(year) + "-Q" + str(
                        self.get_quarter(month)) + html.newline
                index_txt = quarter + index_txt
            new_month = month + 1
            start_date = datetime.date(
                year + (new_month / 13), (new_month % 12) or 12, day)

        return index_txt

    def write_index_rst(self, content=None):
        self.write_files(
            filename=self.index_filename, content=content or self.index_txt)

    def write_files(self, filename, content):
        f = open(self.source_path + "/" + filename, "w")
        f.write(content)
        f.close

    def write_contents(self, filepath, contents):
        Utility.ensure_dir(filepath)
        f = open(filepath, "w")
        f.write(contents)
        f.close

        
    def generate_sub_rsts(self):
        """ Generate reports in this order: 1) monthly report, 2) weekly reports (normally 4-5 reports per month).
        They are grouped by: 1) nodename e.g. India, Sierra, 2) and platform e.g. eucalyptus, openstack.

        It looks like:

        Report
        ------
            Monthly
            -------
                Jan ...
                ---
                    India
                    -----
                        Eucalyptus
                        ----------
                        Openstack
                        ---------
                    Sierra
                    ------
                        Eucalyptus
                        ----------
                        Openstack
                        ---------
            Weekly
            ------
                1 week
                ------
                    India
                    -----
                    ...
        """

        monthly_report = self.get_content_monthly()
        weekly_report = ""
        month = self.start_date.timetuple()[1]

        while (1):
            if self.start_date > self.end_date:
                break

            # If a next month comes, generate contents and clear variables for
            # the next
            current_month = self.start_date.timetuple()[1]
            if ((month + 1) % 12 or 12) == current_month:
                contents = monthly_report + weekly_report

                self.write_contents(content_filepath, contents)
        
                # Clear variables
                monthly_report = self.get_content_monthly()
                weekly_report = ""
                month = current_month

            if current_month % 3 == 0:
                contents = self.get_content_quarter()
                content_filename = self.start_date.strftime(
                    "%Y-Q") + str(self.get_quarter(current_month))
                content_filepath = self.docs_path + \
                    content_filename + self.docs_ext
                self.write_contents(content_filepath, contents)

            content_filename = self.start_date.strftime("%Y-%m")
            content_filepath = self.docs_path + \
                content_filename + self.docs_ext

            self.start_date_plus_six = self.start_date + \
                datetime.timedelta(days=6)
            if (self.start_date_for_weekly + (10 * self.week)) == self.start_date:
                self.start_date_for_weekly = self.start_date_for_weekly + \
                    self.week

            # stacking up weekly reports
            weekly_report += self.get_content_weekly()

            self.start_date = self.start_date + self.week
            # END OF LOOP

        contents = monthly_report + weekly_report
        self.write_contents(content_filepath, contents)

    def get_content_quarter(self):
        width = "qwertyuioplkjhgfdsa"  # 800
        height = 1
        start_date = str(self.start_date)
        end_date = str(self.start_date_plus_six)
        current_month = self.start_date.timetuple()[1]
        quarter = self.get_quarter(current_month)
        title_of_period = self.get_first_date_of_quarter(self.start_date, quarter).strftime(
            "%B %d, %Y") + " to " + self.get_last_date_of_quarter(self.start_date, quarter).strftime("%B %d, %Y")
        month_n_year2 = "Q" + str(self.get_quarter(current_month))
        month_n_year = "Q" + str(quarter) + self.start_date.strftime(" %Y")
        month = self.start_date.strftime("%Y-") + month_n_year2

        dummy = "?time=" + datetime.datetime.utcnow().strftime("%s")
        # ---------------------------------------------------------------------
        number = 1
        metric = "count"
        platform = "all-platforms"
        nodename = "all-nodes"
        groupby = "user"

        main_title = html.heading(1, month_n_year)

        main_title += html.heading(2,
                              "Quarterly report ({0})".format(title_of_period))

        main_title += self.get_content_sub_header(nodename, platform)

        # for metrics groups by a user
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "cluster"
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/master-detailhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # all-nodes & euca
        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        platform = "eucalyptus"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s for %(month_n_year)s on %(nodename)s"
        main_title = self.get_content_sub_header(nodename, platform)
        content += main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "cluster"
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/master-detailhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # for metrics groups by a project
        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "group"
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # for metrics groups by a institution
        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "institution"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # for metrics groups by a project lead
        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "projectlead"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # india & euca
        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        platform = "eucalyptus"
        nodename = "india"
        groupby = "user"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s for %(month_n_year)s on %(nodename)s"
        main_title = self.get_content_sub_header(nodename, platform)
        content += main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/GoogleMotionChart.html"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "cluster"
        # for metrics groups by a platform
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/master-detailhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "ccvm_cores"
        title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "ccvm_mem"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "ccvm_disk"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count_node"
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/columnhighcharts.html"
        title = "Figure %(number)s. Total VMs count per node cluster for %(month_n_year)s on %(nodename)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "group"
        # for metrics groups by a project
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # for metrics groups by a institution
        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "institution"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # for metrics groups by a project lead
        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "projectlead"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # Data for OpenStack on India is only available after 06/01/2012
        if self.start_date >= datetime.date(2012, 6, 01):
            # -----------------------------------------------------------------
            number += 1
            metric = "count"
            platform = "openstack"
            nodename = "india"
            groupby = "user"

            main_title = content + \
                self.get_content_sub_header(nodename, platform)

            src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
            title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s for %(month_n_year)s on %(nodename)s"
            content = main_title + self.get_chart() % vars()
            content = content % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "runtime"
            title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s for %(month_n_year)s on %(nodename)s"
            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "count"
            groupby = "cluster"
            src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/master-detailhighcharts.html"
            title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "runtime"
            title = "Figure %(number)s. Total wall time (hour) of launched VMs over time on %(nodename)s in %(month_n_year)s"
            content += (self.get_chart() % vars()) % vars()

        # Data on Sierra is only available after 05/01/2012
        if self.start_date >= datetime.date(2012, 5, 01):
            # -----------------------------------------------------------------
            number += 1
            metric = "count"
            platform = "eucalyptus"
            nodename = "sierra"
            groupby = "user"

            main_title = content + \
                self.get_content_sub_header(nodename, platform)

            src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
            title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s for %(month_n_year)s on %(nodename)s"
            content = main_title + self.get_chart() % vars()
            content = content % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "runtime"
            title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s for %(month_n_year)s on %(nodename)s"
            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "count"
            groupby = "cluster"

            src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/master-detailhighcharts.html"
            title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "runtime"
            title = "Figure %(number)s. Total wall time (hour) of launched VMs over time on %(nodename)s in %(month_n_year)s"
            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "ccvm_cores"
            title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "ccvm_mem"
            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "ccvm_disk"
            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "count_node"
            src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/columnhighcharts.html"
            title = "Figure %(number)s. Total VMs count per node cluster for %(month_n_year)s on %(nodename)s"

            content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        platform = "nimbus"
        nodename = "hotel"
        groupby = "user"

        main_title = content + self.get_content_sub_header(nodename, platform)

        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "cluster"
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/master-detailhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        nodename = "alamo"
        groupby = "user"

        main_title = content + self.get_content_sub_header(nodename, platform)

        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s for %(month_n_year)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "cluster"
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/master-detailhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        nodename = "foxtrot"
        groupby = "user"

        main_title = content + self.get_content_sub_header(nodename, platform)

        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "cluster"
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/master-detailhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        nodename = "sierra"
        groupby = "user"

        main_title = content + self.get_content_sub_header(nodename, platform)

        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per %(groupby)s for %(month_n_year)s on %(nodename)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        groupby = "cluster"
        src = "data/%(month)s/%(nodename)s/%(platform)s/%(groupby)s/%(metric)s/master-detailhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs over time on %(nodename)s in %(month_n_year)s"
        content += (self.get_chart() % vars()) % vars()

        content = self.set_width(content, width, "100%")
        return content

    def set_width(self, text, old, new):
        return text.replace(old, new)

    def get_content_monthly(self):
        width = "qwertyuioplkjhgfdsa"  # 800
        height = 1
        start_date = str(self.start_date)
        end_date = str(self.start_date_plus_six)
        month_n_year = self.start_date.strftime("%B %Y")
        month_n_year2 = self.start_date.strftime("%m/%Y")
        month = self.start_date.strftime("%Y-%m")

        dummy = "?time=" + datetime.datetime.utcnow().strftime("%s")
        # ---------------------------------------------------------------------
        number = 1
        metric = "count"
        platform = "eucalyptus"
        nodename = "india"

        main_title = html.heading(1, month_n_year)

        main_title += html.heading(2, "Monthly report ({0})".format(month_n_year2))

        main_title += self.get_content_sub_header(nodename, platform)

        src = "data/%(month)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        src = "data/%(month)s/%(nodename)s/%(platform)s/user/GoogleMotionChart.html"
        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(month_n_year)s on %(nodename)s"
        src = "data/%(month)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"

        src = "data/%(month)s/%(nodename)s/%(platform)s/%(metric)s/master-detailhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "ccvm_cores"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "ccvm_mem"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "ccvm_disk"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count_node"

        src = "data/%(month)s/%(nodename)s/%(platform)s/%(metric)s/columnhighcharts.html"
        title = "Figure %(number)s. Total VMs count per node cluster for %(month_n_year)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        # Data for OpenStack on India is only available after 06/01/2012
        if self.start_date >= datetime.date(2012, 6, 01):
            # -----------------------------------------------------------------
            number += 1
            metric = "count"
            platform = "openstack"
            nodename = "india"

            main_title = content + \
                self.get_content_sub_header(nodename, platform)

            src = "data/%(month)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
            title = "Figure %(number)s. Total VMs %(metric)s per user for %(month_n_year)s on %(nodename)s"
            content = main_title + self.get_chart() % vars()
            content = content % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "runtime"
            title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(month_n_year)s on %(nodename)s"

            content += (self.get_chart() % vars()) % vars()

        # Data on Sierra is only available after 05/01/2012
        if self.start_date >= datetime.date(2012, 5, 01):
            # -----------------------------------------------------------------
            number += 1
            metric = "count"
            platform = "eucalyptus"
            nodename = "sierra"

            main_title = content + \
                self.get_content_sub_header(nodename, platform)

            src = "data/%(month)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
            title = "Figure %(number)s. Total VMs %(metric)s per user for %(month_n_year)s on %(nodename)s"
            content = main_title + self.get_chart() % vars()
            content = content % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "runtime"
            title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(month_n_year)s on %(nodename)s"

            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "count"

            src = "data/%(month)s/%(nodename)s/%(platform)s/%(metric)s/master-detailhighcharts.html"
            title = "Figure %(number)s. Total VMs %(metric)s over time on %(nodename)s in %(month_n_year)s"

            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "runtime"

            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "ccvm_cores"

            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "ccvm_mem"

            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "ccvm_disk"

            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "count_node"

            src = "data/%(month)s/%(nodename)s/%(platform)s/%(metric)s/columnhighcharts.html"
            title = "Figure %(number)s. Total VMs count per node cluster for %(month_n_year)s on %(nodename)s"

            content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        platform = "nimbus"
        nodename = "hotel"

        main_title = content + self.get_content_sub_header(nodename, platform)

        src = "data/%(month)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(month_n_year)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        nodename = "alamo"

        main_title = content + self.get_content_sub_header(nodename, platform)

        src = "data/%(month)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(month_n_year)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        nodename = "foxtrot"

        main_title = content + self.get_content_sub_header(nodename, platform)

        src = "data/%(month)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(month_n_year)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        nodename = "sierra"

        main_title = content + self.get_content_sub_header(nodename, platform)

        src = "data/%(month)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(month_n_year)s on %(nodename)s"
        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(month_n_year)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        content = self.set_width(content, width, "100%")
        self.count = number
        return content

    def get_content_weekly(self):
        width = "qwertyuioplkjhgfdsa"  # 800
        height = 1
        start_date = str(self.start_date)
        end_date = str(self.start_date_plus_six)

        dummy = "?time=" + datetime.datetime.utcnow().strftime("%s")
        number = self.count + 1
        metric = "count"
        platform = "eucalyptus"
        nodename = "india"

        main_title = html.heading(2,
                             "{0}-{1}".format(self.start_date.strftime("%m/%d/%Y"), self.start_date_plus_six.strftime("%m/%d/%Y")))

        main_title += self.get_content_sub_header(nodename, platform)

        src = "data/%(end_date)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(start_date)s  ~ %(end_date)s on %(nodename)s"

        content = main_title + self.get_chart() % vars()
        content = content % vars()

        # todo: should that not be  
        # content = (main_title + self.get_chart() % vars()) % vars() 
        # or 
        # content = main_title & vars() + self.get_chart() % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(start_date)s  ~ %(end_date)s on %(nodename)s"
        content += (self.get_chart() % vars()) % vars()
        
        # todo: why not make this a function and use just 
        # content += self.CREATE_GRAPH() and get the vars form the context, maybe the content should be hidden in self.content
        # than we can say just
        # self.CREATE_GRAPH({
        #    metric = "runtime",
        #    title = 'Figure %(number)s. '
        #            'Total wall time (hour) of launched VMs per user for'
        #            ' %(start_date)s  ~ %(end_date)s on %(nodename)s'
        #
        #    }
        #)
        #  we would just keep all dict variables internally in the create graph, this way previous values are stillther
        #  self.CREAT_GRAPH("clear") would clear all variables

        # ---------------------------------------------------------------------
        number += 1
        metric = "count_node"

        src = "data/%(end_date)s/%(nodename)s/%(platform)s/%(metric)s/columnhighcharts.html"
        title = "Figure %(number)s. Total VMs count per node cluster for %(start_date)s  ~ %(end_date)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        # Data for OpenStack on India is only available after 06/01/2012
        if self.start_date >= datetime.date(2012, 6, 01):
            # -----------------------------------------------------------------
            number += 1
            metric = "count"
            platform = "openstack"
            nodename = "india"

            main_title = self.get_content_sub_header(nodename, platform)

            src = "data/%(end_date)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
            title = "Figure %(number)s. Total VMs %(metric)s per user for %(start_date)s ~ %(end_date)s on %(nodename)s"
            content += main_title + self.get_chart() % vars()
            content = content % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "runtime"
            title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(start_date)s ~ %(end_date)s on %(nodename)s"

            content += (self.get_chart() % vars()) % vars()

        # Data on Sierra is only available after 05/01/2012
        if self.start_date >= datetime.date(2012, 5, 01):

            # -----------------------------------------------------------------
            number += 1
            metric = "count"
            platform = "eucalyptus"
            nodename = "sierra"

            main_title = self.get_content_sub_header(nodename, platform)

            src = "data/%(end_date)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
            title = "Figure %(number)s. Total VMs %(metric)s per user for %(start_date)s  ~ %(end_date)s on %(nodename)s"
            content += main_title + self.get_chart() % vars()
            content = content % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "runtime"
            title = "Figure %(number)s. Total %(metric)s hour of VMs submitted per user for %(start_date)s  ~ %(end_date)s on %(nodename)s"

            content += (self.get_chart() % vars()) % vars()

            # -----------------------------------------------------------------
            number += 1
            metric = "count_node"

            src = "data/%(end_date)s/%(nodename)s/%(platform)s/%(metric)s/columnhighcharts.html"
            title = "Figure %(number)s. Total VMs count per node cluster for %(start_date)s  ~ %(end_date)s on %(nodename)s"

            content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        platform = "nimbus"
        nodename = "hotel"

        main_title = self.get_content_sub_header(nodename, platform)

        src = "data/%(end_date)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(start_date)s ~ %(end_date)s on %(nodename)s"
        content += main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(start_date)s ~ %(end_date)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        nodename = "alamo"

        main_title = self.get_content_sub_header(nodename, platform)

        src = "data/%(end_date)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(start_date)s ~ %(end_date)s on %(nodename)s"
        content += main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(start_date)s ~ %(end_date)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        nodename = "foxtrot"

        main_title = self.get_content_sub_header(nodename, platform)

        src = "data/%(end_date)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(start_date)s ~ %(end_date)s on %(nodename)s"
        content += main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(start_date)s ~ %(end_date)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "count"
        nodename = "sierra"

        main_title = self.get_content_sub_header(nodename, platform)

        src = "data/%(end_date)s/%(nodename)s/%(platform)s/user/%(metric)s/barhighcharts.html"
        title = "Figure %(number)s. Total VMs %(metric)s per user for %(start_date)s ~ %(end_date)s on %(nodename)s"
        content += main_title + self.get_chart() % vars()
        content = content % vars()

        # ---------------------------------------------------------------------
        number += 1
        metric = "runtime"
        title = "Figure %(number)s. Total wall time (hour) of launched VMs per user for %(start_date)s ~ %(end_date)s on %(nodename)s"

        content += (self.get_chart() % vars()) % vars()

        content = self.set_width(content, width, "100%")

        self.count = number
        return content

    def get_index_header(self):
        """Return header of index.rst file. (outdated"""

        res =   html.heading(1, "Cloud Metric Results") + \
            "We have collected cloud utilization data from Eucalyptus on CloudMesh (previously FutureGrid) such as India and Sierra resources and provide weekly and monthly reports to show usage of system resources measured by CM Cloud Metric." + html.newline + \
            html.newline + \
            "Contents:" + html.newline + \
            html.newline + \
            ".. toctree::" + html.newline + \
            html.tab + ":maxdepth: 2" + html.newline + \
            html.newline
        return res

    def get_content_sub_header(self, nodename, platform):
        title = "Results for " + platform + " on " + nodename
        title = title.title()
        res = html.heading(3, title)
        return res

    def get_chart(self):
        res =   "" + html.newline + \
                ".. raw:: html" + html.newline + \
                "" + html.newline + \
                html.tab + "<div style=\"margin-top:10px;\">" + html.newline + \
                html.tab + "<iframe id=\"the_iframe%(number)s\" onLoad=\"calcHeight('the_iframe%(number)s');\" width=\"%(width)s\" height=\"%(height)s\" src=\"%(src)s%(dummy)s\" frameborder=\"0\"></iframe>" + html.newline + \
                html.tab + "</div>" + html.newline + \
                html.tab + "%(title)s" + html.newline

        return res

    def get_quarter(self, mon):
        return (mon - 1) // 3 + 1

    def get_first_date_of_quarter(self, current_date, num):
        year, month, day = current_date.timetuple()[:3]
        return {
            '1': datetime.date(year, 1, 1),
            '2': datetime.date(year, 4, 1),
            '3': datetime.date(year, 7, 1),
            '4': datetime.date(year, 9, 1)
        }.get(str(num), datetime.date(year, 1, 1))

    def get_last_date_of_quarter(self, current_date, num):
        year, month, day = current_date.timetuple()[:3]
        return {
            '1': datetime.date(year, 3, 31),
            '2': datetime.date(year, 6, 30),
            '3': datetime.date(year, 9, 30),
            '4': datetime.date(year, 12, 31)
        }.get(str(num), datetime.date(year, 1, 1))

    def get_search_period(self):
        '''Get start and end date of the reports '''
        self._set_date()
        return

    def get_service_info(self):
        '''Get host and service '''
        return


def main():
    result = HtmlReportsRSTs()
    # check to see which hosts and services need to be reported
    result.get_search_period()
    # generate index based on period
    result.generate_index_rst()
    result.get_service_info()
    result.generate_sub_rsts()

if __name__ == "__main__":
    main()
