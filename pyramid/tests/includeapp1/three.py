from pyramid.response import Response

def aview(request):
    return Response('three')

def configure(config):
    config.add_view(aview, name='three')
    config.include('pyramid.tests.includeapp1.two.configure') # should not cycle
    config.add_view(aview) # will be overridden by root when resolved
    
