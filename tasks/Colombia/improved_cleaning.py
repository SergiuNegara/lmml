#!/usr/bin/env python3
"""
Improved Data Cleaning with More Aggressive Outlier Removal
"""

import os
import shutil
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import random
from collections import defaultdict

random.seed(42)
np.random.seed(42)

def count_images(base_path):
    """Count images in each class"""
    counts = {}
    for class_name in sorted(os.listdir(base_path)):
        class_path = os.path.join(base_path, class_name)
        if os.path.isdir(class_path) and not class_name.startswith('.'):
            images = [f for f in os.listdir(class_path) if not f.startswith('.')]
            counts[class_name] = len(images)
    return counts

def get_advanced_features(img_path):
    """Extract more comprehensive features for better outlier detection"""
    try:
        img = Image.open(img_path).convert('L')
        img_array = np.array(img)

        # Basic statistics
        mean_val = np.mean(img_array)
        std_val = np.std(img_array)
        min_val = np.min(img_array)
        max_val = np.max(img_array)

        # Additional features
        median_val = np.median(img_array)
        q25 = np.percentile(img_array, 25)
        q75 = np.percentile(img_array, 75)

        # Edge detection (count of high gradients)
        grad_x = np.abs(np.diff(img_array, axis=1))
        grad_y = np.abs(np.diff(img_array, axis=0))
        edge_intensity = np.mean(grad_x) + np.mean(grad_y)

        # Contrast
        contrast = max_val - min_val

        return [mean_val, std_val, median_val, q25, q75, edge_intensity, contrast]
    except:
        return None

def find_outliers_advanced(base_path):
    """More aggressive outlier detection"""
    outliers_info = {}
    stats_info = {}

    for class_name in sorted(os.listdir(base_path)):
        class_path = os.path.join(base_path, class_name)
        if not os.path.isdir(class_path) or class_name.startswith('.'):
            continue

        print(f"Analyzing class: {class_name}")
        images = [f for f in os.listdir(class_path) if not f.startswith('.')]

        features = []
        image_paths = []

        for img_name in images:
            img_path = os.path.join(class_path, img_name)
            feat = get_advanced_features(img_path)
            if feat is not None:
                features.append(feat)
                image_paths.append(img_path)

        features = np.array(features)

        # More aggressive outlier detection: use 1.0 * IQR instead of 1.5 * IQR
        Q1 = np.percentile(features, 25, axis=0)
        Q3 = np.percentile(features, 75, axis=0)
        IQR = Q3 - Q1

        # Tighter bounds for outlier detection
        outlier_mask = np.any(
            (features < (Q1 - 1.0 * IQR)) | (features > (Q3 + 1.0 * IQR)),
            axis=1
        )
        outlier_indices = np.where(outlier_mask)[0]

        print(f"  Found {len(outlier_indices)} potential outliers out of {len(images)} images")
        outliers_info[class_name] = [image_paths[i] for i in outlier_indices]

        # Store statistics for analysis
        stats_info[class_name] = {
            'mean': np.mean(features, axis=0),
            'std': np.std(features, axis=0)
        }

    return outliers_info, stats_info

def create_cleaned_dataset(base_path, outliers_dict, output_path, removal_rate=0.6):
    """More aggressive cleaning - remove 60% of detected outliers"""
    os.makedirs(output_path, exist_ok=True)

    removed_count = 0
    kept_count = 0

    for class_name in sorted(os.listdir(base_path)):
        class_path = os.path.join(base_path, class_name)
        if not os.path.isdir(class_path) or class_name.startswith('.'):
            continue

        output_class_path = os.path.join(output_path, class_name)
        os.makedirs(output_class_path, exist_ok=True)

        outlier_set = set(outliers_dict.get(class_name, []))

        for img_name in os.listdir(class_path):
            if img_name.startswith('.'):
                continue
            img_path = os.path.join(class_path, img_name)

            # Remove more outliers
            if img_path in outlier_set and len(outlier_set) > 0:
                if random.random() < removal_rate:
                    removed_count += 1
                    continue

            shutil.copy(img_path, output_class_path)
            kept_count += 1

    print(f"\nCleaning complete:")
    print(f"  Kept: {kept_count} images")
    print(f"  Removed: {removed_count} images")

    return output_path

def augment_image_improved(img, aug_type):
    """More diverse and stronger augmentation"""
    if aug_type == 'rotate_small':
        angle = random.randint(-20, 20)  # Increased from -15 to -20
        return img.rotate(angle, fillcolor=255, expand=False)

    elif aug_type == 'rotate_medium':
        angle = random.choice([-10, -5, 5, 10])
        return img.rotate(angle, fillcolor=255)

    elif aug_type == 'brightness':
        enhancer = ImageEnhance.Brightness(img)
        factor = random.uniform(0.6, 1.4)  # Wider range
        return enhancer.enhance(factor)

    elif aug_type == 'contrast':
        enhancer = ImageEnhance.Contrast(img)
        factor = random.uniform(0.7, 1.4)  # Wider range
        return enhancer.enhance(factor)

    elif aug_type == 'sharpness':
        enhancer = ImageEnhance.Sharpness(img)
        factor = random.uniform(0.5, 2.0)
        return enhancer.enhance(factor)

    elif aug_type == 'blur':
        radius = random.uniform(0.3, 2.0)
        return img.filter(ImageFilter.GaussianBlur(radius=radius))

    elif aug_type == 'shift':
        shift_x = random.randint(-4, 4)  # Increased from -3
        shift_y = random.randint(-4, 4)
        return img.transform(img.size, Image.AFFINE, (1, 0, shift_x, 0, 1, shift_y), fillcolor=255)

    elif aug_type == 'zoom':
        # Slight zoom in/out
        scale = random.uniform(0.9, 1.1)
        w, h = img.size
        new_w, new_h = int(w * scale), int(h * scale)
        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # Crop or pad to original size
        if scale > 1:
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            return resized.crop((left, top, left + w, top + h))
        else:
            new_img = Image.new('L' if img.mode == 'L' else 'RGB', (w, h), 255)
            left = (w - new_w) // 2
            top = (h - new_h) // 2
            new_img.paste(resized, (left, top))
            return new_img

    elif aug_type == 'invert':
        # Occasionally useful for handwritten digits
        if random.random() < 0.3:  # Only 30% chance
            return ImageOps.invert(img.convert('RGB')).convert(img.mode)
        return img

    elif aug_type == 'combined':
        # Apply multiple augmentations
        img = augment_image_improved(img, 'rotate_small')
        img = augment_image_improved(img, random.choice(['brightness', 'contrast']))
        return img

    return img

def balance_and_augment_improved(cleaned_path, output_path, target_per_class=300):
    """Enhanced augmentation strategy"""
    os.makedirs(output_path, exist_ok=True)

    augmentation_types = [
        'rotate_small', 'rotate_medium', 'brightness', 'contrast',
        'sharpness', 'blur', 'shift', 'zoom', 'combined'
    ]

    for class_name in sorted(os.listdir(cleaned_path)):
        class_path = os.path.join(cleaned_path, class_name)
        if not os.path.isdir(class_path) or class_name.startswith('.'):
            continue

        output_class_path = os.path.join(output_path, class_name)
        os.makedirs(output_class_path, exist_ok=True)

        images = [f for f in os.listdir(class_path) if not f.startswith('.')]
        current_count = len(images)

        print(f"\nClass {class_name}: {current_count} images -> targeting {target_per_class}")

        # Copy original images
        for img_name in images:
            shutil.copy(os.path.join(class_path, img_name), output_class_path)

        # Augment to reach target
        needed = target_per_class - current_count
        if needed > 0:
            augmented = 0
            while augmented < needed:
                img_name = random.choice(images)
                img_path = os.path.join(class_path, img_name)
                img = Image.open(img_path)

                # Use more diverse augmentation
                aug_type = random.choice(augmentation_types)
                augmented_img = augment_image_improved(img, aug_type)

                base_name = os.path.splitext(img_name)[0]
                ext = os.path.splitext(img_name)[1]
                aug_name = f"{base_name}_aug{augmented}_{aug_type}{ext}"
                augmented_img.save(os.path.join(output_class_path, aug_name))
                augmented += 1

            print(f"  Added {augmented} augmented images")

    return output_path

def main():
    print("="*60)
    print("IMPROVED Data Cleaning & Augmentation")
    print("More aggressive outlier removal + better augmentation")
    print("="*60)

    # Step 1: Find outliers with advanced detection
    print("\n[1/5] Advanced outlier detection...")
    outliers, stats = find_outliers_advanced('dataset/train')

    # Step 2: Aggressive cleaning
    print("\n[2/5] Aggressive cleaning (removing 60% of outliers)...")
    if os.path.exists('dataset_cleaned_v2'):
        shutil.rmtree('dataset_cleaned_v2')
    cleaned_train = create_cleaned_dataset(
        'dataset/train',
        outliers,
        'dataset_cleaned_v2/train',
        removal_rate=0.6  # Remove 60% of outliers
    )

    # Step 3: Better augmentation
    print("\n[3/5] Enhanced augmentation...")
    if os.path.exists('dataset_augmented_v2'):
        shutil.rmtree('dataset_augmented_v2')
    augmented_train = balance_and_augment_improved(
        cleaned_train,
        'dataset_augmented_v2/train',
        target_per_class=300  # More images per class
    )

    # Step 4: Copy validation
    print("\n[4/5] Copying validation set...")
    shutil.copytree('dataset/val', 'dataset_augmented_v2/val')

    # Step 5: Create data_original
    print("\n[5/5] Creating data_original...")
    if os.path.exists('data_original'):
        shutil.rmtree('data_original')
    shutil.copytree('dataset_augmented_v2', 'data_original')

    # Final stats
    print("\n" + "="*60)
    print("FINAL STATISTICS")
    print("="*60)

    final_train = count_images('data_original/train')
    final_val = count_images('data_original/val')

    print("\nFinal Training set:")
    for class_name, count in final_train.items():
        print(f"  {class_name}: {count}")
    print(f"  Total: {sum(final_train.values())}")

    print("\nFinal Validation set:")
    for class_name, count in final_val.items():
        print(f"  {class_name}: {count}")
    print(f"  Total: {sum(final_val.values())}")

    total = sum(final_train.values()) + sum(final_val.values())
    print(f"\nTotal: {total} images")
    print(f"Within limit: {'✓' if total < 10000 else '✗'}")

    print("\n" + "="*60)
    print("Ready to train! Use the updated dataset in Google Colab")
    print("="*60)

if __name__ == "__main__":
    main()
