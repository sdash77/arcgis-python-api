import numpy as np
import pandas as pd

def std(array):
    """
    Calculates the based on the standard deviation of the mean.
    """
    if isinstance(array, pd.Series) == False:
        array = pd.Series(array)
    results = []
    min_val = array.min()
    max_val = array.max()
    mean = array.mean()
    std = array.std()
    steps = [-1.5,-.5, .5, 1.5]
    values = [min_val] + [mean + step * std for step in steps] + [max_val]
    results.append({"classMinValue": min_val, "classMaxValue": values[1], "label": "< -1.5 Std. Dev."})
    results.append({"classMinValue": values[1], "classMaxValue": values[2], "label": "-1.5 - -0.5 Std. Dev."})
    results.append({"classMinValue": values[2], "classMaxValue": values[3], "label": "-0.5 - 0.5 Std. Dev."})
    results.append({"classMinValue": values[3], "classMaxValue": values[4], "label": "0.5 - 1.5 Std. Dev."})
    results.append({"classMinValue": values[4], "classMaxValue": values[5], "label": "> 1.5 Std. Dev."})
    return results