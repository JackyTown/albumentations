import numpy as np
import pytest

from albumentations import RandomCrop, RandomResizedCrop, RandomSizedCrop, Rotate
from albumentations.core.bbox_utils import (
    calculate_bbox_area,
    convert_bbox_from_albumentations,
    convert_bbox_to_albumentations,
    convert_bboxes_to_albumentations,
    denormalize_bbox,
    denormalize_bboxes,
    normalize_bbox,
    normalize_bboxes,
)
from albumentations.core.composition import BboxParams, Compose, ReplayCompose
from albumentations.core.transforms_interface import NoOp


@pytest.mark.parametrize(
    ["bbox", "expected"],
    [((15, 25, 100, 200), (0.0375, 0.125, 0.25, 1.0)), ((15, 25, 100, 200, 99), (0.0375, 0.125, 0.25, 1.0, 99))],
)
def test_normalize_bbox(bbox, expected):
    normalized_bbox = normalize_bbox(bbox, 200, 400)
    assert normalized_bbox == expected


@pytest.mark.parametrize(
    ["bbox", "expected"],
    [((0.0375, 0.125, 0.25, 1.0), (15, 25, 100, 200)), ((0.0375, 0.125, 0.25, 1.0, 99), (15, 25, 100, 200, 99))],
)
def test_denormalize_bbox(bbox, expected):
    denormalized_bbox = denormalize_bbox(bbox, 200, 400)
    assert denormalized_bbox == expected


@pytest.mark.parametrize("bbox", [(15, 25, 100, 200), (15, 25, 100, 200, 99)])
def test_normalize_denormalize_bbox(bbox):
    normalized_bbox = normalize_bbox(bbox, 200, 400)
    denormalized_bbox = denormalize_bbox(normalized_bbox, 200, 400)
    assert denormalized_bbox == bbox


@pytest.mark.parametrize("bbox", [(0.0375, 0.125, 0.25, 1.0), (0.0375, 0.125, 0.25, 1.0, 99)])
def test_denormalize_normalize_bbox(bbox):
    denormalized_bbox = denormalize_bbox(bbox, 200, 400)
    normalized_bbox = normalize_bbox(denormalized_bbox, 200, 400)
    assert normalized_bbox == bbox


def test_normalize_bboxes():
    bboxes = [(15, 25, 100, 200), (15, 25, 100, 200, 99)]
    normalized_bboxes_1 = normalize_bboxes(bboxes, 200, 400)
    normalized_bboxes_2 = [normalize_bbox(bboxes[0], 200, 400), normalize_bbox(bboxes[1], 200, 400)]
    assert normalized_bboxes_1 == normalized_bboxes_2


def test_denormalize_bboxes():
    bboxes = [(0.0375, 0.125, 0.25, 1.0), (0.0375, 0.125, 0.25, 1.0, 99)]
    denormalized_bboxes_1 = denormalize_bboxes(bboxes, 200, 400)
    denormalized_bboxes_2 = [denormalize_bbox(bboxes[0], 200, 400), denormalize_bbox(bboxes[1], 200, 400)]
    assert denormalized_bboxes_1 == denormalized_bboxes_2


@pytest.mark.parametrize(
    ["bbox", "rows", "cols", "expected"], [((0, 0, 1, 1), 50, 100, 5000), ((0.2, 0.2, 1, 1, 99), 50, 50, 1600)]
)
def test_calculate_bbox_area(bbox, rows, cols, expected):
    area = calculate_bbox_area(bbox, rows, cols)
    assert area == expected


@pytest.mark.parametrize(
    ["bbox", "source_format", "expected"],
    [
        ((20, 30, 40, 50), "coco", (0.2, 0.3, 0.6, 0.8)),
        ((20, 30, 40, 50, 99), "coco", (0.2, 0.3, 0.6, 0.8, 99)),
        ((20, 30, 60, 80), "pascal_voc", (0.2, 0.3, 0.6, 0.8)),
        ((20, 30, 60, 80, 99), "pascal_voc", (0.2, 0.3, 0.6, 0.8, 99)),
        ((0.2, 0.3, 0.4, 0.5), "yolo", (0.00, 0.05, 0.40, 0.55)),
        ((0.2, 0.3, 0.4, 0.5, 99), "yolo", (0.00, 0.05, 0.40, 0.55, 99)),
        ((0.1, 0.1, 0.2, 0.2), "yolo", (0.0, 0.0, 0.2, 0.2)),
        ((0.99662423, 0.7520255, 0.00675154, 0.01446759), "yolo", (0.99324846, 0.744791705, 1.0, 0.759259295)),
        ((0.9375, 0.510416, 0.1234375, 0.97638), "yolo", (0.87578125, 0.022226, 0.999218749, 0.998606)),
    ],
)
def test_convert_bbox_to_albumentations(bbox, source_format, expected):
    image = np.ones((100, 100, 3))

    converted_bbox = convert_bbox_to_albumentations(
        bbox, rows=image.shape[0], cols=image.shape[1], source_format=source_format
    )
    assert np.all(np.isclose(converted_bbox, expected))


@pytest.mark.parametrize(
    ["bbox", "target_format", "expected"],
    [
        ((0.2, 0.3, 0.6, 0.8), "coco", (20, 30, 40, 50)),
        ((0.2, 0.3, 0.6, 0.8, 99), "coco", (20, 30, 40, 50, 99)),
        ((0.2, 0.3, 0.6, 0.8), "pascal_voc", (20, 30, 60, 80)),
        ((0.2, 0.3, 0.6, 0.8, 99), "pascal_voc", (20, 30, 60, 80, 99)),
        ((0.00, 0.05, 0.40, 0.55), "yolo", (0.2, 0.3, 0.4, 0.5)),
        ((0.00, 0.05, 0.40, 0.55, 99), "yolo", (0.2, 0.3, 0.4, 0.5, 99)),
    ],
)
def test_convert_bbox_from_albumentations(bbox, target_format, expected):
    image = np.ones((100, 100, 3))
    converted_bbox = convert_bbox_from_albumentations(
        bbox, rows=image.shape[0], cols=image.shape[1], target_format=target_format
    )
    assert np.all(np.isclose(converted_bbox, expected))


@pytest.mark.parametrize(
    ["bbox", "bbox_format"],
    [
        ((20, 30, 40, 50), "coco"),
        ((20, 30, 40, 50, 99), "coco"),
        ((20, 30, 41, 51, 99), "coco"),
        ((21, 31, 40, 50, 99), "coco"),
        ((21, 31, 41, 51, 99), "coco"),
        ((20, 30, 60, 80), "pascal_voc"),
        ((20, 30, 60, 80, 99), "pascal_voc"),
        ((20, 30, 61, 81, 99), "pascal_voc"),
        ((21, 31, 60, 80, 99), "pascal_voc"),
        ((21, 31, 61, 81, 99), "pascal_voc"),
        ((0.01, 0.06, 0.41, 0.56), "yolo"),
        ((0.01, 0.06, 0.41, 0.56, 99), "yolo"),
        ((0.02, 0.06, 0.42, 0.56, 99), "yolo"),
        ((0.01, 0.05, 0.41, 0.55, 99), "yolo"),
        ((0.02, 0.06, 0.41, 0.55, 99), "yolo"),
    ],
)
def test_convert_bbox_to_albumentations_and_back(bbox, bbox_format):
    image = np.ones((100, 100, 3))
    converted_bbox = convert_bbox_to_albumentations(
        bbox, rows=image.shape[0], cols=image.shape[1], source_format=bbox_format
    )
    converted_back_bbox = convert_bbox_from_albumentations(
        converted_bbox, rows=image.shape[0], cols=image.shape[1], target_format=bbox_format
    )
    assert np.all(np.isclose(converted_back_bbox, bbox))


def test_convert_bboxes_to_albumentations():
    bboxes = [(20, 30, 40, 50), (30, 40, 50, 60, 99)]
    image = np.ones((100, 100, 3))
    converted_bboxes = convert_bboxes_to_albumentations(
        bboxes, rows=image.shape[0], cols=image.shape[1], source_format="coco"
    )
    converted_bbox_1 = convert_bbox_to_albumentations(
        bboxes[0], rows=image.shape[0], cols=image.shape[1], source_format="coco"
    )
    converted_bbox_2 = convert_bbox_to_albumentations(
        bboxes[1], rows=image.shape[0], cols=image.shape[1], source_format="coco"
    )
    assert converted_bboxes == [converted_bbox_1, converted_bbox_2]


def test_convert_bboxes_from_albumentations():
    bboxes = [(0.2, 0.3, 0.6, 0.8), (0.3, 0.4, 0.7, 0.9, 99)]
    image = np.ones((100, 100, 3))
    converted_bboxes = convert_bboxes_to_albumentations(
        bboxes, rows=image.shape[0], cols=image.shape[1], source_format="coco"
    )
    converted_bbox_1 = convert_bbox_to_albumentations(
        bboxes[0], rows=image.shape[0], cols=image.shape[1], source_format="coco"
    )
    converted_bbox_2 = convert_bbox_to_albumentations(
        bboxes[1], rows=image.shape[0], cols=image.shape[1], source_format="coco"
    )
    assert converted_bboxes == [converted_bbox_1, converted_bbox_2]


@pytest.mark.parametrize(
    ["bboxes", "bbox_format", "labels"],
    [
        ([(20, 30, 40, 50)], "coco", [1]),
        ([(20, 30, 40, 50, 99), (10, 40, 30, 20, 9)], "coco", None),
        ([(20, 30, 60, 80)], "pascal_voc", [2]),
        ([(20, 30, 60, 80, 99)], "pascal_voc", None),
        ([(0.1, 0.2, 0.1, 0.2)], "yolo", [2]),
        ([(0.1, 0.2, 0.1, 0.2, 99)], "yolo", None),
    ],
)
def test_compose_with_bbox_noop(bboxes, bbox_format, labels):
    image = np.ones((100, 100, 3))
    if labels is not None:
        aug = Compose([NoOp(p=1.0)], bbox_params={"format": bbox_format, "label_fields": ["labels"]})
        transformed = aug(image=image, bboxes=bboxes, labels=labels)
    else:
        aug = Compose([NoOp(p=1.0)], bbox_params={"format": bbox_format})
        transformed = aug(image=image, bboxes=bboxes)
    assert np.array_equal(transformed["image"], image)
    assert np.all(np.isclose(transformed["bboxes"], bboxes))


@pytest.mark.parametrize(["bboxes", "bbox_format"], [[[[20, 30, 40, 50]], "coco"]])
def test_compose_with_bbox_noop_error_label_fields(bboxes, bbox_format):
    image = np.ones((100, 100, 3))
    aug = Compose([NoOp(p=1.0)], bbox_params={"format": bbox_format})
    with pytest.raises(Exception):
        aug(image=image, bboxes=bboxes)


@pytest.mark.parametrize(
    ["bboxes", "bbox_format", "labels"],
    [
        [[(20, 30, 60, 80)], "pascal_voc", {"label": [1]}],
        [[], "pascal_voc", {}],
        [[], "pascal_voc", {"label": []}],
        [[(20, 30, 60, 80)], "pascal_voc", {"id": [3]}],
        [[(20, 30, 60, 80), (30, 40, 40, 50)], "pascal_voc", {"id": [3, 1]}],
        [[(20, 30, 60, 80, 1, 11), (30, 40, 40, 50, 2, 22)], "pascal_voc", {"id": [3, 1]}],
        [[(20, 30, 60, 80, 1, 11), (30, 40, 40, 50, 2, 22)], "pascal_voc", {}],
        [[(20, 30, 60, 80, 1, 11), (30, 40, 40, 50, 2, 21)], "pascal_voc", {"id": [31, 32], "subclass": [311, 321]}],
    ],
)
def test_compose_with_bbox_noop_label_outside(bboxes, bbox_format, labels):
    image = np.ones((100, 100, 3))
    aug = Compose([NoOp(p=1.0)], bbox_params={"format": bbox_format, "label_fields": list(labels.keys())})
    transformed = aug(image=image, bboxes=bboxes, **labels)
    assert np.array_equal(transformed["image"], image)
    assert transformed["bboxes"] == bboxes
    for k, v in labels.items():
        assert transformed[k] == v


def test_random_sized_crop_size():
    image = np.ones((100, 100, 3))
    bboxes = [(0.2, 0.3, 0.6, 0.8), (0.3, 0.4, 0.7, 0.9, 99)]
    aug = RandomSizedCrop(min_max_height=(70, 90), height=50, width=50, p=1.0)
    transformed = aug(image=image, bboxes=bboxes)
    assert transformed["image"].shape == (50, 50, 3)
    assert len(bboxes) == len(transformed["bboxes"])


def test_random_resized_crop_size():
    image = np.ones((100, 100, 3))
    bboxes = [(0.2, 0.3, 0.6, 0.8), (0.3, 0.4, 0.7, 0.9, 99)]
    aug = RandomResizedCrop(height=50, width=50, p=1.0)
    transformed = aug(image=image, bboxes=bboxes)
    assert transformed["image"].shape == (50, 50, 3)
    assert len(bboxes) == len(transformed["bboxes"])


def test_random_rotate():
    image = np.ones((192, 192, 3))
    bboxes = [(78, 42, 142, 80)]
    aug = Rotate(limit=15, p=1.0)
    transformed = aug(image=image, bboxes=bboxes)
    assert len(bboxes) == len(transformed["bboxes"])


def test_crop_boxes_replay_compose():
    image = np.ones((512, 384, 3))
    bboxes = [(78, 42, 142, 80), (32, 12, 42, 72), (200, 100, 300, 200)]
    labels = [0, 1, 2]
    transform = ReplayCompose(
        [RandomCrop(256, 256, p=1.0)],
        bbox_params=BboxParams(format="pascal_voc", min_area=16, label_fields=["labels"]),
    )

    input_data = dict(image=image, bboxes=bboxes, labels=labels)
    transformed = transform(**input_data)
    transformed2 = ReplayCompose.replay(transformed["replay"], **input_data)

    np.testing.assert_almost_equal(transformed["bboxes"], transformed2["bboxes"])
