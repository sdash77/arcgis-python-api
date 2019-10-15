import numpy as np

HAS_OPENCV = True
try:
    import cv2
except:
    HAS_OPENCV = False


def _get_image_chips(image, chip_dim):
    img_h, img_w, _ = image.shape
    chips_data = []
    stride = chip_dim // 2
    start_x = 0
    start_y = 0

    if chip_dim > img_w or chip_dim > img_h:
        return [{'height': img_h, 'width': img_w, 'chip': image, 'xmin': start_x, 'ymin': start_y, 'predictions': []}]

    while start_x < img_w:
        start_y = 0
        while start_y < img_h:
            chip = image[start_y: start_y + chip_dim, start_x: start_x + chip_dim, :]

            if (chip.shape[0] != chip_dim) or (chip.shape[1] != chip_dim):
                tmp = np.zeros((chip_dim, chip_dim, 3))
                tmp[0:chip.shape[0], 0:chip.shape[1], :] = chip[:, :, :]
                chip = tmp.astype(np.uint8)

            start_y = start_y + stride
            chips_data.append({'height': chip_dim, 'width': chip_dim, 'chip': chip, 'xmin': start_x, 'ymin': start_y, 'predictions': []})
        start_x = start_x + stride

    return chips_data


def _get_transformed_predictions(chips_data):
    predictions = []
    labels = []
    scores = []
    for chip_data in chips_data:
        for prediction in chip_data['predictions']:
            prediction['xmin'] = prediction['xmin'] + chip_data['xmin']
            prediction['ymin'] = prediction['ymin'] + chip_data['ymin']

            predictions.append([
                prediction['xmin'],
                prediction['ymin'],
                prediction['width'],
                prediction['height']
            ])
            labels.append(prediction['label'].obj)
            scores.append(prediction['score'])

    return predictions, labels, scores


def _draw_predictions(frame, predictions, labels):
    for index, data in enumerate(predictions):
        frame = cv2.rectangle(
            frame,
            (int(data[0]), int(data[1])), (int(data[0] + data[2]), int(data[1] + data[3])),
            (255, 255, 255),
            5
        )
        cv2.putText(
            frame,
            labels[index],
            (int(data[0]), int(data[1]) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            5
        )

    return frame


def _exclude_detection(data, chip_width, chip_height):
    if chip_height < chip_width:
        padding = chip_height // 4
    else:
        padding = chip_width // 4

    center_coord_x = data[0] + data[2]/2
    center_coord_y = data[1] + data[3]/2

    if center_coord_x < padding or center_coord_y < padding\
            or center_coord_x > (chip_width - padding)\
            or center_coord_y > (chip_height - padding):
        return True

    return False
