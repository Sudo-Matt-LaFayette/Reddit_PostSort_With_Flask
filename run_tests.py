#!/usr/bin/env python3
"""
Test runner script for local development
"""
import sys
import subprocess
import argparse


def run_tests(args):
    """Run tests with specified options"""
    cmd = ["pytest"]
    
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    if args.visible:
        # Run with visible browser (pass --visible flag to pytest)
        cmd.append("--visible")
    
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    if args.html:
        cmd.extend(["--html=test-report.html", "--self-contained-html"])
    
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    if args.test_file:
        cmd.append(f"tests/{args.test_file}")
    else:
        cmd.append("tests/")
    
    if args.failfast:
        cmd.append("-x")
    
    # Run the tests
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run UI tests for Reddit Post Sorter")
    
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("--visible", action="store_true",
                       help="Run tests with visible browser (for debugging)")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report")
    parser.add_argument("--html", action="store_true",
                       help="Generate HTML test report")
    parser.add_argument("-m", "--markers", type=str,
                       help="Run tests matching given mark expression (e.g., 'ui' or 'smoke')")
    parser.add_argument("-f", "--test-file", type=str,
                       help="Run specific test file (e.g., 'test_ui_basic.py')")
    parser.add_argument("-x", "--failfast", action="store_true",
                       help="Stop on first failure")
    
    args = parser.parse_args()
    
    sys.exit(run_tests(args))


if __name__ == "__main__":
    main()

