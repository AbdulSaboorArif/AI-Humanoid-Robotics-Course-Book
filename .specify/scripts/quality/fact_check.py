#!/usr/bin/env python3
"""
Quality validation script for fact-checking technical claims
Placeholder implementation for verifying technical accuracy
"""

import sys
import os
import re
from typing import List, Tuple

def identify_technical_claims(text: str) -> List[str]:
    """
    Identify potential technical claims in the text that should be fact-checked
    """
    # Patterns that often contain technical claims
    claim_patterns = [
        r'(?i)(?:is|are|was|were|has|have|had|can|could|will|would|should|must)\s+used\s+for',
        r'(?i)(?:allows|enables|provides|offers|gives|grants)\s+\w+',
        r'(?i)(?:requires|needs|demands|calls for)\s+\w+',
        r'(?i)(?:improves|enhances|increases|decreases|reduces)\s+\w+',
        r'(?i)(?:achieves|reaches|attains|obtains)\s+\w+',
        r'(?i)(?:runs|operates|functions|works)\s+at',
        r'(?i)(?:supports|handles|manages|processes)\s+\w+',
    ]

    claims = []
    for pattern in claim_patterns:
        matches = re.findall(pattern, text)
        claims.extend(matches)

    # Also look for numerical claims
    numerical_patterns = [
        r'\d+\.\d+% accuracy',
        r'\d+ms response time',
        r'\d+x performance improvement',
        r'\d+GB memory usage',
        r'over \d+% efficiency',
    ]

    for pattern in numerical_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        claims.extend(matches)

    return list(set(claims))  # Return unique claims

def check_common_factual_errors(text: str) -> List[str]:
    """
    Check for common factual errors in technical writing
    """
    errors = []

    # Check for outdated information
    if re.search(r'(?i)(?:ROS 1|ROS Kinetic|ROS Melodic)', text):
        errors.append("Using outdated ROS versions (ROS 1, Kinetic, Melodic) - recommend ROS 2")

    # Check for deprecated or incorrect technical terms
    if re.search(r'(?i)catkin', text) and not re.search(r'(?i)ament|colcon', text):
        errors.append("Mentioning catkin without ament/colcon - may be outdated for ROS 2 context")

    # Check for common misconceptions
    if re.search(r'(?i)real-time.*guarantee', text):
        errors.append("Claiming real-time guarantees without specifying RT kernel or constraints")

    # Check for accuracy in basic facts
    if re.search(r'(?i)python.*version.*2\.\d+', text):
        errors.append("Referencing Python 2 (end-of-life) instead of Python 3")

    # Check for version specifications
    if re.search(r'(?i)Unity.*version.*[3-4]\.', text):
        errors.append("Unity 3.x or 4.x are very old versions - consider more recent versions")

    return errors

def validate_citations_exist(text: str) -> List[str]:
    """
    Check that citation placeholders exist in the text
    """
    issues = []

    # Look for citation patterns that might be missing
    citation_placeholders = re.findall(r'\[\w\s,]+\]', text)
    for placeholder in citation_placeholders:
        if placeholder.strip('[]').lower() in ['tbd', 'todo', 'to be determined', 'to be added']:
            issues.append(f"Unresolved citation placeholder: {placeholder}")

    return issues

def check_consistency(text: str) -> List[str]:
    """
    Check for consistency in terminology and concepts
    """
    issues = []

    # Check for inconsistent terminology
    ros_patterns = re.findall(r'(?i)(?:ROS|Robot Operating System)', text)
    if len(set(ros_patterns)) > 1:
        # This just identifies if different forms are used, which might be OK
        pass

    # Check for version consistency
    if re.search(r'(?i)version.*\d+\.\d+', text) and re.search(r'(?i)latest', text):
        # Check if specific versions are mixed with "latest"
        pass

    # Check for terminology consistency
    terms = ['AI', 'Artificial Intelligence', 'Machine Learning', 'ML']
    found_terms = [term for term in terms if re.search(rf'\b{term}\b', text, re.IGNORECASE)]
    if len(found_terms) > 1:
        # Multiple terms used - may be OK but worth noting for consistency
        pass

    return issues

def fact_check_file(file_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Perform fact-checking on a single file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        technical_claims = identify_technical_claims(content)
        factual_errors = check_common_factual_errors(content)
        citation_issues = validate_citations_exist(content)
        consistency_issues = check_consistency(content)

        all_issues = factual_errors + citation_issues + consistency_issues

        is_valid = len(all_issues) == 0
        return is_valid, technical_claims, all_issues

    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return False, [], [f"Error reading file: {str(e)}"]

def main():
    if len(sys.argv) < 2:
        print("Usage: python fact_check.py <file1.md> [file2.md] ...")
        print("Or: python fact_check.py <directory>")
        print("Note: This is a basic fact-checker for technical content.")
        print("      For comprehensive fact-checking, verify against official documentation.")
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

    print("Technical Fact-Checking (Placeholder Implementation)")
    print("=" * 70)
    print("Note: This checks for common technical errors and inconsistencies.")
    print("      For comprehensive fact-checking, verify against official sources.")
    print("=" * 70)

    all_passed = True
    total_files = len(files_to_check)
    passed_files = 0

    for file_path in files_to_check:
        print(f"\nChecking: {file_path}")

        is_valid, claims, issues = fact_check_file(file_path)

        if is_valid:
            print(f"  PASS: No obvious factual issues found")
            print(f"    Identified technical claims: {len(claims)}")
            passed_files += 1
        else:
            print(f"  ISSUES FOUND: {len(issues)} potential factual problems")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"    - {issue}")
            if len(issues) > 10:
                print(f"    ... and {len(issues) - 10} more")
            all_passed = False

    print("\n" + "=" * 70)
    print(f"Summary: {passed_files}/{total_files} files passed basic fact-checking")

    if all_passed and total_files > 0:
        print("All files passed basic fact-checking!")
        sys.exit(0)
    elif total_files > 0:
        print("Some files contain potential factual issues.")
        print("Review flagged content against official documentation.")
        sys.exit(1)
    else:
        print("No markdown files found to check.")
        sys.exit(0)

if __name__ == "__main__":
    main()