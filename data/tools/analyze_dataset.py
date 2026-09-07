from collections import Counter
from pathlib import Path

import cv2
import numpy as np


DATA_DIR = Path(__file__).resolve().parents[1]

CLASS_NAMES = {
    0: "car",
    1: "motorbike",
    2: "bus",
    3: "truck",
}

SPLITS = ["train", "val", "test"]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def get_images(folder):
    return [
        file
        for file in folder.iterdir()
        if file.is_file() and file.suffix.lower() in IMAGE_EXTS
    ]


def read_image(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def count_objects(label_dir):
    counts = Counter()

    for label_path in label_dir.glob("*.txt"):
        lines = label_path.read_text(encoding="utf-8").splitlines()

        for line in lines:
            parts = line.strip().split()

            if len(parts) != 5:
                continue

            try:
                class_id = int(parts[0])
            except ValueError:
                continue

            if class_id in CLASS_NAMES:
                counts[class_id] += 1

    return counts


def main():
    split_counts = {}
    class_counts = Counter()
    resolution_counts = Counter()

    for split in SPLITS:
        image_dir = DATA_DIR / split / "images"
        label_dir = DATA_DIR / split / "labels"

        if not image_dir.exists() or not label_dir.exists():
            print(f"Missing data in split: {split}")
            return

        images = get_images(image_dir)

        split_counts[split] = len(images)
        class_counts.update(count_objects(label_dir))

        for image_path in images:
            image = read_image(image_path)

            if image is None:
                continue

            height, width = image.shape[:2]
            resolution_counts[(width, height)] += 1

    total_images = sum(split_counts.values())
    total_objects = sum(class_counts.values())

    print("=== Dataset Analysis ===\n")

    print(f"Total images : {total_images}")
    print(f"Total objects: {total_objects}")

    print("\nDataset split:")

    for split in SPLITS:
        count = split_counts[split]
        percent = count / total_images * 100

        print(f"  {split:<5}: {count:>6} ({percent:.2f}%)")

    print("\nClass distribution:")

    for class_id, class_name in CLASS_NAMES.items():
        count = class_counts[class_id]
        percent = count / total_objects * 100

        print(
            f"  {class_name:<10}: "
            f"{count:>6} ({percent:.2f}%)"
        )

    print("\nImage resolutions:")

    for (width, height), count in resolution_counts.most_common():
        percent = count / total_images * 100

        print(
            f"  {width}x{height}: "
            f"{count} ({percent:.2f}%)"
        )

    values = [
        class_counts[class_id]
        for class_id in CLASS_NAMES
        if class_counts[class_id] > 0
    ]

    if values:
        largest = max(values)
        smallest = min(values)

        print(
            f"\nLargest/smallest class ratio: "
            f"{largest / smallest:.2f}x"
        )


if __name__ == "__main__":
    main()