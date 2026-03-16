# Invoice Extraction BAML Schema - Design Notes

## Overview

This BAML schema provides comprehensive invoice data extraction capabilities with full support for:
- Multi-currency invoices
- Complex tax structures
- International invoices with exchange rates
- Line item details with quantities, prices, and taxes
- Vendor and customer information
- Payment terms and banking details

## Schema Structure

### Core Classes

#### 1. **Invoice** (Main Class)
The top-level class containing all invoice information:
- Basic invoice metadata (number, date)
- Vendor and customer information
- Line items array
- Tax breakdown
- Totals with currency support
- Payment information

#### 2. **VendorInfo**
Complete vendor/supplier details:
- Business name and contact information
- Tax ID/VAT number
- All fields optional except vendor_name to handle varying invoice formats

#### 3. **LineItem**
Individual invoice line items with:
- Product/service description
- Quantity (float to support decimals like 2.5 hours)
- Unit price and line total
- Currency per line item (critical for multi-currency invoices)
- Optional tax rate, discount, and item categorization
- Item codes/SKUs when present

#### 4. **TaxEntry**
Detailed tax breakdown:
- Tax name (VAT, GST, Sales Tax, etc.)
- Tax rate as decimal (0.20 for 20%)
- Taxable amount and calculated tax
- Currency support for international invoices

#### 5. **CurrencyAmount**
Structured currency handling:
- Amount and ISO 4217 currency code
- Exchange rate when applicable
- Original currency for converted amounts
- Enables accurate multi-currency tracking

#### 6. **PaymentInfo**
Payment terms and banking details:
- Payment method and terms (Net 30, 2/10 Net 30, etc.)
- Due date in ISO format (YYYY-MM-DD)
- Banking information for wire transfers
- Reference numbers for payment tracking

## Design Decisions

### Multi-Currency Support
The schema handles multi-currency invoices through:
1. **Per-item currency tracking**: Each `LineItem` has its own currency field
2. **CurrencyAmount type**: Structured type for all monetary amounts
3. **Exchange rate capture**: Optional fields for conversion rates
4. **Primary + additional currencies**: Track all currencies used on the invoice

### Tax Flexibility
Supports various tax scenarios:
- Single tax rate (simple sales tax)
- Multiple tax types (VAT + customs duties)
- Tax-exempt items (0% tax rate tracked separately)
- Line-item specific tax rates
- Detailed tax breakdown in `TaxEntry` array

### Optional Fields
Many fields are optional (`?`) because:
- Invoice formats vary widely across industries and countries
- Not all invoices contain complete information
- Better to omit unknown data than guess
- Allows extraction from minimal invoices

### Date Format
All dates use **YYYY-MM-DD** format:
- Unambiguous international format
- Easy to parse programmatically
- Avoids MM/DD vs DD/MM confusion

### Currency Codes
Uses **ISO 4217** standard codes:
- USD, EUR, GBP, JPY, AUD, etc.
- Internationally recognized
- Consistent 3-letter format

## Functions

### ExtractInvoice
- Uses **CustomGPT5Mini** (cost-effective)
- Suitable for standard invoices
- Clear extraction instructions
- Validates mathematical accuracy

### ExtractComplexInvoice
- Uses **CustomGPT5** (more powerful)
- For complex multi-currency invoices
- Handles international trade documents
- Performs detailed validation

**When to use which:**
- Use `ExtractInvoice` for: Standard invoices, single currency, simple tax structure
- Use `ExtractComplexInvoice` for: Multi-currency, international trade, complex taxes, multiple payment terms

## Test Coverage

The schema includes 6 comprehensive test cases:

1. **extract_simple_invoice**: Basic single-currency invoice with standard fields
2. **extract_multicurrency_invoice**: European invoice with EUR and USD amounts
3. **extract_invoice_with_multiple_taxes**: Australian GST with mixed taxable/tax-free items
4. **extract_invoice_with_discounts**: Volume and early-order discounts with shipping
5. **extract_minimal_invoice**: Sparse invoice with limited information
6. **extract_international_invoice**: Japanese export invoice with customs details

These tests cover:
- Different currencies (USD, EUR, GBP, AUD, JPY)
- Various tax systems (US sales tax, EU VAT, Australian GST, Japanese consumption tax)
- Simple to complex invoice structures
- Edge cases (minimal data, multiple currencies, customs)

## Usage Examples

### In Rust (after running `baml generate`):

```rust
use baml_client::baml::functions::extract_invoice;

#[tokio::main]
async fn main() {
    let invoice_text = std::fs::read_to_string("invoice.txt")?;

    let result = extract_invoice(
        &invoice_text,
        Some("text")
    ).await?;

    println!("Invoice #{}", result.invoice_number);
    println!("Vendor: {}", result.vendor.vendor_name);
    println!("Total: {} {}",
        result.total_amount.amount,
        result.total_amount.currency
    );

    for item in result.line_items {
        println!("  {} x{} @ {} {}",
            item.description,
            item.quantity,
            item.unit_price,
            item.currency
        );
    }
}
```

### Testing

Run all tests:
```bash
baml test invoice_extraction
```

Run specific test:
```bash
baml test extract_multicurrency_invoice
```

## Extending the Schema

### Adding Custom Fields

If you need additional fields:

```baml
class LineItem {
  // ... existing fields ...

  warranty_period string? @description("Warranty period if applicable")
  manufacturer string? @description("Product manufacturer")
  batch_number string? @description("Batch or lot number")
}
```

### Supporting More Tax Types

Add to TaxEntry or create specialized tax classes:

```baml
class CustomsDuty {
  duty_rate float @description("Customs duty percentage")
  hs_code string @description("Harmonized System tariff code")
  duty_amount CurrencyAmount @description("Calculated duty amount")
}

class Invoice {
  // ... existing fields ...
  customs_duties CustomsDuty[] @description("Import duties and tariffs")
}
```

### Industry-Specific Extensions

For specialized invoicing (medical, legal, construction):

```baml
class MedicalLineItem {
  procedure_code string @description("CPT or ICD code")
  diagnosis_code string? @description("Diagnosis code")
  insurance_covered bool @description("Whether insurance applies")
  copay_amount float? @description("Patient copay amount")
}
```

## Best Practices

1. **Validate extracted data**: Check that subtotal + taxes = total
2. **Set confidence scores**: Help downstream systems assess reliability
3. **Use appropriate function**: Simple vs Complex based on invoice complexity
4. **Currency consistency**: Verify all amounts have currency codes
5. **Date parsing**: Standardize to YYYY-MM-DD format
6. **Handle missing data**: Leave optional fields unset rather than guessing
7. **Tax verification**: Cross-check tax calculations
8. **Test with real invoices**: Use actual invoice samples for validation

## Common Patterns

### Multi-Currency Conversion
```
Line Item (EUR) → Convert to USD → Track both amounts
Original: €1,000 @ rate 1.10 = $1,100 USD
Store: amount=1100, currency=USD, original_currency=EUR, exchange_rate=1.10
```

### Tax Calculation
```
Subtotal: $1,000
Tax Rate: 8.5% (0.085)
Tax Amount: $85
Total: $1,085
```

### Discount Application
```
Item Price: $500 x 10 units = $5,000
Discount: 10% volume discount = -$500
Line Total: $4,500
```

## Compliance Considerations

This schema supports common compliance requirements:
- **Tax reporting**: Detailed tax breakdown by type and rate
- **Audit trails**: Invoice numbers, dates, payment references
- **International trade**: HS codes, customs duties, FOB terms
- **VAT/GST**: Tax ID capture for both parties
- **Banking**: Payment method and banking details for reconciliation

## Performance Notes

- **ExtractInvoice** (GPT-4o-mini): ~$0.001-0.003 per invoice, 1-3 seconds
- **ExtractComplexInvoice** (GPT-4o): ~$0.01-0.03 per invoice, 2-5 seconds

For batch processing, consider:
- Using ExtractInvoice for 80% of standard invoices
- Only using ExtractComplexInvoice when needed
- Implementing retry logic with the Exponential retry policy
- Caching results to avoid re-extraction

## Troubleshooting

**Problem**: Missing line items
**Solution**: Check if invoice has table formatting; may need OCR pre-processing

**Problem**: Incorrect currency codes
**Solution**: Add validation to ensure ISO 4217 codes; provide examples in prompt

**Problem**: Tax calculations don't match
**Solution**: Include rounding instructions; capture displayed amounts vs calculated

**Problem**: Multi-currency amounts missing
**Solution**: Use ExtractComplexInvoice; explicitly instruct to track all currencies

**Problem**: Low confidence scores
**Solution**: Pre-process image quality; use higher-quality model; verify OCR output
