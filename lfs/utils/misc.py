import re
re_digits_nondigits = re.compile(r'\d+|\D+')

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

def FormatWithCommas(format, value):
    """
    """
    parts = re_digits_nondigits.findall(format % (value,))
    for i in xrange(len(parts)):
        s = parts[i]
        if s.isdigit():
            parts[i] = _commafy(s)
            break
    return ''.join(parts)

def _commafy(s):
    r = []
    for i, c in enumerate(reversed(s)):
        if i and (not (i % 3)):
            r.insert(0, ',')
        r.insert(0, c)
    return ''.join(r)