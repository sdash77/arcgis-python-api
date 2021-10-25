# Create an image from Base Jupyter Notebook Stack from https://github.com/jupyter/docker-stacks
# Currently, use a specific tag for the latest Python 3.8 version
FROM jupyter/base-notebook:python-3.8.8

# Pass in URL to where to get samples ZIP
ARG sampleslink="https://github.com/Esri/arcgis-python-api/releases/download/v1.9.1/samples.zip"
ARG githubfolder="arcgis-python-api"

MAINTAINER Esri Docker <docker_sdk@esri.com>
LABEL vendor="Esri"

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
					 ujson \
                     geomet \
		             requests \
    && conda clean --all -f -y \
    && find /opt/conda -name __pycache__ -type d -exec rm -rf {} +

# Install latest Python API from Conda
RUN conda install -c esri arcgis -y \
    && conda clean --all -f -y \
    && find /opt/conda -name __pycache__ -type d -exec rm -rf {} +

# Pull latest SDK from GitHub
RUN mkdir /home/jovyan/$githubfolder
RUN wget -O samples.zip $sampleslink \
    && unzip -q samples.zip -d /home/jovyan/$githubfolder \
    && rm samples.zip \
    && mv /home/jovyan/$githubfolder/* ./ \
    && rm -rf $githubfolder/ \
           apidoc/ \
           work/ \
           talks/ \
           environment.yml
		   
RUN mv /opt/conda/lib/python3.8/site-packages/notebook/static/base/images/logo.png /opt/conda/lib/python3.8/site-packages/notebook/static/base/images/logo_old.png
COPY --chown=jovyan:users logo.png /opt/conda/lib/python3.8/site-packages/notebook/static/base/images/logo.png
