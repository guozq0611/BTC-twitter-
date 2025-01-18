# -*- coding: utf-8 -*-
"""
Author: guozq

Create Date: 2022/5/22 22:48

Description:

"""
import datetime


class Context(object):
    """
    策略上下文
    """

    def __repr__(self):
        items = ("%s = %r" % (k, v)
                 for k, v in self.__dict__.items()
                 if not callable(v) and not k.startswith("_"))
        return "Context({%s})" % (', '.join(items),)

    def __init__(self):
        self._config = None

    @property
    def now(self):
        """
        """
        return datetime.datetime.now()
