// Invoice Extraction Schema
// Handles vendor info, line items, taxes, totals, and multiple currencies

enum Currency {
  USD
  EUR
  GBP
  JPY
  CAD
  AUD
  CHF
  CNY
  INR
  MXN
  OTHER
}

class MonetaryAmount {
  amount float
  currency Currency
  // Optional: original string representation from invoice
  raw_value string? @description("Original text from invoice, e.g., '$1,234.56'")
}

class VendorInfo {
  name string @description("Vendor/supplier company name")
  address string? @description("Full vendor address")
  phone string? @description("Contact phone number")
  email string? @description("Contact email address")
  tax_id string? @description("Tax ID, VAT number, or EIN")
  website string? @description("Company website")
}

class BillingInfo {
  customer_name string? @description("Bill-to company or person name")
  address string? @description("Billing address")
  tax_id string? @description("Customer tax ID or VAT number")
}

class LineItem {
  description string @description("Product or service description")
  quantity float @description("Quantity ordered")
  unit_price MonetaryAmount @description("Price per unit")
  line_total MonetaryAmount @description("Total for this line item")
  sku string? @description("Product SKU or item code")
  unit_of_measure string? @description("Unit type: ea, lb, kg, hrs, etc.")
  tax_rate float? @description("Tax rate applied to this item (as percentage)")
}

class TaxBreakdown {
  tax_type string @description("Type of tax: VAT, Sales Tax, GST, etc.")
  tax_rate float? @description("Tax rate as percentage")
  taxable_amount MonetaryAmount? @description("Amount subject to this tax")
  tax_amount MonetaryAmount @description("Actual tax amount")
}

class PaymentTerms {
  due_date string? @description("Payment due date in YYYY-MM-DD format")
  payment_terms string? @description("Terms description: Net 30, Due on Receipt, etc.")
  discount_terms string? @description("Early payment discount terms if any")
}

class Invoice {
  invoice_number string @description("Unique invoice identifier")
  invoice_date string @description("Invoice date in YYYY-MM-DD format")

  // Vendor and billing information
  vendor VendorInfo
  billing_info BillingInfo?

  // Line items
  line_items LineItem[] @description("All items listed on the invoice")

  // Financial breakdown
  subtotal MonetaryAmount @description("Sum of all line items before tax")
  tax_breakdown TaxBreakdown[] @description("Breakdown of all taxes applied")
  total_tax MonetaryAmount @description("Total of all taxes")
  total_amount MonetaryAmount @description("Final amount due")

  // Additional charges
  shipping_amount MonetaryAmount? @description("Shipping or freight charges")
  handling_fee MonetaryAmount? @description("Handling or processing fees")
  discount_amount MonetaryAmount? @description("Any discounts applied")

  // Payment information
  payment_terms PaymentTerms?
  purchase_order_number string? @description("PO number if referenced")

  // Multi-currency support
  primary_currency Currency @description("Main currency used in the invoice")
  exchange_rate float? @description("Exchange rate if conversion was applied")
  converted_total MonetaryAmount? @description("Total in alternate currency if provided")

  // Additional metadata
  notes string? @description("Any special notes or instructions on the invoice")
}

// Main extraction function
function ExtractInvoiceData(invoice_image: image) -> Invoice {
  client GPT4Vision
  prompt #"
    Extract all information from this invoice image.

    Pay special attention to:
    1. All line items with their quantities, unit prices, and totals
    2. The vendor information at the top
    3. All tax amounts and tax rates
    4. The final total amount
    5. Currency symbols and currency codes
    6. Any multi-currency information or exchange rates

    For monetary amounts, always capture both the numeric value and the currency.
    If quantities are decimals (like 2.5 hours), preserve the decimal precision.

    If information is not present on the invoice, omit that field rather than guessing.
  "#
}

// Alternative function for text-based invoices (PDF extracts, OCR results, etc.)
function ExtractInvoiceDataFromText(invoice_text: string) -> Invoice {
  client GPT4
  prompt #"
    Extract structured invoice information from the following text.

    {{ invoice_text }}

    Instructions:
    - Extract all line items with quantities, prices, and totals
    - Identify vendor and billing information
    - Capture all tax amounts and breakdowns
    - Note the currency for all monetary amounts
    - If multiple currencies are mentioned, extract the exchange rate if provided
    - Preserve all numerical precision (decimals)

    Only extract information that is explicitly stated in the text.
  "#
}

// Validation function to check for common extraction issues
function ValidateInvoice(invoice: Invoice) -> bool {
  client GPT4
  prompt #"
    Validate this extracted invoice data for consistency:

    {{ invoice }}

    Check that:
    1. Sum of line_items matches the subtotal (within rounding tolerance)
    2. Subtotal + taxes = total_amount
    3. All monetary amounts use the same currency as primary_currency (unless explicitly multi-currency)
    4. Required fields are present: invoice_number, invoice_date, vendor.name, total_amount

    Return true if validation passes, false if there are inconsistencies.
  "#
}
