import csv
from django.http import HttpResponse


def export(request, export):
    """Generic export method.
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=%s.csv" % export.name
    writer = csv.writer(response, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL)

    for product in export.get_products():
        writer.writerow((
            product.get_name().encode("utf-8"),
        ))
    return response
