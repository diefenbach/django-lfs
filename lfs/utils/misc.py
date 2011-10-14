def parse_properties(request):
    """Parses the query string for properties and returns them in the format:
    property_id|option_id
    """
    properties = []
    for property, option_id in request.POST.items():
        if property.startswith("property"):
            try:
                property_id = property.split("_")[1]
            except IndexError:
                continue
            else:
                properties.append("%s|%s" % (property_id, option_id))

    return properties

