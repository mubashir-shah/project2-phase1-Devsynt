# Project 2 - Phase 2: Multi-Agent Retail Data Pipeline

**DevSynt AI Automation Internship** | Mentor: Afnan Shoukat | Individual Project

## Overview

This project is a **multi-agent retail data pipeline** that cleans raw retail sales data, analyzes it, and presents the results through a static HTML dashboard — all coordinated by an orchestrator agent.

This project is the practical application of the **LangChain + LangGraph fundamentals** learned in Phase 1.

## Dataset

**File:** `data/retail_data.csv`

The dataset contains **500 retail sales records** with the following columns:

- `Date` - Transaction date
- `Product` - Product name (Laptop, Mouse, Keyboard, etc.)
- `Category` - Product category (Electronics, Furniture, Accessories)
- `Quantity` - Units sold
- `UnitPrice` - Price per unit
- `Region` - Sales region (North, South, East, West)
- `Sales` - Total sale value (Quantity × UnitPrice)

## Architecture / Agent Workflow

```text
Raw Retail CSV
      |
      v
Orchestrator Agent
(decides processing order)
      |
      v
Clean Agent
(missing values, data types, duplicates)
      |
      v
Analysis Agent
(total sales, top products,
region/category breakdown)
      |
      v
Visualization Agent [Bonus]
(bar/pie/line charts)
      |
      v
Static HTML Dashboard


See the complete flow diagram:

assets/flow-diagram.png

Agents
1. Orchestrator Agent

The Orchestrator Agent acts as the manager of the entire pipeline.

It loads the raw CSV file and determines the processing order. The data is first sent to the Clean Agent and then to the Analysis Agent.

The orchestrator coordinates the complete pipeline and tracks the project state, including:

Raw data
Cleaned data
Analysis insights

File: agents/orchestrator.py

2. Clean Agent

The Clean Agent prepares the raw dataset for analysis.

It performs the following cleaning operations:

Checks for missing values and removes them
Detects and removes duplicate rows
Fixes incorrect data types
Converts Date values to datetime format
Converts numeric columns to appropriate numeric data types

File: agents/clean.py

Cleaning result:

assets/cleaning-result.png

3. Analysis (EDA) Agent

The Analysis Agent performs Exploratory Data Analysis (EDA) on the cleaned dataset.

It generates the following insights:

Total sales
Top 5 best-selling products by quantity
Sales by region
Sales by category
Summary statistics
Average transaction value
Maximum sale
Minimum sale
Date range

File: agents/analysis.py

Analysis output:

assets/analysis-output.png

4. Visualization Agent (Bonus)

The Visualization Agent converts the analysis results into visual charts.

It generates:

Bar chart - Sales by Region
Pie chart - Sales by Category
Horizontal bar chart - Top Products
Line chart - Monthly Sales Trend

File: agents/visualization.py

Charts are stored in:

assets/chart-*.png

Dashboard

A simple static HTML dashboard presents the key results from the analysis.

The dashboard displays:

Key performance metrics
Top products
Sales by region
Sales by category
Summary statistics

File: dashboard.html

Dashboard preview:

assets/dashboard-preview.png

Results Summary
Total Sales: $3,132,571.00
Total Transactions: 500
Total Quantity Sold: 3,853 units
Top Product: Laptop (563 units)
Best Performing Region: North ($896,526)
Best Performing Category: Electronics ($1,072,830)

Full analysis insights are available in:

data/insights.txt

How to Run
1. Activate the virtual environment
source .venv/bin/activate
2. Navigate to the project folder
cd project2-phase2
3. Run the pipeline
python3 main.py

The pipeline will:

Load the raw retail data
Clean the dataset using the Clean Agent
Analyze the cleaned data using the Analysis Agent
Generate charts using the Visualization Agent
Save the generated outputs to data/ and assets/
4. Open the dashboard
xdg-open dashboard.html
Requirements
Python 3.8
pandas
matplotlib
langchain 0.1.20
Folder Structure
project2-phase2/

├── agents/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── clean.py
│   ├── analysis.py
│   └── visualization.py
│
├── data/
│   ├── retail_data.csv
│   ├── cleaned_data.csv
│   └── insights.txt
│
├── assets/
│   ├── flow-diagram.png
│   ├── cleaning-result.png
│   ├── analysis-output.png
│   ├── dashboard-preview.png
│   └── chart-*.png
│
├── dashboard.html
├── main.py
└── README.md
