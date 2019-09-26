from model_mommy import mommy
import pytest

from NutritionService.models import ErrorLog, Product, MinorCategory, MajorCategory, get_nutri_score_category


@pytest.mark.django_db
def test_no_minor_category_no_product_nsc():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    test_product = mommy.make(Product)

    assert Product.objects.count() == 1

    category = get_nutri_score_category(test_product)

    assert test_product.minor_category is None
    assert ErrorLog.objects.count() == 1
    assert test_product.nutri_score_category_estimated is None
    assert category == 'Food'


@pytest.mark.django_db
def test_no_minor_category_product_nsc():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    test_product = mommy.make(Product, nutri_score_category_estimated='Mineral Water')

    assert Product.objects.count() == 1

    category = get_nutri_score_category(test_product)

    assert test_product.minor_category is None
    assert ErrorLog.objects.count() == 1
    assert test_product.nutri_score_category_estimated is not None
    assert category == 'Mineral Water'


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

    category = get_nutri_score_category(test_product)

    assert test_product.minor_category.nutri_score_category is None
    assert ErrorLog.objects.count() == 1
    assert test_product.nutri_score_category_estimated is None
    assert category == 'Food'


@pytest.mark.django_db
def test_no_minor_category_nsc_product_nsc():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category)

    test_product = mommy.make(Product, minor_category=minor_category, nutri_score_category_estimated='Beverage')

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 1

    category = get_nutri_score_category(test_product)

    assert test_product.minor_category.nutri_score_category is None
    assert ErrorLog.objects.count() == 1
    assert test_product.nutri_score_category_estimated is not None
    assert category == 'Beverage'


@pytest.mark.django_db
def test_minor_category_nsc():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category='Added Fat')

    test_product = mommy.make(Product, minor_category=minor_category)

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 1

    category = get_nutri_score_category(test_product)

    assert test_product.minor_category.nutri_score_category is not None
    assert category == 'Added Fat'
