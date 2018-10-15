
class CORSAPIViewMixin(object):
    @property
    def default_response_headers(self):
        ACCESS_CONTROL_ALLOW_ORIGIN = 'Access-Control-Allow-Origin'
        ACCESS_CONTROL_EXPOSE_HEADERS = 'Access-Control-Expose-Headers'
        ACCESS_CONTROL_ALLOW_CREDENTIALS = 'Access-Control-Allow-Credentials'
        ACCESS_CONTROL_ALLOW_HEADERS = 'Access-Control-Allow-Headers'
        ACCESS_CONTROL_ALLOW_METHODS = 'Access-Control-Allow-Methods'

        headers = super().default_response_headers

        headers[ACCESS_CONTROL_ALLOW_ORIGIN] = '*'
        headers[ACCESS_CONTROL_ALLOW_METHODS] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        headers[ACCESS_CONTROL_ALLOW_HEADERS] = 'Authorization,DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,X-Application-Warning'
        headers[ACCESS_CONTROL_EXPOSE_HEADERS] = 'Content-Length,Content-Range,X-Application-Warning'
        headers[ACCESS_CONTROL_ALLOW_CREDENTIALS] = 'true'

        return headers
