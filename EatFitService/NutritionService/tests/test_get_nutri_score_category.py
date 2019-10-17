from model_mommy import mommy
import pytest

from NutritionService.models import ADDED_FAT, BEVERAGE, MINERAL_WATER, FOOD, ErrorLog, Product, MinorCategory, \
    MajorCategory


@pytest.mark.django_db
def test_no_minor_category_no_product_nsc():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    test_product = mommy.make(Product)

    assert Product.objects.count() == 1
    assert test_product.minor_category is None
    assert ErrorLog.objects.count() == 1
    assert test_product.nutri_score_category_estimated is None


@pytest.mark.django_db
def test_no_minor_category_product_nsc():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    test_product = mommy.make(Product, nutri_score_category_estimated=MINERAL_WATER)

    assert Product.objects.count() == 1
    assert test_product.minor_category is None
    assert ErrorLog.objects.count() == 1
    assert test_product.nutri_score_category_estimated == MINERAL_WATER


@pytest.mark.django_db
def test_no_minor_category_nsc_no_product_nsc():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category)

    test_product = mommy.make(Product, minor_category=minor_category)

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 1
    assert test_product.minor_category.nutri_score_category is None
    assert ErrorLog.objects.count() == 1
    assert test_product.nutri_score_category_estimated is None


@pytest.mark.django_db
def test_no_minor_category_nsc_product_nsc():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category)

    test_product = mommy.make(Product, minor_category=minor_category, nutri_score_category_estimated=BEVERAGE)

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 1
    assert test_product.minor_category.nutri_score_category is None
    assert ErrorLog.objects.exclude(reporting_app='').count() == 1
    assert test_product.nutri_score_category_estimated == BEVERAGE


@pytest.mark.django_db
def test_minor_category_nsc():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category=ADDED_FAT)

    test_product = mommy.make(Product, minor_category=minor_category)

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 1
    assert test_product.minor_category.nutri_score_category == ADDED_FAT
