from collections import Counter
from pathlib import Path


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


def check_label(label_path):
    counts = Counter()
    objects = 0
    errors = 0

    try:
        lines = label_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return counts, objects, 1

    for line in lines:
        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) != 5:
            errors += 1
            continue

        try:
            class_id = int(parts[0])
            x, y, w, h = map(float, parts[1:])
        except ValueError:
            errors += 1
            continue

        if class_id not in CLASS_NAMES:
            errors += 1
            continue

        if not (
            0 <= x <= 1
            and 0 <= y <= 1
            and 0 < w <= 1
            and 0 < h <= 1
        ):
            errors += 1
            continue

        counts[class_id] += 1
        objects += 1

    return counts, objects, errors


def main():
    total_images = 0
    total_labels = 0
    total_objects = 0
    total_errors = 0
    total_class_counts = Counter()

    print(f"Checking dataset: {DATA_DIR}\n")

    for split in SPLITS:
        image_dir = DATA_DIR / split / "images"
        label_dir = DATA_DIR / split / "labels"

        print(f"--- {split} ---")

        if not image_dir.exists():
            print(f"Missing image folder: {image_dir}\n")
            total_errors += 1
            continue

        if not label_dir.exists():
            print(f"Missing label folder: {label_dir}\n")
            total_errors += 1
            continue

        images = get_images(image_dir)
        labels = list(label_dir.glob("*.txt"))

        image_names = {file.stem for file in images}
        label_names = {file.stem for file in labels}

        images_without_label = image_names - label_names
        labels_without_image = label_names - image_names

        split_counts = Counter()
        split_objects = 0
        invalid_labels = 0

        for label_path in labels:
            counts, objects, errors = check_label(label_path)

            split_counts.update(counts)
            split_objects += objects
            invalid_labels += errors

        print(f"Images : {len(images)}")
        print(f"Labels : {len(labels)}")

        if images_without_label:
            print(f"Images without labels: {len(images_without_label)}")

        if labels_without_image:
            print(f"Labels without images: {len(labels_without_image)}")

        print(f"Objects: {split_objects}")

        for class_id, class_name in CLASS_NAMES.items():
            print(f"  {class_name:<10}: {split_counts[class_id]}")

        if invalid_labels:
            print(f"Invalid label lines: {invalid_labels}")

        split_errors = (
            len(images_without_label)
            + len(labels_without_image)
            + invalid_labels
        )

        if split_errors == 0:
            print("Status: OK")
        else:
            print(f"Status: {split_errors} problem(s)")

        print()

        total_images += len(images)
        total_labels += len(labels)
        total_objects += split_objects
        total_errors += split_errors

        total_class_counts.update(split_counts)

    print("=== Summary ===")
    print(f"Images : {total_images}")
    print(f"Labels : {total_labels}")
    print(f"Objects: {total_objects}")

    print("\nObjects by class:")

    for class_id, class_name in CLASS_NAMES.items():
        print(f"  {class_name:<10}: {total_class_counts[class_id]}")

    print(f"\nProblems: {total_errors}")

    if total_errors == 0:
        print("Dataset looks good.")
    else:
        print("Dataset has some problems.")


if __name__ == "__main__":
    main()