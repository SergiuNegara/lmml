#!/usr/bin/env python3
"""Analyze number sequences for letter mappings"""

with open("first_10min_transcript.txt", "r") as f:
    text = f.read()

print("="*60)
print("Analyzing Number-Letter Patterns")
print("="*60)

# Find the "One. Two. Three. Four. Five. Sigmoid. Seven..." sequence
import re

# Look for sequences with numbers and words
pattern = r'(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten)[.,\s]+(\w+)'
matches = re.findall(pattern, text, re.IGNORECASE)

print("\nNumber word sequences found:")
for num, word in matches[:20]:  # First 20
    print(f"  {num} -> {word}")

# Specific analysis of the Sigmoid sequence
print("\n" + "="*60)
print("Key sequence: 'One. Two. Three. Four. Five. Sigmoid. Seven...'")
print("="*60)
print("\nInterpretation:")
print("  Position 1: One -> ?")
print("  Position 2: Two -> ?")
print("  Position 3: Three -> ?")
print("  Position 4: Four -> ?")
print("  Position 5: Five -> ?")
print("  Position 6: SIX interrupted by -> SIGMOID (S?)")
print("  Position 7: Seven -> ?")

# Check if I-A-S-S maps to positions 1-4
print("\n" + "="*60)
print("Early hint analysis: 'I-A-S-S'")
print("="*60)
print("\nPossible interpretation:")
print("  Position 1: I")
print("  Position 2: A")
print("  Position 3: S")
print("  Position 4: S")

# But we also found "The first letter in keyword is D"
print("\n" + "="*60)
print("CONFLICT DETECTED!")
print("="*60)
print("  Hint says: I-A-S-S (positions 1-4)")
print("  But audio says: The first letter is D")
print("\n  Hypothesis: I-A-S-S was an EXAMPLE, not the actual keyword")
print("  Actual keyword starts with: D")

print("\n✓ Analysis complete!")
