from NutritionService.models import ErrorLog, CrowdsourceProduct, NotFoundLog, Product
import datetime
from django.template import RequestContext, loader
from django.core.mail.message import EmailMultiAlternatives
from EatFitService.settings import DEFAULT_FROM_EMAIL


def generate_daily_report():
    date_from = datetime.datetime.now() - datetime.timedelta(days=1)

    errors_added = ErrorLog.objects.filter(timestamp__gte = date_from).count()
    total_errors_added = ErrorLog.objects.all().count()
    
    crowdsourced_products_added = CrowdsourceProduct.objects.filter(created__gte = date_from).count()
    crowdsourced_products_updated = CrowdsourceProduct.objects.filter(updated__gte = date_from).count()
    
    new_not_found_products =  NotFoundLog.objects.filter(first_searched_for__gte = date_from).count()
    total_not_found_products = NotFoundLog.objects.all().count()
    
    new_products_from_trustbox = Product.objects.filter(created__gte = date_from, source = Product.TRUSTBOX).count()
    updated_products_from_trustbox = Product.objects.filter(updated__gte = date_from, source = Product.TRUSTBOX).count()

    new_products_from_openfood = Product.objects.filter(created__gte = date_from, source = Product.OPENFOOD).count()

    new_products_from_codecheck = Product.objects.filter(created__gte = date_from, source = Product.CODECHECK).count()

    new_products_from_auto_id_labs = Product.objects.filter(created__gte = date_from, source = Product.AUTO_ID_LABS).count()
    updated_products_from_auto_id_labs = Product.objects.filter(updated__gte = date_from, source = Product.AUTO_ID_LABS).count()

    c = {
        'date_from': date_from,
        'date_to': datetime.datetime.now(),
        'errors_added': errors_added,
        'total_errors_added': total_errors_added,
        'crowdsourced_products_added': crowdsourced_products_added,
        'crowdsourced_products_updated': crowdsourced_products_updated,
        'new_not_found_products': new_not_found_products,
        'total_not_found_products': total_not_found_products,
        'new_products_from_trustbox': new_products_from_trustbox,
        'updated_products_from_trustbox': updated_products_from_trustbox,
        'new_products_from_openfood': new_products_from_openfood,
        'new_products_from_codecheck': new_products_from_codecheck,
        'new_products_from_auto_id_labs': new_products_from_auto_id_labs,
        'updated_products_from_auto_id_labs': updated_products_from_auto_id_labs,

    }
    email = loader.render_to_string("mail/daily_status_report.html", c)
    mail = EmailMultiAlternatives(u"EatFit Report", email, DEFAULT_FROM_EMAIL, ["klaus.fuchs@autoidlabs.ch", "sven.brunner@holo-one.com"])
    mail.attach_alternative(email, "text/html")
    mail.send()
