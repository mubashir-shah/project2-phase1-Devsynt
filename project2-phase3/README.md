# Project 2 - Phase 3
## Production-Grade Build: Dynamic Dashboard + Domain-Aware Agents

A production-oriented multi-agent analytics pipeline that automatically
adapts to different business datasets and generates domain-aware analysis
and dynamic dashboards.

---

## 1. Project Overview

Phase 3 extends the Phase 2 retail analytics prototype into a dynamic,
domain-aware analytics system.

Unlike Phase 2, the pipeline is no longer limited to a single retail
dataset. The system automatically inspects an incoming dataset, detects
its likely business domain, identifies relevant metrics and dimensions,
performs data cleaning and analysis, and generates a dynamic dashboard.

The system was tested across five different business domains:

- Retail Sales
- E-commerce Orders
- Inventory Stock
- Restaurant Sales
- Subscription / SaaS

---

## 2. Phase 3 Objectives

The main objectives of Phase 3 are:

- Build a Domain Configuration Agent.
- Replace the static dashboard with a Dynamic Dashboard Agent.
- Make the analytics pipeline adaptable to different datasets.
- Automatically identify relevant columns and business metrics.
- Improve handling of malformed or unexpected data.
- Test the system across multiple business domains.
- Maintain prompt/rule evolution documentation.
- Produce a professional and consistent analytics output.

---

## 3. Updated Architecture

The Phase 3 pipeline follows this workflow:

Dataset
   |
   v
Domain Configuration Agent
   |
   v
Orchestrator Agent
   |
   v
Clean Agent
   |
   v
Analysis Agent
   |
   v
Dynamic Dashboard Agent
   |
   v
Dashboard Output

### Domain Configuration Agent

The Domain Configuration Agent runs before the main analytics workflow.

It:

1. Validates the input dataset.
2. Profiles the dataset.
3. Detects numeric columns.
4. Detects categorical columns.
5. Detects datetime columns.
6. Detects the likely business domain.
7. Selects relevant metrics.
8. Selects relevant dimensions.
9. Defines domain-specific success metrics.

### Orchestrator Agent

The Orchestrator controls the overall pipeline and passes the domain
configuration to downstream agents.

### Clean Agent

The Clean Agent dynamically prepares incoming datasets.

It handles:

- Duplicate records
- Missing values
- Numeric conversion
- Datetime detection
- Categorical values
- Unnamed columns
- Dataset validation

### Analysis Agent

The Analysis Agent performs domain-aware analytics using the configuration
provided by the Domain Configuration Agent.

It generates:

- Metric statistics
- Primary metric
- Dimension-based analysis
- Top performers
- Grouped analysis
- Time trends
- Domain-specific success metrics

### Dynamic Dashboard Agent

The Dynamic Dashboard Agent replaces the static Phase 2 visualization.

It dynamically generates:

- KPI cards
- Trend charts
- Dimension charts
- Top performers
- Business insights
- Dataset overview

The dashboard structure changes according to the incoming dataset.

---

## 4. Project Structure

```text
project2-phase3/
│
├── agents/
│   ├── __init__.py
│   ├── domain_config.py
│   ├── orchestrator.py
│   ├── clean.py
│   ├── analysis.py
│   ├── dashboard.py
│   └── visualization.py
│
├── test-datasets/
│   ├── ecommerce_orders.csv
│   ├── inventory_stock.csv
│   ├── restaurant_sales.csv
│   └── saas_subscriptions.csv
│
├── assets/
│   ├── flow-diagram.png
│   ├── dataset1-result.png
│   ├── dataset2-result.png
│   ├── dataset3-result.png
│   ├── dataset4-result.png
│   ├── dataset5-result.png
│   └── prompt-evolution-log.png
│
├── data/
│   └── retail_data.csv
│
├── dashboard.html
├── main.py
├── prompt_evolution.md
├── main_phase2_backup.py
└── README.md

5.Technologies Used
Python
Pandas
HTML
CSS
JavaScript
Chart.js
Multi-Agent Architecture
Data Analytics
Git / GitHub
6. Running the Project

Activate the virtual environment:

source /home/mubashir/Documents/project2-phase1/.venv/bin/activate

Run the default retail dataset:

python main.py data/retail_data.csv

Run another dataset:

python main.py test-datasets/ecommerce_orders.csv

Examples:

python main.py test-datasets/inventory_stock.csv
python main.py test-datasets/restaurant_sales.csv
python main.py test-datasets/saas_subscriptions.csv

After successful execution, the system generates:

dashboard.html

Open dashboard.html in a web browser to view the generated dashboard.

7. Multi-Domain Testing

The Phase 3 system was tested using five different datasets.

Dataset 1 - Retail Sales

Detected domain:

retail sales

Detected metrics:

Quantity
UnitPrice
Sales

Detected dimensions:

Product
Category
Region

Result:

PASS
Dataset 2 - E-commerce Orders

Detected domain:

e-commerce

Detected metrics include:

Quantity
UnitPrice
Discount
TotalAmount

Detected dimensions include:

OrderID
Customer
Product
Category
PaymentMethod
Region

Result:

PASS
Dataset 3 - Inventory Stock

Detected domain:

inventory

Detected metrics include:

StockLevel
UnitsIn
UnitsOut
UnitCost

Detected dimensions include:

SKU
Product
Category
Warehouse
Supplier

Result:

PASS
Dataset 4 - Restaurant Sales

Detected domain:

restaurant sales

Detected metrics:

Quantity
UnitPrice
TotalAmount

Detected dimensions include:

Server
Item
Category
PaymentMethod

Domain-specific success metrics include:

Total restaurant revenue
Total items sold
Top menu items
Sales by category
Sales by server
Sales by payment method

Result:

PASS
Dataset 5 - Subscription / SaaS

Detected domain:

subscription / saas

Detected metrics include:

Users
ActiveUsers
Churned

Detected dimensions include:

SubscriptionID
Customer
Plan
Region

Domain-specific metrics include:

Active customers or subscribers
Churn rate
Performance by plan

Result:

PASS
8. Adaptive Domain Detection

The system uses both column semantics and structural relationships
between columns.

Examples:

Product + Quantity
        ↓
Retail Sales
Order + Customer
        ↓
E-commerce
Stock / Inventory
        ↓
Inventory
Item + Table/Server + Payment Method
        ↓
Restaurant Sales
Subscription + Plan + Users/Churn
        ↓
Subscription / SaaS

This allows the system to adapt instead of relying on the fixed retail
schema from Phase 2.

9. Production-Grade Handling

The pipeline includes defensive handling for unexpected input.

Examples include:

Missing dataset files
Invalid file extensions
Empty datasets
Unreadable CSV files
Unnamed columns
Missing values
Duplicate records
Numeric values stored as text
Different datetime formats
Missing expected configured columns
No strongly identifiable metric
No usable dimensions

When possible, the system falls back to general dataset profiling instead
of failing because of a domain-specific assumption.

10. Dynamic Dashboard

The dashboard is generated from the detected dataset structure.

It can dynamically display:

Total records
Primary business metric
Metric statistics
Time trends
Dimension performance
Top-performing categories/items
Domain-aware insights
Dataset overview

The dashboard is not hardcoded for the original retail dataset.

11. Prompt / Rule Evolution

During multi-domain testing, an important failure was identified.

The first domain detection version classified the restaurant dataset as:

e-commerce

because fields such as OrderID and payment information were interpreted
as e-commerce signals.

The detection logic was then improved by adding restaurant-specific
structural signals such as:

Item
Table Number
Server
Payment Method
Category

The refined version correctly classified the restaurant dataset as:

restaurant sales

The complete evolution history is documented in:

prompt_evolution.md
12. Final Testing Summary
Dataset	Domain	Result
Retail Sales	Retail Sales	PASS
E-commerce Orders	E-commerce	PASS
Inventory Stock	Inventory	PASS
Restaurant Sales	Restaurant Sales	PASS
SaaS Subscriptions	Subscription / SaaS	PASS

All five test domains were successfully processed by the Phase 3 pipeline.

13. Phase 3 Outcome

Phase 3 transforms the original static retail analytics prototype into a
more flexible production-oriented analytics system.

The final system can:

Accept different business datasets.
Detect the likely domain automatically.
Configure relevant metrics and dimensions.
Clean unexpected data.
Perform domain-aware analysis.
Generate dynamic dashboards.
Adapt its output to different dataset structures.
Record improvements made during testing.
14. Author

Mubashir Shah

DevSynt AI Automation Internship
Project 2 - Phase 3



