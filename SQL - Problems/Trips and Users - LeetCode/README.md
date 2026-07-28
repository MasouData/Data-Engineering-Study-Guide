# Trips and Users - LeetCode Problem

## Problem Description

Calculate the **cancellation rate** of ride requests with unbanned users for each day between **2013-10-01** and **2013-10-03**.

---

## Table Schemas

<table>
<tr>
<td width="50%" valign="top">

### Table: `Trips`

| Column Name | Type    |
|-------------|---------|
| id          | int     |
| client_id   | int     |
| driver_id   | int     |
| city_id     | int     |
| status      | enum    |
| request_at  | varchar |

**Notes:**
* `id` is the primary key
* `client_id` and `driver_id` reference `users_id` in the Users table
* `status` values: `'completed'`, `'cancelled_by_driver'`, `'cancelled_by_client'`

</td>
<td width="50%" valign="top">

### Table: `Users`

| Column Name | Type |
|-------------|------|
| users_id    | int  |
| banned      | enum |
| role        | enum |

**Notes:**
* `users_id` is the primary key
* `banned` values: `'Yes'`, `'No'`
* `role` values: `'client'`, `'driver'`, `'partner'`

</td>
</tr>
</table>

---

## Requirements

**Objective:** Find the cancellation rate for each day between `"2013-10-01"` and `"2013-10-03"` with at least one trip.

**Rules:**
* Only include trips where **both client and driver are NOT banned**
* Cancellation rate = (Number of canceled trips) / (Total trips with unbanned users)
* Round the cancellation rate to **2 decimal places**
* Return results in any order

**Formula:**
```
Cancellation Rate = Canceled Trips (unbanned users only) / Total Trips (unbanned users only)
```

---

## Example

### Input Data

<table>
<tr>
<td width="65%" valign="top">

**Trips table:**

| id | client_id | driver_id | city_id | status              | request_at |
|----|-----------|-----------|---------|---------------------|------------|
| 1  | 1         | 10        | 1       | completed           | 2013-10-01 |
| 2  | 2         | 11        | 1       | cancelled_by_driver | 2013-10-01 |
| 3  | 3         | 12        | 6       | completed           | 2013-10-01 |
| 4  | 4         | 13        | 6       | cancelled_by_client | 2013-10-01 |
| 5  | 1         | 10        | 1       | completed           | 2013-10-02 |
| 6  | 2         | 11        | 6       | completed           | 2013-10-02 |
| 7  | 3         | 12        | 6       | completed           | 2013-10-02 |
| 8  | 2         | 12        | 12      | completed           | 2013-10-03 |
| 9  | 3         | 10        | 12      | completed           | 2013-10-03 |
| 10 | 4         | 13        | 12      | cancelled_by_driver | 2013-10-03 |

</td>
<td width="35%" valign="top">

**Users table:**

| users_id | banned | role   |
|----------|--------|--------|
| 1        | No     | client |
| 2        | Yes    | client |
| 3        | No     | client |
| 4        | No     | client |
| 10       | No     | driver |
| 11       | No     | driver |
| 12       | No     | driver |
| 13       | No     | driver |

</td>
</tr>
</table>

---

### Expected Output

| Day        | Cancellation Rate |
|------------|-------------------|
| 2013-10-01 | 0.33              |
| 2013-10-02 | 0.00              |
| 2013-10-03 | 0.50              |

---

## Explanation

### **2013-10-01:**
* Total requests: 4 (IDs: 1, 2, 3, 4)
* Request ID=2 has banned client (User_Id=2) → **excluded**
* Unbanned requests: 3 (IDs: 1, 3, 4)
* Canceled unbanned requests: 1 (ID=4)
* **Cancellation Rate = 1 / 3 = 0.33**

### **2013-10-02:**
* Total requests: 3 (IDs: 5, 6, 7)
* Request ID=6 has banned client (User_Id=2) → **excluded**
* Unbanned requests: 2 (IDs: 5, 7)
* Canceled unbanned requests: 0
* **Cancellation Rate = 0 / 2 = 0.00**

### **2013-10-03:**
* Total requests: 3 (IDs: 8, 9, 10)
* Request ID=8 has banned client (User_Id=2) → **excluded**
* Unbanned requests: 2 (IDs: 9, 10)
* Canceled unbanned requests: 1 (ID=10)
* **Cancellation Rate = 1 / 2 = 0.50**

---

## Solution

See the accompanying Databricks notebook: [solution.sql](./solution.sql)

### SQL Solution Code:

```sql
WITH valid_trips AS (
    SELECT 
        t.*,
        c.banned AS client_ban,
        d.banned AS driver_ban
    FROM Trips t
    LEFT JOIN Users as c
        ON t.client_id = c.users_id
    LEFT JOIN Users as d
        ON t.driver_id = d.users_id
),

daily_stats AS (
    SELECT 
        request_at,
        COUNT(*) AS total_count, 
        COUNT(CASE WHEN status LIKE 'cancelled%' THEN 1 END) AS cancelled_count 
    FROM valid_trips 
    WHERE client_ban = 'No' 
      AND driver_ban = 'No'
      AND request_at BETWEEN '2013-10-01' AND '2013-10-03'
    GROUP BY request_at
)

SELECT 
    request_at AS Day, 
    ROUND(cancelled_count / total_count, 2) AS `Cancellation Rate`
FROM daily_stats;
```