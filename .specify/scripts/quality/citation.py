#!/usr/bin/env python3
"""
Quality validation script for APA citation style verification
Checks that citations follow APA 7th edition format
"""

import sys
import os
import re
from typing import List, Tuple

def find_citations_in_text(text: str) -> List[str]:
    """
    Find potential APA citations in text
    Matches patterns like (Author, Year), (Author et al., Year), etc.
    """
    # Pattern for in-text citations: (Author, Year) or (Author et al., Year)
    citation_pattern = r'\([A-Z][a-z]+(?:\s+et\s+al\.)?,\s+\d{4}\)'
    citations = re.findall(citation_pattern, text)

    # Pattern for multiple authors: (Author1 & Author2, Year)
    multi_author_pattern = r'\([A-Z][a-z]+(?:\s*&\s*[A-Z][a-z]+)*,\s+\d{4}\)'
    multi_citations = re.findall(multi_author_pattern, text)

    # Combine and return unique citations
    all_citations = list(set(citations + multi_citations))
    return all_citations

def validate_apa_format(citation: str) -> Tuple[bool, str]:
    """
    Validate if a citation follows APA format
    """
    # Check if it matches basic APA pattern
    if not re.match(r'\([A-Z][a-z]+(?:\s*(?:et\s+al\.|&\s+[A-Z][a-z]+))*\s*,\s+\d{4}\)', citation):
        return False, f"Invalid APA format: {citation}"

    # Extract author and year
    try:
        # Remove parentheses
        content = citation[1:-1]
        parts = content.split(', ')
        if len(parts) < 2:
            return False, f"Missing year in citation: {citation}"

        authors_part = parts[0].strip()
        year_part = parts[-1].strip()

        # Validate year
        if not re.match(r'^\d{4}$', year_part):
            return False, f"Invalid year format in citation: {citation}"

        # Validate author format
        if 'et al.' in authors_part:
            # Should be in format "Author et al."
            author_part = authors_part.split(' et al.')[0]
            if not re.match(r'^[A-Z][a-z]+$', author_part.strip()):
                return False, f"Invalid author format in citation: {citation}"
        elif ' & ' in authors_part:
            # Multiple authors: "Author1 & Author2"
            authors = [a.strip() for a in authors_part.split(' & ')]
            for author in authors:
                if not re.match(r'^[A-Z][a-z]+$', author):
                    return False, f"Invalid author format in citation: {citation}"
        else:
            # Single author: "Author"
            if not re.match(r'^[A-Z][a-z]+$', authors_part.strip()):
                return False, f"Invalid author format in citation: {citation}"

        return True, f"Valid APA citation: {citation}"

    except Exception as e:
        return False, f"Error parsing citation {citation}: {str(e)}"

def check_citations_in_file(file_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Check citations in a single markdown file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        citations = find_citations_in_text(content)
        valid_citations = []
        invalid_citations = []

        for citation in citations:
            is_valid, message = validate_apa_format(citation)
            if is_valid:
                valid_citations.append(citation)
            else:
                invalid_citations.append(citation)
                print(f"  {message}")

        all_valid = len(invalid_citations) == 0
        return all_valid, valid_citations, invalid_citations

    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return False, [], [f"Error reading file: {str(e)}"]

def check_references_section(content: str) -> Tuple[bool, List[str]]:
    """
    Check for proper References section formatting
    """
    # Look for a References or Works Cited section
    references_section = None

    # Find the references section (case insensitive)
    ref_patterns = [
        r'#\s*References',
        r'##\s*References',
        r'###\s*References',
        r'#\s*Works\s+Cited',
        r'##\s*Works\s+Cited',
        r'###\s*Works\s+Cited'
    ]

    for pattern in ref_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            # Get everything after the references heading
            references_section = content[match.end():]
            break

    if not references_section:
        return False, ["No References section found"]

    # Basic check: references should be formatted properly
    # Each reference should typically start with author's last name
    lines = references_section.split('\n')
    ref_lines = [line.strip() for line in lines if line.strip()]

    # Check if there are at least some reference entries
    if len(ref_lines) == 0:
        return False, ["References section is empty"]

    # Validate each reference line format (basic check)
    invalid_refs = []
    for i, line in enumerate(ref_lines):
        if line and not line.startswith('#'):  # Skip heading lines
            # APA references typically start with author's name
            if not re.match(r'^[A-Z][^,]*,\s*[A-Z]\.', line):
                invalid_refs.append(f"Line {i+1}: {line[:50]}...")

    if invalid_refs:
        return False, invalid_refs

    return True, []

def main():
    if len(sys.argv) < 2:
        print("Usage: python citation.py <file1.md> [file2.md] ...")
        print("Or: python citation.py <directory>")
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

    print("APA Citation Style Verification (7th Edition)")
    print("=" * 60)

    all_passed = True
    total_files = len(files_to_check)
    passed_files = 0

    for file_path in files_to_check:
        print(f"\nChecking: {file_path}")

        is_file_pass, valid_cites, invalid_cites = check_citations_in_file(file_path)

        # Check references section
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            refs_pass, ref_issues = check_references_section(content)
        except:
            refs_pass, ref_issues = False, ["Could not read file for references check"]

        file_overall_pass = is_file_pass and refs_pass

        if file_overall_pass:
            print(f"  PASS: {len(valid_cites)} valid citations found")
            passed_files += 1
        else:
            print(f"  FAIL: {len(invalid_cites)} invalid citations, {len(ref_issues)} reference issues")
            all_passed = False

    print("\n" + "=" * 60)
    print(f"Summary: {passed_files}/{total_files} files passed citation requirements")

    if all_passed and total_files > 0:
        print("All files meet APA citation requirements!")
        sys.exit(0)
    elif total_files > 0:
        print("Some files do not meet APA citation requirements.")
        sys.exit(1)
    else:
        print("No markdown files found to check.")
        sys.exit(0)

if __name__ == "__main__":
    main()