---
domain: AxiomaFlowDomain
related_domains:
  - AxiomRegistry
  - AppSpecification
---

CONSTRAINTS:
- All mutations in Axioma Flow must preserve functorial reversibility ([L1-002]).
- Decoupled persistence is strictly mandatory across Boundary 3 ([L1-011_3]).
- All lossy deletions must formally account for Landauer bit erasure ([L1-008]).
- Inter-subsystem requests must be validated against Noun schemas and Verb FSMs ([L1-015]).
- Edge cases that suspend invariants must be isolated in demarcated enclaves ([L1-016]).

GLOSSARY:
- Axioma Flow: Non-generator production software compiled by System G_1.
- Invariant Blast Radius: Contained scope of an exception enclave.

# ENTITY: Task
MUST HAVE:
- id: str (Required)
- title: str (Required)
- description: str (Optional)
- status: str (Required)
- priority: str (Required)
- created_at: float (Required)
