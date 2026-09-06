from pathlib import Path

import cv2
import numpy as np


DATA_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = DATA_DIR.parent

OUTPUT_DIR = (
    PROJECT_DIR
    / "report"
    / "dataset"
    / "dataset_samples"
)

CLASS_NAMES = {
    0: "car",
    1: "motorbike",
    2: "bus",
    3: "truck",
}

SPLITS = ["train", "val", "test"]
IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]


def read_image(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def save_image(path, image):
    success, data = cv2.imencode(".jpg", image)

    if success:
        data.tofile(str(path))


def read_labels(label_path):
    objects = []

    lines = label_path.read_text(encoding="utf-8").splitlines()

    for line in lines:
        parts = line.strip().split()

        if len(parts) != 5:
            continue

        try:
            class_id = int(parts[0])
            x, y, w, h = map(float, parts[1:])
        except ValueError:
            continue

        if class_id in CLASS_NAMES:
            objects.append((class_id, x, y, w, h))

    return objects


def find_image(image_dir, name):
    for ext in IMAGE_EXTS:
        image_path = image_dir / f"{name}{ext}"

        if image_path.exists():
            return image_path

    return None


def find_samples(label_dir):
    samples = {}

    for label_path in sorted(label_dir.glob("*.txt")):
        objects = read_labels(label_path)

        for class_id, *_ in objects:
            if class_id not in samples:
                samples[class_id] = label_path

        if len(samples) == len(CLASS_NAMES):
            break

    return samples


def draw_boxes(image, objects):
    height, width = image.shape[:2]

    for class_id, x, y, w, h in objects:
        center_x = x * width
        center_y = y * height

        box_width = w * width
        box_height = h * height

        x1 = int(center_x - box_width / 2)
        y1 = int(center_y - box_height / 2)
        x2 = int(center_x + box_width / 2)
        y2 = int(center_y + box_height / 2)

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width - 1, x2)
        y2 = min(height - 1, y2)

        class_name = CLASS_NAMES[class_id]

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2,
        )

        cv2.putText(
            image,
            class_name,
            (x1, max(20, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

    return image


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Saving samples to: {OUTPUT_DIR}\n")

    saved = 0

    for split in SPLITS:
        image_dir = DATA_DIR / split / "images"
        label_dir = DATA_DIR / split / "labels"

        if not image_dir.exists() or not label_dir.exists():
            print(f"Missing data in split: {split}")
            continue

        samples = find_samples(label_dir)

        print(f"--- {split} ---")

        for class_id, class_name in CLASS_NAMES.items():
            label_path = samples.get(class_id)

            if label_path is None:
                print(f"{class_name}: sample not found")
                continue

            image_path = find_image(
                image_dir,
                label_path.stem,
            )

            if image_path is None:
                print(f"{class_name}: image not found")
                continue

            image = read_image(image_path)

            if image is None:
                print(f"{class_name}: cannot read image")
                continue

            objects = read_labels(label_path)

            result = draw_boxes(
                image,
                objects,
            )

            output_path = (
                OUTPUT_DIR
                / f"{split}_{class_name}_{image_path.stem}.jpg"
            )

            save_image(output_path, result)

            print(
                f"{class_name:<10}: "
                f"{output_path.name}"
            )

            saved += 1

        print()

    print(f"Saved: {saved} image(s)")


if __name__ == "__main__":
    main()