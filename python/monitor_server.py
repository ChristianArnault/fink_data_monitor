#!/usr/bin/python

# Copyright 2018 AstroLab Software
# Author: Chris Arnault
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This the server part of the dataset monitor
run in the <host> machine as

> python monitor_server.py

Then, call in a web navigator the URL

http://<host>:24701/monitor.py

The monitor.py script has to be present on the <host> machine

"""

import http.server
 
PORT = 24701
server_address = ("", PORT)

server = http.server.HTTPServer
handler = http.server.CGIHTTPRequestHandler

handler.cgi_directories = ["/"]

print("Serveur actif sur le port :", PORT)

httpd = server(server_address, handler)
httpd.serve_forever()


