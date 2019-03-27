import http.server as hs
import os, sys


class RequestHandler(hs.BaseHTTPRequestHandler):
    def send_content(self, page, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(bytes(page, encoding="utf-8"))
        print(page)

    def do_GET(self):
        # handle tow exception:the url exception;the conten-type exception
        try:
            # get the file path
            full_path = os.getcwd() + self.path

            # if the path don't exist
            if not os.path.exists(full_path):
                raise ServerException("{0} not found".format(self.path))
            # if the path is a file
            elif os.path.exists(full_path):
                self.handle_file(full_path)
            else:
                raise ServerException("Unkown object '{0}'".format(self.path))
        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, "r") as f:
                content = f.read()
            self.send_content(content, 200)
        except IOError as msg:
            msg = "'{0}' connot be read:{1}".format(self.path, msg)
            self.handle_error(msg)

    Error_Page = """\
        <html>
        <body>
        <h1>Error aceessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)


class ServerException(Exception):
    """inner server error"""
    pass


if __name__ == "__main__":
    httpAddress = ("", 8000)

    httpd = hs.HTTPServer(httpAddress, RequestHandler)
    httpd.serve_forever()
