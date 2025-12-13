#!/usr/bin/env python3
"""
Quality validation script for Flesch-Kincaid readability check
Checks that content meets Grade 11-13 readability requirements
"""

import sys
import os
import re
from typing import List, Tuple

def calculate_flesch_kincaid_grade(text: str) -> float:
    """
    Calculate Flesch-Kincaid Grade Level for the given text
    Formula: 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
    """
    # Remove markdown formatting for accurate counting
    clean_text = re.sub(r'[`*_~\[\]()]', '', text)

    # Count sentences (periods, exclamation marks, question marks)
    sentences = re.split(r'[.!?]+', clean_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    total_sentences = len(sentences)

    # Count words
    words = re.findall(r'\b\w+\b', clean_text)
    total_words = len(words)

    if total_sentences == 0 or total_words == 0:
        return 0.0

    # Count syllables (simplified approach)
    total_syllables = 0
    for word in words:
        syllable_count = count_syllables(word.lower())
        total_syllables += syllable_count

    # Calculate Flesch-Kincaid Grade Level
    avg_words_per_sentence = total_words / total_sentences
    avg_syllables_per_word = total_syllables / total_words

    grade_level = 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59
    return round(grade_level, 2)

def count_syllables(word: str) -> int:
    """
    Count syllables in a word using a simplified algorithm
    """
    # Count vowel groups
    vowels = "aeiouy"
    syllable_count = 0
    prev_was_vowel = False

    for i, char in enumerate(word):
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            syllable_count += 1
        prev_was_vowel = is_vowel

    # Subtract 1 for silent 'e' at the end
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1

    # Ensure at least 1 syllable
    return max(1, syllable_count)

def check_readability_in_file(file_path: str) -> Tuple[bool, float, str]:
    """
    Check readability of a single markdown file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        grade_level = calculate_flesch_kincaid_grade(content)
        is_acceptable = 11.0 <= grade_level <= 13.0

        status = "PASS" if is_acceptable else "FAIL"
        return is_acceptable, grade_level, f"{file_path}: Grade Level {grade_level} - {status}"
    except Exception as e:
        return False, 0.0, f"{file_path}: Error reading file - {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python readability.py <file1.md> [file2.md] ...")
        print("Or: python readability.py <directory>")
        sys.exit(1)

    files_to_check = []

    # Handle directory input
    if os.path.isdir(sys.argv[1]):
        for root, dirs, files in os.walk(sys.argv[1]):
            for file in files:
                if file.endswith('.md'):
                    files_to_check.append(os.path.join(root, file))
    else:
        files_to_check = sys.argv[1:]

    print("Flesch-Kincaid Readability Check (Target: Grade 11-13)")
    print("=" * 60)

    all_passed = True
    total_files = len(files_to_check)
    passed_files = 0

    for file_path in files_to_check:
        is_pass, grade, message = check_readability_in_file(file_path)
        print(message)

        if is_pass:
            passed_files += 1
        else:
            all_passed = False

    print("=" * 60)
    print(f"Summary: {passed_files}/{total_files} files passed readability requirements")

    if all_passed and total_files > 0:
        print("All files meet readability requirements!")
        sys.exit(0)
    elif total_files > 0:
        print("Some files do not meet readability requirements.")
        sys.exit(1)
    else:
        print("No markdown files found to check.")
        sys.exit(0)

if __name__ == "__main__":
    main()