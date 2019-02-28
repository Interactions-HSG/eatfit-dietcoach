# Changelog

Possible log types:

- `[added]` for new features.
- `[changed]` for changes in existing functionality.
- `[deprecated]` for once-stable features removed in upcoming releases.
- `[removed]` for deprecated features removed in this release.
- `[fixed]` for any bug fixes.
- `[security]` to invite users to upgrade in case of vulnerabilities.
- `[chore]` for things like maintenance tasks

### v1 (2019-03-01)

- [fixed] Fix NonFoundMatchings Error Logging (EAT-9)
- [fixed] DigitalReceipts not stored in database (EAT-14)
- [changed] Increase API calls for `send_receipt_experimental` from 4 to 10 (EAT-13)
- [added] Add price as additional criterion to matching table