# Create an image from Base Jupyter Notebook Stack from https://github.com/jupyter/docker-stacks
# Currently, use a specific tag due to issues with latest Notebook 5.1 version
FROM jupyter/base-notebook

# Pass in URL to where to get samples ZIP
ARG sampleslink="https://github.com/Esri/arcgis-python-api/archive/v1.6.0.zip"
ARG githubfolder="arcgis-python-api-1.6.0"

MAINTAINER Esri Docker <docker_sdk@esri.com>
LABEL vendor="Esri"

# Pinning to Python 3.6
RUN conda install --quiet --yes \
    'python=3.6' \
    && conda clean -tipsy \
    && find $CONDA_DIR/pkgs -maxdepth 1 -mindepth 1 -type d -print -exec rm -r {} +

# Install dependencies for Python API
RUN conda install -y unzip \
					 xlrd \
                     pandas \
                     lxml \
                     html5lib \
                     beautifulsoup4 \
                     matplotlib \
                     pillow \
                     bokeh \
                     numpy \
                     seaborn \
                     scikit-image \
                     scikit-learn \
                     pysal \
                     pyshp \
                     keyring \
		     requests \
    && conda clean -tipsy \
    && find $CONDA_DIR/pkgs -maxdepth 1 -mindepth 1 -type d -print -exec rm -r {} +
#RUN conda install jupyter_dashboards -c conda-forge -y

# Install request packages
RUN conda install -c esri -c defaults -c conda-forge requests-kerberos \
                                                     requests-oauthlib \
													 requests_toolbelt \
													 requests_ntlm \
													 requests-negotiate-sspi \
	&& conda clean -tipsy \
    && find $CONDA_DIR/pkgs -maxdepth 1 -mindepth 1 -type d -print -exec rm -r {} +

# Install latest Python API from Conda
RUN conda install -c esri arcgis -y \
    && conda clean -tipsy \
    && find $CONDA_DIR/pkgs -maxdepth 1 -mindepth 1 -type d -print -exec rm -r {} +



# Fix needed for current jupyter notebook view
#RUN sed -i  's/Out\[%d\]:/Out\[%s\]:/g' /opt/conda/lib/python3.6/site-packages/notebook/static/notebook/js/main.min.js
#RUN sed -i  's/Out\[%d\]:/Out\[%s\]:/g' /opt/conda/lib/python3.6/site-packages/notebook/static/notebook/js/main.min.js.map
#RUN sed -i  's/Out\[%d\]:/Out\[%s\]:/g' /opt/conda/lib/python3.6/site-packages/notebook/static/notebook/js/outputarea.js

# Pull latest SDK from GitHub
RUN wget -O samples.zip $sampleslink \
    && unzip -q samples.zip \
    && rm samples.zip \
    && mv /home/jovyan/$githubfolder/* ./ \
    && rm -rf $githubfolder/ \
           apidoc/ \
           work/ \
           talks/ \
           environment.yml
		   
RUN mkdir -p /home/jovyan/.jupyter/custom
COPY --chown=jovyan:users custom.css /home/jovyan/.jupyter/custom/custom.css
RUN mv /opt/conda/lib/python3.6/site-packages/notebook/static/base/images/logo.png /opt/conda/lib/python3.6/site-packages/notebook/static/base/images/logo_old.png
COPY --chown=jovyan:users logo.png /opt/conda/lib/python3.6/site-packages/notebook/static/base/images/logo.png
#COPY --chown=jovyan:users tree_new.html /opt/conda/lib/python3.6/site-packages/notebook/templates/tree.html
