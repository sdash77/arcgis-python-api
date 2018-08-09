# ArcGIS API for Python Map ipywidget

This directory contains all information needed to build the ipywidget shipped with the `arcgis` package

# Setting up the environment

- Create a new blank conda environment, add all dependencies to the `arcgis` package to it (but not the `arcgis` package itself)
    - This can be accomplished by `conda env create -f /path/to/geosaurus/environment.yml`
- Activate the above environment
- Assert that `jupyter nbextension list` doesn't output any arcgis extension
    - Lines similar to `jupyter-js-widgets/extension  enabled` are OK 
- run `pip install -e /path/to/geosaurus/src --no-deps`
- run `jupyter nbextension install --py --sys-prefix --symlink arcgis`
- run `jupyter nbextension enable --py --sys-prefix arcgis`

# Modifying the source code

## Jupyter notebook
- For any changes to the python source code, or javascript source code, do the following steps:
   - change directories to `./js/`
   - run `yarn run build:notebook`, assert that there are no build errors
   - run `pip install -e /path/to/geosaurus/src --no-deps` again
   - Press the menu button that 'Restarts kernel and clears all output'
   - Refresh the page
 
## Jupyterlab extension

- If you are modifying the javascript source code in ./js/ and want to see the new widget in a jupyterlab setting:
    - change directories into `./js/`
    - run this command: `jupyter labextension install @jupyter-widgets/jupyterlab-manager`
    - run `jupyter labextension install /path/to/geosaurus/src/arcgis/widgets/js/`
    - Launch jupyter lab, and wait a minute or so (may take longer). You should see this message:
        - JupyterLab build is suggested: arcgis-map-ipywidget content changed
    - Press "BUILD", and wait a few minutes for the build to complete
        - You can look at the console output of the jupyterlab server instance to see any compile errors
    - If the build succeeds, the page should alert you to refresh the page.
        - If the build fails, __it won't say anything on the browser page__. You need to monitor the console output of the jupyterlab server for any errors 
    - The Jupyterlab server instance will auto-detect any changes to source code, and you will follow the same prompts as from above
- If you are modiyfing python source code, you may have to rerun  `pip install -e /path/to/geosaurus/src --no-deps` and restart the jupyter kernel

## When you're ready to merge into master

- run `yarn run build:prod`, run through all tests in geosaurus/tests/widget and assert full functionality

## Misc

- npm version 8 might be required if the installation keeps hanging
- the default `npm install` will only build the jupyterlab extension (it does not build the notebook extension)
    - An auto-building of the lab extension is needed for how jupuyterlab handles it's extensions
- To download a notebook as HTML with the widget in it:
    - 'Widget' > 'Save Widget State'
    - 'File' > 'Download as' > 'HTML'
    - Open the downloaded notebook's HTML file in a text editor
    - Delete all <script> tags after the <title> tag on the top of the file
    - Replace with the following:
```
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js" integrity="sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=" crossorigin="anonymous"></script>
<script src="https://unpkg.com/@jupyter-widgets/html-manager@*/dist/embed-amd.js" crossorigin="anonymous"></script>
```
