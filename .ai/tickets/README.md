# Tickets Directory

* `TODO/`: Queued tasks ready for assignment.
* `IN_PROGRESS/`: Currently active task being executed. Only ONE active ticket at a time.
* `DONE/`: Completed tasks with deliverables, verification results, and commit hashes recorded.

## Ticket Lifecycle
1. Master Agent moves ticket from `TODO/` to `IN_PROGRESS/`.
2. Assigned agent executes the ticket strictly according to acceptance criteria.
3. Tests are executed and verified.
4. Assigned agent updates ticket with implementation notes.
5. Master Agent reviews, commits changes to Git, and moves ticket to `DONE/`.
