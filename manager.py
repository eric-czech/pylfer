__author__ = 'eczech'

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pynch.template import default_transform
from IPython.display import HTML, IFrame
from StringIO import StringIO
import tempfile
import os


class VizManager(object):
    """ D3 visualization renderer and manager

    This generator works by saturating HTML templates using jinja2 and data provided.  The templates
    themselves should be D3 visualizations capable of incorporating a required "data" variable, along
    with an arbitrary number of other properties (for titles, captions, date formats, etc).
    """

    DEFAULT_DATA_TRANSFORM = default_transform

    def __init__(self, template_path, render_path=tempfile.gettempdir()):
        """ Create a generator using the given path as the location of all HTML templates
        :param template_path: Absolute path to HTML template files
        :param render_path: Absolute path under which rendered results will be stored
        """
        self.configure(template_path=template_path, render_path=render_path)

    @staticmethod
    def _validate_dir(path):
        exists = os.path.exists(path)
        if exists and not os.path.isdir(path):
            raise IOError('Path "{}" exists but is not a directory'.format(path))
        if not exists:
            os.makedirs(path)
        if not os.path.exists(path):
            raise IOError('Failed to create path "{}"'.format(path))

    @staticmethod
    def _ensure_extension(filename, extension):
        # Add extension to the file name if it is not present
        if not os.path.splitext(filename)[1] == extension:
            filename += extension
        return filename

    def configure(self, template_path=None, render_path=None, url_converter=None):
        """ Set properties of the visualization manager

        :param template_path: Absolute path to HTML template files
        :param render_path: Absolute path under which rendered results will be stored
        :param url_converter: Function used to convert a rendered HTML file to a URL
                - This conversion may actually involve deploying the rendered file to a different location
                - The most common use case for this is converting the local file path to a URL that
                    can be served out of a local web server (e.g. Apache on a Mac)
        :return self
        """
        if url_converter:
            self.url_converter = url_converter
        if template_path:
            VizManager._validate_dir(template_path)
            self.env = Environment(loader=FileSystemLoader(template_path))
            self.template_path = template_path
        if render_path:
            VizManager._validate_dir(render_path)
            self.render_path = render_path
        return self

    def render(self, template, data, transform=DEFAULT_DATA_TRANSFORM, filename=None, **kwargs):
        """ Renders a visualization by saturating the given template with the given data

        :param template: Name of template to saturate (e.g. 'streamgraph', 'stacked_bar', etc.)
        :param data: DataFrame to use in visualization
        :param transform: Transformation applied to data frame to convert it to an acceptable
                string form (this will be embedded somewhere in the template).  Note that "acceptable"
                forms are determined by the template but a common transformation is to CSV using a
                comma delimiter, excluding the index, and putting the frame column names in the first row
                (see visualization.DEFAULT_DATA_TRANSFORM)
        :param filename: Name of file to store render in (e.g. 'my_streamgraph')
                    - Name given will be appended to configured render path unless a full path is given,
                      in which case that path will be used instead (i.e. a string with no slashes)
                    - If no filename is specified, the render will not be saved on disk and will instead
                      be returned as an IPython.display.HTML instance sourced from a raw string
                    - If no .html extension is provided in the file name, one will be added automatically
        :param kwargs: Arguments for the template (e.g. data, date format, title, etc.)
        :return: IPython.display.HTML instance containing visualization
        """
        string_data = StringIO()
        transform(data, string_data)
        html = self.saturate(template, data=string_data.getvalue(), **kwargs)

        # Save the content to a file if a filename was provided
        # and return an HTML instance sourced form the saved location;
        # If no filename was given, return the raw HTML content as a string
        if filename:
            filename = self.save(html, filename)
            # If a url converter was configured, attempt to instead render the
            # HTML within an IFrame (usually much better for IPython Notebooks)
            if self.url_converter:
                url = self.url_converter(filename)
            # If a valid URL was returned, wrap it in an IFrame
            if url:
                html = IFrame(src=url, width=kwargs.get('width', 500), height=kwargs.get('height', 500))._repr_html_ ()
                html = HTML(data=html)    # Create an HTML instance with a raw string but also set the original file
                html.filename = filename  # path even though it wasn't technically used to source the content
                return html
            else:
                return HTML(filename=filename)
        else:
            return HTML(data=html)

    def save(self, html, filename='viz.html'):
        """ Save the given HTML content in a file

        :param html: HTML string to be saved
        :param filename: Name of file to store render in (e.g. 'my_streamgraph')
                    - Name given will be appended to configured render path (see self.configure) unless a
                      full path is given in which case that path will be used instead (i.e. a string with no slashes)
                    - If no .html extension is provided in the file name, one will be added automatically
        :return: Path of file in which render was stored
        """
        # Determine the output path
        if os.sep not in filename:
            filename = os.path.join(self.render_path, filename)

        # Add a .html extension to the file name if it is not present
        filename = VizManager._ensure_extension(filename, '.html')

        # Write the results to a file and return the path for that file
        with open(filename, 'w') as f:
            f.write(html)
        return filename

    def saturate(self, template, **kwargs):
        """ Render visualization using given template and return HTML content as a string

        :param template: Name of template to saturate (e.g. 'streamgraph.html', 'stacked_bar.html', etc.)
        :param kwargs: Arguments for the template (e.g. data, date format, title, etc.)
        :return: HTML string for visualization
        """
        # All templates end with a .html extension so add that if it
        # was not already provided as part of the template name
        template = VizManager._ensure_extension(template, '.html')

        # Fetch and render the template
        try:
            template = self.env.get_template(template)
        except TemplateNotFound:
            raise ValueError(
                'Failed to find template with the name {} in directory {}'.format(template, self.template_path)
            )
        return template.render(**kwargs)


