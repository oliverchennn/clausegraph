## Behavior

Describe the concrete problem and resulting behavior.

## Ownership and dependency

- Lane: dev-a / dev-b
- Contributor: A / B / C (C's delegated UI fixes use dev-b, with a c- task prefix)
- Task handoff link:
- Starting main commit:
- Required merged contract commit (or none):
- For a C patch: committed A assignment and B path-release links, exact allowed files, prerequisite merge, release expiry/stop condition (otherwise not applicable):

## Validation

List exact commands/results and limitations; distinguish fixture tests from live validation.

## Review

- [ ] Fresh task branch; current main incorporated; no out-of-lane edits.
- [ ] Own task handoff updated; shared docs consolidated by A only.
- [ ] Reviewer recorded; all checks green before A merges.

C's additional review is optional; A/B work and merges never wait for it. C patches require A review under the existing B-lane rule. If B reclaims a file, C preserves its work and hands back the optional patch.
