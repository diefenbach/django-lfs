from django.template import Node
from django.template import Library
from django.conf import settings
import django.db as db
import re
from django.utils.html import escape

register = Library()


class DbInfoNode(Node):
    def __init__(self):
        pass

    def __repr__(self):
        return "<DbInfoNode>"

    def render(self, context):
        if not settings.TEMPLATE_DEBUG:
            return ""
        secs = 0.0
        for s in db.connection.queries:
            secs += float(s['time'])
        return str("%d queries, %f seconds" % (len(db.connection.queries), secs)
)


def do_dbinfo(parser, token):
    return DbInfoNode()
do_dbinfo = register.tag('dbinfo', do_dbinfo)


class DbQueryListNode(Node):
    def __init__(self):
        pass

    def __repr__(self):
        return "<DbQueryListNode>"

    def render(self, context):
        if not settings.TEMPLATE_DEBUG:
            return ""
        s = ""
        for q in db.connection.queries:
            s += "<li>" + escape(q["sql"]) + "</li>\n"
        return s


def do_dbquerylist(parser, token):
    return DbQueryListNode()

do_dbquerylist = register.tag('dbquerylist', do_dbquerylist)
