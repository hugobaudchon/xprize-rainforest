import numpy as np
import torch


def collate_fn_segmentation(batch):
    if type(batch[0][0]) is np.ndarray:
        data = np.array([item[0] for item in batch])
        data = torch.tensor(data, dtype=torch.float32)
    else:
        data = torch.tensor([item[0] for item in batch], dtype=torch.float32)

    for item in batch:
        item[1]['labels'] = [-1 if x is None else x for x in item[1]['labels']]

    labels = [{'masks': torch.tensor(np.array(item[1]['masks']), dtype=torch.int8),
               'labels': torch.tensor(np.array(item[1]['labels']), dtype=torch.int8),
               'area': torch.tensor(np.array(item[1]['area']).astype(np.int32), dtype=torch.float32),
               'iscrowd': torch.tensor(np.array(item[1]['iscrowd']), dtype=torch.bool),
               'image_id': torch.tensor(np.array(item[1]['image_id']), dtype=torch.int16)} for item in batch]

    if 'labels_polygons' in batch[0][1]:
        for i, item in enumerate(batch):
            labels[i]['labels_polygons'] = item[1]['labels_polygons']

    return data, labels


def collate_fn_detection(batch):
    if type(batch[0][0]) is np.ndarray:
        data = np.array([item[0] for item in batch])
        data = torch.tensor(data, dtype=torch.float32)
    else:
        data = torch.tensor([item[0] for item in batch], dtype=torch.float32)

    # For detection, we set all labels to 1, we don't care about the object class in our case
    for item in batch:
        item[1]['labels'] = [1 for _ in item[1]['labels']]

    labels = [{'boxes': torch.tensor(np.array(item[1]['boxes']), dtype=torch.float32),
               'labels': torch.tensor(np.array(item[1]['labels']), dtype=torch.long)} for item in batch]

    return data, labels


def collate_fn_images(batch):
    if type(batch[0]) is np.ndarray:
        data = np.array([item for item in batch])
        data = torch.tensor(data, dtype=torch.float32)
    else:
        data = torch.tensor([item for item in batch], dtype=torch.float32)

    return data
