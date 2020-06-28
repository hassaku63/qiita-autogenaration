from qp import deco
from qp.error import QpError
from qp.libs.qiita import create_qiita
from qp.libs.template import render_template
from qp.libs.renderconfig import (
    find_render_config_by_article,
    get_publish_status,
    put_published_status
)
from qp import settings

from qp.logs import get_logger
log = get_logger(__name__)



@deco.from_sfn
def find_template_by_article(data, context={}):
    """記事のレンダリングに使用するパラメータを返す

    :param data: {article<str>}
    :type data: [type]
    :param context: defaults to {}
    :type context: dict, optional
    :return: {article<str>, template_name<str>, template_variables<dict>}
    :rtype: dict
    """
    return find_render_config_by_article(data['article'])


@deco.from_sfn
def get_item_exists(data, context):
    """
    qiita item id を拾って、
    今も Qiita にそのアイテムが存在しているかどうかを確認する
    """
    status = get_publish_status(data['article'])
    return status


@deco.from_sfn
def create_item(data, context):
    log.info({
        'event': 'Create item',
        'data': data
    })
    qiita = create_qiita()
    content = render_template(
        template_name=data['template_name'],
        **data['template_variables']
    )
    log.info({
        'event': 'Content has rendered',
        'content': content
    })
    result = qiita.create_item(
        title=data['article'],
        tags=data['tags'],
        md_content=content
    )
    return result
    

@deco.from_sfn
def update_item(data, context):
    log.info({
        'event': 'Update item',
        'data': data
    })
    qiita = create_qiita()
    content = render_template(
        template_name=data['template_name'],
        **data['template_variables']
    )
    log.info({
        'event': 'Content has rendered',
        'content': content
    })
    result = qiita.update_item(
        id=data['publish_status']['item_id'],
        md_content=content
    )
    return result


@deco.from_sfn
def update_publish_status(data, context):
    log.info(f'update_publish_status {data}')
    put_published_status(data['article'], data['item_id'])
    return data
