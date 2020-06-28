import time
from datetime import datetime
import json
from qp.libs.articlestore import put_article_template_variables
from qp.libs.sfn import start_execution
from qp import settings

from qp import logs
log = logs.get_logger(__name__)


def handler(event, context):
    """From SQS update-template-variables

    Consumer of qp.jobs.jobqueue, enqueue_template_variables()

    :param event: SQS Event, Single record is a dict what has keys as follows; article, template_variables
    :type event: dict
    """
    for record in event['Records']:
        item = json.loads(record['body'])
        article = item['article']
        template_variables = item['template_variables']
        updated_item = put_article_template_variables(
            article=article,
            template_variables=template_variables
        )
        log.info(updated_item)

        resp = start_execution(
            name=settings.PUBLISHER_STATEMACHINE_NAME,
            params=json.dumps({
                'article': article
            })
        )
        log.info({
            'event': 'statemachine executed',
            'name': settings.PUBLISHER_STATEMACHINE_NAME,
            'params': {
                'article': article
            },
            'execution_response': resp
        })
        return updated_item