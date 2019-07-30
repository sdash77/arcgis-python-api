"""
These tools help you identify, quantify, and visualize spatial patterns in your data.

calculate_density takes known quantities of some phenomenon and spreads these quantities across the map.
find_hot_spots identifies statistically significant clustering in the spatial pattern of your data.
"""
import json as _json
from datetime import datetime as _datetime
import logging as _logging
import arcgis as _arcgis
from arcgis.features import FeatureSet as _FeatureSet
from arcgis.features import Table as _Table
from arcgis.geoprocessing._support import _execute_gp_tool
from arcgis.geoprocessing import DataFile
from ._util import _id_generator, _feature_input, _set_context, _create_output_service, GAJob

_log=_logging.getLogger(__name__)

_use_async = True
#--------------------------------------------------------------------------
def forest(input_layer,
           var_prediction,
           var_explanatory,
           trees,
           max_tree_depth=None,
           random_vars=None,
           sample_size=100,
           min_leaf_size=None,
           prediction_type="train",
           features_to_predict=None,
           validation=10,
           importance_tbl=False,
           exp_var_matching=None,
           output_name=None,
           gis=None,
           context=None,
           future=False):
    """
    .. image:: _static/images/forest/forest.png 

    The 'forest' method is a forest-based classification and regression
    task that creates models and generates predictions using an adaptation of
    Leo Breiman's random forest algorithm, which is a supervised machine
    learning method. Predictions can be performed for both categorical
    variables (classification) and continuous variables (regression).
    Explanatory variables can take the form of fields in the attribute
    table of the training features. In addition to validation of model
    performance based on the training data, predictions can be made to
    another feature dataset.

    The following are examples:

        + Given data on occurrence of seagrass, as well as a number of environmental explanatory
          variables represented as both attributes which has been enriched using a multi-variable grid
          to calculate distances to factories upstream and major ports, future seagrass occurrence can
          be predicted based on future projections for those same environmental explanatory variables.
        + Suppose you have crop yield data at hundreds of farms across the country along with other
          attributes at each of those farms (number of employees, acreage, and so on). Using these
          pieces of data, you can provide a set of features representing farms where you don't have
          crop yield (but you do have all of the other variables), and make a prediction about crop
          yield.
        + Housing values can be predicted based on the prices of houses that have been sold in the
          current year. The sale price of homes sold along with information about the number of
          bedrooms, distance to schools, proximity to major highways, average income, and crime counts
          can be used to predict sale prices of similar homes.

    .. note::
        Forest Based Classification and Regression is available at ArcGIS Enterprise 10.7.

    =========================================================================   ===========================================================================
    **Argument**                                                                **Description**
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    input_layer                                                                 Required layer. The features that will be used to train the dataset. 
                                                                                This layer must include fields representing the variable to predict 
                                                                                and the explanatory variables. See :ref:`Feature Input<FeatureInput>`.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    var_prediction                                                              Required dict. The variable from the ``input_layer`` parameter
                                                                                containing the values to be used to train the model, and a
                                                                                boolean denoting if it's categorical. This field contains known
                                                                                (training) values of the variable that will be used to predict
                                                                                at unknown locations.

                                                                                Syntax: {"fieldName":"<field name>", "categorical":bool}
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    var_explanatory                                                             Required list. A list of fields representing the explanatory
                                                                                variables and a boolean value denoting whether the fields are
                                                                                categorical. The explanatory variables help predict the value
                                                                                or category of the ``var_prediction`` parameter. Use the
                                                                                categorical parameter for any variables that represent classes
                                                                                or categories (such as land cover or presence or absence).
                                                                                Specify the variable as 'True' for any that represent classes or
                                                                                categories such as land cover or presence or absence and 'False'
                                                                                if the variable is continuous.

                                                                                Syntax: [{"fieldName":"<field name>", "categorical":bool},...]
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    trees                                                                       Required integer. The number of trees to create in the forest model.
                                                                                More trees will generally result in more accurate model
                                                                                prediction, but the model will take longer to calculate.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    max_tree_depth                                                              Optional integer. The maximum number of splits that will be made
                                                                                down a tree. Using a large maximum depth, more splits will be
                                                                                created, which may increase the chances of overfitting the
                                                                                model. The default is data driven and depends on the number of
                                                                                trees created and the number of variables included. 
                                                                                The ``max_tree_depth`` must be positive and less than or equal to 30.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    random_vars                                                                 Optional integer. Specifies the number of explanatory variables
                                                                                used to create each decision tree.Each of the decision trees in
                                                                                the forest is created using a random subset of the explanatory
                                                                                variables specified. Increasing the number of variables used in
                                                                                each decision tree will increase the chances of overfitting
                                                                                your model particularly if there is one or a couple dominant
                                                                                variables. A common practice is to use the square root of the
                                                                                total number of explanatory variables (fields, distances, and
                                                                                rasters combined) if your variablePredict is numeric or divide
                                                                                the total number of explanatory variables (fields, distances,
                                                                                and rasters combined) by 3 if ``var_prediction`` is categorical.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    sample_size                                                                 Optional integer. Specifies the percentage of the ``input_layer`` used
                                                                                for each decision tree.
                                                                                Samples for each tree are taken randomly from two-thirds of the
                                                                                data specified.

                                                                                The default is 100 percent of the data.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    min_leaf_size                                                               Optional integer. The minimum number of observations required to
                                                                                keep a leaf (that is the terminal node on a tree without
                                                                                further splits). For very large data,
                                                                                increasing these numbers will decrease the run time of the
                                                                                tool.

                                                                                The default minimum for regression is 5 and
                                                                                the default for classification is 1.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    prediction_type                                                             Optional string. Specifies the operation mode of the tool. The tool can be run to
                                                                                train a model to only assess performance, or train a model and
                                                                                predict features. Prediction types are as follows:
                
                                                                                    + ``Train`` - A model will be trained, but
                                                                                      no predictions will be generated. Use this option to
                                                                                      assess the accuracy of your model before generating
                                                                                      predictions. This option will output model diagnostics in
                                                                                      the messages window and a chart of variable importance.
                                                                                    + ``TrainAndPredict`` - Predictions or classifications will be
                                                                                      generated for features. Explanatory variables must be
                                                                                      provided for both the training features and the features
                                                                                      to be predicted. The output of this option will be a
                                                                                      feature service, model diagnostics, and an optional
                                                                                      table of variable importance.
                
                                                                                The default value is 'Train'.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    features_to_predict (Required if using ``TrainAndPredict``)                 Optional layer. A feature layer representing locations where predictions will be made. 
                                                                                This layer must include explanatory variable fields that correspond to fields used in ``input_layer``. 
                                                                                This parameter is only used when the ``prediction_type`` is ``TrainAndPredict`` and is required in that case. 
                                                                                See :ref:`Feature Input<FeatureInput>`.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    validation                                                                  Optional integer. Specifies the percentage (between 10 percent
                                                                                and 50 percent) of inFeatures to reserve as the test dataset
                                                                                for validation. The model will be trained without this random
                                                                                subset of data, and the observed values for those features will
                                                                                be compared to the predicted value. 
                                                                                
                                                                                The default value is 10 percent.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    importance_tbl                                                              Optional boolean. Specifies whether an output table will be
                                                                                generated that contains information describing the importance
                                                                                of each explanatory variable used in the model created.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    exp_var_matching                                                            Optional list of dicts. A list of fields representing the explanatory variables and a
                                                                                boolean values denoting if the fields are categorical. The
                                                                                explanatory variables help predict the value or category of the
                                                                                variable_predict. Use the categorical parameter for any
                                                                                variables that represent classes or categories (such as
                                                                                landcover or presence or absence). Specify the variable as
                                                                                'True' for any that represent classes or categories such as
                                                                                landcover or presence or absence and 'False' if the variable is
                                                                                continuous.
                
                                                                                Syntax: [{"fieldName":"<explanatory field name>", "categorical":bool},
                
                                                                                    + fieldname is the name of the field in the ``input_layer`` used
                                                                                      to predict the ``var_prediction``.
                                                                                    + categorical is one of: 'True' or 'False'. A string field should
                                                                                      always be 'True', and a continue value should always be set as 'False'.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_name                                                                 Optional string. The task will create a feature service of the
                                                                                results. You define the name of the service.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    gis                                                                         Optional GIS. The GIS on which this tool runs. If not
                                                                                specified, the active GIS is used.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    context                                                                     Optional dict. The context parameter contains additional settings that affect task execution. For this task, there are four settings:
 
                                                                                #. Extent (``extent``) - A bounding box that defines the analysis area. Only those features that intersect the bounding box will be analyzed.
                                                                                #. Processing spatial reference (``processSR``) - The features will be projected into this coordinate system for analysis.
                                                                                #. Output spatial reference (``outSR``) - The features will be projected into this coordinate system after the analysis to be saved. The output spatial reference for the spatiotemporal big data store is always WGS84.
                                                                                #. Data store (``dataStore``) - Results will be saved to the specified data store. The default is the spatiotemporal big data store.  
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    future                                                                      Optional boolean. If 'True', a GPJob is returned instead of
                                                                                results. The GPJob can be queried on the status of the execution.

                                                                                The default value is 'False'.
    =========================================================================   ===========================================================================

    :returns: named tuple with the following keys:

        "output_trained" : featureLayer

        "output_predicted" : featureLayer	

        "variable_of_importance" : Table 

        "process_info" : list

    .. code-block:: python

            # Usage Example: To predict the number of 911 calls in each block group.
            predicted_result = forest(input_layer=call_lyr,
                                      var_prediction={"fieldName":"Calls", "categorical":False},
                                      var_explanatory=[{"fieldName":"Pop", "categorical":False},
                                                        {"fieldName":"Unemployed", "categorical":False},
                                                        {"fieldName":"AlcoholX", "categorical":False},
                                                        {"fieldName":"UnEmpRate", "categorical":False},
                                                        {"fieldName":"MedAge00", "categorical":False}],
                                      trees=50,
                                      max_tree_depth=10,
                                      random_vars=3,
                                      sample_size=100,
                                      min_leaf_size=5,
                                      prediction_type='TrainAndPredict',
                                      validation=10,
                                      importance_tbl=True,
                                      output_name='train and predict number of 911 calls')

    """
    allowed_prediction_types = {
        'train' : "Train",
        'trainandpredict' : 'TrainAndPredict'

    }
    if str(prediction_type).lower() not in allowed_prediction_types:
        raise ValueError("Invalid Prediction type.")
    else:
        prediction_type = allowed_prediction_types[prediction_type.lower()]

    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis

    if gis.version < [7]:
        return None
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Forest Based Regression_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Forest Based Classification And Regression')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    if context is not None:
        params["context"] = context
    else:
        _set_context(params)



    param_db={
        "input_layer": (_FeatureSet, "inFeatures"),
        "prediction_type" : (str, "predictionType"),
        "features_to_predict" : (_FeatureSet, "featuresToPredict"),
        "var_prediction" : (dict, "variablePredict"),
        "var_explanatory" : (list, "explanatoryVariables"),
        "exp_var_matching" : (list, "explanatoryVariableMatching"),
        "trees" : (int, "numberOfTrees"),
        "max_tree_depth" : (int, "maximumTreeDepth"),
        "min_leaf_size" : (int, "minimumLeafSize"),
        "sample_size" : (int, "sampleSize"),
        "random_vars" : (int, "randomVariables"),
        "validation" : (float, "percentageForValidation"),
        "output_name" : (str, "outputTrainedName"),
        "context": (str, "context"),
        "importance_tbl" : (bool, "createVariableImportanceTable"),
        "output_trained": (_FeatureSet, "outputTrained"),
        "output_predicted": (_FeatureSet, "outputPredicted"),
        "variable_of_importance": (_Table, "variableOfImportance"),
        "process_info": (list, "processInfo")
    }
    return_values=[
        {"name": 'output_trained', "display_name": "Output Features", "type": _FeatureSet},
        {"name" : "output_predicted", "display_name" : "Output Predicted", "type" : _FeatureSet},
        {"name" : "variable_of_importance", "display_name" : "Variable of Importance", "type" : _Table},
        {"name" : "process_info", "display_name" : "Process Information", "type" : list}
    ]
    if features_to_predict is None and prediction_type == 'TrainAndPredict':
        params["features_to_predict"] = input_layer
        #param_db.pop("features_to_predict")
    try:
        if future:
            gpjob = _execute_gp_tool(gis, "ForestBasedClassificationAndRegression", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        res = _execute_gp_tool(gis, "ForestBasedClassificationAndRegression", params, param_db, return_values, _use_async, url, True, future=future)
        return res
    except:
        output_service.delete()
        raise

    return
#--------------------------------------------------------------------------
def glr(input_layer,
        var_dependent,
        var_explanatory,
        regression_family="Continuous",
        features_to_predict=None,
        gen_coeff_table=False,
        exp_var_matching=None,
        dep_mapping=None,
        output_name=None,
        gis=None,
        future=False):
    """

    This tool performs Generalized Linear Regression (glr) to generate
    predictions or to model a dependent variable's relationship to a set of
    explanatory variables. This tool can be used to fit continuous
    (Gaussian/OLS), binary (logistic), and count (Poisson) models.

    The following are examples of the tool's utility:

        + What demographic characteristics contribute to high rates of public transportation usage?
        + Is there a positive relationship between vandalism and burglary?
        + Which variables effectively predict 911 call volume? Given future projections, what is the expected demand for emergency response resources?
        + What variables affect low birth rates?

    ==========================   ===============================================================
    **Argument**                 **Description**
    --------------------------   ---------------------------------------------------------------
    input_layer                  Required FeatureSet. The layer containing the dependent and
                                 independent variables.
    --------------------------   ---------------------------------------------------------------
    var_dependent                      Required String. The numeric field containing the observed
                                 values you want to model.
    --------------------------   ---------------------------------------------------------------
    var_explanatory              Required String. One or more fields representing independent
                                 explanatory variables in your regression model.
    --------------------------   ---------------------------------------------------------------
    regression_family            Required String. This field specifies the type of data you are
                                 modeling.

                                 regression_family is one of the following:

                                    + Continuous - The dependent_variable is continuous. The
                                                   model used is Gaussian, and the tool performs
                                                   ordinary least squares regression.
                                    + Binary - The dependent_variable represents presence or
                                               absence. Values must be 0 (absence) or 1 (presence)
                                               values, or mapped to 0 and 1 values using the
                                               parameter.
                                    + Count - The dependent_variable is discrete and represents
                                              events, such as crime counts, disease incidents,
                                              or traffic accidents. The model used is Poisson
                                              regression.
    --------------------------   ---------------------------------------------------------------
    features_to_predict          Required FeatureSet. A layer containing features representing
                                 locations where estimates should be computed. Each feature in
                                 this dataset should contain values for all the explanatory
                                 variables specified. The dependent variable for these features
                                 will be estimated using the model calibrated for the input
                                 layer data.

                                 Syntax: As described in Feature input, this parameter can be
                                         one of the following:

                                    + A URL to a feature service layer with an optional filter
                                      to select specific features
                                    + A URL to a big data catalog service layer with an
                                      optional filter to select specific features
                                    + A feature collection
    --------------------------   ---------------------------------------------------------------
    gen_coeff_table              Optional Boolean. Determines if a table with coefficient values
                                 will be returned. By default, the coefficient table is not
                                 returned.
    --------------------------   ---------------------------------------------------------------
    exp_var_matching             Optional List. A list of the explanatoryVariables specified from
                                 the input_layer and their corresponding fields from the
                                 features_to_predict. By default, if an var_explanatoryiables is
                                 not mapped, it will match to a field with the same name in the
                                 features_to_predict. This parameter is only used if there is a
                                 features_to_predict input. You do not need to use it if the
                                 names and types of the fields match between your two input
                                 datasets.

                                 Syntax: [{"predictionLayerField":"<field name>",
                                          "trainingLayerField": "<field name>"},...]

                                    + predictionLayerField is the name of a field specified in the
                                      var_explanatoryiables parameter.
                                    + trainingLayerField is the field that will match to the field
                                      in the var_explanatoryiables parameter.

                                 REST scripting example:

    --------------------------   ---------------------------------------------------------------
    dep_mapping                  Optional List. A list representing the values used to map to 0
                                 (absence) and 1 (presence) for binary regression.

                                 Syntax: [{"value0":"<false value>"},{"value1":"<true value>"}]

                                    + value0 is the string that will be used to represent 0
                                      (absence values).
                                    + value1 is the string that will be used to represent 1
                                      (presence values).

    --------------------------   ---------------------------------------------------------------
    output_name                  Optional String. The task will create a feature service of the
                                 results. You define the name of the service.
    --------------------------   ---------------------------------------------------------------
    gis                          Optional GIS, the GIS on which this tool runs. If not
                                 specified, the active GIS is used.
    --------------------------   ---------------------------------------------------------------
    future                       optional Boolean. If True, a GPJob is returned instead of
                                 results. The GPJob can be queried on the status of the execution.
    ==========================   ===============================================================

    :returns:
       Output feature layer item


    """


    _allowed_regression_family = {
        "continuous" : "Continuous",
        "binary" : "Binary",
        "count" : "Count"
    }
    kwargs=locals()

    if regression_family.lower() in _allowed_regression_family:
        regression_family = _allowed_regression_family[regression_family.lower()]
        if 'regression_family' in kwargs:
            kwargs['regression_family'] = _allowed_regression_family[regression_family.lower()]
    else:
        raise ValueError("Invalid regression_family.")

    gis=_arcgis.env.active_gis if gis is None else gis

    if gis.version < [7]:
        return None
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='GLR_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Generalized Linear Regression')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})


    _set_context(params)

    param_db={
        "input_layer": (_FeatureSet, "inputLayer"),
        "regression_family" : (str, "regressionFamily"),
        "gen_coeff_table" : (bool, "generateCoefficientTable"),
        "exp_var_matching" : (list, "explanatoryVariableMatching"),
        "var_dependent" : (list, "dependentVariable"),
        "var_explanatory" : (list, "explanatoryVariables"),
        "features_to_predict" : (_FeatureSet, "featuresToPredict"),
        "dep_mapping" : (list, "dependentMapping"),
        "output_name" : (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "output"),
        "output_predicted": (_FeatureSet, "outputPredicted"),
        "coefficient_table" : (_FeatureSet, "coefficientTable")
    }
    return_values=[
        {"name": 'output', "display_name": "Output Features", "type": _FeatureSet},
        {"name" : "output_predicted", "display_name" : "Output Predicted", "type" : _FeatureSet},
        {"name" : "coefficient_table", "display_name" : "Coefficient Table", "type" : _FeatureSet},
        #{"name" : "variable_of_importance", "display_name" : "Variable of Importance", "type" : _FeatureSet}
    ]

    try:
        if future:
            gpjob = _execute_gp_tool(gis, "GeneralizedLinearRegression", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        res = _execute_gp_tool(gis, "GeneralizedLinearRegression", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise

    return

#--------------------------------------------------------------------------
def find_point_clusters(
    input_layer,
    method,
    min_feature_clusters,
    search_distance=None,
    distance_unit=None,
    output_name=None,
    gis=None,
    future=False):
    """
    This tool extracts clusters from your input point features and identifies any surrounding noise.

    For example, a nongovernmental organization is studying a particular pest-borne disease. It has
    a point dataset representing households in a study area, some of which are infested, and some of
    which are not. By using the Find Point Clusters tool, an analyst can determine clusters of
    infested households to help pinpoint an area to begin treatment and extermination of pests.

    ==========================   ===============================================================
    **Argument**                 **Description**
    --------------------------   ---------------------------------------------------------------
    input_layer                  required FeatureSet, The table, point, line or polygon features
                                 containing potential incidents.
    --------------------------   ---------------------------------------------------------------
    method                       required String. The algorithm used for cluster analysis. This
                                 parameter must be specified as DBSCAN or HDBSCAN.
    --------------------------   ---------------------------------------------------------------
    min_feature_clusters         optional Integer. Minimum number of clusters to find in a dataset.
    --------------------------   ---------------------------------------------------------------
    search_distance              optional Float.  The distance to search between points to form
                                 a cluster.  This is required for DBSCAN.
    --------------------------   ---------------------------------------------------------------
    distance_unit                optional String. The `search_distance` units.
    --------------------------   ---------------------------------------------------------------
    output_name                  optional string, The task will create a feature service of the
                                 results. You define the name of the service.
    --------------------------   ---------------------------------------------------------------
    gis                          optional GIS, the GIS on which this tool runs. If not
                                 specified, the active GIS is used.
    --------------------------   ---------------------------------------------------------------
    future                       optional Boolean. If True, a GPJob is returned instead of
                                 results. The GPJob can be queried on the status of the execution.
    ==========================   ===============================================================

    :returns:
       Output feature layer item

    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Find Point Clusters_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Find Point Clusters')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db={
        "input_layer": (_FeatureSet, "inputLayer"),
        "method" : (str, "clusterMethod"),
        "min_feature_clusters": (int, "minFeaturesCluster"),
        "distance_unit": (str, "searchDistanceUnit"),
        "search_distance" : (float, "searchDistance"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values=[
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        if future:
            gpjob = _execute_gp_tool(gis, "FindPointClusters", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        _execute_gp_tool(gis, "FindPointClusters", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise

    return
#--------------------------------------------------------------------------
def calculate_density(
    input_layer,
    fields=None,
    weight="""Uniform""",
    bin_type="""Square""",
    bin_size=None,
    bin_size_unit=None,
    time_step_interval=None,
    time_step_interval_unit=None,
    time_step_repeat_interval=None,
    time_step_repeat_interval_unit=None,
    time_step_reference=None,
    radius=None,
    radius_unit=None,
    area_units="""SquareKilometers""",
    output_name=None,
    gis=None,
    future=False):
    """
    .. image:: _static/images/calculate_density/calculate_density.png

    The ``calculate_density`` tool creates a density map from point features by spreading known quantities of some
    phenomenon (represented as attributes of the points) across the map. The result is a layer of areas classified
    from least dense to most dense.

    For point input, each point should represent the location of some event or incident, and the result layer
    represents a count of the incident per unit area. A higher density value in a new location means that there
    are more points near that location. In many cases, the result layer can be interpreted as a risk surface
    for future events. For example, if the input points represent locations of lightning strikes, the result
    layer can be interpreted as a risk surface for future lightning strikes.

    Other use cases of this tool include the following:

    * Creating crime density maps to help police departments properly allocate resources to high crime areas.
    * Calculating densities of hospitals within a county. The result layer will show areas with high and low accessibility to
      ospitals, and this information can be used to decide where new hospitals should be built.
    * Identifying areas that are at high risk of forest fires based on historical locations of forest fires.
    * Locating communities that are far from major highways in order to plan where new roads should be constructed.

    =================================================     ========================================================================
    **Argument**                                          **Description**
    -------------------------------------------------     ------------------------------------------------------------------------
    input_layer                                           Required point feature layer. The point layer on which the density will be calculated.

                                                          Analysis using ``Square`` or ``Hexagon`` bins requires a projected coordinate system.
                                                          When aggregating layers into bins, the input layer or processing extent (``processSR``) must
                                                          have a projected coordinate system. At 10.5.1, 10.6, and 10.6.1, if a projected coordinate
                                                          system is not specified when running analysis, the World Cylindrical Equal
                                                          Area (WKID 54034) projection will be used. At 10.7 or later, if a projected coordinate system
                                                          is not specified when running analysis, a projection will be picked based on the extent of the data.
                                                          See :ref:`Feature Input<FeatureInput>`.
    -------------------------------------------------     ------------------------------------------------------------------------
    fields                                                Optional string. Provides one or more field specifying the number of incidents at each location.
                                                          You can calculate the density on multiple fields, and the count of points will always have the density calculated.
    -------------------------------------------------     ------------------------------------------------------------------------
    weight                                                Required string. The type of weighting applied to the density calculation. There are two options:

                                                            * ``Uniform`` - Calculates a magnitude-per-area. This is the default.
                                                            * ``Kernel`` - Applies a kernel function to fit a smooth tapered surface to each point.

                                                          The default value is "Uniform".
    -------------------------------------------------     ------------------------------------------------------------------------
    bin_type                                              Required string. The type of bin used to calculate density.

                                                          Choice list: ['Hexagon', 'Square'].
    -------------------------------------------------     ------------------------------------------------------------------------
    bin_size                                              Required float. The distance for the bins that the ``input_layer`` will be analyzed using.
                                                          When generating bins, for Square, the number and units specified determine the
                                                          height and length of the square. For ``Hexagon``, the number and units specified
                                                          determine the distance between parallel sides.
    -------------------------------------------------     ------------------------------------------------------------------------
    bin_size_unit                                         Required string. The distance unit for the bins for which the density will be calculated.
                                                          The linear unit to be used with the value specified in ``bin_size``.

                                                          The default is 'Meters'.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_interval                                    Optional integer. A numeric value that specifies duration of the time step interval. This option is
                                                          only available if the input points are time-enabled and represent an instant in time.

                                                          The default value is 'None'.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_interval_unit                               Optional string. A string that specifies units of the time step interval.
                                                          This option is only available if the input points are time-enabled and represent an instant in time.

                                                          Choice list: ['Milliseconds', 'Seconds', 'Minutes', 'Hours', 'Days', 'Weeks', 'Months', 'Years']

                                                          The default value is 'None'.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_repeat_interval                             Optional integer. A numeric value that specifies how often the time step repeat occurs.
                                                          This option is only available if the input points are time-enabled and of time type instant.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_repeat_interval_unit                        Optional string. A string that specifies the temporal unit of the step repeat.
                                                          This option is only available if the input points are time-enabled and of time type instant.

                                                          Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

                                                          The default value is 'None'.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_reference                                   Optional datetime. A date that specifies the reference time to align the time slices to,
                                                          represented in milliseconds from epoch. If time_step_reference is set
                                                          to 'None', time stepping will align to January 1st, 1970 (datetime(1970, 1, 1)).
                                                          This option is only available if the input points are time-enabled and of time type instant.

                                                          The default value is 'None'.
    -------------------------------------------------     ------------------------------------------------------------------------
    radius                                                Required integer. The size of the neighborhood within which to calculate the density.
                                                          The radius size must be larger than the ``bin_size``.
    -------------------------------------------------     ------------------------------------------------------------------------
    radius_unit                                           Required string. The distance unit for the radius defining the neighborhood for which the density will be calculated.
                                                          The linear unit to be used with the value specified in ``bin_size``.

                                                          Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

                                                          The default value is 'Meters'.
    -------------------------------------------------     ------------------------------------------------------------------------
    area_units                                            Optional string. The desired output units of the density values. If density values are very small, you can increase the
                                                          size of the area units (for example, square meters to square kilometers) to return larger values.
                                                          This value only scales the result. Possible area units are:

                                                          Choice list: ['SquareMeters', 'SquareKilometers', 'Hectares', 'SquareFeet', 'SquareYards', 'SquareMiles', 'Acres'].

                                                          The default value is "SquareKilometers".
    -------------------------------------------------     ------------------------------------------------------------------------
    output_name                                           Optional string. The method will create a feature service of the results. You define the name of the service.
    -------------------------------------------------     ------------------------------------------------------------------------
    gis                                                   Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------------------------------     ------------------------------------------------------------------------
    context                                               Optional dict. The context parameter contains additional settings that affect task execution. For this task, there are four settings:

                                                            * Extent (``extent``) - A bounding box that defines the analysis area. Only those features that intersect the bounding box will be analyzed.
                                                            * Processing spatial reference (``processSR``) - The features will be projected into this coordinate system for analysis.
                                                            * Output spatial reference (``outSR``) - The features will be projected into this coordinate system after the analysis to be saved. The output spatial reference for the spatiotemporal big data store is always WGS84.
                                                            * Data store (``dataStore``) - Results will be saved to the specified data store. The default is the spatiotemporal big data store.
    -------------------------------------------------     ------------------------------------------------------------------------
    future                                                optional Boolean. If True, a GPJob is returned instead of
                                                          results. The GPJob can be queried on the status of the execution.
    =================================================     ========================================================================

    :returns: result_layer : Output Features as feature layer item.

    .. code-block:: python

            # Usage Example: Aggregate the number of Hurricanes within 1 meter to calculate density of Hurricane damage.

            cal_den_result = calculate_density(input_layer=hurricane_lyr,
                                               fields='Damage',
                                               weight='Uniform',
                                               bin_type='Square',
                                               bin_size=1,
                                               bin_size_unit="Meters",
                                               radius=2,
                                               radius_unit="Yards")

    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Calculate Density Analysis_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Calculate Density')

    params['output_name']=_json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db={
        "input_layer": (_FeatureSet, "inputLayer"),
        "fields": (str, "fields"),
        "weight": (str, "weight"),
        "bin_type": (str, "binType"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_repeat_interval": (int, "timeStepRepeatInterval"),
        "time_step_repeat_interval_unit": (str, "timeStepRepeatIntervalUnit"),
        "time_step_reference": (_datetime, "timeStepReference"),
        "radius": (float, "radius"),
        "radius_unit": (str, "radiusUnit"),
        "area_units": (str, "areaUnits"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values=[
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        if future:
            gpjob = _execute_gp_tool(gis, "CalculateDensity", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        _execute_gp_tool(gis, "CalculateDensity", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise


calculate_density.__annotations__={
    'fields': str,
    'weight': str,
    'bin_type': str,
    'bin_size': float,
    'bin_size_unit': str,
    'time_step_interval': int,
    'time_step_interval_unit': str,
    'time_step_repeat_interval': int,
    'time_step_repeat_interval_unit': str,
    'time_step_reference': _datetime,
    'radius': float,
    'radius_unit': str,
    'area_units': str,
    'output_name': str}

#--------------------------------------------------------------------------
def find_hot_spots(
    point_layer,
    bin_size=5,
    bin_size_unit="Miles",
    neighborhood_distance=5,
    neighborhood_distance_unit="Miles",
    time_step_interval=None,
    time_step_interval_unit=None,
    time_step_alignment=None,
    time_step_reference=None,
    output_name=None,
    gis=None,
    future=False):
    """
    .. image:: _static/images/geo_find_hot_spots/geo_find_hot_spots.png

    The ``find_hot_spots`` tool analyzes point data (such as crime incidents, traffic accidents, trees, and so on)
    or field values associated with points. It finds statistically significant spatial clusters of high incidents (hot spots)
    and low incidents (cold spots). Hot spots are locations with lots of points and cold spots are locations with very few points.

    The result map layer shows hot spots in red and cold spots in blue. The darkest red features indicate the strongest
    clustering of point densities; you can be 99 percent confident that the clustering associated with these features
    could not be the result of random chance. Similarly, the darkest blue features are associated with the strongest
    spatial clustering of the lowest point densities. Features that are beige are not part of a statistically
    significant cluster; the spatial pattern associated with these features could very likely be the result of random
    processes and random chance.

    ==============================================================================================  ===============================================================
    **Argument**                                                                                    **Description**
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    point_layer                                                                                     Required feature layer. The point feature layer for which hot spots will be calculated.
                                                                                                    See :ref:`Feature Input<FeatureInput>`.

                                                                                                    .. Note::
                                                                                                        Analysis using bins requires a projected coordinate system. When aggregating layers into bins,
                                                                                                        the input layer or processing extent (``processSR``) must have a projected coordinate system.
                                                                                                        At 10.5.1, 10.6, and 10.6.1, if a projected coordinate system is not specified when running
                                                                                                        analysis, the World Cylindrical Equal Area (WKID 54034) projection will be used. At 10.7 or later,
                                                                                                        if a projected coordinate system is not specified when running analysis, a projection will be
                                                                                                        picked based on the extent of the data.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    bin_size                                                                                        Optional float. The distance for the square bins the ``point_layer`` will be aggregated into.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    bin_size_unit                                                                                   Optional string. The distance unit for the bins with which hot spots will be calculated.
                                                                                                    The linear unit to be used with the value specified in ``bin_size``.
                                                                                                    When generating bins the number and units specified determine the height and length of the square.

                                                                                                    Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

                                                                                                    The default value is ``Miles``.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    neighborhood_distance                                                                           Optional float. The size of the neighborhood within which to calculate the hot spots.
                                                                                                    The radius size must be larger than ``bin_size``.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    neighborhood_distance_unit                                                                      Optional string. The distance unit for the radius defining the neighborhood where the hot spots
                                                                                                    will be calculated. The linear unit to be used with the value specified in ``bin_size``.

                                                                                                    Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

                                                                                                    The default value is 'Miles'.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    time_step_interval                                                                              Optional integer. A numeric value that specifies duration of the time step interval.
                                                                                                    This option is only available if the input points are time-enabled and represent an instant in time.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    time_step_interval_unit                                                                         Optional string. A string that specifies units of the time step interval.
                                                                                                    This option is only available if the input points are time-enabled and represent an instant in time.

                                                                                                    Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    time_step_alignment                                                                             Optional string. Defines how aggregation will occur based on a given ``time_step_interval``. Options are as follows:

                                                                                                    Choice list:['EndTime', 'StartTime', 'ReferenceTime']

                                                                                                        * ``StartTime`` - Time is aligned to the first feature in time.
                                                                                                        * ``EndTime`` - Time is aligned to the last feature in time.
                                                                                                        * ``ReferenceTime`` - Time is aligned a specified time in ``time_step_reference``.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    time_step_reference (Required if ``time_step_alignment`` is ReferenceTime)                      Optional datetime. A date that specifies the reference time to align the time slices to.
                                                                                                    This option is only available if the input points are time-enabled and of time type instant.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    output_name                                                                                     Optional string. The task will create a feature service of the results. You define the name of the service.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    context                                                                                         Optional string. Context contains additional settings that affect task execution. For this task, there are three settings:

                                                                                                    #.  Extent (``extent``) - a bounding box that defines the analysis area. Only those features that intersect the bounding box will be analyzed.
                                                                                                    #. Processing spatial reference (``processSR``) The features will be projected into this coordinate system for analysis.
                                                                                                    #. Output Spatial Reference (``outSR``) - the features will be projected into this coordinate system after the analysis to be saved.
                                                                                                       The output spatial reference for the spatiotemporal big data store is always WGS84.
                                                                                                    #. Data store (``dataStore``) Results will be saved to the specified data store. The default is the spatiotemporal big data store.
    ----------------------------------------------------------------------------------------------  ---------------------------------------------------------------
    gis                                                                                             Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    ==============================================================================================  ===============================================================

    :returns: Output Features as a feature layer collection item

    .. code-block:: python

        # Usage Example: To find significantly hot or cold spots of fire incidents.
        find_hot_spots(point_layer=fire,
                       bin_size=5,
                       bin_size_unit='Miles',
                       neighborhood_distance=5,
                       neighborhood_distance_unit='Miles',
                       time_step_interval=1,
                       time_step_interval_unit="Years",
                       time_step_alignment="StartTime",
                       time_step_reference=None,
                       output_name='find hot spots')


    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Hotspot Analysis_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Find Hotspots')

    params['output_name']=_json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db={
        "point_layer": (_FeatureSet, "pointLayer"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "neighborhood_distance": (float, "neighborhoodDistance"),
        "neighborhood_distance_unit": (str, "neighborhoodDistanceUnit"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_alignment": (str, "timeStepAlignment"),
        "time_step_reference": (_datetime, "timeStepReference"),
        #"cell_size" : (int, "cellSize"),
        #"cell_size_units": (str, "cellSizeUnits"),
        #"shape_type" : (str, "shapeType"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values=[
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        if future:
            gpjob = _execute_gp_tool(gis, "FindHotSpots", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        _execute_gp_tool(gis, "FindHotSpots", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise

find_hot_spots.__annotations__={
    'bin_size': float,
    'bin_size_unit': str,
    'neighborhood_distance': float,
    'neighborhood_distance_unit': str,
    'time_step_interval': int,
    'time_step_interval_unit': str,
    'time_step_alignment': str,
    'time_step_reference': _datetime,
    'output_name': str}

#--------------------------------------------------------------------------
def create_space_time_cube(point_layer: _FeatureSet,
                           bin_size: float,
                           bin_size_unit: str,
                           time_step_interval: int,
                           time_step_interval_unit: str,
                           time_step_alignment: str=None,
                           time_step_reference: _datetime=None,
                           summary_fields: str=None,
                           output_name: str=None,
                           context: str=None,
                           gis=None,
                           future: bool=False) -> DataFile:
    """
    Summarizes a set of points into a netCDF data structure by aggregating them into space-time bins. Within each bin,
    the points are counted and specified attributes are aggregated. For all bin locations, the trend for counts and
    summary field values are evaluated.

    Parameters:

       point_layer: Input Features (FeatureSet). Required parameter.

       bin_size: Distance Interval (float). Required parameter.

       bin_size_unit: Distance Interval Unit (str). Required parameter.
          Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

       time_step_interval: Time Step Interval (int). Required parameter.

       time_step_interval_unit: Time Step Interval Unit (str). Required parameter.
          Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

       time_step_alignment: Time Step Alignment (str). Optional parameter.
          Choice list:['EndTime', 'StartTime', 'ReferenceTime']

       time_step_reference: Time Step Reference (datetime). Optional parameter.

       summary_fields: Summary Fields (str). Optional parameter.

       output_name: Output Name (str). Required parameter.

       context: Context (str). Optional parameter.

        gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

        future: Optional, If True, a GPJob is returned instead of results. The GPJob can be queried on the status of the execution.

    Returns:
       output_cube - Output Space Time Cube as a DataFile

    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    _set_context(params)

    param_db={
        "point_layer": (_FeatureSet, "pointLayer"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_alignment": (str, "timeStepAlignment"),
        "time_step_reference": (_datetime, "timeStepReference"),
        "summary_fields": (str, "summaryFields"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output_cube": (DataFile, "Output Space Time Cube"),
    }
    return_values=[
        {"name": "output_cube", "display_name": "Output Space Time Cube", "type": DataFile},
    ]
    if future:
        output_service = None
        gpjob = _execute_gp_tool(gis, "CreateSpaceTimeCube", params, param_db, return_values, _use_async, url, True, future=future)
        return GAJob(gpjob=gpjob, return_service=output_service)
    return _execute_gp_tool(gis, "CreateSpaceTimeCube", params, param_db, return_values, _use_async, url, True, future=future)

