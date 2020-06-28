import json
import decimal
import boto3
from qp.error import QpError
from qp import settings

from qp import logs
log = logs.get_logger(__name__)

dynamodb = None
config_table = None


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def _get_dynamodb():
    global dynamodb
    if dynamodb is None:
        dynamodb = boto3.resource('dynamodb')
    return dynamodb


def _get_table(table_name: str):
    global config_table
    dynamodb = _get_dynamodb()
    if config_table is None:
        config_table = dynamodb.Table(table_name)
    return config_table


def find_render_config_by_article(article: str):
    table = _get_table(settings.ARTICLE_TABLE_NAME)
    log.info(msg=f'find_render_config_by_article: article = {article}')
    result = table.get_item(Key={
        'article': article,
        'parameter_type': 'template'
    })
    if not 'Item' in result:
        log.error(msg=f'find_render_config_by_article: not found {article}')
    item = result['Item']
    item.pop('parameter_type')
    return json.loads(json.dumps(item, cls=DecimalEncoder))


def get_publish_status(article: str):
    table = _get_table(settings.ARTICLE_TABLE_NAME)
    log.info(msg=f'get_publish_status: article = {article}')
    result = table.get_item(Key={
        'article': article,
        'parameter_type': 'publish_status'
    })
    if not 'Item' in result:
        log.info(msg=f'get_publish_status: item not found article = {article}')
        return {
            'is_published': False,
            'item_id': None
        }
    item = result['Item']
    return {
        'is_published': item['publish_status']['is_publish'],
        'item_id': None if item['publish_status'].get('item_id', '') == '' else item['publish_status'].get('item_id', '')
    }


def put_published_status(article: str, item_id: str):
    table = _get_table(settings.ARTICLE_TABLE_NAME)
    log.info(f'put_published_status: article = {article}, item_id = {item_id}')
    table.put_item(Item={
        'article': article,
        'parameter_type': 'publish_status',
        'publish_status': {
            'is_publish': True,
            'item_id': item_id
        }
    })


if __name__ == '__main__':
    from pprint import pprint
    table = _get_table('qiita-publish-article-dev')
    ret = table.scan()
    pprint(ret)

    article = '[Test for Qiita API publish] my article'
    parameter_type = 'template'
    data = {
        'article': article,
        'tags': [
            {'name': 'Qiita', 'versions': []}
        ],
        'parameter_type': parameter_type,
        'template_name': 'portfolio.jinja2',
        'template_variables': {
            'tags_count': [
                {'name': 'python', 'count': 10},
                {'name': 'TypeScript', 'count': 5}
            ],
            'items': [
                {'name': 'exapmle item 1', 'link': 'https://qiita.com/hassaku_63/items/3acfca4f386b74a6ffca', 'likes': 1},
                {'name': 'exapmle item 2', 'link': 'https://qiita.com/hassaku_63/items/3acfca4f386b74a6ffca', 'likes': 0}
            ]
        }
    }
    pprint(data)
    table.put_item(Item=data)

    publish_status = {
        'article': article,
        'parameter_type': 'publish_status',
        'publish_status': {
            'is_publish': False,
            'item_id': ''
        }
    }
    table.put_item(Item=publish_status)
    # ret = table.get_item(Key={
    #     'article': article,
    #     'parameter_type': parameter_type
    # })
    # item = ret['Item']
    item = find_render_config_by_article(article)
    item = json.loads(json.dumps(item, cls=DecimalEncoder))
    print(json.dumps(item, indent=2))

    item = get_publish_status(article)
    item = json.loads(json.dumps(item, cls=DecimalEncoder))
    print(json.dumps(item, indent=2))

    get_publish_status(article='notfound')