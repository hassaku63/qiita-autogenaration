import json
from collections import Counter
from qp.libs.qiita import create_qiita
from qp.libs.jobqueue import enqueue_template_variables
from qp import settings

from qp import logs
log = logs.get_logger(__name__)


# 投稿記事を特定するための名前
ARTICLE_NAME = 'Qiita Contributions Portfolio (Auto Generated)'
# タグ出現頻度の上位N件
MAX_FREQUENT_TAGS = 10
# Like 数の上位N件
MAX_LIKED_ITEMS = 5


def handler(event, context):
    qiita = create_qiita()
    items = qiita.list_own_items()

    # Get frequent tags
    item_tags = [item['tags'] for item in items]
    tag_counts = Counter()
    for item_tags in item_tags:
        tag_names = [tag['name'] for tag in item_tags]
        tag_counts.update(tag_names)
    frequent_tags = _get_most_frequents(tag_counts, n=MAX_FREQUENT_TAGS)
    frequent_tags = [
        dict(name=name, count=count)
        for (name, count) in frequent_tags
    ]

    # Get most liked items
    items_sorted_by_liked = sorted(items, key=lambda i: i.get('likes_count', 0), reverse=True)
    liked_items = [
        dict(name=item['title'], link=item['url'], likes=item['likes_count'])
        for item in items_sorted_by_liked[:MAX_LIKED_ITEMS]
    ]

    # print(json.dumps(frequent_tags, indent=2))
    # print(json.dumps(liked_items, indent=4))
    template_vars = {
        'items': liked_items,
        'tags_count': frequent_tags
    }
    enqueue_template_variables(
        article_name=ARTICLE_NAME,
        template_variables=template_vars
    )
    return template_vars


def _get_most_frequents(counter, n):
    most_frequent_keys = sorted(counter, key=lambda k: counter[k], reverse=True)
    return [(k, counter[k]) for k in most_frequent_keys[:n]]


if __name__ == '__main__':
    template_vars = handler({}, {})
    print(json.dumps(template_vars, indent=4))