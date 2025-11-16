#!/usr/bin/env python3
"""Analyze the -oid words pattern to see if letters are hidden"""

# Read the transcription
with open("first_10min_transcript.txt", "r") as f:
    text = f.read()

# Find all -oid words
import re
oid_words = re.findall(r'\b(\w*oid)\b', text, re.IGNORECASE)

print("="*60)
print("Analyzing -oid words pattern")
print("="*60)
print(f"\nFound {len(oid_words)} -oid words:")

# Count occurrences
from collections import Counter
counts = Counter([w.lower() for w in oid_words])

for word, count in counts.most_common():
    print(f"  {word}: {count} times")

# Check if first letters spell something
print("\nFirst letters of -oid words in order of appearance:")
unique_order = []
seen = set()
for word in oid_words:
    w = word.lower()
    if w not in seen:
        unique_order.append(word)
        seen.add(w)

first_letters = ''.join([w[0].upper() for w in unique_order])
print(f"  {' '.join(unique_order)}")
print(f"  First letters: {first_letters}")

# Check for specific position mentions
print("\n" + "="*60)
print("Looking for position clues...")
print("="*60)

# Pattern: number word followed by -oid word
number_words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
for i, num_word in enumerate(number_words, 1):
    pattern = f'{num_word}.*?(\\w*oid)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        print(f"Position {i} ({num_word}): {matches}")

print("\n✓ Analysis complete!")
