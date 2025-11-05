#!/usr/bin/env python3
"""
Data Cleaning and Augmentation Script for Roman Numeral Recognition
This script cleans and augments the dataset to improve model accuracy
"""

import os
import shutil
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import random
from collections import defaultdict

# Set random seeds
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

def get_image_features(img_path):
    """Extract features from an image for outlier detection"""
    img = Image.open(img_path).convert('L')
    img_array = np.array(img)

    return [
        np.mean(img_array),
        np.std(img_array),
        np.min(img_array),
        np.max(img_array),
    ]

def find_outliers(base_path):
    """Find potential outliers in each class"""
    outliers_info = {}

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
            try:
                feat = get_image_features(img_path)
                features.append(feat)
                image_paths.append(img_path)
            except Exception as e:
                print(f"  Error processing {img_name}: {e}")

        features = np.array(features)

        # Find outliers using IQR method
        Q1 = np.percentile(features, 25, axis=0)
        Q3 = np.percentile(features, 75, axis=0)
        IQR = Q3 - Q1

        outlier_mask = np.any((features < (Q1 - 1.5 * IQR)) | (features > (Q3 + 1.5 * IQR)), axis=1)
        outlier_indices = np.where(outlier_mask)[0]

        print(f"  Found {len(outlier_indices)} potential outliers out of {len(images)} images")
        outliers_info[class_name] = [image_paths[i] for i in outlier_indices]

    return outliers_info

def create_cleaned_dataset(base_path, outliers_dict, output_path, removal_rate=0.3):
    """Create a cleaned version of the dataset"""
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

            # Remove some outliers
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

def augment_image(img, augmentation_type):
    """Apply various augmentation techniques"""
    if augmentation_type == 'rotate_small':
        angle = random.randint(-15, 15)
        return img.rotate(angle, fillcolor=255)

    elif augmentation_type == 'brightness':
        enhancer = ImageEnhance.Brightness(img)
        factor = random.uniform(0.7, 1.3)
        return enhancer.enhance(factor)

    elif augmentation_type == 'contrast':
        enhancer = ImageEnhance.Contrast(img)
        factor = random.uniform(0.8, 1.2)
        return enhancer.enhance(factor)

    elif augmentation_type == 'blur':
        return img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))

    elif augmentation_type == 'shift':
        shift_x = random.randint(-3, 3)
        shift_y = random.randint(-3, 3)
        return img.transform(img.size, Image.AFFINE, (1, 0, shift_x, 0, 1, shift_y), fillcolor=255)

    return img

def balance_and_augment(cleaned_path, output_path, target_per_class=280):
    """Balance classes and apply augmentation"""
    os.makedirs(output_path, exist_ok=True)

    augmentation_types = ['rotate_small', 'brightness', 'contrast', 'blur', 'shift']

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

                aug_type = random.choice(augmentation_types)
                augmented_img = augment_image(img, aug_type)

                base_name = os.path.splitext(img_name)[0]
                ext = os.path.splitext(img_name)[1]
                aug_name = f"{base_name}_aug{augmented}_{aug_type}{ext}"
                augmented_img.save(os.path.join(output_class_path, aug_name))
                augmented += 1

            print(f"  Added {augmented} augmented images")

    return output_path

def main():
    print("="*60)
    print("Roman Numeral Dataset Cleaning & Augmentation")
    print("="*60)

    # Step 1: Analyze original dataset
    print("\n[1/6] Analyzing original dataset...")
    train_counts = count_images('dataset/train')
    val_counts = count_images('dataset/val')

    print("\nOriginal Training set:")
    for class_name, count in train_counts.items():
        print(f"  {class_name}: {count}")
    print(f"  Total: {sum(train_counts.values())}")

    print("\nOriginal Validation set:")
    for class_name, count in val_counts.items():
        print(f"  {class_name}: {count}")
    print(f"  Total: {sum(val_counts.values())}")

    # Step 2: Find outliers
    print("\n[2/6] Detecting outliers...")
    outliers = find_outliers('dataset/train')

    # Step 3: Clean dataset
    print("\n[3/6] Cleaning dataset...")
    if os.path.exists('dataset_cleaned'):
        shutil.rmtree('dataset_cleaned')
    cleaned_train_path = create_cleaned_dataset('dataset/train', outliers, 'dataset_cleaned/train', removal_rate=0.3)

    # Step 4: Balance and augment
    print("\n[4/6] Balancing and augmenting training data...")
    if os.path.exists('dataset_augmented'):
        shutil.rmtree('dataset_augmented')
    augmented_train_path = balance_and_augment(cleaned_train_path, 'dataset_augmented/train', target_per_class=280)

    # Step 5: Copy validation set
    print("\n[5/6] Copying validation set...")
    shutil.copytree('dataset/val', 'dataset_augmented/val')

    # Step 6: Create data_original for training
    print("\n[6/6] Creating data_original directory for training...")
    if os.path.exists('data_original'):
        shutil.rmtree('data_original')
    shutil.copytree('dataset_augmented', 'data_original')

    # Final statistics
    print("\n" + "="*60)
    print("FINAL DATASET STATISTICS")
    print("="*60)

    final_train_counts = count_images('data_original/train')
    final_val_counts = count_images('data_original/val')

    print("\nFinal Training set:")
    for class_name, count in final_train_counts.items():
        print(f"  {class_name}: {count}")
    print(f"  Total: {sum(final_train_counts.values())}")

    print("\nFinal Validation set:")
    for class_name, count in final_val_counts.items():
        print(f"  {class_name}: {count}")
    print(f"  Total: {sum(final_val_counts.values())}")

    total = sum(final_train_counts.values()) + sum(final_val_counts.values())
    print(f"\nTotal dataset size: {total}")
    print(f"Within 10,000 limit: {'✓ Yes' if total < 10000 else '✗ No'}")

    print("\n" + "="*60)
    print("Data preparation complete!")
    print("Next step: Run 'python train.py' to train the model")
    print("="*60)

if __name__ == "__main__":
    main()
