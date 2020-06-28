import functools
import json
from qp import settings
from qp.logs import get_logger

def from_sfn(func):
    """Logging decorator. from_sfn decorator passes given both arguments and return values as it is

    :param func: wrapped lambda function that has signature handler(event, context)
    :type func: function
    :raises e: Exception
    :return: any value
    :rtype: any
    """
    @functools.wraps(func)
    def wrapper(event, context):
        log = get_logger(__name__)
        log.info(event)
        try:
            result = func(event, context)
        except Exception as e:
            log.exception(e)
            raise e
        return result
    return wrapper


def from_sns(func):
    @functools.wraps(func)
    def wrapper(event, context):
        ret = []
        log = get_logger(__name__)
        for record in event['Records']:
            message = json.loads(record['Sns']['Message'])
            log.info(event)
            try:
                result = func(message, context)
            except Exception as e:
                log.exception(e)
                raise e
        return result
    return wrapper