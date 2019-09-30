import numpy as np
import pandas as pd
def quantiles(array, c=3):
    """
    Calculates the Quantiles based on a normalize distribution curve.
    Each class has roughly the same number of features. If your data is
    evenly distributed and you want to emphasize the difference in relative
    position between features, you should use the quantile classification
    method.
    """
    if c <= 0:
        raise ValueError("c must be greater than 0.")
    if isinstance(array, pd.Series) == False:
        array = pd.Series(array)
    results = []
    if array.min() < 0:
        min_val = array.min()
    else:
        min_val = 0
    for i in range(c):
        q = (i + 1)/c
        if i == 0:
            mv = array.quantile(q, 'nearest')
            results.append({"classMinValue": min_val, "classMaxValue": mv, "label": "%s - %s" % (min_val, mv)})
        else:
            mv = array.quantile(q, 'nearest')
            min_value = results[i-1]['classMaxValue']
            results.append({"classMinValue": min_value, "classMaxValue": mv, "label": "%s - %s" % (min_value, mv)})
    return results