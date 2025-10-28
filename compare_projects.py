#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Folder Comparison Tool
Recursively compares two folders, reports file differences and content differences.
"""

import os
import sys
import argparse
import difflib
import fnmatch
from pathlib import Path
from typing import Set, Dict, List, Tuple, Optional
from collections import defaultdict
from tqdm import tqdm
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)


class ProjectComparator:
    """Main class for comparing two project folders"""
    
    def __init__(self, path1: str, path2: str, ignore_ext: List[str] = None, 
                 only_ext: List[str] = None, ignore_dirs: List[str] = None,
                 ignore_files: List[str] = None):
        self.path1 = Path(path1).resolve()
        self.path2 = Path(path2).resolve()
        self.ignore_ext = set(ignore_ext or [])
        self.only_ext = set(only_ext or [])
        self.ignore_dirs = set(ignore_dirs or [])
        self.ignore_files = set(ignore_files or [])
        
        # Result records
        self.only_in_path1: Set[str] = set()
        self.only_in_path2: Set[str] = set()
        self.diff_files: Dict[str, List[str]] = {}
        
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if the file should be ignored"""
        ext = file_path.suffix.lower()
        filename = file_path.name
        
        # Check if filename matches any ignore pattern
        for pattern in self.ignore_files:
            if fnmatch.fnmatch(filename, pattern):
                return True
        
        # If only_ext is specified, only include those
        if self.only_ext and ext not in self.only_ext:
            return True
            
        # If ignore_ext is specified, skip those
        if ext in self.ignore_ext:
            return True
            
        return False
    
    def _get_relative_files(self, base_path: Path) -> Set[str]:
        """Recursively scan all files in a folder (return relative paths)"""
        files = set()
        for root, dirs, filenames in os.walk(base_path):
            # Remove ignored directories from dirs list (modifies in-place to prevent descent)
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for filename in filenames:
                full_path = Path(root) / filename
                
                # Filtering check
                if self._should_ignore(full_path):
                    continue
                    
                # Calculate relative path
                rel_path = full_path.relative_to(base_path)
                files.add(str(rel_path))
        return files
    
    def _compare_file_content(self, rel_path: str) -> Optional[List[str]]:
        """Compare the content of two files line by line"""
        file1 = self.path1 / rel_path
        file2 = self.path2 / rel_path
        
        try:
            # Read files line by line (memory-friendly)
            with open(file1, 'r', encoding='utf-8', errors='ignore') as f1:
                lines1 = f1.readlines()
            with open(file2, 'r', encoding='utf-8', errors='ignore') as f2:
                lines2 = f2.readlines()
            
            # Generate unified diff
            diff = list(difflib.unified_diff(
                lines1, lines2,
                fromfile=f"Project1/{rel_path}",
                tofile=f"Project2/{rel_path}",
                lineterm=''
            ))
            
            # Return if there are differences
            return diff if len(diff) > 0 else None
            
        except Exception as e:
            return [f"ERROR: File could not be compared - {str(e)}"]
    
    def compare(self) -> None:
        """Perform the main comparison operation"""
        print(f"{Fore.CYAN}📁 Scanning folders...{Style.RESET_ALL}")
        
        # Scan files in both folders
        files1 = self._get_relative_files(self.path1)
        files2 = self._get_relative_files(self.path2)
        
        # Find files that exist only on one side
        self.only_in_path1 = files1 - files2
        self.only_in_path2 = files2 - files1
        
        # Common files
        common_files = files1 & files2
        
        print(f"{Fore.CYAN}🔍 Comparing {len(common_files)} common files...{Style.RESET_ALL}\n")
        
        # Compare contents of common files (with progress bar)
        for rel_path in tqdm(sorted(common_files), desc="Progress", unit="file"):
            diff = self._compare_file_content(rel_path)
            if diff:
                self.diff_files[rel_path] = diff
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate detailed report"""
        lines = []
        lines.append("=" * 80)
        lines.append("PROJECT COMPARISON REPORT")
        lines.append("=" * 80)
        lines.append(f"Project 1: {self.path1}")
        lines.append(f"Project 2: {self.path2}")
        lines.append("=" * 80)
        lines.append("")
        
        # Files only in Project1
        if self.only_in_path1:
            lines.append(f"📌 FILES FOUND ONLY IN PROJECT1 ({len(self.only_in_path1)} files):")
            lines.append("-" * 80)
            for file in sorted(self.only_in_path1):
                lines.append(f"  ➤ {file}")
            lines.append("")
        
        # Files only in Project2
        if self.only_in_path2:
            lines.append(f"📌 FILES FOUND ONLY IN PROJECT2 ({len(self.only_in_path2)} files):")
            lines.append("-" * 80)
            for file in sorted(self.only_in_path2):
                lines.append(f"  ➤ {file}")
            lines.append("")
        
        # Files with content differences
        if self.diff_files:
            lines.append(f"📌 FILES WITH CONTENT DIFFERENCES ({len(self.diff_files)} files):")
            lines.append("-" * 80)
            for file in sorted(self.diff_files.keys()):
                lines.append(f"  ➤ {file}")
            lines.append("")
        
        report = "\n".join(lines)
        
        # Write to file
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report
    
    def print_summary(self, output_file: Optional[str] = None) -> None:
        """Print summary report to console"""
        print("\n" + "=" * 80)
        print(f"{Fore.GREEN}✅ COMPARISON COMPLETED{Style.RESET_ALL}")
        print("=" * 80)
        
        if self.only_in_path1:
            print(f"{Fore.YELLOW}📁 {len(self.only_in_path1)} files found only in Project1.{Style.RESET_ALL}")
        
        if self.only_in_path2:
            print(f"{Fore.YELLOW}📁 {len(self.only_in_path2)} files found only in Project2.{Style.RESET_ALL}")
        
        if self.diff_files:
            print(f"{Fore.RED}📝 {len(self.diff_files)} files with content differences detected.{Style.RESET_ALL}")
        
        if not self.only_in_path1 and not self.only_in_path2 and not self.diff_files:
            print(f"{Fore.GREEN}✨ Folders are identical!{Style.RESET_ALL}")
        
        if output_file:
            print(f"{Fore.CYAN}📄 Detailed report: {output_file}{Style.RESET_ALL}")
        
        print("=" * 80)


def main():
    """Main program entry point"""
    parser = argparse.ArgumentParser(
        description="Compares two project folders and reports their differences.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compare_projects.py "C:\\Project1" "C:\\Project2"
  python compare_projects.py ./project1 ./project2 --output differences.txt
  python compare_projects.py ./src1 ./src2 --only-ext .py .js .json
  python compare_projects.py ./dir1 ./dir2 --ignore-ext .log .tmp .pyc
  python compare_projects.py ./web1 ./web2 --ignore-dirs node_modules .git
  python compare_projects.py ./app1 ./app2 --ignore-files "*.log" package-lock.json
        """
    )
    
    parser.add_argument('path1', help='First folder path')
    parser.add_argument('path2', help='Second folder path')
    parser.add_argument('--output', '-o', help='Output file (default: print to screen)')
    parser.add_argument('--ignore-ext', nargs='+', default=[], 
                       help='File extensions to ignore (e.g., .log .tmp)')
    parser.add_argument('--only-ext', nargs='+', default=[],
                       help='Only compare these extensions (e.g., .py .js)')
    parser.add_argument('--ignore-dirs', nargs='+', default=[],
                       help='Directory names to ignore (e.g., node_modules .git __pycache__)')
    parser.add_argument('--ignore-files', nargs='+', default=[],
                       help='File name patterns to ignore (e.g., *.log package-lock.json)')
    
    args = parser.parse_args()
    
    # Check if folders exist
    if not os.path.isdir(args.path1):
        print(f"{Fore.RED}❌ ERROR: Folder '{args.path1}' not found!{Style.RESET_ALL}")
        sys.exit(1)
    
    if not os.path.isdir(args.path2):
        print(f"{Fore.RED}❌ ERROR: Folder '{args.path2}' not found!{Style.RESET_ALL}")
        sys.exit(1)
    
    # Create and run comparator
    comparator = ProjectComparator(
        args.path1, 
        args.path2,
        ignore_ext=args.ignore_ext,
        only_ext=args.only_ext,
        ignore_dirs=args.ignore_dirs,
        ignore_files=args.ignore_files
    )
    
    try:
        comparator.compare()
        report = comparator.generate_report(args.output)
        
        # If no output file specified, print to screen
        if not args.output:
            print("\n" + report)
        
        comparator.print_summary(args.output)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Operation cancelled by user.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}❌ ERROR: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
