from arcgis.raster import _util


def generate_direct_access_url(expiration=None, *, gis=None):
    """
    Function to get the direct access url for user's rasterStore on ArcGIS Online.

    ====================================     ====================================================================
    **Argument**                             **Description**
    ------------------------------------     --------------------------------------------------------------------
    expiration                               Optional integer. Direct access URL expiration time in minutes.
                                             (The default is 1440 ie. 24 hours)
    ------------------------------------     --------------------------------------------------------------------
    gis                                      Keyword only parameter. Optional GIS. The GIS on which this function runs.
                                             If not specified, the active GIS is used.
    ====================================     ====================================================================

    :return:
        String. Direct Access URL
    """

    return _util._generate_direct_access_url(expiration=expiration, gis=gis)


def upload_imagery_to_agol_userstore(
    files, direct_access_url=None, auto_renew=True, upload_properties=None, *, gis=None
):
    """
    Uploads file/files to the user's rasterstore on ArcGIS Online and returns the list of urls.
    The list of urls can then be used with arcgis.raster.analytics.copy_raster() method to create imagery layer on AGOL.

    ====================================     ====================================================================
    **Argument**                             **Description**
    ------------------------------------     --------------------------------------------------------------------
    files                                    Required. It can be a folder, list of files or single file that needs to be uploaded.
    ------------------------------------     --------------------------------------------------------------------
    direct_access_url                        Optional string. The direct access url generated using generate_direct_access_url function.
                                             If not specified, the function would generate the direct access url internally which is valid for 1440 minutes.
    ------------------------------------     --------------------------------------------------------------------
    auto_renew                               Optional boolean. If set to True, function would continue uploading 
                                             until the entire data is uploaded by auto renewing the direct access url.
                                             (The default is True)
    ------------------------------------     --------------------------------------------------------------------
    upload_properties                        | Optional dictionary. ``upload_properties`` can be used to control specific \
                                             upload parameters. 

                                             Available options:

                                                - "maxUploadConcurrency": Optional integer. Maximum number of parallel connections \
                                                    to use for large uploads (when individual file/blob size exceeds 64MB). \
                                                    This is the **max_concurrency** parameter of the `BlobClient.upload_blob() <https://docs.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#upload-blob-data--blob-type--blobtype-blockblob---blockblob----length-none--metadata-none----kwargs->`__ method. \
                                                    (The default is 6)
                                                - "maxWorkerThreads": Optional integer. Maximum number of threads to execute asynchronously \
                                                    when uploading multiple files. This is the **max_workers** parameter of the `ThreadPoolExecutor() <https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor>`__ class. \
                                                    (The default is None)
                                                - "displayProgress": Optional boolean. If set to True, a progress bar will be \
                                                    displayed for tracking the progress of the uploads to user's rasterstore. \
                                                    (The default is False)

                                                Example:
                                                    {"maxUploadConcurrency":8, "maxWorkerThreads":20, "displayProgress":True}
    ------------------------------------     --------------------------------------------------------------------
    gis                                      Keyword only parameter. Optional GIS. The GIS on which this function runs.
                                             If not specified, the active GIS is used.
    ====================================     ====================================================================

    :return:
        List of file paths.
    """

    return _util._upload_imagery_agol(
        files=files,
        direct_access_url=direct_access_url,
        auto_renew=auto_renew,
        upload_properties=upload_properties,
        gis=gis,
    )
