# django imports
import hashlib

from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import _get_queryset
from django.utils.encoding import force_str


def key_from_instance(instance):
    opts = instance._meta
    return '%s.%s:%s' % (opts.app_label, opts.module_name, instance.pk)


class SimpleCacheQuerySet(QuerySet):
    def filter(self, *args, **kwargs):
        pk = None
        for val in ('pk', 'pk__exact', 'id', 'id__exact'):
            if val in kwargs:
                pk = kwargs[val]
                break
        if pk is not None:
            opts = self.model._meta
            key = '%s.%s.%s:%s' % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, opts.app_label, opts.module_name, pk)
            obj = cache.get(key)
            if obj is not None:
                self._result_cache = [obj]
        return super(SimpleCacheQuerySet, self).filter(*args, **kwargs)


class SimpleCacheManager(models.Manager):
    def get_query_set(self):
        return SimpleCacheQuerySet(self.model)


def lfs_get_object(klass, *args, **kwargs):
    """
    Uses get() to return an object, or raises a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    cache_key = "%s-%s-%s" % (force_str(settings.CACHE_MIDDLEWARE_KEY_PREFIX), klass.__name__.lower(),
                              force_str(kwargs.values()[0]))
    cache_key = hashlib.md5(cache_key).hexdigest()
    object = cache.get(cache_key)
    if object is not None:
        return object

    queryset = _get_queryset(klass)

    try:
        object = queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None
    else:
        cache.set(cache_key, object)
        return object


def lfs_get_object_or_404(klass, *args, **kwargs):
    """
    Uses get() to return an object, or raises a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    cache_key = "%s-%s-%s" % (force_str(settings.CACHE_MIDDLEWARE_KEY_PREFIX), klass.__name__.lower(),
                              force_str(kwargs.values()[0]))
    cache_key = hashlib.md5(cache_key).hexdigest()
    object = cache.get(cache_key)
    if object is not None:
        return object

    queryset = _get_queryset(klass)
    try:
        object = queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
    else:
        cache.set(cache_key, object)
        return object


def clear_cache():
    """Clears the complete cache.
    """
    # memcached
    try:
        cache._cache.flush_all()
    except AttributeError:
        pass
    else:
        return

    try:
        cache._cache.clear()
    except AttributeError:
        pass
    try:
        cache._expire_info.clear()
    except AttributeError:
        pass

    try:
        cache.clear()
    except AttributeError:
        pass


def delete_cache(cache_key):
    cache.delete(cache_key)
    cache.delete(hashlib.md5(cache_key).hexdigest())


def get_cache_group_id(group_code):
    """ Get id for group_code that is stored in cache. This id is supposed to be included in cache key for all items
        from specific group.
    """
    cache_group_key = '%s-%s-GROUP' % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_code)
    group_id = cache.get(cache_group_key, 0)
    if group_id == 0:
        group_id = 1
        cache.set(cache_group_key, group_id, cache.default_timeout * 2)
    return group_id


def invalidate_cache_group_id(group_code):
    """ Invalidation of group is in fact only incrementation of group_id
    """
    cache_group_key = '%s-%s-GROUP' % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_code)
    try:
        cache.incr(cache_group_key)
    except ValueError:
        pass
