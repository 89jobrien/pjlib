# Quick Start Guide - Invoice Extraction Schema

## Setup

1. **Add to your BAML project**:
   ```bash
   cp invoice_extraction.baml your-project/baml_src/
   ```

2. **Ensure you have a client configured** in `baml_src/clients.baml`:
   ```baml
   client<llm> CustomGPT5Mini {
     provider openai-responses
     retry_policy Exponential
     options {
       model "gpt-4o-mini"
       api_key env.OPENAI_API_KEY
     }
   }

   client<llm> CustomGPT5 {
     provider openai-responses
     options {
       model "gpt-4o"
       api_key env.OPENAI_API_KEY
     }
   }
   ```

3. **Generate client code**:
   ```bash
   baml generate
   ```

4. **Set your API key**:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

## Testing

Run the included tests to verify everything works:

```bash
# Run all invoice extraction tests
baml test invoice_extraction

# Run a specific test
baml test extract_simple_invoice

# Run multi-currency test
baml test extract_multicurrency_invoice
```

## Basic Usage

### Extract from a simple invoice:

```rust
use baml_client::baml::functions::extract_invoice;

let invoice_text = r#"
INVOICE #001
Date: 2026-03-10

From: Acme Corp
To: Customer Inc

Item: Consulting Services - 10 hours @ $150/hr = $1,500.00
Tax (10%): $150.00
Total: $1,650.00
"#;

let result = extract_invoice(invoice_text, Some("text")).await?;

println!("Invoice: {}", result.invoice_number);
println!("Total: {} {}",
    result.total_amount.amount,
    result.total_amount.currency
);
```

### Extract from a multi-currency invoice:

```rust
use baml_client::baml::functions::extract_complex_invoice;

let complex_invoice = std::fs::read_to_string("invoice_multicurrency.txt")?;

let result = extract_complex_invoice(&complex_invoice, Some("text")).await?;

// Check for multiple currencies
println!("Primary currency: {}", result.primary_currency);
for currency in result.additional_currencies {
    println!("Also uses: {}", currency);
}

// Examine line items with different currencies
for item in result.line_items {
    println!("{}: {} {} {}",
        item.description,
        item.quantity,
        item.unit_price,
        item.currency
    );
}
```

## Common Use Cases

### 1. Extract and Validate Totals

```rust
let result = extract_invoice(invoice_text, Some("text")).await?;

// Calculate expected total
let subtotal = result.subtotal.amount;
let taxes = result.total_tax.amount;
let expected = subtotal + taxes;

// Compare with extracted total
let actual = result.total_amount.amount;
let diff = (expected - actual).abs();

if diff > 0.01 {
    println!("Warning: Total mismatch! Expected: {}, Got: {}", expected, actual);
}
```

### 2. Export to JSON

```rust
use serde_json;

let result = extract_invoice(invoice_text, Some("text")).await?;
let json = serde_json::to_string_pretty(&result)?;

std::fs::write("extracted_invoice.json", json)?;
```

### 3. Process Batch of Invoices

```rust
use tokio::fs;
use futures::future::join_all;

async fn process_invoices(directory: &str) -> Result<Vec<Invoice>> {
    let mut tasks = vec![];

    let mut entries = fs::read_dir(directory).await?;
    while let Some(entry) = entries.next_entry().await? {
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) == Some("txt") {
            tasks.push(async move {
                let content = fs::read_to_string(&path).await?;
                extract_invoice(&content, Some("text")).await
            });
        }
    }

    let results = join_all(tasks).await;
    results.into_iter().collect()
}
```

### 4. Handle Multi-Currency Conversion

```rust
let result = extract_complex_invoice(invoice_text, Some("text")).await?;

// Find items in different currencies
let mut currency_totals: HashMap<String, f64> = HashMap::new();

for item in &result.line_items {
    *currency_totals.entry(item.currency.clone()).or_insert(0.0) += item.line_total;
}

println!("Totals by currency:");
for (currency, total) in currency_totals {
    println!("{}: {:.2}", currency, total);
}
```

### 5. Filter by Tax Status

```rust
let result = extract_invoice(invoice_text, Some("text")).await?;

// Separate taxable and tax-exempt items
let (taxable, exempt): (Vec<_>, Vec<_>) = result.line_items
    .iter()
    .partition(|item| item.tax_amount.unwrap_or(0.0) > 0.0);

println!("Taxable items: {}", taxable.len());
println!("Tax-exempt items: {}", exempt.len());
```

## Advanced Patterns

### Custom Validation

```rust
fn validate_invoice(invoice: &Invoice) -> Vec<String> {
    let mut warnings = vec![];

    // Check for missing vendor tax ID (important for B2B)
    if invoice.vendor.vendor_tax_id.is_none() {
        warnings.push("Missing vendor tax ID".to_string());
    }

    // Verify line item totals
    for (i, item) in invoice.line_items.iter().enumerate() {
        let expected = item.quantity * item.unit_price;
        let diff = (expected - item.line_total).abs();
        if diff > 0.01 {
            warnings.push(format!("Line item {} total mismatch", i + 1));
        }
    }

    // Check confidence score
    if let Some(score) = invoice.confidence_score {
        if score < 0.8 {
            warnings.push(format!("Low confidence score: {:.2}", score));
        }
    }

    warnings
}
```

### Database Storage

```rust
use sqlx::PgPool;

async fn store_invoice(pool: &PgPool, invoice: Invoice) -> Result<i64> {
    let invoice_id = sqlx::query!(
        r#"
        INSERT INTO invoices (
            invoice_number, invoice_date, vendor_name,
            total_amount, total_currency, primary_currency
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id
        "#,
        invoice.invoice_number,
        invoice.invoice_date,
        invoice.vendor.vendor_name,
        invoice.total_amount.amount,
        invoice.total_amount.currency,
        invoice.primary_currency
    )
    .fetch_one(pool)
    .await?
    .id;

    // Store line items
    for item in invoice.line_items {
        sqlx::query!(
            r#"
            INSERT INTO line_items (
                invoice_id, description, quantity, unit_price, currency, line_total
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            "#,
            invoice_id,
            item.description,
            item.quantity,
            item.unit_price,
            item.currency,
            item.line_total
        )
        .execute(pool)
        .await?;
    }

    Ok(invoice_id)
}
```

### Integration with OCR

For PDF or image invoices, use OCR preprocessing:

```rust
use tesseract::Tesseract;

async fn extract_from_pdf(pdf_path: &str) -> Result<Invoice> {
    // Convert PDF to images (using pdf2image or similar)
    let images = convert_pdf_to_images(pdf_path)?;

    // OCR each page
    let mut full_text = String::new();
    for image in images {
        let ocr_text = Tesseract::new()?
            .set_image(&image)?
            .get_text()?;
        full_text.push_str(&ocr_text);
        full_text.push_str("\n\n");
    }

    // Extract invoice data
    extract_complex_invoice(&full_text, Some("pdf")).await
}
```

## Error Handling

```rust
use baml_client::baml::functions::extract_invoice;

async fn safe_extract(invoice_text: &str) -> Result<Invoice, String> {
    match extract_invoice(invoice_text, Some("text")).await {
        Ok(invoice) => {
            // Validate critical fields
            if invoice.invoice_number.is_empty() {
                return Err("Missing invoice number".to_string());
            }
            if invoice.line_items.is_empty() {
                return Err("No line items found".to_string());
            }
            Ok(invoice)
        }
        Err(e) => Err(format!("Extraction failed: {}", e))
    }
}
```

## Performance Optimization

### Choose the right function:

```rust
async fn smart_extract(invoice_text: &str) -> Result<Invoice> {
    // Simple heuristic: if invoice mentions multiple currencies, use complex extraction
    let has_multiple_currencies = invoice_text.matches("USD").count() > 0
        && invoice_text.matches("EUR").count() > 0;

    if has_multiple_currencies || invoice_text.len() > 5000 {
        extract_complex_invoice(invoice_text, Some("text")).await
    } else {
        extract_invoice(invoice_text, Some("text")).await
    }
}
```

### Caching results:

```rust
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

struct InvoiceCache {
    cache: Arc<RwLock<HashMap<String, Invoice>>>,
}

impl InvoiceCache {
    async fn get_or_extract(&self, invoice_text: &str) -> Result<Invoice> {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        invoice_text.hash(&mut hasher);
        let key = hasher.finish().to_string();

        // Check cache
        {
            let cache = self.cache.read().await;
            if let Some(cached) = cache.get(&key) {
                return Ok(cached.clone());
            }
        }

        // Extract and cache
        let invoice = extract_invoice(invoice_text, Some("text")).await?;

        {
            let mut cache = self.cache.write().await;
            cache.insert(key, invoice.clone());
        }

        Ok(invoice)
    }
}
```

## Customization

### Add custom fields to the schema:

Edit `invoice_extraction.baml` and add to the relevant class:

```baml
class Invoice {
  // ... existing fields ...

  // Your custom fields
  department string? @description("Department code for internal accounting")
  project_code string? @description("Project or cost center code")
  approval_status string? @description("Approval workflow status")
}
```

Then regenerate:
```bash
baml generate
```

### Modify prompts for your domain:

```baml
function ExtractMedicalInvoice(invoice_content: string) -> Invoice {
  client CustomGPT5
  prompt #"
    Extract medical invoice information including procedure codes and insurance details.

    Invoice Content:
    {{ invoice_content }}

    Focus on:
    - CPT/ICD codes in line items
    - Insurance provider information
    - Patient copay amounts
    - Covered vs non-covered items

    {{ ctx.output_format }}
  "#
}
```

## Next Steps

1. **Review the full schema**: See `invoice_extraction.baml` for all fields
2. **Read design notes**: Check `DESIGN_NOTES.md` for architecture details
3. **Run tests**: Execute `baml test invoice_extraction` to verify setup
4. **Customize**: Add domain-specific fields and tests
5. **Integrate**: Use in your application with the examples above

## Support

For BAML documentation: https://docs.boundaryml.com/
For issues with this schema: Review the test cases in `invoice_extraction.baml`
