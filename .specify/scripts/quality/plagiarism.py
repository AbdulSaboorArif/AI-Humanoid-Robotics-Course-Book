#!/usr/bin/env python3
"""
Quality validation script for plagiarism detection
Placeholder implementation for checking content originality
"""

import sys
import os
import re
from typing import List, Tuple
from difflib import SequenceMatcher

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity ratio between two texts using SequenceMatcher
    """
    return SequenceMatcher(None, text1, text2).ratio()

def check_for_plagiarism_in_file(file_path: str, reference_texts: List[str],
                                threshold: float = 0.8) -> Tuple[bool, List[Tuple[str, float]]]:
    """
    Check a file for potential plagiarism against reference texts
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract paragraphs to check individually
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        potential_issues = []

        for i, paragraph in enumerate(paragraphs):
            # Skip short paragraphs (likely headers, lists, etc.)
            if len(paragraph) < 50:
                continue

            for ref_text in reference_texts:
                similarity = calculate_text_similarity(paragraph, ref_text)
                if similarity > threshold:
                    potential_issues.append((f"Paragraph {i+1}", similarity, paragraph[:100] + "..."))

        is_clean = len(potential_issues) == 0
        return is_clean, potential_issues

    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return False, [(f"Error reading file", 0.0, str(e))]

def check_file_against_known_sources(file_path: str) -> Tuple[bool, List[str]]:
    """
    Check file against known sources or common phrases that might indicate plagiarism
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()

        # Common phrases that might indicate copied content
        suspicious_patterns = [
            r'wikipedia.*',
            r'from the.*documentation',
            r'as stated in.*',
            r'according to.*',
            r'wikipedia defines.*',
            r'by definition.*',
        ]

        issues = []
        for pattern in suspicious_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues.extend(matches)

        return len(issues) == 0, issues

    except Exception as e:
        print(f"Error checking file {file_path}: {str(e)}")
        return False, [f"Error: {str(e)}"]

def main():
    if len(sys.argv) < 2:
        print("Usage: python plagiarism.py <file1.md> [file2.md] ...")
        print("Or: python plagiarism.py <directory>")
        print("Note: This is a placeholder implementation. For real plagiarism detection,")
        print("      integrate with commercial services like Turnitin, Grammarly, or Copyscape.")
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

    print("Plagiarism Detection Check (Placeholder Implementation)")
    print("=" * 70)
    print("Note: This is a basic similarity checker. For comprehensive plagiarism")
    print("      detection, integrate with commercial services or academic databases.")
    print("=" * 70)

    all_passed = True
    total_files = len(files_to_check)
    passed_files = 0

    for file_path in files_to_check:
        print(f"\nChecking: {file_path}")

        # For this placeholder, we'll just check against common patterns
        # In a real implementation, you would compare against a database of sources
        is_clean, pattern_issues = check_file_against_known_sources(file_path)

        if is_clean and not pattern_issues:
            print(f"  PASS: No obvious plagiarism indicators found")
            passed_files += 1
        else:
            print(f"  POTENTIAL ISSUES: Found {len(pattern_issues)} suspicious patterns")
            for issue in pattern_issues[:5]:  # Show first 5 issues
                print(f"    - {issue}")
            if len(pattern_issues) > 5:
                print(f"    ... and {len(pattern_issues) - 5} more")
            all_passed = False

    print("\n" + "=" * 70)
    print(f"Summary: {passed_files}/{total_files} files passed basic checks")

    if all_passed and total_files > 0:
        print("All files passed basic plagiarism checks!")
        print("Note: This is a basic check. For comprehensive detection,")
        print("      use specialized plagiarism detection services.")
        sys.exit(0)
    elif total_files > 0:
        print("Some files show potential plagiarism indicators.")
        print("Review flagged content carefully.")
        sys.exit(1)
    else:
        print("No markdown files found to check.")
        sys.exit(0)

if __name__ == "__main__":
    main()