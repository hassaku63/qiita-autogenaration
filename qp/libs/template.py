import pathlib
from jinja2 import Environment, PackageLoader

env = None

def _get_env() -> Environment:
    global env
    if env is None:
        env = Environment(
            loader=PackageLoader('qp', 'templates')
        )
    return env


def render_template(template_name: str, **kwargs):
    """Return rendered string

    :param template_name: template filename
    :type template_name: str
    :param kwargs: template variables
    :return: rendered string
    :rtype: str
    """
    return _get_env().get_template(template_name).render(**kwargs)


class RenderConfig(object):
    pass