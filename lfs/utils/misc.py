def parse_properties(request):
    """Parses the query string for properties and returns them in the format:
    property_id|option_id
    """
    properties = []
    for prop, option_id in request.POST.items():
        if prop.startswith("property"):
            try:
                prop_group_id = prop.split("_")[1]
            except IndexError:
                continue
            else:
                property_group_id, property_id = prop_group_id.split("|")
                properties.append("%s|%s|%s" % (property_group_id, property_id, option_id))
    return properties
