__author__ = 'eczech'

from pynch.template import NVD3LineChart, NVD3StackedAreaChart, HighchartsLineChart, has_date_index

class VizEngine(object):

    def __init__(self, manager):
        """ Create a VizEngine that will wrap the given VizManager with convenience methods
        :param manager: Manager used to render and store templates
        """
        self.manager = manager

    def get_viz_manager(self):
        return self.manager

    def nvd3_line_chart(self, data, fill_area_cols=None, date_format='%Y-%m-%d', height=300, width=300, filename=None):
        """ Render an NVD3 Line Chart "with Focus" or "Zoom"

        This template was created based on the example here: http://nvd3.org/examples/lineWithFocus.html

        :param data: Data frame to be rendered
        :param fill_area_cols (optional): Names of columns that should have the area under them filled; if a column
                is not specified here, it will simply be plotted as a line instead of an area
        :param date_format (optional): Format for dates on x-axis, if x values are specified as dates
        :param height (optional): Height of the resulting visualization
        :param width (optional): Width of the resulting visualization
        :param filename (optional): Name of html file in which to store the resulting visualization:
                - if no filename is given, the plot will not be saved and only its content returned
                - if the filename does not have a .html suffix, one will be appended automatically
                - the full path of the resulting file will be accessible in the IPython.display.HTML
                    instance returned as result.filename (it will be an absolute path and not just a name)
        :return: IPython.display.HTML instance containing plot content (and the absolute path of the resulting
                HTML render if a filename was specified)
        """
        viz = NVD3LineChart(fill_area_cols=fill_area_cols)
        props = {
            'transform': viz.transform,
            'date_format': date_format,
            'filename': filename,
            'height': height,
            'width': width,
            # Set a flag for the template indicating whether or not the x-axis is a date or number
            'x_is_date': has_date_index(data)
        }
        return self.manager.render(viz.get_template(), data, **props)

    def nvd3_stacked_area_chart(self, data, date_format='%Y-%m-%d', height=100, width=300, filename=None):
        """ Render an NVD3 Stacked Area Chart

        This template was created based on the example here: http://nvd3.org/examples/stackedArea.html

        It includes radio options to switch between stacked area, streamgraph, and relative area plots

        :param data: Data frame to be rendered
        :param date_format (optional): Format for dates on x-axis, if x values are specified as dates
        :param height (optional): Height of the resulting visualization
        :param width (optional): Width of the resulting visualization
        :param filename (optional): Name of html file in which to store the resulting visualization:
                - if no filename is given, the plot will not be saved and only its content returned
                - if the filename does not have a .html suffix, one will be appended automatically
                - the full path of the resulting file will be accessible in the IPython.display.HTML
                    instance returned as result.filename (it will be an absolute path and not just a name)
        :return: IPython.display.HTML instance containing plot content (and the absolute path of the resulting
                HTML render if a filename was specified)
        """
        viz = NVD3StackedAreaChart()
        props = {
            'transform': viz.transform,
            'date_format': date_format,
            'filename': filename,
            'height': height,
            'width': width,
            # Set a flag for the template indicating whether or not the x-axis is a date or number
            'x_is_date': has_date_index(data)
        }
        return self.manager.render(viz.get_template(), data, **props)


    def hc_line_chart(self, data, date_format='%Y-%m-%d', height=100, width=300, filename=None):
        """ Renders a Highcharts Line Chart

        This template was created based on the example here: http://nvd3.org/examples/stackedArea.html

        :param data: Data frame to be rendered
        :param date_format (optional): Format for dates on x-axis, if x values are specified as dates
        :param height (optional): Height of the resulting visualization
        :param width (optional): Width of the resulting visualization
        :param filename (optional): Name of html file in which to store the resulting visualization:
                - if no filename is given, the plot will not be saved and only its content returned
                - if the filename does not have a .html suffix, one will be appended automatically
                - the full path of the resulting file will be accessible in the IPython.display.HTML
                    instance returned as result.filename (it will be an absolute path and not just a name)
        :return: IPython.display.HTML instance containing plot content (and the absolute path of the resulting
                HTML render if a filename was specified)
        """
        viz = HighchartsLineChart()
        props = {
            'transform': viz.transform,
            'date_format': date_format,
            'filename': filename,
            'height': height,
            'width': width,
            # Set a flag for the template indicating whether or not the x-axis is a date or number
            'x_is_date': has_date_index(data)
        }
        return self.manager.render(viz.get_template(), data, **props)
