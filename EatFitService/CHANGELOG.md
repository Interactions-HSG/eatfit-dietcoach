# Changelog

Possible log types:

- `[added]` for new features.
- `[changed]` for changes in existing functionality.
- `[deprecated]` for once-stable features removed in upcoming releases.
- `[removed]` for deprecated features removed in this release.
- `[fixed]` for any bug fixes.
- `[security]` to invite users to upgrade in case of vulnerabilities.
- `[chore]` for things like maintenance tasks

### v4 (2019-04-01)

- [added] New tables to NutritionDB (EAT-7)
- [added] Implement allergens import logic (EAT-8)
- [removed] Remove unused media_bkp and static_bkp files from server (EAT-20)
- [added] Add wait-for-it-container to docker-compose (EAT-23)
- [fixed] Digital receipts not saved to DB (EAT-24)
- [fixed] Fix broken migrations (EAT-25)
- [added] Add docker-compose/Docker config for local development (EAT-26)
- [added] Nutrients import Logic (EAT-27)
- [added] Products import Logic (EAT-28)
- [added] Add logging model for data import (EAT-29)
- [added] Add py.test pipeline config (EAT-30)
- [added] SSIM tests and bugfix (EAT-31)
- [changed] Mock image download get request in tests (EAT-32)
- [added] Add bootstrap styling to Import Views (EAT-35)
- [fixed] Handle server timeout issue when uploading large csv files (EAT-36)
- [added] Write test to check authorization for all existing views (EAT-37)
- [added] Add RabbitMQ server and Celery worker to docker-compose (EAT-38)
- [added] Add English, French and Italian product names to Product import logic (EAT-42)
- [removed] Remove product id from csv as database query argument in products import logic (EAT-43)
- [changed] Asynchronous allergen import logic (EAT-44)
- [added] Asynchronous nutrient import logic (EAT-45)
- [added] Asynchronous product import logic (EAT-46)
- [changed] Migrate docker image from jessie to stretch (EAT-48)

### v3 (2019-03-05)

- [fixed] NoneType and ValueType error on product_size_unit_of_measure (EAT-22)
- [added] Azure application insights integration (EAT-11)

### v2 (2019-03-04)

- [changed] Transfer storage to Azure Blob (EAT-12)
- [fixed] Fix crash when matching not specified in Product (EAT-18)
- [added] Log all exceptions to logfile (EAT-19)

### v1 (2019-03-01)

- [fixed] Fix NonFoundMatchings Error Logging (EAT-9)
- [fixed] DigitalReceipts not stored in database (EAT-14)
- [changed] Increase API calls for `send_receipt_experimental` from 4 to 10 (EAT-13)

