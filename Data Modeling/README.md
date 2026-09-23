# Customer–Account–Transaction Analytical Data Model

## Question

> You have **Customer**, **Account**, and **Transaction** data.  
> A customer can own multiple accounts, and an account can have multiple customers, for example a joint account.  
> If one of the joint account holders later leaves the account, how would you design the analytical data model so that you preserve the historical relationship and can still analyze past transactions correctly?

---

## Answer

I would use a **star-schema style model**.

The **Transaction** table is the **fact table**, with a grain of **one row per transaction**.  
**Customer** and **Account** are dimensions.

Because **Customer** and **Account** have a **many-to-many relationship**, I would add a **CustomerAccount bridge table**.

To preserve history when one customer leaves a joint account, the bridge table would contain:

- `StartDate`
- `EndDate`
- optionally `IsCurrent`

This lets me determine which customers were associated with the account **at the time of a transaction**.

---

## Example Data Model

### DimCustomer

| Column |
|---|
| `CustomerKey` |

### DimAccount

| Column |
|---|
| `AccountKey` |

### BridgeCustomerAccount

| Column |
|---|
| `CustomerKey` |
| `AccountKey` |
| `StartDate` |
| `EndDate` |
| `IsCurrent` |

### FactTransaction

| Column |
|---|
| `TransactionKey` |
| `AccountKey` |
| `DateKey` |
| `Amount` |

---

## Example: Customer B Leaves a Joint Account

| Customer | Account | StartDate | EndDate | Status |
|---|---|---|---|---|
| Customer A | Account 100 | 2025-01-01 | 9999-12-31 | Current |
| Customer B | Account 100 | 2025-01-01 | 2026-06-30 | Not Current |

With this design, a transaction dated before **2026-06-30** can still be analyzed with the knowledge that both Customer A and Customer B were associated with Account 100 at that time.

---

## Important Nuance

If a transaction belongs to the **account**, I would **not automatically put both joint customers into the transaction fact table**, because that could duplicate the transaction amount.

Instead:

1. Store the transaction once in `FactTransaction`.
2. Connect the transaction to the account using `AccountKey`.
3. Use `BridgeCustomerAccount` together with `StartDate` and `EndDate` to determine which customers owned the account at the transaction date.

This avoids double-counting while preserving the historical ownership relationship.

Microsoft's Power BI guidance uses essentially this same **Customer–Account–Transaction** many-to-many scenario and recommends a bridge table between Customer and Account.

Source: [Microsoft Learn — Many-to-many relationship guidance](https://learn.microsoft.com/en-us/power-bi/guidance/relationships-many-to-many)

---

## Memory Sentence

> **FactTransaction = one transaction; Customer + Account = dimensions; joint ownership = bridge table; ownership history = StartDate/EndDate.**
