// Invoice data extraction schema with support for multi-currency invoices

// Vendor/supplier information
class VendorInfo {
  vendor_name string @description("Legal name of the vendor/supplier")
  vendor_address string? @description("Full address of the vendor")
  vendor_phone string? @description("Contact phone number")
  vendor_email string? @description("Contact email address")
  vendor_tax_id string? @description("Tax ID, VAT number, or business registration number")
  vendor_website string? @description("Company website URL")
}

// Individual line item on the invoice
class LineItem {
  description string @description("Description of the product or service")
  quantity float @description("Quantity of items (supports decimals for partial units)")
  unit_price float @description("Price per unit in the line item currency")
  currency string @description("ISO 4217 currency code (USD, EUR, GBP, etc.)")
  line_total float @description("Total for this line item (quantity * unit_price)")
  tax_rate float? @description("Tax rate applied to this line item (e.g., 0.20 for 20%)")
  tax_amount float? @description("Tax amount for this line item")
  discount_amount float? @description("Any discount applied to this line item")
  item_code string? @description("Product/service code or SKU if present")
  category string? @description("Category or type of item (e.g., 'Hardware', 'Service', 'Consulting')")
}

// Tax breakdown entry
class TaxEntry {
  tax_name string @description("Name of the tax (e.g., 'VAT', 'Sales Tax', 'GST')")
  tax_rate float @description("Tax rate as decimal (e.g., 0.20 for 20%)")
  taxable_amount float @description("Amount subject to this tax")
  tax_amount float @description("Calculated tax amount")
  currency string @description("ISO 4217 currency code for this tax entry")
}

// Currency amount with conversion info
class CurrencyAmount {
  amount float @description("The monetary amount")
  currency string @description("ISO 4217 currency code (USD, EUR, GBP, etc.)")
  exchange_rate float? @description("Exchange rate if converted from another currency")
  original_currency string? @description("Original currency if this is a converted amount")
}

// Payment information
class PaymentInfo {
  payment_method string? @description("Method of payment (e.g., 'Wire Transfer', 'Credit Card', 'Check')")
  payment_terms string? @description("Payment terms (e.g., 'Net 30', 'Due on Receipt', '2/10 Net 30')")
  due_date string? @description("Payment due date in YYYY-MM-DD format")
  bank_name string? @description("Bank name for wire transfers")
  account_number string? @description("Last 4 digits of account number (for security)")
  routing_number string? @description("Bank routing number")
  reference_number string? @description("Payment reference or remittance number")
}

// Complete invoice structure
class Invoice {
  invoice_number string @description("Unique invoice identifier/number")
  invoice_date string @description("Invoice issue date in YYYY-MM-DD format")

  vendor VendorInfo @description("Vendor/supplier information")

  customer_name string? @description("Name of the customer/buyer")
  customer_address string? @description("Customer billing address")
  customer_tax_id string? @description("Customer tax ID or business registration")

  line_items LineItem[] @description("All line items on the invoice")

  subtotal CurrencyAmount @description("Subtotal before taxes and discounts")
  tax_entries TaxEntry[] @description("Breakdown of all taxes applied")
  total_tax CurrencyAmount @description("Total of all taxes")
  discount_total CurrencyAmount? @description("Total discounts applied")
  shipping_cost CurrencyAmount? @description("Shipping/freight charges")
  total_amount CurrencyAmount @description("Final total amount due")

  primary_currency string @description("Primary currency used for the invoice (ISO 4217 code)")
  additional_currencies string[] @description("Other currencies present on the invoice if multi-currency")

  payment_info PaymentInfo? @description("Payment details and terms")

  notes string? @description("Additional notes, terms, or conditions")
  purchase_order_number string? @description("Related PO number if present")
  confidence_score float? @description("Overall confidence in extraction accuracy (0.0-1.0)")
}

// Extract structured invoice data from text, image, or PDF content
function ExtractInvoice(
  invoice_content: string,
  content_type: string?
) -> Invoice {
  client CustomGPT5Mini
  prompt #"
    You are an expert invoice data extraction system. Extract all relevant information
    from the provided invoice content with high accuracy.

    Invoice Content:
    {{ invoice_content }}

    Content Type: {{ content_type }}

    Instructions:
    1. Extract all vendor information (name, address, contact details, tax ID)
    2. Identify and extract all line items with their quantities, prices, and descriptions
    3. Calculate or verify line totals (quantity * unit_price)
    4. Extract all tax information including tax rates and amounts
    5. Identify the currency for each amount (use ISO 4217 codes like USD, EUR, GBP)
    6. For multi-currency invoices, track all currencies used
    7. Extract payment terms, methods, and due dates
    8. Parse dates in YYYY-MM-DD format
    9. Extract any discount information
    10. Verify that subtotal + taxes - discounts = total (accounting for rounding)

    Important:
    - Use ISO 4217 currency codes (USD, EUR, GBP, JPY, etc.)
    - Express tax rates as decimals (20% = 0.20)
    - If invoice uses multiple currencies, ensure each amount is tagged with its currency
    - Set confidence_score based on data quality and completeness
    - For missing optional fields, omit them rather than guessing

    {{ ctx.output_format }}
  "#
}

// Alternative function using a more powerful model for complex invoices
function ExtractComplexInvoice(
  invoice_content: string,
  content_type: string?
) -> Invoice {
  client CustomGPT5
  prompt #"
    You are an expert invoice data extraction system specializing in complex,
    multi-currency, and international invoices.

    Invoice Content:
    {{ invoice_content }}

    Content Type: {{ content_type }}

    This may be a complex invoice with:
    - Multiple currencies and exchange rates
    - Complex tax structures (VAT, GST, customs duties, etc.)
    - International shipping and trade terms
    - Multiple payment methods or installment plans

    Extract all available information with high precision:
    1. Complete vendor and customer details
    2. All line items with quantities, prices, taxes, and discounts
    3. Multi-currency amounts with exchange rates if present
    4. Detailed tax breakdown (different rates, tax types)
    5. Payment terms, methods, and banking details
    6. Any special terms, conditions, or notes

    Validation:
    - Verify mathematical accuracy of totals
    - Cross-check currency codes and amounts
    - Ensure tax calculations are correct
    - Flag any inconsistencies in notes field

    Use ISO 4217 currency codes and YYYY-MM-DD date format.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// TESTS - Invoice extraction scenarios
// ============================================================================

// Basic single-currency invoice
test extract_simple_invoice {
  functions [ExtractInvoice]
  args {
    invoice_content #"
      INVOICE #INV-2026-001
      Date: March 10, 2026

      From:
      Acme Corporation
      123 Business St
      New York, NY 10001
      Tax ID: 12-3456789
      Phone: (555) 123-4567
      Email: billing@acme.com

      Bill To:
      TechStart Inc
      456 Innovation Ave
      San Francisco, CA 94102

      Line Items:
      1. Cloud Hosting Services (March 2026) - Qty: 1 @ $499.00 = $499.00
      2. SSL Certificate - Qty: 2 @ $89.00 = $178.00
      3. Technical Support Hours - Qty: 10 @ $125.00 = $1,250.00

      Subtotal: $1,927.00
      Sales Tax (8.5%): $163.80
      Total: $2,090.80

      Payment Terms: Net 30
      Due Date: April 9, 2026
      Payment Method: Wire Transfer
      Bank: First National Bank
      Account: ****5678
    "#
    content_type "text"
  }
}

// Multi-currency invoice with exchange rates
test extract_multicurrency_invoice {
  functions [ExtractComplexInvoice]
  args {
    invoice_content #"
      INVOICE #EU-2026-042
      Invoice Date: 2026-03-10

      Supplier:
      European Tech Solutions GmbH
      Hauptstraße 45
      10115 Berlin, Germany
      VAT: DE123456789

      Customer:
      Global Enterprises Ltd
      London EC1A 1BB, United Kingdom
      VAT: GB987654321

      Items:
      1. Software License (Annual) - 5 licenses × €1,200.00 = €6,000.00
      2. Implementation Service - 40 hours × €150.00 = €6,000.00
      3. Hardware Units - 3 units × $2,500.00 USD = $7,500.00 USD (≈€6,825.00 @ rate 1.10)

      Subtotal (EUR): €18,825.00
      VAT 19%: €3,576.75
      Total (EUR): €22,401.75

      Hardware Subtotal (USD): $7,500.00
      Exchange Rate: 1 EUR = 1.10 USD

      Payment Terms: 2/10 Net 30 (2% discount if paid within 10 days)
      Due: 2026-04-09
      Wire Transfer Details:
      IBAN: DE89370400440532013000
      BIC: COBADEFFXXX
    "#
    content_type "text"
  }
}

// Invoice with complex tax structure
test extract_invoice_with_multiple_taxes {
  functions [ExtractInvoice]
  args {
    invoice_content #"
      Tax Invoice #AU-2026-789
      Date: 10/03/2026

      ABN: 12 345 678 901
      Supplier: Sydney Tech Supplies Pty Ltd
      Address: 100 George St, Sydney NSW 2000

      Customer: Melbourne Innovations
      ABN: 98 765 432 109

      Description                    Qty    Unit Price    Line Total    GST
      Professional Services          20h    $180.00 AUD   $3,600.00     $360.00
      Equipment Rental               5      $450.00 AUD   $2,250.00     $225.00
      Imported Components (GST-free) 10     $200.00 AUD   $2,000.00     $0.00
      Software Subscription          1      $1,500.00 AUD $1,500.00     $150.00

      Subtotal (GST applicable): $7,350.00
      GST (10%): $735.00

      GST-free items: $2,000.00

      Total excluding GST: $9,350.00
      Total GST: $735.00
      Grand Total: $10,085.00

      Payment due: 30 days from invoice date
      Reference: PO-2026-456
    "#
    content_type "text"
  }
}

// Invoice with discounts and shipping
test extract_invoice_with_discounts {
  functions [ExtractInvoice]
  args {
    invoice_content #"
      INVOICE #2026-Q1-555
      March 10, 2026

      Wholesale Supplier Co.
      789 Commerce Blvd, Chicago, IL 60601
      EIN: 36-1234567

      Retail Customer Inc.
      PO Box 999, Miami, FL 33101

      Items:
      1. Product A (Bulk Order) - 100 units @ $50.00 = $5,000.00
         Volume Discount (10%): -$500.00
         Subtotal: $4,500.00

      2. Product B - 50 units @ $75.00 = $3,750.00

      3. Product C - 25 units @ $120.00 = $3,000.00
         Early Order Discount (5%): -$150.00
         Subtotal: $2,850.00

      Merchandise Subtotal: $11,100.00
      Shipping & Handling: $275.00

      Subtotal before tax: $11,375.00
      Sales Tax (7%): $796.25

      Total Amount Due: $12,171.25

      Payment Terms: Net 15
      Due Date: March 25, 2026
    "#
    content_type "text"
  }
}

// Minimal invoice with missing data
test extract_minimal_invoice {
  functions [ExtractInvoice]
  args {
    invoice_content #"
      Invoice: #2026-MIN-001
      Date: 2026-03-10

      From: QuickService LLC

      Service: Website Maintenance (March)
      Amount: $850.00 USD

      Pay to: payments@quickservice.com
      Due: March 31, 2026
    "#
    content_type "text"
  }
}

// International invoice with customs and duties
test extract_international_invoice {
  functions [ExtractComplexInvoice]
  args {
    invoice_content #"
      COMMERCIAL INVOICE
      Invoice No: INTL-2026-JP-042
      Date: March 10, 2026

      Exporter:
      Tokyo Electronics Ltd.
      Shibuya-ku, Tokyo 150-0042, Japan
      Tax ID: JP-1234567890

      Importer:
      US Tech Importers Inc.
      San Jose, CA 95110, USA
      EIN: 94-1234567

      Description of Goods          Qty    Unit Price (JPY)    Amount (JPY)
      Electronic Components A       500    ¥8,500             ¥4,250,000
      Electronic Components B       300    ¥12,000            ¥3,600,000
      Specialty Semiconductors      100    ¥45,000            ¥4,500,000

      Subtotal (JPY): ¥12,350,000
      Consumption Tax 10%: ¥1,235,000
      Total (JPY): ¥13,585,000

      USD Equivalent: $91,216.22 (Exchange rate: 1 USD = 148.91 JPY)

      Terms: FOB Tokyo
      Payment: Letter of Credit
      Shipment: Air Freight
      Freight Cost: ¥450,000 (included in total)
      Insurance: ¥125,000 (included in total)

      Notes: Harmonized System Code: 8542.31
      Import duties and customs fees are responsibility of importer.
    "#
    content_type "text"
  }
}
