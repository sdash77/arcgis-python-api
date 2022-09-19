import warnings


def extract_zipfile(filepath, filename, remove=False):
    """Function to extract the contents of a zip file
    Args:
        filepath: absolute path to the file directory.
        filename: name of the zip file to be extracted.
        remove: default=False, removes the original zip file
                after extracting the contents if True
    """
    import os, zipfile

    with zipfile.ZipFile(os.path.join(filepath, filename), "r") as zip_ref:
        zip_ref.extractall(filepath)
    if remove:
        os.remove(os.path.join(filepath, filename))


def arcpy_localization_helper(msg, id, msg_type="ERROR", param=None):
    try:
        import arcpy

        arcpy.AddIDMessage(msg_type, id, param)
        if msg_type == "ERROR":
            try:
                exit()
            except:
                pass
    except:
        return msg


def check_imbalance(total_sample, unique_sample, class_imbalance_pct, stratify):
    """Function to check class imabalance in the data
    Args:
        total_sample: Total number of samples combining all the class(es).
        unique_sample: Class(es) in the data.
        class_imbalance_pct: Percentage of data for each class to consider for imbalance
    """
    imabalanced_class_list = []
    for sample in unique_sample:
        if (total_sample == sample).sum() < len(total_sample) * class_imbalance_pct:
            imabalanced_class_list.append(sample)

    if stratify == True and len(imabalanced_class_list) > 0:
        warnings.warn(
            f'We see a class imbalance in the dataset. The class(es) {",".join(imabalanced_class_list)} does not have enough data points in your dataset.'
        )
    elif stratify == False and len(imabalanced_class_list) > 0:
        warnings.warn(
            f'We see a class imbalance in the dataset. The class(es) {",".join(imabalanced_class_list)} does not have enough data points in your dataset. Although, class imbalance cannot be overcome easily, adding the parameter stratify = True will to a certain extent help get over this problem.'
        )
