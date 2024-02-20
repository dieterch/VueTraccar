############################################################################################################
############################################################################################################
##                                                                                                        ##
## Quart Vuetify Template  (c)2024 Dieter Chvatal                                                         ##
##                                                                                                        ##
############################################################################################################
############################################################################################################

import uvicorn
import asyncio
import json
import math
import os
from pprint import pformat as pf
from pprint import pprint as pp
from quart import Quart, jsonify, render_template, request, redirect, url_for, send_file, send_from_directory
from quart_cors import cors
import subprocess
import time

try:
    import tomllib as toml
except ImportError as e:
    print('tomllib not found. using "tomli" instead.')
    import tomli as toml

from dtraccar import kml, traccar2 as traccar

with open("config.toml", mode="rb") as fp:
    cfg = toml.load(fp)

# https://stackoverflow.com/questions/37039835/how-to-change-jinja2-delimiters
class CustomQuart(Quart):
    jinja_options = Quart.jinja_options.copy()
    jinja_options.update(dict( block_start_string='<%', block_end_string='%>', variable_start_string='%%', 
                              variable_end_string='%%',comment_start_string='<#',comment_end_string='#>',))

# use the same directories as in the vite.config.js
app = CustomQuart(__name__, static_folder = "dist/static", template_folder = "dist", static_url_path = "/static")
app = cors(app, allow_origin="*")
app.config.from_object(__name__)


# force IE or Chrome compatibility, cache rendered page for x minutes.
# uncomment to disable caching, e.g. for development when you are changing the frontend often.
@app.after_request
async def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/devices")
async def devices():
    return traccar.getDevices(cfg)

# route to call for traccar data
@app.route("/route", methods=['POST'])
async def route():
    await request.get_data()
    if request.method == 'POST':
        req = await request.json
        return traccar.getData(cfg, req)

# route to call for traccar data
@app.route("/events", methods=['POST'])
async def events():
    await request.get_data()
    if request.method == 'POST':
        req = await request.json
        return traccar.getEvents(cfg, req)

# route to call for traccar data
@app.route("/travels", methods=['POST'])
async def travels():
    await request.get_data()
    if request.method == 'POST':
        req = await request.json
        return traccar.getTravels(cfg, req)

# route to download kml file
@app.route("/download.kml", methods=['POST'])
async def downloadkml():
    await request.get_data()
    if request.method == 'POST':
        req = await request.json
        file_name , full_path = traccar.downloadkml(cfg, req)
        return await send_file(full_path, attachment_filename=file_name, as_attachment=True)

@app.route("/plotmaps", methods=['POST'])
async def plotmaps():
    await request.get_data()
    if request.method == 'POST':
        req = await request.json
        return traccar.plotmaps(cfg, req)

# deliver the vuetify frontend
@app.route("/")
async def index():
    return await render_template('index.html')

if __name__ == '__main__':
    print('''
\033[H\033[J
********************************************************
* Vuetify Quart Template V0.01  (c)2024 Dieter Chvatal *
* Async Backend                                        *
********************************************************
''')
    try:
        if 'PRODUCTION' in os.environ:
            uvicorn.run('app:app', host='0.0.0.0', port=5999, log_level="info")
        else:
            uvicorn.run('app:app', host='0.0.0.0', port=5999, log_level="info", reload=True, reload_dirs =['.','./dist'], reload_includes=['*.py','*.js','*.toml'])
            #asyncio.run(app.run_task(host='0.0.0.0', port=5999, debug=True))
    except Exception as e:
        print(str(e))
    print('Bye!')