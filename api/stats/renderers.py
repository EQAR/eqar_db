import json

from django.conf import settings

from rest_framework.renderers import BaseRenderer, JSONRenderer

class InfogramJSONRenderer(JSONRenderer):
    """
    Renderer which returns "tablized" JSON for consumption by Infogram

    derived from https://github.com/mjumbewu/django-rest-framework-csv
    """
    format = 'infogram'

    level_sep = '_' # used for flattening nested lists/dicts
    empty_cell = '0' # cells otherwise empty will be filled with this value
    header = None
    labels = None  # {'<field>':'<label>'}

    def render(self, data, media_type=None, renderer_context={}):
        """
        Renders serialized data into a collection of tables for Infogram/Prezi:

        - The top-level object is a list representing sheets.
        - Each sheet is a two-level list, the outer list representing rows, the inner lists the rows' columns.
        """
        if data is None:
            return []

        header = renderer_context.get('header', self.header)
        labels = renderer_context.get('labels', self.labels)
        encoding = renderer_context.get('encoding', settings.DEFAULT_CHARSET)

        if isinstance(data, list):
            # if data is a list, it will be converted into a single table/sheet
            tablized = [ list(self.tablize(data, header=header, labels=labels)) ]
        elif isinstance(data, dict):
            # if data is a dict, each element will become one sheet
            tablized = []
            for sheet_name in data:
                if isinstance(data[sheet_name], dict) or isinstance(data[sheet_name], list):
                    # nested lists or dicts will be converted
                    sheet = list(self.tablize(data[sheet_name], header=header, labels=labels))
                    sheet[0][0] = str(sheet_name) # All values must be strings
                else:
                    # not very meaningful, but to ensure all kind of data can be rendered:
                    # scalar values are simply put on a sheet by themselves
                    sheet = [ [ str(sheet_name) ], [ str(data[sheet_name]) ] ]
                tablized.append(sheet)

        return super().render(tablized, media_type, renderer_context)


    def tablize(self, data, header=None, labels=None):
        """
        Convert a list of data into a table.

        If there is a header provided to tablize it will efficiently yield each
        row as needed. If no header is provided, tablize will need to process
        each row in the data in order to construct a complete header. Thus, if
        you have a lot of data and want to stream it, you should probably
        provide a header to the renderer (using the `header` attribute, or via
        the `renderer_context`).
        """
        # Try to pull the header off of the data, if it's not passed in as an
        # argument.
        if not header and hasattr(data, 'header'):
            header = data.header

        if data:
            # First, flatten the data (i.e., convert it to a list of
            # dictionaries that are each exactly one level deep).  The key for
            # each item designates the name of the column that the item will
            # fall into.
            data = self.flatten_data(data)

            # Get the set of all unique headers, and sort them (unless already provided).
            if not header:
                data = tuple(data)
                header_fields = set()
                for item in data:
                    header_fields.update(list(item.keys()))
                header = sorted(header_fields)

            # Return your "table", with the headers as the first row.
            if labels:
                yield [labels.get(x, x) for x in header]
            else:
                yield list(header) # header could be a touple, but result should be mutable

            # Create a row for each dictionary, filling in columns for which the
            # item has no data with None values.
            for item in data:
                yield [item.get(key, self.empty_cell) for key in header]

        elif header:
            # If there's no data but a header was supplied, return just the header.
            if labels:
                yield [labels.get(x, x) for x in header]
            else:
                yield list(header)

        else:
            # empty list if there's no data and no header
            pass

    def flatten_data(self, data):
        """
        Convert the given data collection to a list of dictionaries that are
        each exactly one level deep. The key for each value in the dictionaries
        designates the name of the column that the value will fall into.
        """
        for item in data:
            flat_item = self.flatten_item(item)
            yield flat_item

    def flatten_item(self, item):
        if isinstance(item, list):
            flat_item = self.flatten_list(item)
        elif isinstance(item, dict):
            flat_item = self.flatten_dict(item)
        else:
            flat_item = {'': self.convert_value(item)}

        return flat_item

    def convert_value(self, value):
        """
        apply any kind of conversion to all values

        by default, converts all numbers to string, required for Prezi.com
        - subclass and override as needed
        """
        return str(value)

    def nest_flat_item(self, flat_item, prefix):
        """
        Given a "flat item" (a dictionary exactly one level deep), nest all of
        the column headers in a namespace designated by prefix.  For example:

         header... | with prefix... | becomes...
        -----------|----------------|----------------
         'lat'     | 'location'     | 'location.lat'
         ''        | '0'            | '0'
         'votes.1' | 'user'         | 'user.votes.1'

        """
        nested_item = {}
        for header, val in flat_item.items():
            nested_header = self.level_sep.join([prefix, header]) if header else prefix
            nested_item[nested_header] = val
        return nested_item

    def flatten_list(self, l):
        flat_list = {}
        for index, item in enumerate(l):
            index = str(index)
            flat_item = self.flatten_item(item)
            nested_item = self.nest_flat_item(flat_item, index)
            flat_list.update(nested_item)
        return flat_list

    def flatten_dict(self, d):
        flat_dict = {}
        for key, item in d.items():
            flat_item = self.flatten_item(item)
            nested_item = self.nest_flat_item(flat_item, key)
            flat_dict.update(nested_item)
        return flat_dict


class PaginatedInfogramJSONRenderer(InfogramJSONRenderer):
    """
    Paginated renderer - use when pagination is turned on for DRF

    Generally, InfogramJSONRenderer is not ideally used with pagination - but this class makes
    sure that if it is, then only the results list is rendered into a table
    """
    results_field = 'results' # default of DRF pagination classes - adjust if needed

    def render(self, data, media_type=None, renderer_context=None):
        # there is no explicit way to recognise a paginated result, but if the following is true
        # it probably is one:
        if isinstance(data, dict) and isinstance(data.get(self.results_field, None), list):
            data = data.get(self.results_field)
        return super().render(data, media_type=media_type, renderer_context=renderer_context)

