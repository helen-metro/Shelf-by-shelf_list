# Shelf-by-Shelf List

A Python tool for generating and processing shelf-by-shelf library collection lists.

## Overview

This project automates the preparation of shelf-by-shelf reports by:

- Loading and preprocessing collection data
- Categorizing materials
- Generating formatted output lists
- Supporting print-ready workflows

The repository is designed to streamline collection review and shelf maintenance tasks.

## Project Structure

```
.
├── main.py               # Main entry point
├── preprocessing.py      # Data cleaning and preparation
├── category.py           # Category processing logic
├── category.json         # Category mappings/configuration
├── utils.py              # Shared utility functions
├── add_page_break.py     # Output formatting/page break handling
├── requirements.txt      # Project dependencies
└── README.md
```

## Requirements

- Python 3.9+ (recommended)
- Dependencies listed in `requirements.txt`

## Installation

Clone the repository:

```bash
git clone https://github.com/helen-metro/Shelf-by-shelf_list.git
cd Shelf-by-shelf_list
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the main program:

```bash
python main.py
```

If your workflow includes additional formatting steps, run:

```bash
python add_page_break.py
```

## Configuration

Category definitions are stored in:

```text
category.json
```

Update this file as needed to match your collection categories and reporting requirements.

## Workflow

1. Load source data.
2. Preprocess and clean records.
3. Apply category mappings.
4. Generate shelf-by-shelf output.
5. Add page formatting if needed.
6. Export final report.

## Development

To contribute:

1. Create a feature branch.
2. Make changes.
3. Test the workflow.
4. Submit a pull request.

## License

Add your preferred license information here.

## Author

Helen Dinh
