# Import from csv (csv filename must correspond to model)
# If gtin in csv does not exist in model:
## create entry in model
# else:
## get list of all fields which do not exist
## if fields do not exist in model AND exist in csv:
#### update fields from value from csv

# views.py

from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser
import csv

@api_view(['PUT'])
@parser_classes((FileUploadParser,))
def upload_view(request, filename):

	model = filename.split('.')[0]

	reader = csv.reader(request.data['file'])
	headers = next(reader, None)
	
	header_map = {header: headers.index(header) for header in headers}

	for row in reader:
		if not model.objects.get(gtin=row[header_map['gtin']]).exists():
			obj = model()
			obj.save()
		else:
			for field in model._meta.get_fields():
				if not getattr(model, field).exists() and row[header_map[field.name]] != '':
					model.objects.filter(gtin=row[header_map['gtin']]).update(field=row[header_map[field.name]])

# urls.py

from .views import upload_view

urlpatterns = [
    # ...
    url(r'^upload/(?P<filename>[^/]+)$', views.upload_view)
]