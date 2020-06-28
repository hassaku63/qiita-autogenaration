import os
import pathlib
from dotenv import load_dotenv


QP_ENV = os.environ.get('QP_ENV', 'dev')
ENV_FILE = pathlib.Path(__file__).parent / '..' / f".env.{QP_ENV}"

if not ENV_FILE.exists():
    FileNotFoundError(f'{ENV_FILE.absolute()}.')

load_dotenv(ENV_FILE.resolve().absolute())

# env
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
QIITA_API_TOKEN = os.environ.get('QIITA_API_TOKEN', '')
QIITA_USER_ID = os.environ.get('QIITA_USER_ID', '')
ARTICLE_TABLE_NAME = os.environ.get('ARTICLE_TABLE_NAME', '')
PUBLISH_REQUEST_QUEUE_NAME = os.environ.get('PUBLISH_REQUEST_QUEUE_NAME')
UPDATE_TEMPLATE_VARIABLES_QUEUE_NAME = os.environ.get('UPDATE_TEMPLATE_VARIABLES_QUEUE_NAME')

# AWS
AWS_ACCOUNT_ID = os.environ.get('AWS_ACCOUNT_ID')
AWS_REGION = os.environ.get('AWS_REGION')

# StateMachine
PUBLISHER_STATEMACHINE_NAME = os.environ.get('PUBLISHER_STATEMACHINE_NAME')