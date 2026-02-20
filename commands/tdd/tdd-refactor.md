---
argument-hint: [code_to_refactor]
description: Safe, test-driven refactoring with incremental improvements
---

# TDD-Safe Refactoring Agent

Refactor code systematically while maintaining 100% green test coverage throughout the process.

## Pre-Flight Check

Verify working directory and test baseline:

```bash
pwd
```

## Execution

Use Task tool with `subagent_type="tdd-orchestrator"` and provide this prompt:

"Apply TDD refactoring to: $ARGUMENTS

Follow the Red-Green-Refactor safety protocol with incremental changes."

## Core Protocol

### Phase 1: Establish Baseline
**Before any changes:**
- Run full test suite → confirm 100% green
- Document current test coverage percentage
- Capture baseline performance metrics (if applicable)
- Identify code smells and prioritize targets

**Stop here if tests aren't green** → fix failing tests first

### Phase 2: Plan Refactoring
Create step-by-step plan before executing:
- List specific code smells detected
- Order changes from safest to riskiest
- Define success criteria for each step
- Identify rollback points

**Review plan before proceeding**

### Phase 3: Incremental Refactoring
**For each refactoring step:**
1. Make ONE atomic change
2. Run affected tests immediately
3. If tests fail → revert and adjust approach
4. If tests pass → commit and proceed
5. Run full suite every 3-5 changes

**Never batch multiple refactorings** → one change per cycle

### Phase 4: Verify & Document
- Final full test suite run
- Compare before/after metrics
- Document improvements made
- Note remaining technical debt

## Code Smell Catalog

### Structural Issues
- **Duplicated Code** → Extract method/class/module
- **Long Method** (>20 lines) → Decompose into smaller functions
- **Large Class** (>300 lines) → Split by responsibility
- **Long Parameter List** (>3 params) → Parameter object/builder
- **Dead Code** → Remove unused methods/variables

### Design Issues  
- **Feature Envy** → Move method to data owner
- **Primitive Obsession** → Create value objects
- **Switch Statements** → Replace with polymorphism/strategy
- **Data Clumps** → Group into cohesive objects
- **Message Chains** → Introduce intermediate method

### Naming Issues
- **Unclear Names** → Rename for clarity and intent
- **Magic Numbers** → Named constants
- **Inconsistent Naming** → Follow project conventions

## Design Patterns (Apply Judiciously)

Only introduce patterns that solve actual problems in the code.

**Creational:**
- Factory: Complex object creation logic
- Builder: Objects with many optional parameters
- Singleton: Truly shared global state (use sparingly)

**Structural:**
- Adapter: Interface compatibility
- Facade: Simplify complex subsystem
- Decorator: Add behavior dynamically

**Behavioral:**
- Strategy: Swap algorithms at runtime
- Observer: Event-driven decoupling
- Command: Encapsulate operations as objects

**Domain-Driven:**
- Repository: Data access abstraction
- Service: Business logic orchestration
- Value Object: Immutable domain concepts

## SOLID Principles Checklist

- [ ] **Single Responsibility:** Each class has one reason to change
- [ ] **Open/Closed:** Extend behavior without modifying existing code
- [ ] **Liskov Substitution:** Subtypes are truly interchangeable
- [ ] **Interface Segregation:** Clients depend on minimal interfaces
- [ ] **Dependency Inversion:** Depend on abstractions, not concrete implementations

## Safety Rules

**MUST follow:**
1. Tests green before starting → tests green after each step
2. One refactoring technique per cycle
3. No behavior changes during refactoring
4. Revert immediately on test failure
5. Commit after each successful change

**NEVER:**
- Skip test runs to save time
- Combine refactoring with new features
- Assume tests cover edge cases without verification
- Make large structural changes in one step

## Output Format

Provide structured results:

### Changes Made
- List each refactoring applied with file:line references
- Pattern/technique used per change

### Test Results
```
✓ All tests passing (X/X)
✓ Coverage: X% (baseline) → Y% (current)
✓ Performance: [metric comparison if measured]
```

### Code Quality Metrics
- Cyclomatic complexity: Before → After
- Lines of code: Before → After
- Duplication percentage: Before → After

### Remaining Improvements
- Prioritized list of unaddressed code smells
- Estimated effort for each

## Recovery Protocol

**If tests fail during refactoring:**
1. Immediately revert last change
2. Run tests to confirm green state restored
3. Analyze why refactoring broke tests
4. Split change into smaller steps or adjust approach
5. Never proceed with broken tests

## Example: Practical Refactoring

**Before** (violates SRP, has duplication):
```typescript
class OrderProcessor {
  processOrder(order: Order): ProcessResult {
    // Validation inline
    if (!order.customerId || order.items.length === 0) {
      return { success: false, error: "Invalid order" };
    }

    // Calculation inline
    let subtotal = 0;
    for (const item of order.items) {
      subtotal += item.price * item.quantity;
    }
    const tax = subtotal * 0.08;
    const shipping = subtotal > 100 ? 0 : 15;
    const total = subtotal + tax + shipping;

    // Side effects scattered
    this.chargePayment(order.payment, total);
    this.updateInventory(order.items);
    this.sendEmail(order.customerEmail, total);
    
    return { success: true, orderId: order.id };
  }
}
```

**After** (Step 1: Extract validation):
```typescript
class OrderProcessor {
  processOrder(order: Order): ProcessResult {
    const validation = this.validateOrder(order);
    if (!validation.isValid) {
      return ProcessResult.failure(validation.error);
    }

    let subtotal = 0;
    for (const item of order.items) {
      subtotal += item.price * item.quantity;
    }
    const tax = subtotal * 0.08;
    const shipping = subtotal > 100 ? 0 : 15;
    const total = subtotal + tax + shipping;

    this.chargePayment(order.payment, total);
    this.updateInventory(order.items);
    this.sendEmail(order.customerEmail, total);
    
    return ProcessResult.success(order.id);
  }

  private validateOrder(order: Order): ValidationResult {
    if (!order.customerId) {
      return ValidationResult.invalid("Customer ID required");
    }
    if (order.items.length === 0) {
      return ValidationResult.invalid("Order must contain items");
    }
    return ValidationResult.valid();
  }
}
```

**Run tests** ✓ Green

**After** (Step 2: Extract calculation to value object):
```typescript
class OrderProcessor {
  processOrder(order: Order): ProcessResult {
    const validation = this.validateOrder(order);
    if (!validation.isValid) {
      return ProcessResult.failure(validation.error);
    }

    const pricing = OrderPricing.calculate(order.items);

    this.chargePayment(order.payment, pricing.total);
    this.updateInventory(order.items);
    this.sendEmail(order.customerEmail, pricing.total);
    
    return ProcessResult.success(order.id);
  }

  private validateOrder(order: Order): ValidationResult { /* ... */ }
}

class OrderPricing {
  constructor(
    public readonly subtotal: number,
    public readonly tax: number,
    public readonly shipping: number
  ) {}

  get total(): number {
    return this.subtotal + this.tax + this.shipping;
  }

  static calculate(items: OrderItem[]): OrderPricing {
    const subtotal = items.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    );
    const tax = subtotal * 0.08;
    const shipping = subtotal > 100 ? 0 : 15;
    return new OrderPricing(subtotal, tax, shipping);
  }
}
```

**Run tests** ✓ Green

**After** (Step 3: Inject dependencies):
```typescript
class OrderProcessor {
  constructor(
    private readonly paymentService: PaymentService,
    private readonly inventoryService: InventoryService,
    private readonly notificationService: NotificationService
  ) {}

  async processOrder(order: Order): Promise<ProcessResult> {
    const validation = this.validateOrder(order);
    if (!validation.isValid) {
      return ProcessResult.failure(validation.error);
    }

    const pricing = OrderPricing.calculate(order.items);

    await this.paymentService.charge(order.payment, pricing.total);
    await this.inventoryService.reserve(order.items);
    await this.notificationService.sendConfirmation(
      order.customerEmail,
      order,
      pricing
    );
    
    return ProcessResult.success(order.id);
  }

  private validateOrder(order: Order): ValidationResult { /* ... */ }
}
```

**Run tests** ✓ Green → **Refactoring Complete**

**Applied techniques:**
- Extract Method (validation)
- Value Object (OrderPricing)
- Dependency Injection (services)
- Single Responsibility Principle
- Async/await for side effects

---

**Code to refactor:** $ARGUMENTS
