# Consequence walkthrough — implemented synthetic presenter segment

This segment uses the original six-document synthetic example. It performs no cancellation, payment, application, message or provider call. Every amount and date shown in the walkthrough comes from the deterministic preview response.

## Proposed 35-second beat

1. On **Your next moves**, find **Cancel phone service**. Its card already warns about the hidden consequence. Press **Compare option alone**.
2. The side-by-side preview shows the recorded plan still at a $50 minimum/$500 ending balance and the cancellation-only preview at a -$820 minimum/$80 ending balance. The saved plan and history remain unchanged.
3. In **Follow this option from clause to cash**, move through Source, Reviewed rule, Dependency, Proposed effect and Cash consequence. The statuses keep evidence support, human review and third-party approval separate.
4. Open exact evidence. The synthetic phone contract says the $60 service payment is removed and the existing $480 device balance becomes due on cancellation. Close the drawer and highlight the linked dependency graph.
5. On Proposed effect, show the returned `remove` and `accelerate` changes: the phone charge disappears; the same device obligation moves from November 20 to September 1. It is not duplicated, forgiven or newly created.
6. On Cash consequence, show the server-returned comparison and the change in beyond-horizon obligations. Say: “Removing one charge can still make cash worse when another existing debt moves earlier. This is a read-only preview, not advice to cancel.”

The 35-second budget is proposed, not a measured spoken run. Do not call the $60 removal savings without also showing the accelerated $480 debt and resulting ledger. Do not describe -$820 as a robust worst case; it is the nominal action-only preview under the saved assumptions.

## Blocked-action fallback

If the presenter selects **Check emergency assistance eligibility**, the walkthrough shows the pending-approval blocker and withholds action-specific cash. The generic comparison may still show the unchanged ledger, but the walkthrough explicitly refuses to attribute that cash to the blocked claim. Open its source if useful; cash cannot create approval or evidence.

## Recovery

- If the comparison reports a stale plan/workspace, close it, wait for the current plan, and retry. Never reuse the old preview.
- If the browser is unavailable, use the already-tested synthetic source/trace values as a **previously computed result**, not a live run.
- If the graph is cramped, stay in the walkthrough's mobile list; every step and evidence control remains keyboard accessible.
- Keep the original saved plan unless the judge explicitly asks to demonstrate the existing **Use this preview as plan** control. That control recalculates and still executes nothing externally.
