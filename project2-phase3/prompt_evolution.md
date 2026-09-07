# Prompt Evolution Log

## Phase 3 - Domain-Aware Analytics System

### Version 1.0 - Initial Domain Detection

The first version of the Domain Configuration Agent used basic column-name
keyword matching to identify the dataset domain.

Initial supported domains:

- Retail Sales
- E-commerce
- Inventory
- Restaurant Sales
- Subscription / SaaS

The agent also identified:

- Numeric columns
- Categorical columns
- Date/time columns
- Candidate metrics
- Candidate dimensions
- Domain-specific success metrics

### Testing Observation

During testing with the restaurant sales dataset, the initial domain
detection logic incorrectly classified the dataset as:

`e-commerce`

The dataset contained an `OrderID` column and payment information, which
caused the e-commerce rules to receive a high score.

However, the dataset also contained restaurant-specific fields such as:

- TableNumber
- Server
- Item
- Category
- PaymentMethod
- Quantity
- UnitPrice
- TotalAmount

This showed that simple keyword matching was not sufficiently domain-aware.

---

## Version 2.0 - Improved Domain Detection

The domain detection logic was refined to consider combinations of related
columns instead of relying only on individual keywords.

Restaurant-specific signals were added for:

- Item / Menu Item / Dish / Food
- Table Number
- Server / Waiter
- Payment Method
- Category

Additional structural scoring was introduced.

For example, the presence of:

`Item + Table/Server + Payment Method`

provides a strong indication of restaurant sales data.

Similar structural checks were also added for:

- Product + Quantity → Retail Sales
- Order + Customer → E-commerce
- Stock / Inventory → Inventory
- Subscription identifiers → Subscription / SaaS

---

## Version 2.1 - Datetime Parsing Improvement

Datetime detection was improved to safely handle datasets containing
different date formats.

The parser first attempts mixed-format datetime parsing and falls back to
standard parsing when required.

This reduced unnecessary pandas datetime parsing warnings and improved
robustness across different datasets.

---

## Version 2.2 - Domain-Aware Success Metrics

Success metrics were made domain-specific.

### Retail Sales

- Total sales
- Total quantity
- Average transaction value
- Top products
- Sales by category
- Sales by region

### E-commerce

- Total revenue
- Total orders or units
- Top products
- Sales by category
- Customer performance

### Inventory

- Total inventory
- Total units
- Inventory by product
- Inventory by location
- Inventory by supplier

### Restaurant Sales

- Total restaurant revenue
- Total items sold
- Top menu items
- Sales by category
- Sales by server
- Sales by payment method

### Subscription / SaaS

- Monthly recurring revenue
- Annual recurring revenue
- Active customers or subscribers
- Churn rate
- Retention rate
- Performance by plan

---

## Version 3.0 - Production-Oriented Configuration

The final version was designed to handle datasets dynamically rather than
being tied to the original retail dataset.

The configuration process now:

1. Validates the input CSV.
2. Removes unnecessary unnamed columns.
3. Profiles the dataset structure.
4. Detects numeric, categorical and datetime fields.
5. Detects the likely business domain.
6. Selects useful metrics.
7. Selects useful dimensions.
8. Defines domain-specific success metrics.
9. Returns a structured configuration for downstream agents.

### Final Testing Result

The refined configuration was tested across five different domains:

| Dataset | Domain Detected | Result |
|---|---|---|
| Retail Sales | Retail Sales | PASS |
| E-commerce Orders | E-commerce | PASS |
| Inventory Stock | Inventory | PASS |
| Restaurant Sales | Restaurant Sales | PASS |
| SaaS Subscriptions | Subscription / SaaS | PASS |

### Key Learning

Testing across multiple domains exposed weaknesses that were not visible
when using only the original retail dataset.

The main improvement was moving from simple keyword-based classification
towards combined semantic and structural signals.

This makes the Phase 3 pipeline more adaptable to unseen datasets and
different business domains.
