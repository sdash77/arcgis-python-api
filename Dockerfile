# Create an image from Base Jupyter Notebook Stack from https://github.com/jupyter/docker-stacks
# Currently, use a specific tag due to issues with latest Notebook 5.1 version
FROM jupyter/base-notebook

# Pass in URL to where to get samples ZIP
ARG sampleslink="https://github.com/Esri/arcgis-python-api/archive/v1.3.zip"
ARG githubfolder="arcgis-python-api-1.3"

MAINTAINER Esri Docker <docker_sdk@esri.com>
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
                     scikit-learn \
    && conda clean -y -a
RUN conda install jupyter_dashboards -c conda-forge -y
RUN conda install notebook=5.2.1 -y \
    && conda clean -y -a

# Install latest Python API from Conda
RUN conda install -c esri arcgis -y \
    && conda clean -y -a

RUN sed -i  's/Out\[%d\]:/Out\[%s\]:/g' /opt/conda/lib/python3.6/site-packages/notebook/static/notebook/js/main.min.js
RUN sed -i  's/Out\[%d\]:/Out\[%s\]:/g' /opt/conda/lib/python3.6/site-packages/notebook/static/notebook/js/main.min.js.map
RUN sed -i  's/Out\[%d\]:/Out\[%s\]:/g' /opt/conda/lib/python3.6/site-packages/notebook/static/notebook/js/outputarea.js

# Pull latest SDK from GitHub
RUN wget -O samples.zip $sampleslink \
    && unzip -q samples.zip \
    && rm samples.zip \
    && mv /home/jovyan/$githubfolder/* ./ \
    && rm -rf $githubfolder/ \
           apidoc/ \
           work/ \
           talks/
RUN mkdir -p /home/jovyan/.jupyter/custom
RUN wget -O ~/.jupyter/custom/custom.css https://s3.us-east-2.amazonaws.com/notebooks-esri-com/notebookfiles/custom.css
RUN mv /opt/conda/lib/python3.6/site-packages/notebook/static/base/images/logo.png /opt/conda/lib/python3.6/site-packages/notebook/static/base/images/logo_old.png
RUN wget -O /opt/conda/lib/python3.6/site-packages/notebook/static/base/images/logo.png https://s3.us-east-2.amazonaws.com/notebooks-esri-com/notebookfiles/logo.png
RUN wget -O /opt/conda/lib/python3.6/site-packages/notebook/templates/tree.html https://s3-us-west-1.amazonaws.com/notebooks-esri-com-alb-logs/notebookfiles/tree.html
