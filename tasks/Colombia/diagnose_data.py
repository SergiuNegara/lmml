#!/usr/bin/env python3
"""
Diagnostic script to identify data quality issues
"""

import os
import numpy as np
from PIL import Image
import random
from collections import defaultdict

def analyze_class_similarity(base_path):
    """Check if images within each class are consistent"""
    print("\n" + "="*60)
    print("CLASS CONSISTENCY ANALYSIS")
    print("="*60)

    for class_name in sorted(os.listdir(base_path)):
        class_path = os.path.join(base_path, class_name)
        if not os.path.isdir(class_path) or class_name.startswith('.'):
            continue

        images = [f for f in os.listdir(class_path) if not f.startswith('.')]

        # Sample features
        features = []
        for img_name in random.sample(images, min(50, len(images))):
            img_path = os.path.join(class_path, img_name)
            try:
                img = Image.open(img_path).convert('L')
                img_array = np.array(img)
                features.append([
                    np.mean(img_array),
                    np.std(img_array),
                    np.min(img_array),
                    np.max(img_array)
                ])
            except:
                pass

        features = np.array(features)
        mean_features = np.mean(features, axis=0)
        std_features = np.std(features, axis=0)

        # Calculate coefficient of variation (high = inconsistent)
        cv = (std_features / (mean_features + 1e-6)) * 100

        print(f"\nClass: {class_name} ({len(images)} images)")
        print(f"  Mean brightness: {mean_features[0]:.2f} ± {std_features[0]:.2f}")
        print(f"  Mean std dev: {mean_features[1]:.2f} ± {std_features[1]:.2f}")
        print(f"  Consistency (lower is better):")
        print(f"    Brightness CV: {cv[0]:.2f}%")
        print(f"    Texture CV: {cv[1]:.2f}%")

        if cv[0] > 30:
            print(f"  ⚠ HIGH VARIATION in brightness - may have mislabeled images")
        if cv[1] > 40:
            print(f"  ⚠ HIGH VARIATION in texture - may have quality issues")

def compare_train_val_distribution(train_path, val_path):
    """Check if train and val have similar distributions"""
    print("\n" + "="*60)
    print("TRAIN vs VAL DISTRIBUTION COMPARISON")
    print("="*60)

    classes = sorted([d for d in os.listdir(train_path) if os.path.isdir(os.path.join(train_path, d)) and not d.startswith('.')])

    for class_name in classes:
        train_class = os.path.join(train_path, class_name)
        val_class = os.path.join(val_path, class_name)

        # Sample from train
        train_images = [f for f in os.listdir(train_class) if not f.startswith('.')]
        train_features = []
        for img_name in random.sample(train_images, min(30, len(train_images))):
            img_path = os.path.join(train_class, img_name)
            try:
                img = Image.open(img_path).convert('L')
                img_array = np.array(img)
                train_features.append(np.mean(img_array))
            except:
                pass

        # Sample from val
        val_images = [f for f in os.listdir(val_class) if not f.startswith('.')]
        val_features = []
        for img_name in val_images[:30]:
            img_path = os.path.join(val_class, img_name)
            try:
                img = Image.open(img_path).convert('L')
                img_array = np.array(img)
                val_features.append(np.mean(img_array))
            except:
                pass

        train_mean = np.mean(train_features)
        val_mean = np.mean(val_features)
        diff = abs(train_mean - val_mean)

        print(f"\nClass {class_name}:")
        print(f"  Train mean brightness: {train_mean:.2f}")
        print(f"  Val mean brightness: {val_mean:.2f}")
        print(f"  Difference: {diff:.2f}")

        if diff > 20:
            print(f"  ⚠ LARGE DIFFERENCE - train/val mismatch!")

def find_extreme_outliers(base_path, output_dir='extreme_outliers'):
    """Find the most extreme outliers for manual inspection"""
    print("\n" + "="*60)
    print("EXTREME OUTLIER DETECTION")
    print("="*60)

    os.makedirs(output_dir, exist_ok=True)

    for class_name in sorted(os.listdir(base_path)):
        class_path = os.path.join(base_path, class_name)
        if not os.path.isdir(class_path) or class_name.startswith('.'):
            continue

        images = [f for f in os.listdir(class_path) if not f.startswith('.')]

        # Collect all features
        features = []
        paths = []
        for img_name in images:
            img_path = os.path.join(class_path, img_name)
            try:
                img = Image.open(img_path).convert('L')
                img_array = np.array(img)
                features.append([
                    np.mean(img_array),
                    np.std(img_array)
                ])
                paths.append((img_path, img_name))
            except:
                pass

        features = np.array(features)
        median = np.median(features, axis=0)

        # Calculate distance from median
        distances = np.sqrt(np.sum((features - median)**2, axis=1))

        # Get top 5 most extreme
        extreme_indices = np.argsort(distances)[-5:]

        print(f"\nClass {class_name}: Top 5 most extreme outliers:")
        class_outlier_dir = os.path.join(output_dir, class_name)
        os.makedirs(class_outlier_dir, exist_ok=True)

        for idx in extreme_indices:
            img_path, img_name = paths[idx]
            print(f"  - {img_name} (distance: {distances[idx]:.2f})")

            # Copy for inspection
            import shutil
            shutil.copy(img_path, class_outlier_dir)

    print(f"\nExtreme outliers saved to: {output_dir}/")
    print("Review these images - they may be mislabeled!")

def main():
    print("="*60)
    print("DATA QUALITY DIAGNOSTIC TOOL")
    print("="*60)

    # Run diagnostics
    analyze_class_similarity('dataset/train')
    compare_train_val_distribution('dataset/train', 'dataset/val')
    find_extreme_outliers('dataset/train', 'extreme_outliers')

    print("\n" + "="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60)
    print("\nRecommendations:")
    print("1. Review images in 'extreme_outliers/' directory")
    print("2. Manually delete obviously mislabeled images")
    print("3. Run improved_cleaning.py for aggressive cleaning")
    print("4. Retrain with cleaned data")

if __name__ == "__main__":
    main()
