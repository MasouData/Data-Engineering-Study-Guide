# ADF Multi-Source Ingestion Design — Oracle and SAP

## Formal Interview Question

You need to ingest data from two source systems using Azure Data Factory:

- **5 source objects/files from Oracle**
- **2 source objects/files from SAP**

How many ADF pipelines would you create, and which activities would you use?

Your design should avoid unnecessary duplication and should be scalable if more source objects are added later.

---

## Interview-Ready Answer

I would **not create seven separate pipelines** just because there are seven source objects.

A good design is to use **parameterized, metadata-driven pipelines**.

### Recommended Design

I would normally create:

1. **One reusable Oracle ingestion pipeline**
2. **One reusable SAP ingestion pipeline**
3. Optionally, **one master/orchestration pipeline** that calls both child pipelines

So the design is typically:

- **2 ingestion pipelines**
- or **3 pipelines total if a master pipeline is included**

---

## Activities

For each source-specific ingestion pipeline:

```text
Lookup / Get Metadata
        ↓
     ForEach
        ↓
  Copy Activity
```

### 1. Lookup / Get Metadata

Use this to retrieve the list of source objects to process.

Examples:

```text
Oracle:
table_1
table_2
table_3
table_4
table_5
```

```text
SAP:
object_1
object_2
```

The metadata can also come from a configuration/control table.

### 2. ForEach

`ForEach` iterates over the list of source objects.

Instead of manually creating five Oracle Copy activities, the same parameterized Copy activity can run once for each Oracle object.

ADF supports sequential or parallel `ForEach` execution.

### 3. Copy Activity

The Copy activity performs the actual ingestion.

The source object/table/file name and destination can be passed as parameters.

For Oracle, ADF supports activities such as **Copy** and **Lookup** through the Oracle connector.

---

## Optional Master Pipeline

If both Oracle and SAP ingestion need to be orchestrated together, I can create:

```text
Master Pipeline
   |
   +-- Execute Pipeline → Oracle Ingestion Pipeline
   |
   +-- Execute Pipeline → SAP Ingestion Pipeline
```

The master pipeline can control:

- execution order
- parallel execution
- dependencies
- failure handling
- monitoring

---

## Why Not Seven Pipelines?

Creating one pipeline per object would lead to:

- duplicated logic
- harder maintenance
- more deployment effort
- poor scalability when new objects are added

With a metadata-driven approach, adding a new Oracle or SAP object can often mean simply adding a new metadata/configuration entry instead of creating a new pipeline.

---

## Short Interview Answer

> “I would not create seven separate pipelines. Because Oracle and SAP are different source systems, I would normally create one parameterized ingestion pipeline for Oracle and one for SAP. Each pipeline would use a Lookup or Get Metadata activity to retrieve the source-object list, a ForEach activity to iterate over it, and a parameterized Copy activity for ingestion. If I need central orchestration, I would add a master pipeline that calls both child pipelines using Execute Pipeline.”

---

## Important Nuance

The exact number of pipelines is an **architecture choice**, not a fixed rule.

If the Oracle and SAP ingestion patterns are sufficiently similar and the connector/configuration differences can be abstracted cleanly, a more generic metadata-driven framework could be built.

However, in an interview, **two reusable source-specific ingestion pipelines plus an optional master pipeline** is a clear and maintainable answer.

---

## Memory Version

**Do not create one pipeline per file/object.**

**Oracle → Lookup/Get Metadata → ForEach → Copy**

**SAP → Lookup/Get Metadata → ForEach → Copy**

**Optional Master → Execute Pipeline**

**Principle: parameterize and reuse.**

---

## References

- Microsoft Learn — ForEach activity in Azure Data Factory:  
  https://learn.microsoft.com/en-us/azure/data-factory/control-flow-for-each-activity

- Microsoft Learn — Azure Data Factory parameters:  
  https://learn.microsoft.com/en-us/azure/data-factory/frequently-asked-questions

- Microsoft Learn — Oracle connector for Azure Data Factory:  
  https://learn.microsoft.com/en-us/azure/data-factory/connector-oracle
