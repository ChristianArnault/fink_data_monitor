#!/usr/bin/python

# coding: utf-8

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

# coding: utf-8

"""
Dataset monitor

This is the client part.

The monitor.py script has to be present on the <host> machine

where the minimal HTML server has been activated as

> python server.py

Then, call in a web navigator the URL

http://<host>:24701/monitor.py
"""


import cgi
from pylivy.session import *
from pylivy.client import *
from variables import HTMLVariableSet


# ======================================================
LIVY_URL = "http://vm-75222.lal.in2p3.fr:21111"

form = cgi.FieldStorage()
print("Content-type: text/html; charset=utf-8\n")

client = LivyClient(LIVY_URL)

# init data
html = HTMLVariableSet(["started",
                        "simul",
                        "change_simul",
                        "livy_session",
                        "waiting_session",
                        "waiting_statement",
                        "livy_statement",
                        "kill_session"],
                       ["new_statement", "result"])

url = "/monitor.py"
method = "POST"

# ======================================================


def html_header():
    """
    Global & common html header. SHould be used everywhere

    Returns:
    --------
    out: str
    """
    return """
    <!DOCTYPE html>
    <head>
        <link rel="stylesheet" type="text/css" href="css/finkstyle.css">
        <title>Mon programme test</title>
    </head>
    <body>
    <div class="hero-image">
      <div class="hero-text">
        <h1 style="font-size:50px">Fink</h1>
        <h3>Alert dataset monitor</h3>
        <div class="topnav"> """


def html_trailer():
    """
    Global & common html trailer. SHould be used everywhere

    Returns:
    --------
    out: str
    """
    return """
      </div>
    <p>&copy; AstroLab Software 2018-2019</p>
  </div>
</div>

</body>
</html>
"""

def html_manage_simulation_mode(out: str) -> str:
    # manage Livy simulation
    will_change_simul = html.change_simul.is_set()

    print("<br>change simul = {}".format(will_change_simul))

    html.change_simul.reset()

    if will_change_simul:
        if html.simul.is_set():
            out += """<form action="{}" method="{}">""".format(url, method)
            out += """
                <br> Currently using real Livy"""
            html.simul.reset()
            out += html.to_form()
            out += """<button type="submit">Simul Livy</button>
            </form>
            """
        else:
            out += """<form action="{}" method="{}">""".format(url, method)
            out += """
                <br> Currently simulate Livy """
            html.simul.set(1)
            out += html.to_form()
            out += """<button type="submit">Use real Livy</button>
                </form>
            """
    else:
        if html.simul.is_set():
            out += """<form action="{}" method="{}">""".format(url, method)
            out += """
                <br> Currently simulate Livy&nbsp;"""
            html.change_simul.set(1)
            out += html.to_form()
            out += """
                <button type="submit">Use real Livy</button>
            </form>
            """
        else:
            out += """<form action="{}" method="{}">""".format(url, method)
            out += """
                <br> Currently using real Livy"""
            html.change_simul.set(1)
            out += html.to_form()
            out += """
                <button type="submit">Simul Livy</button>
            </form>
            """
        # out += html.debug()

    html.change_simul.reset()

    return out


# Read all HTML POST variables
html.read(form)

if not html.started.is_set():
    # Handle the very first launch to set the default
    html.simul.set(1)
    html.started.set(1)

# ======================================================
# the start of the WEB page
# ======================================================
out = html_header()

out = html_manage_simulation_mode(out)

# out += html.debug()

# Manage Livy session & Spark statements
out += """<form action="{}" method="{}">""".format(url, method)

if html.simul.is_set():
    if html.waiting_session.above(5):
        print("<br> session is now idle")
        html.waiting_session.reset()
        html.waiting_statement.reset()
        html.livy_statement.reset()
        html.livy_session.set(1)

    if html.waiting_statement.above(5):
        print("<br> statement just finished")
        html.waiting_session.reset()
        html.waiting_statement.reset()
        html.livy_statement.incr()

# debugging
# print("<br>")
# print("Keys = [", ",".join(form.keys()), "]")
# print(html.debug())

"""
Command interface
- select Livy simulation
- open session & wait for idle
- start statement & wait for completion
"""

if html.kill_session.is_set():
    session_id = html.livy_session.value
    try:
        client.delete_session(session_id)
    except:
        print("error killing session ", session_id)

    html.livy_session.reset()
    html.waiting_session.reset()
    html.kill_session.reset()

if html.livy_session.is_set():
    # statement management
    if not html.waiting_statement.is_set():
        out += """<br>session is idle: we may start a statement<br>"""
        html.waiting_statement.set(0)
        out += html.to_form()
        out += """
        Enter a Spark statement 
        <input type="text" name="new_statement" value="{}" /> 
        <input type="text" name="result" value="{}" />
        <button type="submit">Run</button>        
        """.format(html.new_statement.value, html.result.value)
    else:
        out += """<br>session is idle, we do wait a statement to complete<br>"""
        html.waiting_statement.incr()
        s = client.get_session(html.livy_session.value)
        if not html.livy_statement.is_set():
            st = client.create_statement(s.session_id, html.new_statement.value)
            html.livy_statement.set(st.statement_id)
        else:
            st = client.get_statement(s.session_id, html.livy_statement.value)
            if st.state == StatementState.AVAILABLE:
                html.waiting_statement.reset()
                html.result.set(st.output.text)
                print("<br>", html.result.value)
                html.livy_statement.reset()

        out += html.to_form()
        out += """<button type="submit">waiting statement to complete</button>"""
else:
    # session management
    if not html.waiting_session.is_set():
        out += """<br>No session<br>"""
        html.waiting_session.set(0)

        # print(html.waiting_session.debug())

        html.waiting_statement.reset()
        out += html.to_form()
        out += """<button type="submit">Open a session</button>"""
    else:
        # we have requested a new session thus waiting_session is set

        if html.simul.is_set():
            html.waiting_session.incr()
        else:

            if not html.livy_session.is_set():
                print("Create a session ")
                s = client.create_session(SessionKind.PYSPARK)
                print("<br> session {} <br>".format(s.session_id))
                html.livy_session.set(s.session_id)

            # we test if the session is already idle
            s = client.get_session(html.livy_session.value)
            if s.state == SessionState.IDLE:
                print("<br> session is now idle")
                html.waiting_session.reset()
                html.waiting_statement.reset()
                html.livy_statement.reset()
                html.new_statement.reset()

        out += """<br>Waiting session to become idle<br>"""
        out += html.to_form()
        out += """<button type="submit">waiting session</button>"""

out += """</form>"""

if html.livy_session.is_set():
    out += """<form action="{}" method="{}">""".format(url, method)
    html.kill_session.set(1)
    out += html.to_form()
    out += """
         <button type="submit">Delete the session</button>
    </form>
    """

out += html_trailer()

print(out)

