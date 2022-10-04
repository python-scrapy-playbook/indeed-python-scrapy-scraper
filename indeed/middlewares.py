from urllib.parse import urlencode
from scrapy import Request
class ScrapeOpsProxyMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)


    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = 'https://proxy.scrapeops.io/v1/?'
        self.scrapeops_proxy_active = settings.get('SCRAPEOPS_PROXY_ENABLED', False)


    @staticmethod
    def _param_is_true(request, key):
        if request.meta.get(key) or request.meta.get(key, 'false').lower() == 'true':
            return True
        return False


    @staticmethod
    def _replace_response_url(response):
        real_url = response.headers.get(
            'Sops-Final-Url', def_val=response.url)
        return response.replace(
            url=real_url.decode(response.headers.encoding))
    

    def _get_scrapeops_url(self, request):
        payload = {'api_key': self.scrapeops_api_key, 'url': request.url}
        if self._param_is_true(request, 'sops_render_js'):
            payload['render_js'] = True
        if self._param_is_true(request, 'sops_residential'): 
            payload['residential'] = True
        if self._param_is_true(request, 'sops_keep_headers'): 
            payload['keep_headers'] = True
        if request.meta.get('sops_country') is not None:
            payload['country'] = request.meta.get('sops_country')
        proxy_url = self.scrapeops_endpoint + urlencode(payload)
        return proxy_url


    def _scrapeops_proxy_enabled(self):
        if self.scrapeops_api_key is None or self.scrapeops_api_key == '' or self.scrapeops_proxy_active == False:
            return False
        return True
    
    def process_request(self, request, spider):
        if self._scrapeops_proxy_enabled is False or self.scrapeops_endpoint in request.url:
            return None
        
        scrapeops_url = self._get_scrapeops_url(request)
        new_request = request.replace(
            cls=Request, url=scrapeops_url, meta=request.meta)
        return new_request


    def process_response(self, request, response, spider):
        new_response = self._replace_response_url(response)
        return new_response
