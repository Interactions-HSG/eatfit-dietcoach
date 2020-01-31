# Changelog

Possible log types:

- `[added]` for new features.
- `[changed]` for changes in existing functionality.
- `[deprecated]` for once-stable features removed in upcoming releases.
- `[removed]` for deprecated features removed in this release.
- `[fixed]` for any bug fixes.
- `[security]` to invite users to upgrade in case of vulnerabilities.
- `[chore]` for things like maintenance tasks

### unreleased (2019-01-31)

- [fixed] Fix wrong r2n_partner key in send-receipts API view
- [fixed] Fix middleware bug with applicationinsights

### v13 (2019-12-22)
- [changed] Rebuild SendReceipts view and refactor on basis of send_receipts_experimental (EAT-92)
- [changed] Update Python from 2.7.16 to 3.6.9 (EAT-93)

### v12 (2019-10-17)
- [changed] Change non-editable fields on Product to read-only fields in admin view (EAT-86)
- [added] Add calculation for nutri_score_final on Product model (EAT-88)
- [added] Add `nutri_score_final` as field to ProductSerializer (EAT-89)
- [added] Create `NutriScoreFactsSerializer` and add `nutri_score_facts` as field to `ProductSerializer` (EAT-90)
- [changed] Change FVPN value target field to `fvpn_total_percentage_estimated` (EAT-91)
- [changed] No more automatic estimation of product Nutri-score category (EAT-91)

### v11 (2019-10-08)

- [added] Add new fields for Nutri-Score categories and scores in Product model (EAT-78)
- [added] Add new fields for Nutri-Score categories in MinorCategory model (EAT-79)
- [added] New model NutriScoreFacts added (EAT-80)
- [added] New calculation scheme and integration tests for Ofcom values and Nutri-Scores (EAT-81)
- [changed] Adjusted tests to run correctly under new calculations (EAT-81)
- [added] Tests for various elements of Nutri-score/Ofcom calculations (EAT-82, EAT-83, EAT-84, EAT-85)

### v10 (2019-09-09)

- [changed] Trustbox importer should only import data which has a base unit of measure in grams and a base amount of 100 (EAT-77)

### v9 (2019-08-27)

- [changed] Make Openfood updater more strict by enforcing a higher data quality score (EAT-73)
- [changed] Trustbox importer should only update Products which allow automatic updates (EAT-74)
- [added] Add parameters for market region and retailer to better products endpoint (EAT-75)
- [fixed] Fix duplicate error when also querying for major categories in better products endpoint (EAT-75)

### v8 (2019-08-20)

- [added] Display Ingredients models in Product model admin view (EAT-67)
- [added] Display Additional Images in Product model admin view (EAT-68)
- [added] Add new fields to NutritionFact model to indicate pre -vs. post-processing of food item (EAT-69)
- [fixed] Fix TrustBox importer (EAT-70)
- [fixed] Fix OpenFood importer to handle duplicate GTIN cases (EAT-71)

### v7 (2019-05-10)

- [changed] Change default behavior of Allergen Model (EAT-55)
- [added] Backup data from DB (EAT-55)
- [fixed] Fix Allergens in production database (EAT-55)

### v6 (2019-04-05)

- [changed] Rebuild Retailer and MarketRegion Models (EAT-50)
- [added] Extend product import to retailers and market_regions (EAT-54)

### v5 (2019-04-03)

- [changed] Rebuild Retailer and Allergen models (EAT-50)

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

