__author__ = 'eczech'

import pandas as pd
import json

###########################
# Abstractions & Defaults #
###########################


class Viz(object):
    def transform(self, data, output):
        """ Encodes data frames as csv/json and writes results to given output buffer
        :param data: pandas DataFrame to be converted
        :param output: output buffer into which converted output will be written
        """
        raise NotImplementedError()

    def get_name(self):
        """ Get the pretty name of this visualization type (e.g. 'NVD3 Line Chart')
        :return String name for visualization
        """
        raise NotImplementedError()

    def get_template(self):
        """ Return the name of the template file for this visualization
        :return: Filename for template with or without .html extension
        """
        raise NotImplementedError()


def default_transform(data, output):
    """ Default CSV transformation (assumes no data in index) """
    data.to_csv(output, index=False, line_terminator='\\n', sep=',')


def has_date_index(data):
    return type(data.index) is pd.DatetimeIndex


def get_data_index(data):
    # If the index is a date, transform it to UTC ms and make sure
    # to copy the result to a new index object so as not to alter
    # the original index
    if has_date_index(data):
        idx = data.index.map(lambda d: int(pd.to_datetime(d, utc=True).value / 1E6))
    else:
        idx = data.index
    return idx

############################
# NVD3 Zoomable Line Chart #
############################


class NVD3LineChart(Viz):
    """ NVD3 Line Chart Model (with "Focus" or "Zoom")
    Taken from http://nvd3.org/examples/lineWithFocus.html
    """

    def __init__(self, fill_area_cols=None):
        """ Create a new NVD3 Line Chart instance
        :param fill_area_cols: The names of the columns/series that should have their area filled under
        """
        self.fill_area_cols = fill_area_cols if fill_area_cols else []

    def get_name(self):
        return 'NVD3 Line Chart'

    def get_template(self):
        return 'nvd3_line_zoom.html'

    def transform(self, data, output):
        """ Convert data frame to json

        Generates json results in the form:
            [{'area': False, 'key': 'Series A', 'values': [{'x': <x_value>, 'y': <y_value>}, ...]}, ...]
        """

        # Get numeric data index (possibly converted from dates)
        idx = get_data_index(data)

        # Create a json object for each series in the frame and write the resulting
        # json object to the given buffer
        res = []
        for col in data:
            series = {
                'area': col in self.fill_area_cols,
                'key': col,
                'values': [{'x': x, 'y': y} for (x, y) in zip(idx, data[col])]
            }
            res.append(series)
        output.write(json.dumps(res))


###########################
# NVD3 Stacked Area Chart #
###########################

class NVD3StackedAreaChart(Viz):
    """ NVD3 Stacked Area Chart Model

    Taken from http://nvd3.org/examples/stackedArea.html
    """
    def __init__(self):
        pass

    def get_name(self):
        return 'NVD3 Stacked Area Chart'

    def get_template(self):
        return 'nvd3_stacked_area.html'

    def transform(self, data, output):
        """ Convert data frame to json

        Generates results in the form:
            [ { 'key': 'Series Name', values: [ [<timestamp>, <value>], ...] }, ... ]
        """

        # Get numeric data index (possibly converted from dates)
        idx = get_data_index(data)

        # Create a json object for each series in the frame and write the resulting
        # json object to the given buffer
        res = []
        for col in data:
            series = {
                'key': col,
                'values': [[x, y] for (x, y) in zip(idx, data[col])]
            }
            res.append(series)
        output.write(json.dumps(res))


#########################
# Highcharts line chart #
#########################


def _highcharts_series(data, series_types={}):
    """ Convert data frame to Highcharts compatible json

    Generates results in the form:
        [{
            type: 'area',
            name: 'Series name',
            <other highcharts per-series options>,
            data: [ <value>, <value>, ... ]
        }, ...]
    """

    # If the index is a date, transform it to UTC ms making sure
    # to copy the result to a new index object so as not to alter
    # the original index
    if has_date_index(data):
        idx = data.index.map(lambda d: int(pd.to_datetime(d, utc=True).value / 1E6))
    else:
        idx = data.index

    # Create a json object for each series in the frame and write the resulting
    # json object to the given buffer
    res = []
    for col in data:
        series = {
            'type': series_types[col] if col in series_types.keys() else 'line',
            'name': col,
            'data': [[x, y] for (x, y) in zip(idx, data[col])]
        }
        res.append(series)
    return res


class HighchartsLineChart(Viz):
    """ Highcharts Line Chart Model

    Taken from http://www.highcharts.com/demo/line-time-series
    """
    def __init__(self, fill_area_cols=None, chart_props=None):
        """ Create a new Highcharts Line Chart instance
        :param fill_area_cols: The names of the columns/series that should have their area filled under
        :param chart_props: Chart configuration properties (these are Highcharts specific and would include
                anything like xAxis, subtitle, title, legend, or plotOptions)
        """
        self.fill_area_cols = dict([(c, 'area') for c in fill_area_cols]) if fill_area_cols else {}
        self.chart_props = chart_props

    def get_name(self):
        return 'Highcharts Line Chart'

    def get_template(self):
        return 'hc_line_chart.html'

    def transform(self, data, output):
        """ Convert data frame to json

        Generates results in the form:
            [{
                type: 'area',
                name: 'Series name',
                <other highcharts per-series options>,
                data: [ <value>, <value>, ... ]
            }, ...]
        """
        res = _highcharts_series(data, series_types=self.fill_area_cols)
        res = {'series': res}
        if self.chart_props:
            res.update(self.chart_props)
        output.write(json.dumps(res))

class HighchartsConfigurableLineChart(Viz):
    """ Configurable Highcharts Line Chart Model

    Taken from http://www.highcharts.com/demo/line-time-series
    """
    def __init__(self):
        """ Create a new Highcharts Line Chart instance"""

    def get_name(self):
        return 'Highcharts Configurable Line Chart'

    def get_template(self):
        return 'hc_brian.html'

    def transform(self, data, output):
        """ Convert data frame to json

        Generates results in the form:
            [{
                type: 'area',
                name: 'Series name',
                <other highcharts per-series options>,
                data: [ <value>, <value>, ... ]
            }, ...]
        """
        res = _highcharts_series(data)
        output.write(json.dumps(res))
