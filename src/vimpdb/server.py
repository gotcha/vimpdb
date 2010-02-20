import BaseHTTPServer
import urllib
import cgi

PDB = 'pdbcmd'


class PDBHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        querystring = urllib.splitquery(self.path)
        if len(querystring) > 1:
            query = cgi.parse_qs(querystring[1])
        if PDB in query:
            command = query[PDB][0]
        self.server.pdbcommand = command
        self.send_response(200)


class PDBServer(BaseHTTPServer.HTTPServer):

    def __init__(self, server_address, RequestHandlerClass, debugger):
        BaseHTTPServer.HTTPServer.__init__(self, server_address,
            RequestHandlerClass)
        self.debugger = debugger


def run(debugger):
    server_address = ('', 8000)
    httpd = PDBServer(server_address, PDBHandler, debugger)
    httpd.handle_request()
    return httpd.pdbcommand


if __name__ == '__main__':
    run(handler_class=PDBHandler)
