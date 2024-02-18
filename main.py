# main.py
from dtraccar import kml, traccar
import os

from fastapi import FastAPI, Request, Form, datastructures
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


cfg = {
    'url': 'https://tracking.seriousfamilybusiness.net',
    # User credentials, traccar server
    'user': 'dieter.chvatal@gmail.com',
    'password': '81aNUlLY',
}

app = FastAPI()


@app.post("/form/", response_class=HTMLResponse)
async def download_kml(
    name: str = Form('out'),
    device: str = Form('WMB Tk106'),
    startdate: str = Form("YYYY-MM-DDTHH:MM:SSZ"),
    enddate: str = Form("YYYY-MM-DDTHH:MM:SSZ")
):

    options = {
        'name': name,
        'device': device,
        'startdate': startdate,
        'enddate': enddate,
        'maxpoints': '2500',
    }

    print(options)
    data = traccar.getData(cfg, options)  # lese Daten über Traccar API
    kmldata = kml.tokml(data)  # Daten umwandeln

    file_name = options['name']+'.kml'
    file_path = os.getcwd() + "/" + file_name

    kml.writeKML(cfg, options, file_path, kmldata)  # als KML ausgeben

    return FileResponse(filename=file_name, path=file_path, media_type='application/octet-stream')


@app.get("/devices", response_class=HTMLResponse)
async def devices(request: Request):
    dres = traccar.getDevices(cfg)
    return templates.TemplateResponse("test.html", {"request": request, "list": dres})


@app.get("/travels", response_class=HTMLResponse)
async def devices(request: Request):

    options = {
        'device': '4',
        'startdate': "2019-01-01T00:00:00Z",
        'enddate': "2100-01-01T00:00:00Z",
    }

    dres = traccar.getTravels(cfg, options)
    return JSONResponse(dres)


@app.get("/", response_class=HTMLResponse)
async def showhtml(request: Request):
    dres = traccar.getDevices(cfg)

    options = {
        'device': '4',
        'startdate': "2019-01-01T00:00:00Z",
        'enddate': "2021-10-01T00:00:00Z",
    }

    tres = traccar.getTravels(cfg, options)

    return templates.TemplateResponse("showhtml.html", {"request": request, "list": dres, "travels": tres})
