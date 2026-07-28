# Databricks notebook source
# MAGIC %md
# MAGIC # Trips and Users - LeetCode Problem
# MAGIC
# MAGIC ## Problem Description
# MAGIC
# MAGIC Calculate the **cancellation rate** of ride requests with unbanned users for each day between **2013-10-01** and **2013-10-03**.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Table Schemas
# MAGIC
# MAGIC ### Table: `Trips`
# MAGIC
# MAGIC | Column Name | Type    | Description |
# MAGIC |-------------|---------|-------------|
# MAGIC | id          | int     | Primary key - unique trip ID |
# MAGIC | client_id   | int     | Foreign key to Users table |
# MAGIC | driver_id   | int     | Foreign key to Users table |
# MAGIC | city_id     | int     | City identifier |
# MAGIC | status      | enum    | Trip status: `'completed'`, `'cancelled_by_driver'`, `'cancelled_by_client'` |
# MAGIC | request_at  | varchar | Request date |
# MAGIC
# MAGIC **Notes:**
# MAGIC * `id` is the primary key
# MAGIC * `client_id` and `driver_id` reference `users_id` in the Users table
# MAGIC * `status` is an ENUM with values: `'completed'`, `'cancelled_by_driver'`, `'cancelled_by_client'`
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Table: `Users`
# MAGIC
# MAGIC | Column Name | Type | Description |
# MAGIC |-------------|------|-------------|
# MAGIC | users_id    | int  | Primary key - unique user ID |
# MAGIC | banned      | enum | User ban status: `'Yes'`, `'No'` |
# MAGIC | role        | enum | User role: `'client'`, `'driver'`, `'partner'` |
# MAGIC
# MAGIC **Notes:**
# MAGIC * `users_id` is the primary key
# MAGIC * `banned` is an ENUM: `'Yes'`, `'No'`
# MAGIC * `role` is an ENUM: `'client'`, `'driver'`, `'partner'`
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Requirements
# MAGIC
# MAGIC **Objective:** Find the cancellation rate for each day between `"2013-10-01"` and `"2013-10-03"` with at least one trip.
# MAGIC
# MAGIC **Rules:**
# MAGIC * Only include trips where **both client and driver are NOT banned**
# MAGIC * Cancellation rate = (Number of canceled trips) / (Total trips with unbanned users)
# MAGIC * Round the cancellation rate to **2 decimal places**
# MAGIC * Return results in any order
# MAGIC
# MAGIC **Formula:**
# MAGIC ```
# MAGIC Cancellation Rate = Canceled Trips (unbanned users only) / Total Trips (unbanned users only)
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Example
# MAGIC
# MAGIC ### Input Data
# MAGIC
# MAGIC **Trips table:**
# MAGIC
# MAGIC | id | client_id | driver_id | city_id | status              | request_at |
# MAGIC |----|-----------|-----------|---------|---------------------|------------|
# MAGIC | 1  | 1         | 10        | 1       | completed           | 2013-10-01 |
# MAGIC | 2  | 2         | 11        | 1       | cancelled_by_driver | 2013-10-01 |
# MAGIC | 3  | 3         | 12        | 6       | completed           | 2013-10-01 |
# MAGIC | 4  | 4         | 13        | 6       | cancelled_by_client | 2013-10-01 |
# MAGIC | 5  | 1         | 10        | 1       | completed           | 2013-10-02 |
# MAGIC | 6  | 2         | 11        | 6       | completed           | 2013-10-02 |
# MAGIC | 7  | 3         | 12        | 6       | completed           | 2013-10-02 |
# MAGIC | 8  | 2         | 12        | 12      | completed           | 2013-10-03 |
# MAGIC | 9  | 3         | 10        | 12      | completed           | 2013-10-03 |
# MAGIC | 10 | 4         | 13        | 12      | cancelled_by_driver | 2013-10-03 |
# MAGIC
# MAGIC **Users table:**
# MAGIC
# MAGIC | users_id | banned | role   |
# MAGIC |----------|--------|--------|
# MAGIC | 1        | No     | client |
# MAGIC | 2        | Yes    | client |
# MAGIC | 3        | No     | client |
# MAGIC | 4        | No     | client |
# MAGIC | 10       | No     | driver |
# MAGIC | 11       | No     | driver |
# MAGIC | 12       | No     | driver |
# MAGIC | 13       | No     | driver |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Expected Output
# MAGIC
# MAGIC | Day        | Cancellation Rate |
# MAGIC |------------|-------------------|
# MAGIC | 2013-10-01 | 0.33              |
# MAGIC | 2013-10-02 | 0.00              |
# MAGIC | 2013-10-03 | 0.50              |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Explanation
# MAGIC
# MAGIC ### **2013-10-01:**
# MAGIC * Total requests: 4 (IDs: 1, 2, 3, 4)
# MAGIC * Request ID=2 has banned client (User_Id=2) → **excluded**
# MAGIC * Unbanned requests: 3 (IDs: 1, 3, 4)
# MAGIC * Canceled unbanned requests: 1 (ID=4)
# MAGIC * **Cancellation Rate = 1 / 3 = 0.33**
# MAGIC
# MAGIC ### **2013-10-02:**
# MAGIC * Total requests: 3 (IDs: 5, 6, 7)
# MAGIC * Request ID=6 has banned client (User_Id=2) → **excluded**
# MAGIC * Unbanned requests: 2 (IDs: 5, 7)
# MAGIC * Canceled unbanned requests: 0
# MAGIC * **Cancellation Rate = 0 / 2 = 0.00**
# MAGIC
# MAGIC ### **2013-10-03:**
# MAGIC * Total requests: 3 (IDs: 8, 9, 10)
# MAGIC * Request ID=8 has banned client (User_Id=2) → **excluded**
# MAGIC * Unbanned requests: 2 (IDs: 9, 10)
# MAGIC * Canceled unbanned requests: 1 (ID=10)
# MAGIC * **Cancellation Rate = 1 / 2 = 0.50**

# COMMAND ----------

# DBTITLE 1,Solution
# MAGIC %sql
# MAGIC WITH valid_trips AS (
# MAGIC     SELECT 
# MAGIC         t.*,
# MAGIC         c.banned AS client_ban,
# MAGIC         d.banned AS driver_ban
# MAGIC     FROM Trips t
# MAGIC     LEFT JOIN Users as c
# MAGIC         ON t.client_id = c.users_id
# MAGIC     LEFT JOIN Users as d
# MAGIC         ON t.driver_id = d.users_id
# MAGIC ),
# MAGIC
# MAGIC daily_stats AS (
# MAGIC     SELECT 
# MAGIC         request_at,
# MAGIC         COUNT(*) AS total_count, 
# MAGIC         COUNT(CASE WHEN status LIKE 'cancelled%' THEN 1 END) AS cancelled_count 
# MAGIC     FROM valid_trips 
# MAGIC     WHERE client_ban = 'No' 
# MAGIC       AND driver_ban = 'No'
# MAGIC       AND request_at BETWEEN '2013-10-01' AND '2013-10-03'
# MAGIC     GROUP BY request_at
# MAGIC )
# MAGIC
# MAGIC SELECT 
# MAGIC     request_at AS Day, 
# MAGIC     ROUND(cancelled_count / total_count, 2) AS `Cancellation Rate`
# MAGIC FROM daily_stats;

# COMMAND ----------

