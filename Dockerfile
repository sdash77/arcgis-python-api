# Create an image from Base Jupyter Notebook Stack from https://github.com/jupyter/docker-stacks
# Currently, use a specific tag due to issues with latest Notebook 5.1 version
FROM jupyter/base-notebook:03398900b724

# Pass in URL to where to get samples ZIP
ARG sampleslink="https://github.com/Esri/arcgis-python-api/archive/v1.2.1.zip"
ARG githubfolder="arcgis-python-api-1.2.1"

MAINTAINER Bill Major <bmajor@esri.com>
LABEL vendor="Esri"
# Install dependencies for Python API
RUN conda install -y unzip \
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
                     scikit-learn
RUN conda install jupyter_dashboards -c conda-forge -y

# Install latest Python API from Conda
RUN conda install -c esri arcgis -y

# Pull latest SDK from GitHub
WORKDIR /home/jovyan
RUN wget -O samples.zip $sampleslink
RUN unzip -q samples.zip 
RUN rm samples.zip
WORKDIR /home/jovyan/$githubfolder/
RUN mv * ../
WORKDIR /home/jovyan
RUN rm -rf $githubfolder/ \
           apidoc/ \
           work/ \
           talks/
RUN mkdir -p /home/jovyan/.jupyter/custom
RUN wget -O ~/.jupyter/custom/custom.css https://s3.us-east-2.amazonaws.com/notebooks-esri-com/notebookfiles/custom.css
RUN mv /opt/conda/lib/python3.6/site-packages/notebook/static/base/images/logo.png /opt/conda/lib/python3.6/site-packages/notebook/static/base/images/logo_old.png
RUN wget -O /opt/conda/lib/python3.6/site-packages/notebook/static/base/images/logo.png https://s3.us-east-2.amazonaws.com/notebooks-esri-com/notebookfiles/logo.png

