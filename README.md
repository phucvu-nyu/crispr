# CRISPR Summary Dashboard

This interactive dashboard allows exploration of gene expression and sgRNA activity data.

## Requirements

- Python 3.7 or higher
- Required data files:
  - `modified_mu_jg.csv` (gene expression data)
  - `modified_phi_ig.csv` (sgRNA activity data)

## Quick Start

### Setup

1. Clone this repository
   ```bash
   git clone https://github.com/phucvu-nyu/crispr.git
   cd CRISPR_summary
   ```

2. Set up environment and install dependencies
   ```bash
   make setup
   ```

### Running the Application

Start the application:
```bash
make run
```

For development with hot reloading:
```bash
make dev
```

The dashboard will be available at http://127.0.0.1:8050/ in your web browser.

## Features

- Select and explore genes of interest
- Filter data by group and number of replicates
- Visualize gene expression and sgRNA activity across different cell lines
- Download selected data as CSV files

## Data Structure

The application expects two CSV files:
- `modified_mu_jg.csv`: Contains gene expression data with columns for design, gene names, size, and group.
- `modified_phi_ig.csv`: Contains sgRNA activity data with columns for design, sgRNA values, size, and group.

## Cleanup

To remove the virtual environment and clean up cache files:
```bash
make clean
```
