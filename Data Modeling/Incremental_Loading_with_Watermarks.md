#Incremental Loading with Watermarks

## Interview Question

You have a `customer` table:

```text
customer
---------
id
create_date
update_date
```

You see the following query used for incremental loading:

```sql
SELECT *
FROM customer
WHERE update_date > '2026-01-23';
```

There is no important syntax issue for the purpose of this question.

**What is the design problem with this approach, and how would you implement a scalable watermark-based incremental load?**

As a follow-up:

- How do you determine the **old watermark** and the **new watermark**?
- Why should you avoid scanning a very large source table unnecessarily?
- What changes if the table is partitioned?
- How would you handle **late-arriving data**?

---

## Interview-Ready Answer

The main problem is that `'2026-01-23'` is a **hard-coded cutoff**. In a production incremental pipeline, I would use a **watermark-based approach**.

### 1. Old watermark

The **old watermark** is normally read from a **control/watermark table**. It is the high-watermark value saved after the **previous successful pipeline run**.

For example:

```text
WatermarkControl
----------------
TableName   WatermarkValue
customer    2026-01-23 10:00:00
```

I do **not** recompute the old watermark from the whole source table on every run.

---

### 2. New watermark

The **new watermark** represents the upper boundary for the current run.

A simple implementation can obtain it with:

```sql
SELECT MAX(update_date)
FROM customer;
```

However, on a very large table this may be expensive because it can require scanning a large amount of data.

For a large **partitioned** table, I would restrict the query to the **relevant partition or range** so the database can prune unnecessary partitions and avoid a full-table scan.

---

### 3. Incremental extraction

Then I copy only rows between the two watermark values:

```sql
SELECT *
FROM customer
WHERE update_date > @OldWatermark
  AND update_date <= @NewWatermark;
```

After the copy and downstream processing succeed, I update the control table:

```text
Old watermark for next run = current NewWatermark
```

The watermark should be advanced **only after a successful run**, so a failed run does not cause records to be skipped.

---

## First Run

For the first execution, initialize the watermark with an agreed starting value, for example:

```text
2010-01-01 00:00:00
```

or another business-defined historical starting point.

---

## Large / Partitioned Tables

For a large source table:

> **Do not repeatedly calculate the high watermark by scanning the entire table if you can avoid it.**

Instead:

1. Read the old watermark from the control table.
2. Identify the relevant date/key partition or bounded range.
3. Calculate or select the new high watermark within that range.
4. Read only rows between the old and new watermark.
5. Update the control table after success.

This improves scalability through **partition pruning / bounded reads**.

---

## Late-Arriving Data

A strict timestamp watermark can miss records that arrive late with an `update_date` older than the current watermark.

Possible solutions include:

- using a small **look-back / overlap window** and deduplicating on load,
- using **CDC / Change Tracking** when available,
- or using another reliable monotonically increasing change column.

Example:

```text
Stored watermark = 2026-01-23 10:00
Look back 10 minutes
Read again from 2026-01-23 09:50
Deduplicate/upsert at the target
```

---

## Short Interview Answer

> “The problem is the hard-coded date. I would store the previous successful watermark in a control table, determine a new high watermark for the current run, and load only records where `update_date` is between those two values. For a very large partitioned table, I would restrict the high-watermark lookup and extraction to the relevant partition or range instead of scanning the whole table. I would update the stored watermark only after a successful run, and for late-arriving data I would use a look-back window with deduplication or CDC.”

---

## Memory Version

**Old watermark = previous successful high watermark**

**New watermark = current upper boundary**

**Load = `old < update_date <= new`**

**After success = save new watermark**

**Large table = use partition/range pruning**

**Late arrival = look-back + dedup, or CDC**

---

## References

- Microsoft Learn — Incrementally copy a table using Azure Data Factory:  
  https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-portal

- Microsoft Learn — Incrementally copy multiple tables using Azure Data Factory:  
  https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-multiple-tables-portal

- Microsoft Learn — Incremental loading overview:  
  https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-overview

- Microsoft Learn — Watermark-based incremental copy in Fabric Data Factory:  
  https://learn.microsoft.com/en-us/fabric/data-factory/incremental-copy-job
