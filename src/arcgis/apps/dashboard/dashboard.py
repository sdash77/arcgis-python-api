import atexit
import json
import arcgis

_DASHBOARD_VERSION = 27

_created_dashboards = []


class Dashboard(object):
    def __init__(self, title, description, summary='', tags=None):
        """
        Creates a Dashboard Object.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        title                       Optional string. Title or Caption for the
                                   Dashboard.
        -------------------------   -------------------------------------------
        description                 Optional string. Description for the Dashboard.
        -------------------------   -------------------------------------------
        summary                     Optional string. Summary of the Dashboard.
        -------------------------   -------------------------------------------
        tags                        Optional string. Comma separated tags.
        =========================   ===========================================
        """

        #Dashboard variables start here.

        if not title:
            raise Exception("Please specify a title.")

        if not description:
            raise Exception("Please specify a description.")

        self.title = title
        self.description = description

        self.summary = summary
        self.tags = tags if tags else ''
        self.elements = []

        self._orientation = 'col'
        self._theme = 'light'

        self._header = None
        self._side_panel = None
        self._layout = {}
        self._widgets = []
        #Dashboard variables end here.

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._orientation = value
        if value not in ["row", "col"]:
            self._orientation = "row"

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, value):
        self._theme = value
        if value not in ["light", "dark"]:
            self._theme = "light"

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        self._header = value

    @property
    def side_panel(self):
        return self._side_panel

    @side_panel.setter
    def side_panel(self, value):
        self._side_panel = value

    def _convert_to_json(self):
        json_data = {
            "version": _DASHBOARD_VERSION,
            "widgets":
                [
                    element._convert_to_json()
                    for element in self.elements
                ],
            "settings":
                {
                    "maxPaginationRecords": 50000,
                    "allowElementResizing": False
                },
            "mapOverrides":
                {
                    "trackedFeatureRadius": 60
                },
            "theme": self.theme,
            "themeOverrides": {},
            "numberPrefixOverrides": [],
            "layout": self._layout
        }

        if self.header:
            json_data['headerPanel'] = self.header._convert_to_json()

        if self.side_panel:
            json_data['leftPanel'] = self.side_panel._convert_to_json()

        return json_data

    @property
    def layout(self):
        """
        :return: Layout of the dashboard
        """
        return self._layout

    @layout.setter
    def layout(self, value):
        """
        Set the layout of the dashboard.
        """
        self.elements = value['widgets']
        del value['widgets']
        self._layout = {"rootElement" : value}

    @property
    def widgets(self):
        """
        :return: widgets of the dashboard
        """
        return self._widgets

    def publish(self, gis):
        return gis.content.add({
            'type': 'Dashboard',
            'description': self.description,
            'title': self.title,
            'overwrite': 'true',
            'text': json.dumps(self._convert_to_json())}
        )

    def from_dashboard(self, dashboard_item):
        widget_map = {
            "indicatorWidget": Indicator,
            "gaugeWidget": Gauge,
            "pieChartWidget": PieChart,
            "serialChartWidget": SerialChart,
            "detailsWidget": Details,
            "richTextWidget": RichText,
            "listWidget": List,
            "embeddedContentWidget": EmbeddedContent,
            "legendWidget": MapLegend
        }
        item_json = dashboard_item.get_data()
        for widget_json in item_json["widgets"]:
            type = widget_json["type"]
            self._widgets.append(widget_map[type]._from_json(widget_json))

        return dashboard_item

    @staticmethod
    def _publish_random(widget):
        from arcgis.apps import add_row
        gis = arcgis.env.active_gis
        import random
        import string

        letters = string.ascii_lowercase
        title = ''.join(random.choice(letters) for i in range(10))
        summary = ''.join(random.choice(letters) for i in range(10))
        db = Dashboard(title, summary)

        if widget.type == 'headerPanel':
            db.header = widget
        elif widget.type == 'leftPanel':
            db.side_panel = widget
        else:
            if hasattr(widget, 'item') and widget.item.type == 'mapWidget':
                db.layout = add_row([widget.item, widget])
            else:
                db.layout = add_row([widget])

        db = db.publish(gis)
        _created_dashboards.append((gis, db))
        url = f'{gis.url}/apps/opsdashboard/index.html#/{db.itemid}'

        return url


@atexit.register
def _delete_objects():
    for dashboard in _created_dashboards:
        gis = dashboard[0]
        db = dashboard[1]
        db.delete(force=True)