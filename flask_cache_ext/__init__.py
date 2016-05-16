# -*- coding: utf-8 -*-
import functools

from flask_cache import Cache as _Cache
from flask_cache._compat import PY2

if PY2:
    str = unicode  # noqa


class Cache(_Cache):

    def get_items(self, func, keys):
        """批量获取缓存的值, 按照所给key的顺序返回,
        如果缓存没有, 将通过func获取值, 并设置缓存

        :param func: 有cache.memoize装饰的方法, 只支持一个参数
        :param keys: list或者tuple, 每一项可作为func的参数
        :return: list
        """
        if not keys:
            return dict()

        instance_self = getattr(func, '__self__', None)
        if instance_self:
            make_cache_key_func = functools.partial(func.make_cache_key,
                                                    func.uncached,
                                                    instance_self)
            uncached_func = functools.partial(func.uncached, instance_self)
        else:
            make_cache_key_func = functools.partial(func.make_cache_key,
                                                    func.uncached)
            uncached_func = func.uncached

        # cache_key列表
        cache_key_list = []
        for item_key in keys:
            cache_key = make_cache_key_func(item_key)
            cache_key_list.append(cache_key)

        # 批量获取缓存
        items = self.get_many(*cache_key_list)

        uncached_dict = {}
        # 单独获取缓存中没有的数据, 应该使用set_many设置缓存
        for (index, item) in enumerate(items):
            if item is None:
                item_key = keys[index]
                cache_key = cache_key_list[index]

                value = uncached_func(item_key)
                items[index] = value
                uncached_dict[cache_key] = value
        if uncached_dict:
            self.set_many(uncached_dict, timeout=func.cache_timeout)

        return items

    def get_item_dict(self, func, keys):
        """批量获取缓存的值, 并返回key为keys的值, value为func返回值的dict,
        如果缓存没有, 将通过func获取值, 并设置缓存

        :param func: 有cache.memoize装饰的方法, 只支持一个参数
        :param keys: list或者tuple, 每一项可作为func的参数
        :return: dict
        """
        keys = list(set(keys))
        items = self.get_items(func, keys)
        return dict(zip(keys, items))

    def _memoize_kwargs_to_args(self, f, *args, **kwargs):
        """重写父类方法, 所有参数都转为字符串,
        例如下面的参数, 实际使用中我们期望得到一样的key
        func.make_cache_key(1)
        func.make_cache_key(1L)
        func.make_cache_key('1')
        func.make_cache_key(u'1')
        """
        keyargs, keykwargs = super(Cache, self) \
            ._memoize_kwargs_to_args(f, *args, **kwargs)

        new_args = tuple(map(str, keyargs))

        return new_args, keykwargs
