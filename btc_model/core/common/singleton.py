# -*- coding: UTF-8 –*-

"""
Author:

Create Date: 2021/6/18

Description:

"""


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)

        return instances[cls]

    return get_instance
