# Database notes

The initial schema includes categories, members, equipment, loans, incidents
and maintenance records. `equipment.uuid` is generated once and used in QR
payloads (`DCM:<uuid>`).

An active loan is a row where `returned_at IS NULL`. A partial unique index
prevents more than one active loan per equipment item on PostgreSQL and SQLite.
Checkout and return operations update loan and equipment state in one database
transaction.

Before live use, add audit events, actor identity, incident creation/clearance
workflow, backup automation and restore tests.
