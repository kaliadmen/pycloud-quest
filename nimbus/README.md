# nimbus/

The cloud itself. It starts empty and grows one lesson at a time.

## Graduation rule
When a lesson is done (code works, bugs fixed, challenges pass, notes reviewed), its reusable code is
copied here, cleaned up, and given tests in `nimbus/<area>/tests/`. From then on, later lessons import
from `nimbus.*` instead of the lesson folder. Reusing your own old code is spaced review built into the work.

| Area | Comes from | Status |
|---|---|---|
| `nimbus/storage/` | L01 blob store, later L16 object storage | waiting for L01 |
| `nimbus/log/` | L02 structured logging | not started |
| `nimbus/models/` | L03 resource models | not started |
| `nimbus/api/` | L11 control plane API | not started |
| `nimbus/iam/` | L13 identity, L14 policy engine | not started |
| `nimbus/audit/` | L15 audit trail | not started |
| `nimbus/compute/` | L17 compute, L18 node agent + scheduler | not started |
| `nimbus/net/` | L19 virtual networking | not started |
| `nimbus/kms/` | L20 secrets manager | not started |
| `nimbus/observe/` | L22 to L25 logs, metrics, detections | not started |
