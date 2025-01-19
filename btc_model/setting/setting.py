# -*- coding: utf-8 -*-
"""
Author: guozq

Create Date: 2022/5/22 17:39

Description:

"""
import os
from logging import CRITICAL
from typing import Dict, Any
from tzlocal import get_localzone
from btc_model.core.util.file_util import FileUtil


SETTINGS: Dict[str, Any] = {
    "font.family": "微软雅黑",
    "font.size": 12,

    "log.active": True,
    "log.level": CRITICAL,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "datafeed.name": "",
    "datafeed.username": "",
    "datafeed.password": "",

    "cex.okx.apikey": "8458f3f2-2336-45a6-8478-5faadb1faeb8",
    "cex.okx.secretkey": "C3D924B57DE38D9A3466139B4814C8D0",
    "cex.okx.passphrase": "970410Sjw.",
    "cex.okx.limit": int(100),



    "database.uri": "",
    "database.name": "",
    "database.database": "",
    "database.host": "",
    "database.port": 0,
    "database.user": "",
    "database.password": "",
    "database.auth_source": ''
}


# Load global setting from json file.
# SETTING_FILENAME: str = "blockchain_setting.json"
# SETTINGS.update(FileUtil.load_json(SETTING_FILENAME))


def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length = len(prefix)
    if prefix_length > 0 and not prefix.endswith('.'):
        prefix = prefix + '.'
        prefix_length += 1

    return {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}

