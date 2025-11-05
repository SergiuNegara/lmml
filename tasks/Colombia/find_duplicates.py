#!/usr/bin/env python3
"""
Find duplicate images across different classes
Duplicates in wrong classes are mislabeled!
"""

import os
import numpy as np
from PIL import Image
import hashlib
from collections import defaultdict

def get_image_hash(img_path):
    """Get hash of image for duplicate detection"""
    try:
        img = Image.open(img_path).convert('L')
        img = img.resize((32, 32))  # Normalize size
        img_array = np.array(img)
        return hashlib.md5(img_array.tobytes()).hexdigest()
    except:
        return None

def find_duplicate_images(base_path='dataset/train'):
    """Find images that appear in multiple classes (likely mislabeled)"""
    print("="*60)
    print("SEARCHING FOR DUPLICATE IMAGES ACROSS CLASSES")
    print("="*60)

    hash_to_images = defaultdict(list)

    # Collect all images and their hashes
    classes = sorted([d for d in os.listdir(base_path)
                     if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('.')])

    for class_name in classes:
        class_path = os.path.join(base_path, class_name)
        images = [f for f in os.listdir(class_path) if not f.startswith('.')]

        print(f"Processing class {class_name}... ({len(images)} images)")

        for img_name in images:
            img_path = os.path.join(class_path, img_name)
            img_hash = get_image_hash(img_path)

            if img_hash:
                hash_to_images[img_hash].append((class_name, img_name, img_path))

    # Find duplicates
    duplicates = {h: imgs for h, imgs in hash_to_images.items() if len(imgs) > 1}

    print("\n" + "="*60)
    print(f"FOUND {len(duplicates)} DUPLICATE IMAGE GROUPS")
    print("="*60)

    cross_class_duplicates = []

    for img_hash, images in duplicates.items():
        classes_involved = set(img[0] for img in images)

        if len(classes_involved) > 1:
            # Same image in different classes - DEFINITELY MISLABELED!
            print(f"\n⚠️  CROSS-CLASS DUPLICATE (MISLABELED!):")
            for class_name, img_name, img_path in images:
                print(f"    Class {class_name}: {img_name}")
            cross_class_duplicates.extend(images)
        else:
            # Same image duplicated within same class
            print(f"\n  Duplicate within class {images[0][0]}:")
            for class_name, img_name, img_path in images:
                print(f"    {img_name}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total duplicate groups: {len(duplicates)}")
    print(f"Cross-class duplicates: {len(cross_class_duplicates)} images")
    print("  → These are DEFINITELY mislabeled!")

    if cross_class_duplicates:
        print("\n⚠️  RECOMMENDED ACTION:")
        print("Delete these cross-class duplicates - they're confusing the model!")

        # Save to file
        with open('mislabeled_duplicates.txt', 'w') as f:
            f.write("MISLABELED IMAGES (cross-class duplicates):\\n")
            f.write("="*60 + "\\n")
            for class_name, img_name, img_path in cross_class_duplicates:
                f.write(f"{img_path}\\n")

        print("\nSaved list to: mislabeled_duplicates.txt")

    return cross_class_duplicates

if __name__ == "__main__":
    duplicates = find_duplicate_images('dataset/train')

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Review mislabeled_duplicates.txt")
    print("2. Decide which copies to keep/remove")
    print("3. Delete the wrong ones manually")
    print("   OR use: python clean_duplicates.py")
