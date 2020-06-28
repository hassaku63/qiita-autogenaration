from urllib.parse import urlparse, parse_qs
from qp import settings
from qp.error import QpError
from qiita_v2.client import QiitaClient
from qiita_v2.exception import QiitaApiException

from qp.logs import get_logger
log = get_logger(__name__)

qiita = None

def _get_qiita_client():
    global qiita
    if qiita is None:
        qiita = QiitaClient(access_token=settings.QIITA_API_TOKEN)
        log.info(f'QiitaClient initialized')
    return qiita


class QpItemNotFoundError(QpError):
    pass


class QpItemCreateError(QpError):
    pass


class QpItemUpdateError(QpError):
    pass


class Qiita(object):
    def __init__(self):
        self.client: QiitaClient

    def set_client(self, client: QiitaClient):
        self.client = client

    def get_item(self, item_id: str):
        """returns dict value which get_item API returns

        https://qiita.com/api/v2/docs#get-apiv2itemsitem_id

        raises:  qiita_v2.exception.QiitaApiException

        :param item_id: item id
        :type id: str
        :return: dict_value
        :rtype: [type]
        """
        qiita = _get_qiita_client()
        try:
            return qiita.get_item(item_id).to_json()
        except QiitaApiException as e:
            raise QpItemNotFoundError(f'item id = {item_id}')
    
    def create_item(self, title: str, tags: list, md_content: str, params: dict={}) -> str:
        """[summary]

        :param title: [description]
        :type title: str
        :param md_content: [description]
        :type md_content: str
        :return: item id
        """
        p = params
        p['title'] = title
        p['tags'] = tags
        p['body'] = md_content
        try:
            res = self.client.create_item(params=p).to_json()
            log.info(f"publisher create an item {res['id']}")
            return res['id']
        except QiitaApiException as e:
            log.error(f"publisher.create {str(e)}")
            raise QpItemCreateError(str(e))

    def update_item(self, id: str, md_content: str) -> str:
        """
        タイトルとタグは更新しない仕様なので、いずれDynamoDBから動的に引っ張るようにしたい

        render_info = {
            'template_name': 'str',
            'template_variables': [
                {'var1': 'value1'},
                # ...
            ]
        }
        :return: item id
        """
        qiita = _get_qiita_client()
        item = self.get_item(id)
        p = {
            'title': item.get('title', ''),
            'tags': item.get('tags', []),
            'body': md_content
        }
        try:
            res = qiita.update_item(id=id, params=p).to_json()
            log.info(f"publisher update an item {res['id']}")
            return res['id']
        except QiitaApiException as e:
            log.error(f"update item {str(e)}")
            raise QpItemUpdateError(str(e))

    def list_own_items(self, page_size=100):
        """Pagenation を考慮して、item のリストを返す

        # Qiita の Pagenation について
        link ヘッダによって制御される。

        ## 複数ページが存在する場合の例

        ```python
        {'first': 'https://qiita.com/api/v2/authenticated_user/items?page=1&per_page=5',
        'next': 'https://qiita.com/api/v2/authenticated_user/items?page=2&per_page=5',
        'last': 'https://qiita.com/api/v2/authenticated_user/items?page=9&per_page=5'}
        ```

        ## ページが1つだけ存在する場合の例
        
        {'first': 'https://qiita.com/api/v2/authenticated_user/items?page=1&per_page=100',
        'prev': 'https://qiita.com/api/v2/authenticated_user/items?page=&per_page=100',
        'next': 'https://qiita.com/api/v2/authenticated_user/items?page=&per_page=100',
        'last': 'https://qiita.com/api/v2/authenticated_user/items?page=1&per_page=100'}

        ページネーションを含めた総数は 'Total-Count' ヘッダに格納される。qiita_v2 の場合はレスポンスの 'result_count' を参照してintにキャストすることで取得可能。

        :param page_size: qiita pagenation per_page, defaults to 100, up to 100
        :type page_size: int, optional
        """
        page = 1
        resp = self._get_authenticated_user_items(page=page, page_size=page_size)
        result: list = resp.to_json()
        if resp.link_first == resp.link_last:
            return result

        last_page, _ = self._get_last_link_page(resp.link_last)
        for p in range(2, last_page+1):
            resp = qiita.get_authenticated_user_items(params={
                'page': p,
                'per_page': page_size
            })
            result.extend(resp.to_json())
        return result

    def _get_authenticated_user_items(self, page: int, page_size: int):
        qiita = _get_qiita_client()
        return qiita.get_authenticated_user_items(params={
            'page': page,
            'per_page': page_size
        })

    def _get_last_link_page(self, link_last: str):
        """Returns 

        Pagenagion link example:
        https://qiita.com/api/v2/authenticated_user/items?page=1&per_page=100

        :param link_last: Qiita API Last-Link URL (this url must has query string page and per_page)
        :type link: str
        :return: tuple of (last_page_number, page_size_you_specified)
        """
        u = urlparse(link_last)
        qs = parse_qs(u.query)
        last_page = int(qs.get('page')[0])
        page_size = int(qs.get('per_page')[0])
        return (last_page, page_size)



def create_qiita(client: QiitaClient=None):
    qiita = Qiita()
    if client is None:
        qiita.set_client(_get_qiita_client())
    else:
        qiita.set_client(client)
    return qiita


if __name__ == '__main__':
    from pprint import pprint
    qiita = create_qiita()
    # qiita.create_item(
    #     title='api test',
    #     md_content='# h1\nTEST'
    # )

    # res = qiita.client.get_item(id='b9be7797ead4390b628c')
    # print(res)

    # try:
    #     res = qiita.client.create_item(params={
    #         'title': 'test for api publish',
    #         'body': '# h1\nTEST',
    #         'coediting': False,
    #         'tags': [
    #             {'name': 'Python', 'versions': []},
    #             {'name': 'Ruby', 'versions': ['2.2']}
    #         ],
    #         'private': True,
    #     })
    #     print(res.to_json())
    # except Exception as e:
    #     print(e)

    data = {
        'template_name': 'portfolio.jinja2', 
        'template_variables': {
            'items': [
                {'link': 'https://qiita.com/hassaku_63/items/3acfca4f386b74a6ffca', 'name': 'exapmle item 1', 'likes': 1}, {'link': 'https://qiita.com/hassaku_63/items/3acfca4f386b74a6ffca', 'name': 'exapmle item 2', 'likes': 0}
            ], 
            'tags_count': [
                {'count': 10, 'name': 'Python'}, 
                {'count': 5, 'name': 'TypeScript'}
            ]
        }, 
        'article': '[Test for Qiita API publish] my article', 
        'tags': [
            {'name': 'Qiita', 'versions': []}
        ], 
        'publish_status': {
            'is_published': True, 
            'item_id': 'b9be7797ead4390b628c'
        }
    }

    pprint({
        'title': data['article'],
        'tags': data['tags'],
        'content': 'a',
    })
    qiita.client.update_item(
        id=data['publish_status']['item_id'],
        params={
            'title': data['article'],
            'tags': data['tags'],
            'body': 'a',
        }
    )
