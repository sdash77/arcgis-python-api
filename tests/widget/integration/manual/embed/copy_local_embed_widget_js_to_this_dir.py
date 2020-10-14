import os
import shutil

def copy_local_embed_widget_js_to_this_dir():
    def get_dir_of_curr_exec_notebook():
        """
        Returns the absolute path of the directory that the currently executing 
        jupyter notebook resides in
        """
        try:
            kernel_id = re.search('kernel-(.*).json',
                                ipykernel.connect.get_connection_file()).group(1)
            servers = list_running_servers()
            for ss in servers:
                import requests
                from requests.compat import urljoin
                response = requests.get(urljoin(ss['url'], 'api/sessions'),
                                        params={'token': ss.get('token', '')})
                for nn in json.loads(response.text):
                    if nn['kernel']['id'] == kernel_id:
                        relative_path = nn['notebook']['path']
                        nb_path = os.path.join(ss['notebook_dir'], relative_path)
                        return os.path.dirname(nb_path)
        except Exception:
            return os.getcwd()

    curr_dir = get_dir_of_curr_exec_notebook()
    GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(curr_dir,
                                        "..",
                                        "..",
                                        "..",
                                        "..",
                                        ".."))
    EMBED_WIDGET_JS_FILE = os.path.join(GEOSAURUS_ROOT_DIR,
                                        "src",
                                        "arcgis",
                                        "widgets",
                                        "js",
                                        "dist",
                                        "index.js")

    # Placing an `arcgis-map-ipywidget.js` file in the same dir as this notebook
    # should make it load from that local dev copy instead of the unpkg.com one
    OVERRIDE_JS_FILE = os.path.join(curr_dir, "arcgis-map-ipywidget.js")
    return shutil.copy(EMBED_WIDGET_JS_FILE, 
                       os.path.join(curr_dir, OVERRIDE_JS_FILE))