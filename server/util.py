__author__ = 'coreygriggs'

from datetime import datetime


def converted_time(timestamp):
    """
    Utility wrapper around strftime to the desired format
    :param timestamp: A datetime object to be converted to a jsonifiable string
    :return: A string formatted as YYYY-MM-DD HH:MM
    """
    return timestamp.strftime('%Y-%m-%d %H:%M')