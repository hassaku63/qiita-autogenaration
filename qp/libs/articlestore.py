import json
import time
from decimal import Decimal
import boto3
from qp import settings

from qp.logs import get_logger
log = get_logger(__name__)


dynamodb_resource = None


def _get_resource():
    global dynamodb_resource
    if dynamodb_resource is None:
        dynamodb_resource = boto3.resource('dynamodb')
    return dynamodb_resource


def get_table(name):
    return _get_resource().Table(name)


def flat_dict_convert_number_to_decimal(d):
    """
    :param tv: flat dict
    :type tv: dict
    """
    result = {}
    for k, v in d.items():
        if type(v) == int or type(v) == float:
            v = Decimal(v)
        result.setdefault(k, v)
    return result


def put_article_template_variables(article, template_variables):
    """[summary]

    :param article: [description]
    :type article: [type]
    :param template_variables: [description]
    :type template_variables: [type]
    """
    table = get_table(settings.ARTICLE_TABLE_NAME)
    # resp = table.get_item(Key={
    #     'article': article,
    #     'parameter_type': 'template'
    # })
    # item = resp['Item']
    # item
    items = table.scan()

    tvars = flat_dict_convert_number_to_decimal(template_variables)
    updated_result = table.update_item(
        Key={
            'article': article,
            'parameter_type': 'template'
        },
        UpdateExpression="set template_variables=:tv, last_updated=:ts",
        ExpressionAttributeValues={
            ':tv': tvars,
            ':ts': Decimal(int(time.time()))
        },
        ReturnValues="ALL_NEW"
    )
    
    return updated_result['Attributes']