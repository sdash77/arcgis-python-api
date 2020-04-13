import torch
import numpy as np
from .pointcloud_data import calculate_metrics
import pandas as pd

def calculate_precision_recall(all_y, all_pred, false_positives, true_positives, false_negatives, class_mapping):

    for i in range(len(all_y)):        
        false_positives[all_pred[i]] += int(all_y[i] != all_pred[i])
        true_positives[all_pred[i]] += int(all_y[i] == all_pred[i])
        false_negatives[all_y[i]] += int(all_y[i] != all_pred[i])

    precision, recall, f_1 = calculate_metrics(false_positives, true_positives, false_negatives)
    data = [precision, recall, f_1]
    index = ['precision', 'recall', 'f1_score']
    class_mapping = {z+1:v for z, v in enumerate(class_mapping.values())}
    df = pd.DataFrame(data, columns=['background']+[class_mapping[i] for i in range(1, len(false_negatives))], index=index) 
    return df        

def per_class_metrics(self, **kwargs):
    dl = kwargs.get('dl', None)
    model = self.learn.model.eval()
    all_y = []
    all_pred = []    
    false_positives = [0] * self._data.c
    true_positives = [0] * self._data.c
    false_negatives = [0] * self._data.c
    for batch in self._data.valid_dl if dl is None else dl:
        x, y = batch
        y = y.cpu().numpy()
        with torch.no_grad():
            predictions = model(x).detach().argmax(dim=1).cpu().numpy()
        all_y.append(y.reshape(-1))
        all_pred.append(predictions.reshape(-1))

    all_y = np.concatenate(all_y)
    all_pred = np.concatenate(all_pred)

    return calculate_precision_recall(all_y, all_pred, false_positives, true_positives, false_negatives, self._data.class_mapping)
