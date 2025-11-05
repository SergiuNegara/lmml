#!/usr/bin/env python3
"""
Manual Image Inspection Tool
Displays images from each class for visual inspection to find mislabeled samples
"""

import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import random

def inspect_class(class_path, class_name, n_samples=50, grid_size=(5, 10)):
    """Display random samples from a class for manual inspection"""
    images = [f for f in os.listdir(class_path) if not f.startswith('.')]

    if len(images) == 0:
        print(f"No images in {class_name}")
        return

    # Sample images
    samples = random.sample(images, min(n_samples, len(images)))

    fig, axes = plt.subplots(grid_size[0], grid_size[1], figsize=(20, 10))
    fig.suptitle(f'Class: {class_name.upper()} ({len(images)} total images)',
                 fontsize=16, fontweight='bold')

    axes = axes.flatten()

    for idx, img_name in enumerate(samples):
        if idx >= len(axes):
            break

        img_path = os.path.join(class_path, img_name)
        try:
            img = Image.open(img_path)
            axes[idx].imshow(img, cmap='gray')
            axes[idx].set_title(img_name[:15], fontsize=6)
            axes[idx].axis('off')
        except Exception as e:
            axes[idx].text(0.5, 0.5, 'Error', ha='center', va='center')
            axes[idx].axis('off')

    # Hide unused subplots
    for idx in range(len(samples), len(axes)):
        axes[idx].axis('off')

    plt.tight_layout()
    plt.savefig(f'inspection_{class_name}.png', dpi=150, bbox_inches='tight')
    print(f"Saved: inspection_{class_name}.png")
    plt.close()

def inspect_all_classes(base_path='dataset/train'):
    """Inspect all classes"""
    print("="*60)
    print("VISUAL INSPECTION OF ALL CLASSES")
    print("="*60)
    print("\nGenerating inspection images...")
    print("Look for:")
    print("  1. Wrong numerals in the folder")
    print("  2. Completely blank or corrupted images")
    print("  3. Images that look very different from others")
    print("  4. Duplicates")
    print()

    classes = sorted([d for d in os.listdir(base_path)
                     if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('.')])

    for class_name in classes:
        class_path = os.path.join(base_path, class_name)
        print(f"\nInspecting class: {class_name}")
        inspect_class(class_path, class_name, n_samples=50, grid_size=(5, 10))

    print("\n" + "="*60)
    print("INSPECTION COMPLETE")
    print("="*60)
    print("\nReview the generated PNG files:")
    for class_name in classes:
        print(f"  - inspection_{class_name}.png")
    print("\nLook for obvious mislabeled images and note their filenames.")

def compare_classes_side_by_side(base_path='dataset/train', n_per_class=20):
    """Show all classes side by side for easy comparison"""
    classes = sorted([d for d in os.listdir(base_path)
                     if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('.')])

    fig, axes = plt.subplots(len(classes), n_per_class, figsize=(24, 2*len(classes)))

    for i, class_name in enumerate(classes):
        class_path = os.path.join(base_path, class_name)
        images = [f for f in os.listdir(class_path) if not f.startswith('.')]
        samples = random.sample(images, min(n_per_class, len(images)))

        for j, img_name in enumerate(samples):
            img_path = os.path.join(class_path, img_name)
            try:
                img = Image.open(img_path)
                axes[i, j].imshow(img, cmap='gray')
                axes[i, j].axis('off')
                if j == 0:
                    axes[i, j].text(-10, 16, class_name.upper(),
                                  fontsize=14, fontweight='bold',
                                  ha='right', va='center')
            except:
                axes[i, j].axis('off')

        # Hide unused
        for j in range(len(samples), n_per_class):
            axes[i, j].axis('off')

    plt.suptitle('All Classes Side-by-Side Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('all_classes_comparison.png', dpi=150, bbox_inches='tight')
    print("\nSaved: all_classes_comparison.png")
    print("Use this to spot which images don't match their class!")
    plt.close()

if __name__ == "__main__":
    random.seed(42)

    # Generate inspection images
    inspect_all_classes('dataset/train')

    # Generate side-by-side comparison
    print("\n" + "="*60)
    print("Generating side-by-side comparison...")
    compare_classes_side_by_side('dataset/train', n_per_class=20)

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Review all inspection_*.png files")
    print("2. Note down filenames of obviously wrong images")
    print("3. Run: python remove_mislabeled.py <filenames>")
    print("   OR manually delete them from dataset/train/")
