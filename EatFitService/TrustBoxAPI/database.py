from django.contrib.auth.models import Permission, User

def setup_database():

    user, created = User.objects.get_or_create(
        username="eatfit", email="eatfit@autoidlabs.ch",
        defaults={'first_name': 'Eat', "last_name" : "Fit"},
    )
    if created:
        user.set_password("nRbUrdMUCZycQHsNv9dX")
        user.save()