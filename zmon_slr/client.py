import requests

from typing import List

from urllib.parse import urljoin


class SLRClientError(Exception):
    pass


class Client:
    PRODUCT_GROUPS = 'product-groups'
    PRODUCTS = 'products'
    SLO = 'slo'
    SLI = 'sli'

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer {}'.format(token), 'User-Agent': 'SLR-SLI/0.1-alpha'})

    def _count(self, obj: dict) -> int:
        return obj['_meta']['count']

    def endpoint(self, *args, trailing_slash=False, base_url=None) -> str:
        parts = list(args)

        # Ensure trailing slash!
        if trailing_slash:
            parts.append('')

        url = self.url if not base_url else base_url

        return urljoin(url, '/'.join(str(p).strip('/') for p in parts))

    def product_list(self, name: str=None, product_group_name: str=None) -> List[dict]:
        params = {} if not name else {'name': name}
        if product_group_name:
            params['product_group'] = product_group_name

        res = self.session.get(self.endpoint(self.PRODUCTS), params=params)
        res.raise_for_status()

        ps = res.json()
        return ps['data']

    def product_delete(self, product: dict) -> requests.Response:
        res = self.session.delete(product['uri'])
        res.raise_for_status()

        return res

    def product_create(self, name, product_group_uri) -> dict:
        data = {'name': name, 'product_group_uri': product_group_uri}

        res = self.session.post(self.endpoint(self.PRODUCTS), json=data)
        res.raise_for_status()

        return res.json()

    def product_update(self, product: dict) -> dict:
        if 'uri' not in product:
            raise SLRClientError('Cannot determine product URI')

        res = self.session.put(product['uri'], json=product)
        res.raise_for_status()

        return res.json()

    def product_group_list(self, name=None) -> List[dict]:
        params = {} if not name else {'name': name}
        res = self.session.get(self.endpoint(self.PRODUCT_GROUPS), params=params)
        res.raise_for_status()

        pgs = res.json()
        return pgs['data']

    def product_group_get(self, uri) -> dict:
        res = self.session.get(uri)
        res.raise_for_status()

        return res.json()

    def product_group_delete(self, uri) -> requests.Response:
        res = self.session.delete(uri)
        res.raise_for_status()

        return res

    def product_group_create(self, name, department) -> dict:
        data = {
            'name': name,
            'department': department
        }

        res = self.session.post(self.endpoint(self.PRODUCT_GROUPS), json=data)
        res.raise_for_status()

        return res.json()

    def product_group_update(self, product_group: dict) -> dict:
        if 'uri' not in product_group:
            raise SLRClientError('Cannot determine product-group URI')

        res = self.session.put(product_group['uri'], json=product_group)
        res.raise_for_status()

        return res.json()

    def slo_list(self, product: dict) -> List[dict]:
        res = self.session.get(product['product_slo_uri'])
        res.raise_for_status()

        slo = res.json()
        return slo['data']

    def slo_get(self, uri) -> dict:
        res = self.session.get(uri)
        res.raise_for_status()

        return res.json()

    def slo_delete(self, slo: dict) -> requests.Response:
        res = self.session.delete(slo['uri'])
        res.raise_for_status()

        return res

    def slo_create(self, product: dict, title: str, description: str) -> dict:
        slo = {
            'title': title,
            'description': description
        }

        res = self.session.post(product['product_slo_uri'], json=slo)
        res.raise_for_status()

        return res.json()

    def slo_update(self, slo: dict) -> dict:
        if 'uri' not in slo:
            raise SLRClientError('Cannot determine slo URI')

        res = self.session.put(slo['uri'], json=slo)
        res.raise_for_status()

        return res.json()

    def target_list(self, slo: dict) -> List[dict]:
        res = self.session.get(slo['slo_targets_uri'])
        res.raise_for_status()

        slo = res.json()
        return slo['data']

    def target_get(self, uri) -> dict:
        res = self.session.get(uri)
        res.raise_for_status()

        return res.json()

    def target_delete(self, target: dict) -> requests.Response:
        res = self.session.delete(target['uri'])
        res.raise_for_status()

        return res

    def target_create(self, slo: dict, sli_uri: str, target_from: float=0.0, target_to: float=0.0) -> dict:
        target = {
            'from': target_from,
            'to': target_to,
            'sli_uri': sli_uri
        }

        res = self.session.post(slo['slo_targets_uri'], json=target)
        res.raise_for_status()

        return res.json()

    def target_update(self, target: dict) -> dict:
        if 'uri' not in target:
            raise SLRClientError('Cannot determine target URI')

        res = self.session.put(target['uri'], json=target)
        res.raise_for_status()

        return res.json()

    def sli_list(self, product: dict, name=None) -> List[dict]:
        params = {} if not name else {'name': name}

        res = self.session.get(product['product_sli_uri'], params=params)
        res.raise_for_status()

        sli = res.json()
        return sli['data']

    def sli_get(self, uri) -> dict:
        res = self.session.get(uri)
        res.raise_for_status()

        return res.json()

    def sli_delete(self, sli: dict) -> requests.Response:
        res = self.session.delete(sli['uri'])
        res.raise_for_status()

        return res

    def sli_create(self, product: dict, name: str, unit: str, source: dict) -> dict:
        sli = {
            'name': name,
            'source': source,
            'unit': unit
        }

        res = self.session.post(product['product_sli_uri'], json=sli)
        res.raise_for_status()

        return res.json()

    def sli_update(self, sli: dict) -> dict:
        if 'uri' not in sli:
            raise SLRClientError('Cannot determine sli URI')

        res = self.session.put(sli['uri'], json=sli)
        res.raise_for_status()

        return res.json()

    def sli_values(self, sli: dict, page_size=None) -> List[dict]:
        params = {'page_size': page_size} if page_size else {}
        res = self.session.get(sli['sli_values_uri'], params=params)
        res.raise_for_status()

        values = res.json()
        return values['data']

    def sli_query(self, sli: dict, start: int, end: str=None) -> dict:
        data = {}
        if start:
            data['start'] = start
        if end:
            data['end'] = end

        res = self.session.post(sli['sli_query_uri'], json=data)
        res.raise_for_status()

        return res.json()
