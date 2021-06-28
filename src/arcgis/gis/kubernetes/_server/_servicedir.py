import logging
from arcgis.gis import GIS

from arcgis.gis.kubernetes._admin._base import _BaseKube
from arcgis.gis.server._service import Service

_log = logging.getLogger()


class KubeServiceDirectory(_BaseKube):
    """
    A representation of the Kubernetes Hosting Service Directory.

    This is a private method and should not be created by a user.
    """

    _con = None
    _gis = None
    _url = None
    _folders = None
    _folder = None
    _services = None

    def __init__(self, url: str, gis: GIS) -> None:
        """initializer"""
        super()
        self._url = url
        self._gis = gis
        self._con = gis._con

    # ----------------------------------------------------------------------
    def __str__(self):
        return "<%s at %s>" % (type(self).__name__, self._url)

    # ----------------------------------------------------------------------
    def __repr__(self):
        return "<%s at %s>" % (type(self).__name__, self._url)

    # ----------------------------------------------------------------------
    def report(self, as_html=True, folder=None):
        """
        Generates a table of Services in the given folder, as a Pandas dataframe.


        """
        import pandas as pd

        pd.set_option("display.max_colwidth", -1)
        data = []
        a_template = """<a href="%s?token=%s">URL Link</a>"""
        columns = ["Service Name", "Service URL"]
        if folder is None:
            res = self._con.get(self._url, {"f": "json"})
        elif folder.lower() in [f.lower() for f in self.folders]:
            res = self._con.get("%s/%s" % (self._url, folder), {"f": "json"})
        if "services" in res:
            for s in res["services"]:
                # if s['name'].split('/')[-1].lower() == name.lower():
                url = "%s/%s/%s" % (self._url, s["name"], s["type"])
                data.append(
                    [s["name"].split("/")[-1], """<a href="%s">Service</a>""" % url]
                )
        # for service in self.list(folder=folder):
        # name = os.path.basename(os.path.dirname(service._url))
        # data.append([name, a_template % (service._url, self._con.token)])
        # del service
        df = pd.DataFrame(data=data, columns=columns)
        if as_html:
            table = (
                """<div class="9item_container" style="height: auto; overflow: hidden; """
                + """border: 1px solid #cfcfcf; border-radius: 2px; background: #f6fafa; """
                + """line-height: 1.21429em; padding: 10px;">%s</div>"""
                % df.to_html(escape=False, index=False)
            )
            return table.replace("\n", "")
        else:
            return df

    # ----------------------------------------------------------------------
    def get(self, name, folder=None):
        """returns a single service in a folder"""
        if folder is None:
            res = self._con.get(self._url, {"f": "json"})
        elif folder.lower() in [f.lower() for f in self.folders]:
            res = self._con.get("%s/%s" % (self._url, folder), {"f": "json"})
        if "services" in res:
            for s in res["services"]:
                if s["name"].split("/")[-1].lower() == name.lower():
                    return Service(
                        url="%s/%s/%s" % (self._url, s["name"], s["type"]),
                        server=self._con,
                    )
                del s
        return None

    # ----------------------------------------------------------------------
    def list(self, folder=None):
        """
        returns a list of services at the given folder
        """
        services = []
        if folder:
            url = "%s/%s" % (self._url, folder)
        else:
            url = self._url
        if folder is None:
            res = self._con.get(url, {"f": "json"})
        elif folder.lower() in [f.lower() for f in self.folders]:
            res = self._con.get(url, {"f": "json"})
        if "services" in res:
            for s in res["services"]:
                try:
                    services.append(
                        Service(
                            url="%s/%s/%s" % (url, s["name"], s["type"]),
                            server=self._con,
                        )
                    )

                except:
                    url = "%s/%s/%s" % (url, s["name"], s["type"])
                    _log.warning("Could not load service: %s" % url)
        return services

    # ----------------------------------------------------------------------
    def find(self, service_name, folder=None):
        """
        finds a service based on it's name in a given folder
        """
        return self.get(name=service_name, folder=folder)

    # ----------------------------------------------------------------------
    @property
    def folders(self):
        """
        returns a list of server folders
        """
        self._init()
        if self._is_agol:
            return ["/"]
        else:
            return self.properties["folders"]
        return []
