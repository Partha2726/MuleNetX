"""Every Cypher statement used by the application (SRS §6.8.5, SR-07).

All statements are parameterized; labels, relationship types and property names come from the allow-list
below and are written literally — no Cypher is assembled from request input. Every statement is scoped by
`$sid` (the snapshot ID).
"""

from __future__ import annotations

from typing import Final

LABELS: Final[frozenset[str]] = frozenset({"Account", "Transaction"})
RELATIONSHIPS: Final[frozenset[str]] = frozenset({"SENDS", "RECEIVED_BY", "TRANSFERRED_TO"})

MERGE_ACCOUNTS: Final[str] = """
UNWIND $rows AS row
MERGE (a:Account {snapshot_key: row.key})
ON CREATE SET a.snapshot_id = $sid, a.account_id = row.account_id, a.dataset_id = $dataset_id,
              a.account_type = row.account_type
"""

MERGE_TRANSACTIONS: Final[str] = """
UNWIND $rows AS row
MERGE (t:Transaction {snapshot_key: row.key})
ON CREATE SET t.snapshot_id = $sid, t.transaction_id = row.transaction_id, t.amount = row.amount,
              t.amount_micros = row.amount_micros, t.timestamp = row.timestamp,
              t.transaction_type = row.transaction_type
WITH t, row
MATCH (src:Account {snapshot_key: row.source_key})
MATCH (dst:Account {snapshot_key: row.destination_key})
MERGE (src)-[:SENDS]->(t)
MERGE (t)-[:RECEIVED_BY]->(dst)
"""

MERGE_TRANSFERS: Final[str] = """
UNWIND $keys AS key
MATCH (a:Account {snapshot_key: key})-[:SENDS]->(t:Transaction)-[:RECEIVED_BY]->(b:Account)
WITH a, b, count(t) AS tx_count, sum(t.amount_micros) AS micros, min(t.timestamp) AS first_ts,
     max(t.timestamp) AS last_ts
MERGE (a)-[r:TRANSFERRED_TO {snapshot_id: $sid}]->(b)
SET r.tx_count = tx_count, r.total_amount_micros = micros, r.total_amount = toFloat(micros) / 1000000.0,
    r.first_ts = first_ts, r.last_ts = last_ts
"""

COUNT_ACCOUNTS: Final[str] = "MATCH (a:Account {snapshot_id: $sid}) RETURN count(a) AS n"
COUNT_TRANSACTIONS: Final[str] = "MATCH (t:Transaction {snapshot_id: $sid}) RETURN count(t) AS n"
TRANSFER_TOTALS: Final[str] = """
MATCH (a:Account {snapshot_id: $sid})-[r:TRANSFERRED_TO]->(:Account)
RETURN count(r) AS n, coalesce(sum(r.total_amount_micros), 0) AS micros
"""
TRANSACTION_IDS: Final[str] = "MATCH (t:Transaction {snapshot_id: $sid}) RETURN t.transaction_id AS id"

DELETE_TRANSACTIONS_BATCH: Final[str] = """
MATCH (t:Transaction {snapshot_id: $sid})
WITH t LIMIT $batch
DETACH DELETE t
RETURN count(*) AS n
"""
DELETE_ACCOUNTS_BATCH: Final[str] = """
MATCH (a:Account {snapshot_id: $sid})
WITH a LIMIT $batch
DETACH DELETE a
RETURN count(*) AS n
"""
