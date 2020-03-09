import torch
from torch import nn, LongTensor
import torch.nn.functional as F
from fastai.vision import imagenet_stats
from fastai.vision.image import ImageBBox
from fastai.vision.data import ObjectCategoryList, ObjectItemList
from fastprogress.fastprogress import progress_bar
import numpy as np
import random
import math

def conv_params(in_size, out_size):
    filters = [3,2,5,4]
    strides = [1,2,3] # max_stride = 3
    pads = [0,1,2,3] # max pad
    
    if out_size == 1:
        return 1, 0, in_size
    
    for filter_size in filters:
        for pad in pads:
            for stride in strides:
                if ((out_size - 1) * stride == (in_size - filter_size) + 2 * pad):
                    return stride, pad, filter_size
    return None, None, None

def conv_paramsv2(in_size, out_size):
    filters = [3]
    strides = [1,2] # max_stride = 2
    pads = [0,1] # max pad
    
    if out_size == 1:
        return 1, 0, in_size
    
    for filter_size in filters:
        for pad in pads:
            for stride in strides:
                if (((in_size - filter_size) + 2 * pad) // stride) + 1 == out_size:
                    return stride, pad, filter_size
    return None, None, None


class StdConv(nn.Module):
    def __init__(self, nin, nout, filter_size=3, stride=2, padding=1, drop=0.1):
        super().__init__()
        self.conv = nn.Conv2d(nin, nout, filter_size, stride=stride, padding=padding)
        self.bn = nn.BatchNorm2d(nout)
        self.drop = nn.Dropout(drop)
        
    def forward(self, x): 
        return self.drop(self.bn(F.relu(self.conv(x))))

class StdConvv2(nn.Module):
    def __init__(self, nin, nout, upsample_size=0, upsample=False, filter_size=3, stride=2, padding=1, drop=0.1):
        super().__init__()
        self.upsample = upsample
        self.conv = nn.Conv2d(nin, nout, filter_size, stride=stride, padding=padding)
        self.up = nn.Upsample(upsample_size)
        self.bn = nn.BatchNorm2d(nout)
        self.drop = nn.Dropout(drop)
        
    def forward(self, x):
        if self.upsample == True:
             return self.drop(self.bn(F.relu(self.conv(self.up(x)))))
        return self.drop(self.bn(F.relu(self.conv(x))))
            
def flatten_conv(x,k):
    bs,nf,gx,gy = x.size()
    x = x.permute(0,2,3,1).contiguous()
    return x.view(bs,-1,nf//k)

class OutConv(nn.Module):
    def __init__(self, k, nin, num_classes, bias):
        super().__init__()
        self.k = k
        self.oconv1 = nn.Conv2d(nin, (num_classes)*k, 3, padding=1)
        self.oconv2 = nn.Conv2d(nin, 4*k, 3, padding=1)
        self.oconv1.bias.data.zero_().add_(bias)
        
    def forward(self, x):
        return [flatten_conv(self.oconv1(x), self.k),
                flatten_conv(self.oconv2(x), self.k)]
    
class SSDHead(nn.Module):
    def __init__(self, grids, anchors_per_cell, num_classes, num_features=7, drop=0.3, bias=-4., num_channels=512):
        super().__init__()
        self.drop = nn.Dropout(drop)
        
        self.sconvs = nn.ModuleList([])
        self.oconvs = nn.ModuleList([])
        
        self.anc_grids = grids
        
        self._k = anchors_per_cell

        
        self.sconvs.append(StdConv(num_channels, 256, stride=1, drop=drop))
        
        
        for i in range(len(grids)):
            
            if i == 0:
                stride, pad, filter_size = conv_params(num_features, grids[i])
            else:
                stride, pad, filter_size = conv_params(grids[i-1], grids[i])
            
            if stride is None:
                print(grids[i-1], ' --> ', grids[i])
                raise Exception('cannot create model for specified grids')
                
            self.sconvs.append(StdConv(256, 256, filter_size, stride=stride, padding=pad, drop=drop))
            self.oconvs.append(OutConv(self._k, 256, num_classes=num_classes, bias=bias))
       
    def forward(self, x):
        x = self.drop(F.relu(x))
        x = self.sconvs[0](x)
        out_classes = []
        out_bboxes = []
        for sconv, oconv in zip(self.sconvs[1:], self.oconvs):
            x = sconv(x)
            out_class, out_bbox = oconv(x)
            out_classes.append(out_class)
            out_bboxes.append(out_bbox)
            
        return [torch.cat(out_classes, dim=1),
                torch.cat(out_bboxes, dim=1)]

class SSDHeadv2(nn.Module):
    def __init__(self, grids, anchors_per_cell, num_classes, num_features=7, drop=0.3, bias=-4., num_channels=512):
        super().__init__()
        self.drop = nn.Dropout(drop)
        
        self.sconvs = nn.ModuleList([])
        self.oconvs = nn.ModuleList([])
        
        self.anc_grids = grids
        
        self._k = anchors_per_cell

        
        self.sconvs.append(StdConvv2(num_channels, 256, stride=1, drop=drop))
        
        
        for i in range(len(grids)):
            
            upsample = False

            if i == 0 and num_features >= grids[i]:
                stride, pad, filter_size = conv_paramsv2(num_features, grids[i])
                if stride is None:
                    upsample = True
                    stride, pad, filter_size = 1, 1, 3
            elif i == 0 and num_features < grids[i]:
                upsample = True
                stride, pad, filter_size = 1, 1, 3

            elif i != 0 and grids[i-1] > grids[i]:
                stride, pad, filter_size = conv_paramsv2(grids[i-1], grids[i])
                if stride is None:
                    upsample=True
                    stride, pad, filter_size = 1,1,3
            else:
                upsample=True
                stride, pad, filter_size = 1,1,3 
                
            self.sconvs.append(StdConvv2(256, 256, grids[i], upsample, filter_size, stride=stride, padding=pad, drop=drop))
            self.oconvs.append(OutConv(self._k, 256, num_classes=num_classes, bias=bias))
                
    def forward(self, x):
        x = self.drop(F.relu(x))
        x = self.sconvs[0](x)
        out_classes = []
        out_bboxes = []
        for sconv, oconv in zip(self.sconvs[1:], self.oconvs):
            x = sconv(x)
            out_class, out_bbox = oconv(x)
            out_classes.append(out_class)
            out_bboxes.append(out_bbox)
            
        return [torch.cat(out_classes, dim=1),
                torch.cat(out_bboxes, dim=1)]


def one_hot_embedding(labels, num_classes):
    return torch.eye(num_classes)[labels.data.cpu()]

class BCE_Loss(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.num_classes = num_classes

    def forward(self, pred, targ):
        t = one_hot_embedding(targ, self.num_classes)
        t = torch.Tensor(t[:,1:].contiguous()).to(pred.device)
        x = pred[:,1:]
        w = self.get_weight(x,t)
        return F.binary_cross_entropy_with_logits(x, t, w, reduction='sum')/(self.num_classes-1)
    
    def get_weight(self,x,t): return None

class FocalLoss(BCE_Loss):
    def get_weight(self,x,t):
        alpha,gamma = 0.25,1
        p = x.sigmoid()
        pt = p*t + (1-p)*(1-t)
        w = alpha*t + (1-alpha)*(1-t)
        w = w * (1-pt).pow(gamma)
        return w.detach()

def nms(boxes, scores, overlap=0.5, top_k=100):
    keep = scores.new(scores.size(0)).zero_().long()
    if boxes.numel() == 0: return keep
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    area = torch.mul(x2 - x1, y2 - y1)
    v, idx = scores.sort(0)  # sort in ascending order
    idx = idx[-top_k:]  # indices of the top-k largest vals
    xx1 = boxes.new()
    yy1 = boxes.new()
    xx2 = boxes.new()
    yy2 = boxes.new()
    w = boxes.new()
    h = boxes.new()

    count = 0
    while idx.numel() > 0:
        i = idx[-1]  # index of current largest val
        keep[count] = i
        count += 1
        if idx.size(0) == 1: break
        idx = idx[:-1]  # remove kept element from view
        # load bboxes of next highest vals
        torch.index_select(x1, 0, idx, out=xx1)
        torch.index_select(y1, 0, idx, out=yy1)
        torch.index_select(x2, 0, idx, out=xx2)
        torch.index_select(y2, 0, idx, out=yy2)
        # store element-wise max with next highest score
        xx1 = torch.clamp(xx1, min=x1[i])
        yy1 = torch.clamp(yy1, min=y1[i])
        xx2 = torch.clamp(xx2, max=x2[i])
        yy2 = torch.clamp(yy2, max=y2[i])
        w.resize_as_(xx2)
        h.resize_as_(yy2)
        w = xx2 - xx1
        h = yy2 - yy1
        # check sizes of xx1 and xx2.. after each iteration
        w = torch.clamp(w, min=0.0)
        h = torch.clamp(h, min=0.0)
        inter = w*h
        # IoU = i / (area(a) + area(b) - i)
        rem_areas = torch.index_select(area, 0, idx)  # load remaining areas)
        union = (rem_areas - inter) + area[i]
        IoU = inter/union  # store result in iou
        # keep only elements with an IoU <= overlap
        idx = idx[IoU.le(overlap)]
    return keep, count

def _analyze_pred(pred, thresh=0.5, nms_overlap=0.1, ssd=None, ret_scores=True, device=torch.device('cpu')):
    """
    It works on a single activation, does not support batch.
    """
    from ._ssd import SingleShotDetector
    from ._retinanet import RetinaNet

    if type(ssd).__name__ == "SingleShotDetector": #isinstance(ssd, SingleShotDetector):
        b_clas, b_bb = pred
        a_ic = ssd._actn_to_bb(b_bb.to(device), ssd._anchors.to(device), ssd._grid_sizes.to(device))
        conf_scores, clas_ids = b_clas[:, 1:].max(1)
        conf_scores = b_clas.t().sigmoid().to(device)

        out1, bbox_list, class_list = [], [], []

        for cl in range(1, len(conf_scores)):
            c_mask = conf_scores[cl] > thresh
            if c_mask.sum() == 0: 
                continue
            scores = conf_scores[cl][c_mask]
            l_mask = c_mask.unsqueeze(1)
            l_mask = l_mask.expand_as(a_ic)
            boxes = a_ic[l_mask].view(-1, 4) # boxes are now in range[ 0, 1]
            boxes = (boxes-0.5) * 2.0        # putting boxes in range[-1, 1]
            ids, count = nms(boxes.data, scores, nms_overlap, 50) # FIX- NMS overlap hardcoded
            ids = ids[:count]
            out1.append(scores[ids])
            bbox_list.append(boxes.data[ids])
            class_list.append(torch.tensor([cl]*count))

        if len(bbox_list) == 0:
            return None #torch.Tensor(size=(0,4)), torch.Tensor()

        if ret_scores:
            return torch.cat(bbox_list, dim=0).to(device), torch.cat(class_list, dim=0).to(device), torch.cat(out1, dim=0).to(device)
        else:
            return torch.cat(bbox_list, dim=0), torch.cat(class_list, dim=0) # torch.cat(out1, dim=0), 
    
    elif type(ssd).__name__ == "RetinaNet":
        from ._retinanet_utils import get_predictions
        bbox_pred, preds, scores =  get_predictions(pred, 0, crit=ssd._loss_f, detect_thresh=thresh, nms_overlap=nms_overlap)
        return bbox_pred, preds, scores

def _reconstruct(t, x, pad_idx, classes):
    if t is None: return None

    t = list(t)
    if len(t[0]) == 0:
        return None

    if len(t) == 3:
        bboxes, labels, scores = t
        if len((labels - pad_idx).nonzero()) == 0: 
            ret = ImageBBox.create(*x.size, bboxes, labels=labels, classes=classes, scale=False)
            ret.scores = t[2]
            return ret
        i = (labels - pad_idx).nonzero().min()
        bboxes,labels,scores = bboxes[i:],labels[i:], scores[i:]
        ret = ImageBBox.create(*x.size, bboxes, labels=labels, classes=classes, scale=False)
        ret.scores = t[2]
        return ret
    else:
        bboxes, labels = t
        if len((labels - pad_idx).nonzero()) == 0: return ImageBBox.create(*x.size, bboxes, labels=labels, classes=classes, scale=False)
        i = (labels - pad_idx).nonzero().min()
        bboxes,labels = bboxes[i:],labels[i:]
        return ImageBBox.create(*x.size, bboxes, labels=labels, classes=classes, scale=False)    


class SSDObjectCategoryList(ObjectCategoryList):
    "`ItemList` for labelled bounding boxes detected using SSD."
    def analyze_pred(self, pred, thresh=0.5, nms_overlap=0.1, ssd=None, ret_scores=True, device=torch.device('cpu')):
        return _analyze_pred(pred, thresh=thresh, nms_overlap=nms_overlap, ssd=ssd, ret_scores=ret_scores, device=device)

    def reconstruct(self, t, x):
        return _reconstruct(t, x, self.pad_idx, self.classes)

    
class SSDObjectItemList(ObjectItemList):
    "`ItemList` suitable for object detection."
    _label_cls,_square_show_res = SSDObjectCategoryList,False

def compute_ap(precision, recall):
    "Compute the average precision for `precision` and `recall` curve."
    recall = np.concatenate(([0.], list(recall), [1.]))
    precision = np.concatenate(([0.], list(precision), [0.]))
    for i in range(len(precision) - 1, 0, -1):
        precision[i - 1] = np.maximum(precision[i - 1], precision[i])
    idx = np.where(recall[1:] != recall[:-1])[0]
    ap = np.sum((recall[idx + 1] - recall[idx]) * precision[idx + 1])
    return ap

def compute_class_AP(ssd, dl, n_classes, show_progress, iou_thresh=0.5, detect_thresh=0.35, num_keep=100):
    tps, clas, p_scores = [], [], []
    classes, n_gts = LongTensor(range(n_classes)),torch.zeros(n_classes).long()
    with torch.no_grad():
        for input,target in progress_bar(dl, display=show_progress):
            output = ssd.learn.pred_batch(batch=(input, target))#, reconstruct=True)

            for i in range(target[0].size(0)):
                op = ssd._data.y.analyze_pred((output[0][i], output[1][i]), thresh=detect_thresh, nms_overlap=iou_thresh, ssd=ssd, ret_scores=True, device=ssd._device)
                tgt_bbox, tgt_clas = ssd._get_y(target[0][i], target[1][i])
                
                try:
                    bbox_pred, preds, scores = op
                    if len(bbox_pred) != 0 and len(tgt_bbox) != 0:
                        ious = ssd._jaccard(bbox_pred, tgt_bbox)
                        max_iou, matches = ious.max(1)
                        detected = []
                        for i in range(len(preds)):
                            if max_iou[i] >= iou_thresh and matches[i] not in detected and tgt_clas[matches[i]] == preds[i]:
                                detected.append(matches[i])
                                tps.append(1)
                            else: tps.append(0)
                        clas.append(preds.cpu())
                        p_scores.append(scores.cpu())
                except Exception as e:
                    pass
                n_gts += ((tgt_clas.cpu()[:,None] - 1) == classes[None,:]).sum(0)

    # If no true positives are found return an average precision score of 0.
    if len(tps) == 0: return [0. for cls in range(1, n_classes + 1)]

    tps, p_scores, clas = torch.tensor(tps), torch.cat(p_scores,0), torch.cat(clas,0)
    fps = 1-tps
    idx = p_scores.argsort(descending=True)
    tps, fps, clas = tps[idx], fps[idx], clas[idx]
    aps = []
    for cls in range(1,n_classes+1):
        tps_cls, fps_cls = tps[clas==cls].float().cumsum(0), fps[clas==cls].float().cumsum(0)
        if tps_cls.numel() != 0 and tps_cls[-1] != 0:
            precision = tps_cls / (tps_cls + fps_cls + 1e-8)
            recall = tps_cls / (n_gts[cls - 1] + 1e-8)
            aps.append(compute_ap(precision, recall))
        else: aps.append(0.)
    return aps

def iou(ann, centroids): 
    
    similarities = []

    for centroid in centroids:

        inter = np.prod(np.minimum(ann, centroid))       
        union = np.prod(ann) + np.prod(centroid) - inter
        similarities.append(inter/union)

    return np.array(similarities)


def avg_iou(bboxes, centroids):
    
    sum = 0.
    
    for bbox in bboxes:
        sum += max(iou(bbox, centroids))
        
    return sum/bboxes.shape[0]


def kmeans(bboxes, num_anchor):
    # Method based on https://github.com/experiencor/keras-yolo3

    num_points, dim = bboxes.shape
    prev_centroids = np.ones(num_points)*(-1)
    indices = [random.randrange(num_points) for i in range(num_anchor)]
    centroids = bboxes[indices]
    
    while True:
        distances = []
        for bbox in bboxes:
            d = 1 - iou(bbox, centroids)
            distances.append(d)
        distances = np.array(distances)
        cur_centroids = np.argmin(distances, axis=1)
        
        if (prev_centroids == cur_centroids).all() :
            return centroids
        
        centroid_sums = np.zeros((num_points, dim), np.float)
        for i in range(num_points):
            centroid_sums[cur_centroids[i]] += bboxes[i]
        for i in range(num_anchor):
            centroids[i] = centroid_sums[i]/(np.sum(cur_centroids == i) + 1e-6)
            
        prev_centroids = cur_centroids.copy()
    
def show_results_multispectral(self, nrows=5, thresh=0.3, nms_overlap=0.1, alpha=1, **kwargs): # parameters adjusted in kwargs
    from matplotlib import pyplot as plt
    from matplotlib import patheffects

    # Get Number of items
    ncols = 2

    type_data_loader = kwargs.get('data_loader', 'validation') # options : traininig, validation, testing
    if type_data_loader == 'training':
        data_loader = self._data.train_dl
    elif type_data_loader == 'validation':
        data_loader = self._data.valid_dl
    elif type_data_loader == 'testing':
        data_loader = self._data.test_dl
    else:
        e = Exception(f'could not find {type_data_loader} in data.')
        raise(e)

    nodata = kwargs.get('nodata', 0)

    index = kwargs.get('start_index', 0)

    imsize = kwargs.get('imsize', 4)

    title_font_size = 16
    _top = 1 - (math.sqrt(title_font_size)/math.sqrt(100*nrows*imsize))
    top = kwargs.get('top', _top)

    statistics_type = kwargs.get('statistics_type', 'dataset') # Accepted Values `dataset`, `DRA`
    label_font_size = kwargs.get('label_font_size', 16)
    
    # Get Batch
    x_batch, y_batch = [], []
    i = 0
    dl_iterater = iter(data_loader)
    while i < nrows:
        x, y = next(dl_iterater)
        x_batch.append(x)
        y_batch.append(y)
        i+=self._data.batch_size
    x_batch = torch.cat(x_batch)
    y_bboxes = []
    y_classes = []
    for yb in y_batch:
        y_bboxes.extend(yb[0])
        y_classes.extend(yb[1])
    
     # Get Predictions
    # predictions_class_store = []
    # predictions_confidence_store = []
    # predictions_activation_store = []
    # for i in range(0, x_batch.shape[0], self._data.batch_size):
    #     _classes_sparse, _activations = self.learn.model.eval()(x_batch[i:i+self._data.batch_size])
    #     _confidences, _classes = _classes_sparse[:, :, 1:].max(dim=-1) # _class_confidences are not used anywhere
    #     #_confidences = torch.stack([_classes_sparse[:, :, -1], _confidences], dim=-1).max(dim=-1)[0] # Confidence wether there is an object in the anchor box or not
    #     predictions_confidence_store.append(_confidences)
    #     predictions_class_store.append(_classes)
    #     predictions_activation_store.append(_activations)
    # predictions_activation_store = torch.cat(predictions_activation_store)
    # predictions_class_store = torch.cat(predictions_class_store)
    # predictions_confidence_store = torch.cat(predictions_confidence_store)
    
    predictions_class_store = []
    predictions_activation_store = []
    for i in range(0, x_batch.shape[0], self._data.batch_size):
        if self._backend == 'pytorch':
            _classes_sparse, _activations = self.learn.model.eval()(x_batch[i:i+self._data.batch_size])
        elif self._backend == 'tensorflow':
            from .._utils.fastai_tf_fit import _pytorch_to_tf_batch
            _classes_sparse, _activations = self.learn.model(_pytorch_to_tf_batch(x_batch[i:i+self._data.batch_size]))
            _classes_sparse, _activations = _classes_sparse.detach().numpy(), _activations.detach().numpy()
            _classes_sparse, _activations = torch.tensor(_classes_sparse), torch.tensor(_activations)
        predictions_class_store.append(_classes_sparse)
        predictions_activation_store.append(_activations)
    predictions_activation_store = torch.cat(predictions_activation_store)
    predictions_class_store = torch.cat(predictions_class_store)
    # predictions_bbox_store, predictions_class_store, predictions_confidence_store = _analyze_pred((predictions_class_store, predictions_activation_store), thresh=thresh, nms_overlap=nms_overlap, ssd=self, ret_scores=True, device=self._device)


    if self._is_multispectral:

        rgb_bands = kwargs.get('rgb_bands', self._data._symbology_rgb_bands)

        e = Exception('`rgb_bands` should be a valid band_order, list or tuple of length 3 or 1.')
        symbology_bands = []
        if not ( len(rgb_bands) == 3 or len(rgb_bands) == 1 ):
            raise(e)
        for b in rgb_bands:
            if type(b) == str:
                b_index = self._bands.index(b)
            elif type(b) == int:
                self._bands[b] # To check if the band index specified by the user really exists.
                b_index = b
            else:
                raise(e)
            b_index = self._data._extract_bands.index(b_index)
            symbology_bands.append(b_index)

        # Denormalize X
        x_batch = (self._data._scaled_std_values[self._data._extract_bands].view(1, -1, 1, 1).to(x_batch) * x_batch ) + self._data._scaled_mean_values[self._data._extract_bands].view(1, -1, 1, 1).to(x_batch)

        # Extract RGB Bands
        symbology_x_batch = x_batch[:, symbology_bands]
        if statistics_type == 'DRA':
            shp = symbology_x_batch.shape
            min_vals = symbology_x_batch.view(shp[0], shp[1], -1).min(dim=2)[0]
            max_vals = symbology_x_batch.view(shp[0], shp[1], -1).max(dim=2)[0]
            symbology_x_batch = symbology_x_batch / ( max_vals.view(shp[0], shp[1], 1, 1) - min_vals.view(shp[0], shp[1], 1, 1) + .001 )
    else:
        # normalization stats
        norm_mean = torch.tensor(imagenet_stats[0]).to(x_batch).view(1, -1, 1, 1)
        norm_std = torch.tensor(imagenet_stats[1]).to(x_batch).view(1, -1, 1, 1)
        symbology_x_batch = (x_batch * norm_std) + norm_mean

    # Channel first to channel last for plotting
    symbology_x_batch = symbology_x_batch.permute(0, 2, 3, 1)
    # Clamp float values to range 0 - 1
    if symbology_x_batch.mean() < 1:
        symbology_x_batch = symbology_x_batch.clamp(0, 1)
    
    # Squeeze channels if single channel (1, 224, 224) -> (224, 224)
    if symbology_x_batch.shape[-1] == 1:
        symbology_x_batch = symbology_x_batch.squeeze()

    # Get color Array
    color_array = self._data._multispectral_color_array
    color_array[:, 3] = alpha

    # Size for plotting
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*imsize, nrows*imsize))
    fig.suptitle('Ground Truth / Predictions', fontsize=title_font_size)
    plt.subplots_adjust(top=top)
    idx=0
    for r in range(0, nrows):
        # Plot Ground Truth
        ax_ground_truth = ax[r][0]
        ax_ground_truth.axis('off')
        ax_ground_truth.imshow(symbology_x_batch[idx])
        gt_classes = y_classes[idx][y_classes[idx] > 0]
        gt_bboxes = y_bboxes[idx][y_classes[idx] > 0]
        gt_bboxes = (gt_bboxes+1)*.5
        gt_bboxes = gt_bboxes.clamp(0, 1)*(x_batch.shape[-1]-1)
        for i, bbox in enumerate(gt_bboxes):
            xs = bbox[[1, 1, 3, 3, 1]]
            ys = bbox[[0, 2, 2, 0, 0]]
            color = self._data._multispectral_color_array[gt_classes[i]]
            ax_ground_truth.plot(xs, ys, color=color, linewidth=2, path_effects=[patheffects.Stroke(linewidth=3, foreground='black'), patheffects.Normal()])
            ax_ground_truth.text(xs[0]+1, ys[0]+1+(label_font_size*(x_batch.shape[-1]-1)/256), self._data.classes[gt_classes[i]], size=label_font_size, color=color, path_effects=[patheffects.Stroke(linewidth=1, foreground='black'), patheffects.Normal()])

        # Plot Predictions
        ax_prediction  = ax[r][1]
        ax_prediction.axis('off')
        ax_prediction.imshow(symbology_x_batch[idx])
        analyzed_prediction = _analyze_pred(
            (predictions_class_store[idx], predictions_activation_store[idx]), 
            thresh=thresh, 
            nms_overlap=nms_overlap, 
            ssd=self, 
            ret_scores=True, 
            device=self._device
        )
        if analyzed_prediction is not None:
            predicted_bboxes, predicted_classes, predicted_confidences = analyzed_prediction
            predicted_bboxes = (predicted_bboxes+1)*.5
            predicted_bboxes = predicted_bboxes.clamp(0, 1)*(x_batch.shape[-1]-1)
            if len(predicted_bboxes) > 0:
                for i, bbox in enumerate(predicted_bboxes):
                    xs = bbox[[1, 1, 3, 3, 1]]
                    ys = bbox[[0, 2, 2, 0, 0]]
                    color = self._data._multispectral_color_array[predicted_classes[i]]
                    ax_prediction.plot(xs, ys, color=color, linewidth=2, path_effects=[patheffects.Stroke(linewidth=3, foreground='black'), patheffects.Normal()])
                    ax_prediction.text(xs[0]+1, ys[0]+1+(label_font_size*(x_batch.shape[-1]-1)/256), self._data.classes[predicted_classes[i]], size=label_font_size, color=color, path_effects=[patheffects.Stroke(linewidth=1, foreground='black'), patheffects.Normal()])
            
        idx+=1
    return ax