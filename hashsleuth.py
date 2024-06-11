import argparse
import csv
import os

def load_hashes(file_path):
    """Load hashes and signed status from a given CSV file."""
    hashes = {}
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            path = row['Path']
            hash_value = row['Hash']
            signed = row['Signed']
            hashes[path] = {'hash': hash_value, 'signed': signed}
    return hashes

def save_results(results, output_path):
    """Save results to the specified output file."""
    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Path', 'Result'])
        for path, result in results.items():
            writer.writerow([path, result])

def is_source_code(filename):
    """Determine if a file is source code based on its extension."""
    source_code_extensions = {'.c', '.cpp', '.py', '.java', '.js', '.html', '.css', '.rb', '.go'}
    return os.path.splitext(filename)[1].lower() in source_code_extensions

def is_expected_change(filename):
    """Determine if a file is expected to change."""
    expected_change_directories = {'/logs/', '/prefetch/'}
    for directory in expected_change_directories:
        if directory in filename:
            return True
    return False

def compare_hashes(baseline_hashes, current_hashes):
    """Compare baseline hashes with current system hashes."""
    results = {}

    # Mark all baseline files
    for file, baseline_info in baseline_hashes.items():
        if file in current_hashes:
            current_info = current_hashes[file]
            if baseline_info['hash'] == current_info['hash']:
                results[file] = "Hash match"
            else:
                if is_expected_change(file):
                    results[file] = "File not expected to match"
                elif is_source_code(file):
                    results[file] = "Alert: Source Code"
                elif current_info['signed'] != 'Signed':
                    results[file] = "Hashes do not match (unsigned)"
                else:
                    results[file] = "Hashes do not match"
        else:
            results[file] = "File not in baseline"

    # Check for new files in the current system that are not in baseline
    for file in current_hashes:
        if file not in results:
            if is_expected_change(file):
                results[file] = "File not expected to match"
            elif is_source_code(file):
                results[file] = "Alert: Source Code"
            else:
                results[file] = "File not in baseline"

    return results

def main():
    parser = argparse.ArgumentParser(description="Compare system hashes against a baseline.")
    parser.add_argument('--baseline', required=True, help="Path to the baseline hashes CSV file.")
    parser.add_argument('--current', required=True, help="Path to the current system hashes CSV file.")
    parser.add_argument('--output', required=True, help="Path to the output file to store results.")

    args = parser.parse_args()

    baseline_hashes = load_hashes(args.baseline)
    current_hashes = load_hashes(args.current)
    results = compare_hashes(baseline_hashes, current_hashes)
    save_results(results, args.output)

if __name__ == "__main__":
    main()
