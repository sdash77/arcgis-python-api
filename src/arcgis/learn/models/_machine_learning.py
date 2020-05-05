import os
import random
import json
import pickle
import warnings
from pathlib import Path

from .._utils.tabular_data import TabularDataObject
from arcgis.features import FeatureLayer

HAS_SK_LEARN = True
try:
    import sklearn
    from sklearn import *
except:
    HAS_SK_LEARN = False

HAS_FAST_PROGRESS = True
try:
    from fastprogress.fastprogress import progress_bar
except:
    HAS_FAST_PROGRESS = False

_PROTOCOL_LEVEL = 2


def _get_model_type(model_type, **kwargs):
    if not model_type:
        raise Exception("Invalid model type.")

    if not isinstance(model_type, str):
        return model_type(**kwargs)

    if not model_type.startswith('sklearn.'):
        raise Exception("Invalid model_type.")

    model_type = model_type.replace('sklearn.', '')

    module = model_type.split('.')[0]

    if len(model_type.split('.')) > 1:
        model = model_type.split('.')[1]
    else:
        raise Exception("Invalid model_type.")

    if not hasattr(sklearn, module) or \
            not hasattr(getattr(sklearn, module), model):
        raise Exception("Invalid model_type.")

    model = getattr(getattr(sklearn, module), model)

    return model(**kwargs)


def raise_data_exception():
    raise Exception("Cannot call this function without data.")


class MLModel(object):
    """
    Creates a machine learning model based on it's implementation from scikit-learn.
    Refer https://scikit-learn.org/stable/supervised_learning.html#supervised-learning

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    data                    Required TabularDataObject. Returned data object from
                            `prepare_tabulardata` function.
    ---------------------   -------------------------------------------
    model_type              Required string path to the module.
                            For example for SVM:
                                sklearn.svm.SVR or sklearn.svm.SVC
                            For tree:
                                sklearn.tree.DecisionTreeRegressor or sklearn.tree.DecisionTreeClassifier
    ---------------------   -------------------------------------------
    **kwargs                model_type specific arguments.
                            Refer Parameters section
                            https://scikit-learn.org/stable/supervised_learning.html#supervised-learning
    =====================   ===========================================

    :returns: `MLModel` Object
    """

    def __init__(self, data, model_type, **kwargs):
        if not HAS_SK_LEARN:
            raise Exception("This module requires scikit-learn.")

        self._data = data
        if kwargs.get('pretrained_model'):
            self._model = kwargs.get('pretrained_model')
        else:
            self._model = _get_model_type(model_type, **kwargs)

        self._training_data, self._training_labels, self._validation_data, self._validation_labels = self._data._ml_data

    def fit(self):
        if self._training_data is None or self._training_labels is None:
            raise_data_exception()

        self._model.fit(self._training_data, self._training_labels)

    def show_results(self, rows=5):
        """
        Shows sample results for the model.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        rows                    Optional number of rows. By default, 5 rows
                                are displayed.
        =====================   ===========================================
        :returns dataframe
        """
        if self._validation_data is None or self._validation_labels is None:
            raise_data_exception()

        min_size = len(self._validation_data)

        if rows < min_size:
            min_size = rows

        sample_batch = random.sample(range(len(self._validation_data)), min_size)

        validation_data_batch = self._validation_data.take(sample_batch, axis=0)

        output_labels = self._predict(validation_data_batch)

        df = self._data._dataframe.loc[self._data._validation_indexes].reset_index(drop=True).loc[sample_batch].reset_index(drop=True)

        df[self._data._dependent_variable + '_results'] = output_labels

        return df

    def score(self):
        """
        :returns output from scikit-learn's model.score()
        """
        if self._validation_data is None or self._validation_labels is None:
            raise_data_exception()

        return self._model.score(self._validation_data, self._validation_labels)

    def save(self, name_or_path):
        """
        Saves the model, creates an Esri Model Definition. Uses pickle to save the model.
        Using protocol level 2.Protocol level is backward compatible.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        name_or_path            Required string. Folder path to save the model.
        =====================   ===========================================
        :returns dataframe
        """

        if self._training_data is None or self._training_labels is None:
            raise_data_exception()

        if '\\' in name_or_path or '/' in name_or_path:
            path = name_or_path
        else:
            path = os.path.join(os.getcwd(), name_or_path)

        if not os.path.exists(os.path.dirname(path)):
            raise Exception("Path doesn't exist")

        if not os.path.exists(path):
            os.mkdir(path)

        base_file_name = os.path.basename(path)

        model_file = os.path.join(path, base_file_name + '.pkl')

        with open(model_file, 'wb') as f:
            f.write(pickle.dumps(self._model, protocol=_PROTOCOL_LEVEL))

        MLModel._save_encoders(self._data._encoder_mapping, path, base_file_name)
        self._write_emd(path, base_file_name)

        return Path(path)

    def _write_emd(self, path, base_file_name):
        emd_file = os.path.join(path, base_file_name + '.emd')
        emd_params = {}
        emd_params['score'] = self.score()
        emd_params['_is_classification'] = "classification" if self._data._is_classification else "regression"
        emd_params['ModelName'] = type(self._model).__name__
        emd_params['ModelFile'] = base_file_name + '.pkl'
        emd_params['ModelParameters'] = self._model.get_params()
        emd_params['categorical_variables'] = self._data._categorical_variables
        emd_params['dependent_variable'] = self._data._dependent_variable
        emd_params['continuous_variables'] = self._data._continuous_variables

        with open(emd_file, 'w') as f:
            f.write(json.dumps(emd_params, indent=4))

    @classmethod
    def from_model(cls, emd_path, data=None):
        """
        Creates a `MLModel` Object from an Esri Model Definition (EMD) file.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to Esri Model Definition
                                file.
        ---------------------   -------------------------------------------
        data                    Required TabularDataObject or None. Returned data
                                object from `prepare_tabulardata` function or None for
                                inferencing.
        =====================   ===========================================

        :returns: `MLModel` Object
        """

        if not os.path.exists(emd_path):
            raise Exception("Invalid data path.")

        with open(emd_path, 'r') as f:
            emd = json.loads(f.read())

        categorical_variables = emd['categorical_variables']
        dependent_variable = emd['dependent_variable']
        continuous_variables = emd['continuous_variables']
        model_parameters = emd['ModelParameters']

        _is_classification = True
        if emd['_is_classification'] != "classification":
            _is_classification = False

        encoder_mapping = None
        if categorical_variables:
            encoder_path = os.path.join(os.path.dirname(emd_path), os.path.basename(emd_path).split('.')[0] + '_encoders.pkl')
            if os.path.exists(encoder_path):
                with open(encoder_path, 'rb') as f:
                    encoder_mapping = pickle.loads(f.read())

        if data is None:
            data = TabularDataObject._empty(categorical_variables, continuous_variables, dependent_variable, encoder_mapping)
            data._is_classification = _is_classification

        model_file = os.path.join(os.path.dirname(emd_path), emd['ModelFile'])
        with open(model_file, 'rb') as f:
            model = pickle.loads(f.read())

        return cls(data, emd['ModelName'], pretrained_model=model, **model_parameters)

    def _predict(self, data):
        return self._model.predict(data)

    @staticmethod
    def _save_encoders(encoder_mapping, path, base_file_name):
        if not encoder_mapping:
            return

        encoder_file = os.path.join(path, base_file_name + '_encoders.pkl')
        with open(encoder_file, 'wb') as f:
            f.write(pickle.dumps(encoder_mapping, protocol=_PROTOCOL_LEVEL))

    def predict(
            self,
            input_features=None,
            explanatory_rasters=None,
            datefield=None,
            distance_features=None,
            output_layer_name="Prediction Layer",
            gis=None,
            predict_features=True,
            output_raster_folder_path=None,
            match_field_names=None):
        """

        Predict on data from feature layer and or raster data.

        =================================   =========================================================================
        **Argument**                        **Description**
        ---------------------------------   -------------------------------------------------------------------------
        input_features                      Optional Feature Layer or spatial dataframe. Required is predict_features=True.
                                            Contains features with location and
                                            some or all fields required to infer the dependent variable value.
        ---------------------------------   -------------------------------------------------------------------------
        explanatory_rasters                 Optional list. Required if predict_features=False.
                                            Contains a list of raster objects containing
                                            some or all fields required to infer the dependent variable value.
        ---------------------------------   -------------------------------------------------------------------------
        datefield                           Optional string. Field name from feature layer
                                            that contains the date, time for the input features.
                                            Same as `prepare_tabulardata()`.
        ---------------------------------   -------------------------------------------------------------------------
        distance_features                   Optional List of Feature Layers.
                                            These layers are used for calculation of field "NEAR_DIST_1",
                                            "NEAR_DIST_2" etc in the output dataframe.
                                            These fields contain the nearest feature distance
                                            from the input_features.
                                            Same as `prepare_tabulardata()`.
        ---------------------------------   -------------------------------------------------------------------------
        output_layer_name                   Optional string. Used for publishing the output layer.
        ---------------------------------   -------------------------------------------------------------------------
        gis                                 Optional GIS Object. Used for publishing the item.
                                            If not specified then active gis user is taken.
        ---------------------------------   -------------------------------------------------------------------------
        predict_features                    Optional Boolean.
                                            Set True to make output feature layer predictions.
                                            When True, feature_layer argument is required.

                                            Set False, to make prediction raster.
                                            When False, rasters must be specified.
        ---------------------------------   -------------------------------------------------------------------------
        output_raster_folder_path           Optional Folder path.
                                            Required when predict_features=False, saves
                                            the output raster to this path.
        ---------------------------------   -------------------------------------------------------------------------
        match_field_names                   Optional dictionary.
                                            Specify mapping of field names from prediction set
                                            to training set.
                                            For example:
                                                {
                                                    "Field_Name_1": "Field_1",
                                                    "Field_Name_2": "Field_2"
                                                }
        =================================   =========================================================================

        :returns Feature Layer predict_features=True or creates an output raster.

        """

        rasters = explanatory_rasters if explanatory_rasters else []
        if predict_features:

            if input_features is None:
                raise Exception("Feature Layer required for predict_features=True")

            return self._predict_features(input_features, rasters, datefield, distance_features, output_layer_name, gis, match_field_names)
        else:
            if not rasters:
                raise Exception("Rasters required for predict_features=False")

            if not output_raster_folder_path:
                raise Exception("Please specify output_raster_folder_path to save the output.")

            return self._predict_rasters(output_raster_folder_path, rasters, match_field_names)

    def _predict_features(
            self,
            input_features,
            rasters=None,
            datefield=None,
            distance_feature_layers=None,
            output_name="Prediction Layer",
            gis=None,
            match_field_names=None
    ):
        if isinstance(input_features, FeatureLayer):
            dataframe = input_features.query().sdf
        else:
            dataframe = input_features

        fields_needed = self._data._categorical_variables + self._data._continuous_variables
        distance_feature_layers = distance_feature_layers if distance_feature_layers else []
        continuous_variables = self._data._continuous_variables

        columns = dataframe.columns
        feature_layer_columns = []
        for column in columns:
            column_name = column
            categorical = False

            if column_name in fields_needed:
                if column_name not in continuous_variables:
                    categorical = True
            elif match_field_names and match_field_names.get(column_name):
                if match_field_names.get(column_name) not in continuous_variables:
                    categorical = True
            else:
                continue

            feature_layer_columns.append((column_name, categorical))

        raster_columns = []
        if rasters:
            for raster in rasters:
                column_name = raster.name
                categorical = False
                if column_name in fields_needed:
                    if column_name not in continuous_variables:
                        categorical = True
                elif match_field_names and match_field_names.get(column_name):
                    column_name = match_field_names.get(column_name)
                    if column_name not in continuous_variables:
                        categorical = True
                else:
                    continue

                raster_columns.append((raster, categorical))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            processed_dataframe, fields_mapping = TabularDataObject._prepare_dataframe_from_features(
                input_features,
                self._data._dependent_variable,
                feature_layer_columns,
                raster_columns,
                datefield,
                distance_feature_layers
            )

        if match_field_names:
            processed_dataframe.rename(columns=match_field_names, inplace=True)

        for field in fields_needed:
            if field not in processed_dataframe.columns:
                raise Exception(f"Field missing {field}")

        for column in processed_dataframe.columns:
            if column not in fields_needed:
                processed_dataframe = processed_dataframe.drop(column, axis=1)

        processed_numpy = self._data._process_data(processed_dataframe.reindex(sorted(processed_dataframe.columns), axis=1))

        predictions = self._predict(processed_numpy)
        dataframe["prediction_results"] = predictions

        return dataframe.spatial.to_featurelayer(output_name, gis)

    def _predict_rasters(self, output_folder_path, rasters, match_field_names=None):

        if not os.path.exists(os.path.dirname(output_folder_path)):
            raise Exception("Output directory doesn't exist")

        if os.path.exists(output_folder_path):
            raise Exception("Output Folder already exists")

        try:
            import arcpy
        except:
            raise Exception("This function requires arcpy.")

        try:
            import numpy as np
        except:
            raise Exception("This function requires numpy.")

        try:
            import pandas as pd
        except:
            raise Exception("This function requires pandas.")

        if not HAS_FAST_PROGRESS:
            raise Exception("This function requires fastprogress.")

        fields_needed = self._data._categorical_variables + self._data._continuous_variables

        arcpy.env.outputCoordinateSystem = rasters[0].extent['spatialReference']['wkt']

        lower_point_x = rasters[0].extent['xmin']
        lower_point_y = rasters[0].extent['ymin']

        max_raster_rows = rasters[0].rows
        max_raster_columns = rasters[0].columns

        x_cell_size = rasters[0].mean_cell_width
        y_cell_size = rasters[0].mean_cell_height

        for raster in rasters:
            if raster.rows > max_raster_rows:
                max_raster_rows = raster.rows
                y_cell_size = raster.mean_cell_height

            if raster.columns > max_raster_columns:
                max_raster_columns = raster.columns
                x_cell_size = raster.mean_cell_width

            if raster.extent['xmin'] < lower_point_x:
                lower_point_x = raster.extent['xmin']

            if raster.extent['ymin'] < lower_point_y:
                lower_point_y = raster.extent['ymin']

        raster_data = {}
        for raster in rasters:
            field_name = raster.name
            if field_name in fields_needed:
                raster_data[field_name] = raster.read(ncols=max_raster_columns, nrows=max_raster_rows)
            elif match_field_names and match_field_names.get(raster.name):
                field_name = match_field_names.get(raster.name)
                raster_data[field_name] = raster.read(ncols=max_raster_columns, nrows=max_raster_rows)
            else:
                continue

        for field in fields_needed:
            if field not in list(raster_data.keys()):
                raise Exception(f"Field missing {field}")

        processed_data = []

        for row in progress_bar(range(max_raster_rows)):
            for column in range(max_raster_columns):
                processed_row = []
                for raster_name in sorted(raster_data):
                    value = raster_data[raster_name][row][column]
                    if len(value) > 0:
                        processed_row.append(value[0])
                    else:
                        processed_row.append(0)
                processed_data.append(processed_row)

        processed_df = pd.DataFrame(data=np.array(processed_data), columns=sorted(raster_data))

        processed_numpy = self._data._process_data(processed_df)

        predictions = self._predict(processed_numpy)

        predictions = predictions.reshape([max_raster_rows, max_raster_columns])
        processed_raster = arcpy.NumPyArrayToRaster(predictions, arcpy.Point(lower_point_x, lower_point_y), x_cell_size=x_cell_size, y_cell_size=y_cell_size)
        processed_raster.save(output_folder_path)

        return True
