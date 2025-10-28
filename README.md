# BasicFolderCompare

A Python tool to recursively compare two project folders, detecting file differences and line-by-line content changes.

## Description

BasicFolderCompare is a command-line utility that compares two directories and generates detailed reports about:
- Files that exist only in one folder
- Files that exist in both folders but have different content
- Line-by-line differences in modified files

Perfect for comparing project versions, backups, or tracking changes across codebases.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lutfiengizek/BasicFolderCompare.git
cd BasicFolderCompare
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Comparison
Compare two folders and display results in terminal:
```bash
python compare_projects.py "/path/to/folder1" "/path/to/folder2"
```

### Save Results to File
```bash
python compare_projects.py ./project1 ./project2 --output differences.txt
```

### Compare Only Specific File Types
Compare only Python files:
```bash
python compare_projects.py ./src1 ./src2 --only-ext .py .pyi
```

Compare web project files:
```bash
python compare_projects.py ./web1 ./web2 --only-ext .js .jsx .ts .tsx .html .css
```

### Ignore Specific File Types
Exclude log and temporary files:
```bash
python compare_projects.py ./app1 ./app2 --ignore-ext .log .tmp .pyc .pyo
```

### Ignore Specific Directories
Exclude folders like `node_modules`, `.git`, or `__pycache__`:
```bash
python compare_projects.py ./project1 ./project2 --ignore-dirs node_modules .git __pycache__
```

### Ignore Specific File Patterns
Exclude files by name pattern (supports wildcards):
```bash
python compare_projects.py ./web1 ./web2 --ignore-files "*.log" "package-lock.json" ".DS_Store"
```

### Combined Options
```bash
python compare_projects.py ./project1 ./project2 \
  --only-ext .py .js .json \
  --ignore-dirs node_modules .git \
  --ignore-files "*.pyc" "*.log" \
  --output report.txt
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `path1` | First folder path (required) |
| `path2` | Second folder path (required) |
| `--output`, `-o` | Output file for detailed report (optional) |
| `--ignore-ext` | File extensions to ignore (e.g., `.log .tmp`) |
| `--only-ext` | Only compare these extensions (e.g., `.py .js`) |
| `--ignore-dirs` | Directory names to skip (e.g., `node_modules .git`) |
| `--ignore-files` | File name patterns to ignore (supports wildcards: `*.log`) |

## Example Output

```
📁 Scanning folders...
🔍 245 common files to compare...

Progress: 100%|████████████████████| 245/245 [00:03<00:00, 78.5 files/s]

================================================================================
✅ COMPARISON COMPLETED
================================================================================
📁 18 files found only in Project1.
📁 12 files found only in Project2.
📝 43 files with content differences detected.
📄 Detailed report: differences.txt
================================================================================
```

## Requirements

- Python 3.8+
- tqdm >= 4.66.0
- colorama >= 0.4.6

## License

MIT License

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
