# Changelog

Possible log types:

- `[added]` for new features.
- `[changed]` for changes in existing functionality.
- `[deprecated]` for once-stable features removed in upcoming releases.
- `[removed]` for deprecated features removed in this release.
- `[fixed]` for any bug fixes.
- `[security]` to invite users to upgrade in case of vulnerabilities.
- `[chore]` for things like maintenance tasks


### Unnamed Release

- [added] Log of product errors to `NutritionService.test_product` (EAT-9)
- [fixed] Fix NonFoundMatching Error (EAT-9)
- [changed] Rebuild send_receipts_experimental API (EAT-9)

#### Migration notes
- Create logfile /var/log/NutritionService.log with `chmod 775` (EAT-9)
