import os
import json
import logging
from datetime import datetime

from qp import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        line = {}
        rdict = record.__dict__
        if 'asctime' in rdict:
            line['asctime'] = self.formatTime(record)
        if 'levelno' in rdict:
            line['level'] = logging.getLevelName(record.levelno)
        if 'name' in rdict:
            line['name'] = record.name
        if 'fliename' in rdict:
            line['filename'] = record.filename
        if 'exc_info' in rdict and rdict.get('exc_info', None) is not None:
            line['exc_info'] = self.formatException(record.exc_info)
        if 'stack_info' in rdict and rdict.get('stack_info', None) is not None:
            line['stack_info'] = self.formatStack(record.stack_info)
        if 'created' in rdict:
            dt = datetime.fromtimestamp(rdict['created'])
            line['@timestamp'] = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        if 'msg' in rdict:
            if not isinstance(rdict['msg'], dict):
                line['msg'] = rdict['msg']
            else:
                line['msg'] = str(rdict['msg'])
        return json.dumps(line)


class JsonLogger(logging.Logger):
    def __init__(self, name, level):
        super().__init__(name, level)
    
    def makeRecord(self, name, lvl, fn, lno, msg, args, exc_info, func, extra, sinfo):
        return super().makeRecord(name, lvl, fn, lno, msg, args, exc_info, func, extra, sinfo)


def get_logger(name, level=settings.LOG_LEVEL) -> JsonLogger:
    log = JsonLogger(name, level)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    log.addHandler(handler)
    return log