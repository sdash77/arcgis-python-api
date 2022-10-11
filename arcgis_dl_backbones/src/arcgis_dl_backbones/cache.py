
def cache():
    import torchvision

    # Deeplab
    torchvision.models.segmentation.deeplabv3_resnet101(pretrained=True)

    # densenet
    torchvision.models.densenet121(pretrained=True)
    torchvision.models.densenet161(pretrained=True)
    torchvision.models.densenet169(pretrained=True)
    torchvision.models.densenet201(pretrained=True)

    # Mobilenet    
    torchvision.models.mobilenet_v2(pretrained=True)
    torchvision.models.mobilenet_v3_large(pretrained=True)
    torchvision.models.mobilenet_v3_small(pretrained=True)

    # resnet
    torchvision.models.resnet18(pretrained=True)
    torchvision.models.resnet34(pretrained=True)
    torchvision.models.resnet50(pretrained=True)
    torchvision.models.resnet101(pretrained=True)
    torchvision.models.resnet152(pretrained=True)

    # Rcnn
    torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)

    # Vgg
    torchvision.models.vgg11(pretrained=True)
    torchvision.models.vgg11_bn(pretrained=True)
    torchvision.models.vgg13(pretrained=True)
    torchvision.models.vgg13_bn(pretrained=True)
    torchvision.models.vgg16(pretrained=True)
    torchvision.models.vgg16_bn(pretrained=True)
    torchvision.models.vgg19(pretrained=True)
    torchvision.models.vgg19_bn(pretrained=True)

    # Yolo
    from arcgis.learn.models import YOLOv3
    YOLOv3(pretrained=True)

if __name__ == '__main__':
    cache()