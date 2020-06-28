import json
import boto3
from qp import settings

from qp.logs import get_logger
log = get_logger(__name__)


sqs_client = None


def _get_queue_url(account, region, queue_name):
    return f'https://sqs.{region}.amazonaws.com/{account}/{queue_name}'


def _get_sqs_client():
    global sqs_client
    if sqs_client is None:
        sqs_client = boto3.client('sqs')
    return sqs_client


def _send_message(queue_url: str, message):
    sqs = _get_sqs_client()
    return sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message
    )


def enqueue_template_variables(article_name: str, template_variables):
    queue_url = _get_queue_url(
        account=settings.AWS_ACCOUNT_ID,
        region=settings.AWS_REGION,
        queue_name=settings.UPDATE_TEMPLATE_VARIABLES_QUEUE_NAME
    )
    log.info(queue_url)
    result = _send_message(
        queue_url=queue_url,
        message=json.dumps({
            'article': article_name,
            'template_variables': template_variables
        })
    )
    return result['MessageId']


def done(receipy_handle):
    """Remove message from queue

    :param receipy_handle: queue
    :type receipy_handle: str
    :return: RequestId of delete_message
    :rtype: str
    """
    sqs = _get_sqs_client()
    result = sqs.delete_message(
        QueueUrl=_get_queue_url(
            account=settings.AWS_ACCOUNT_ID,
            region=settings.AWS_REGION,
            queue_name=settings.RSS_QUEUE_NAME
        ),
        ReceiptHandle=receipy_handle
    )
    return result['ResponseMetadata']['RequestId']