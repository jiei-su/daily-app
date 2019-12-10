"""
LOG定義モジュール
"""
import logging
import inspect


def base_conf(file_name):
    file_name = file_name.split('/')[-1][:-3]
    filename = '../log/' + file_name + '.log'
    logging.basicConfig(filename=filename,
                        format='[%(asctime)s][%(levelname)s] %(message)s')


def info(msg):
    base_conf(inspect.stack()[1][1])
    return logging.info(msg)


def warn(msg):
    base_conf(inspect.stack()[1][1])
    return logging.warning(msg)


def error(msg):
    base_conf(inspect.stack()[1][1])
    return logging.error(msg)
