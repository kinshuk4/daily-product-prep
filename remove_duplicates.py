#!/usr/bin/env python3
"""
Script to remove duplicate problems from README.md while keeping one copy of each.
"""

import re
from pathlib import Path

def extract_problem_content(problem_text):
    """Extract the core question from a problem to identify duplicates."""
    # Remove problem numbers
    text = re.sub(r'^Problem \d+\s*\n', '', problem_text, flags=re.MULTILINE)
    # Remove "Here's today's problem:" lines
    text = re.sub(r"Here's today's problem:\s*\n", '', text)
    # Remove solution links
    text = re.sub(r'\[Get an in-depth solution.*?\]\(.*?\)', '', text)
    # Remove horizontal rules
    text = re.sub(r'^-+$', '', text, flags=re.MULTILINE)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_readme(content):
    """Parse README and return list of problems with metadata."""
    # Split by "Problem" markers, but also handle special cases
    parts = re.split(r'(?=^Problem \d+)', content, flags=re.MULTILINE)

    problems = []
    header = parts[0] if parts else ""

    for part in parts[1:]:
        if part.strip():
            problems.append(part)

    return header, problems

def main():
    readme_path = Path("/Users/kinshuk.chandra/lyf/scm/github/k2/daily-product-prep/README.md")

    # Read the file
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse into header and problems
    header, problems = parse_readme(content)

    # Track unique problems
    seen_contents = set()
    unique_problems = []
    duplicate_count = 0

    for problem in problems:
        # Extract core content for comparison
        problem_content = extract_problem_content(problem)

        # Create a simple hash of the problem text for comparison
        # We'll look for the actual question text inside code blocks or after "asked by"
        question_match = re.search(r'This (?:problem|question) was (?:recently )?asked by.*?\n\n(.*?)(?=\n\nMake it harder|\n\n```|\Z)',
                                   problem, re.DOTALL)

        if question_match:
            question_text = question_match.group(1).strip()
        else:
            # Try to find question in code blocks
            code_block_match = re.search(r'```\s*\n.*?asked by.*?\n\n(.*?)(?=\n\nMake it harder|\n```)',
                                        problem, re.DOTALL)
            if code_block_match:
                question_text = code_block_match.group(1).strip()
            else:
                # Use the entire problem content as fallback
                question_text = problem_content

        # Normalize the question for comparison
        normalized_question = re.sub(r'\s+', ' ', question_text).strip().lower()

        if normalized_question and normalized_question not in seen_contents:
            seen_contents.add(normalized_question)
            unique_problems.append(problem)
        else:
            duplicate_count += 1
            print(f"Removing duplicate: {problem[:100]}...")

    # Reconstruct the file
    new_content = header + '\n'.join(unique_problems)

    # Write to a new file first (backup)
    backup_path = readme_path.with_suffix('.md.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Created backup at: {backup_path}")

    # Write the cleaned version
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\n✓ Removed {duplicate_count} duplicate problems")
    print(f"✓ Kept {len(unique_problems)} unique problems")
    print(f"✓ Updated README.md")

if __name__ == "__main__":
    main()
