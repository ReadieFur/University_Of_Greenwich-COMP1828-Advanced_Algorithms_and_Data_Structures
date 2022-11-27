from typing import Callable, Any
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection
from threading import Thread, Event
from time import sleep
import os

#Modified from: https://pythonbasics.org/webserver/
class Webserver(BaseHTTPRequestHandler):
    HOSTNAME = "localhost"
    PORT = 8080
    MIME_TYPES = {
        "html": "text/html",
        "css": "text/css",
        "js": "application/javascript",
        "json": "application/json",
    }

    def do_GET(self) -> None:
        """Handles GET requests."""
        #Get the request path.
        path = self.path
        if path.endswith("/"):
            path += "index.html"
        path = path[1:]
        local_path = os.path.join(os.getcwd(), "www", path)

        #Get the file extension and match it to a known MIME type.
        extension = path.split(".")[-1]
        mime_type = self.MIME_TYPES.get(extension, "text/plain")

        #Try to get the requested file's content.
        try:
            with open(local_path, "rb") as file:
                content = file.read()
        except FileNotFoundError:
            self.send_error(404)
            return

        #Send the response.
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: Any) -> None:
        #Only log debug messages if this is the main file.
        if __name__ == "__main__":
            super().log_message(format, *args)

    #Below is a very messy "async/awaiter" implementation that I can use to start and stop the webserver.
    @staticmethod
    def run() -> Callable[[], None]:
        reset_event = Event()
        end_event = Event()
        webserver_thread = Thread(target=Webserver.__start, args=(reset_event,end_event))
        webserver_thread.start()
        return lambda: Webserver.__stop(reset_event, end_event)

    @staticmethod
    def __start(reset_event: Event, end_event: Event) -> Event:
        # try:
        webserver = HTTPServer((Webserver.HOSTNAME, Webserver.PORT), Webserver)
        #We have to assign the event below to a discard variable to keep the instance in scope, otherwise GC will collect it and dispose of it early.
        end_watchdog = Thread(target=Webserver.__end_watchdog, args=(reset_event,))
        end_watchdog.start()
        while not reset_event.is_set():
            webserver.handle_request()
        webserver.server_close()
        # finally:
        end_event.set()

    @staticmethod
    def __end_watchdog(reset_event: Event) -> None:
        while not reset_event.is_set():
            sleep(1)
        #The webserver handle_request will wait for a request, meaning once we want to stop the webserver, we have to send a request to unblock the handle_request.
        connection = HTTPConnection(Webserver.HOSTNAME, Webserver.PORT)
        connection.request("GET", "/")
        connection.getresponse()

    @staticmethod
    def __stop(reset_event: Event, end_event: Event) -> None:
        reset_event.set()
        while not end_event.is_set():
            sleep(1)

if __name__ == "__main__":
    os.chdir(os.path.join(os.getcwd(), "src"))
    end_callback = Webserver.run()
    print(f"Webserver started at http://{Webserver.HOSTNAME}:{Webserver.PORT}")
    print("Press enter to stop the webserver")
    input()
    print("Stopping webserver...")
    end_callback()
    print("Webserver stopped.")
