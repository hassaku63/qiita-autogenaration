import json
import boto3
from qp import settings

from qp import logs
log = logs.get_logger(__name__)


client = None


def _get_client():
    global client
    if client is None:
        client = boto3.client('stepfunctions')
    return client


def _get_state_machine_name(name):
    return 'arn:aws:states:{}:{}:stateMachine:{}'.format(
        settings.AWS_REGION,
        settings.AWS_ACCOUNT_ID,
        name
    )


def start_execution(name, params):
    return _get_client().start_execution(
        stateMachineArn=_get_state_machine_name(name),
        input=params
    )