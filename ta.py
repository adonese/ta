from starlette.applications import Starlette
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
import uvicorn
from pin import PinBlock
from utils import http_errors_or_ok, is_hex
from utils import RequestFields, wants_json, get_cookies
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import typesystem
import uuid
import pickle
import datetime
import json

# templates dir
forms = typesystem.Jinja2Forms(package="bootstrap4")
templates = Jinja2Templates(directory="templates")
statics = StaticFiles(directory="statics", packages=["bootstrap4"])

async def homepage(request):
    # get the cookie. If it is not found, then set a new cookie
    # for this particular user (so they can retrieve their data later)

    
    # data = await request.form()
    form = forms.Form(RequestFields)
    context = {"request": request, "form": form}

    response = templates.TemplateResponse("index.html", context)
    response.set_cookie("my_cookie", id)
    return response

async def submit(request):
    if wants_json(request):
        try:
            b = await request.json()
        except Exception as e:
            return JSONResponse({"message": "Empty or malformed Json"}, 400)
        data, errors = RequestFields.validate_or_error(b)
    
        if errors:
            return JSONResponse(dict(errors), 400)
        if not is_hex(data.get("twk")) or not is_hex(data.get("tmk")):
            return JSONResponse({"error": "tmk and twk should be hex strings"}, 400)

        pin_calculation = PinBlock(b.get("pin"), b.get("pan"), b.get("twk"), b.get("tmk"))
        pin = pin_calculation.encrypted_pin_block()
        return JSONResponse({"pin_block": pin}, 200)

    form = await request.form()
    data, errors = RequestFields.validate_or_error(form)
    print(errors)
    if errors:
        form = forms.Form(RequestFields, values=data, errors=errors)
        context = {"request": request, "form": form}
        return templates.TemplateResponse("index.html", context)

    if not is_hex(data.get("twk")) or not is_hex(data.get("tmk")):
        form = forms.Form(RequestFields)
        context = {"request": request, "error_code":"not_hex", "form": form}
        return templates.TemplateResponse("index.html", context)

    pin_calculation = PinBlock(form.get("pin"), form.get("pan"), form.get("twk"), form.get("tmk"))
    pin = pin_calculation.encrypted_pin_block()

    id = get_cookies(request)

    context = {"request": request, "form": form, "pin": pin}
    return templates.TemplateResponse("success.html", context)


async def reverse(request):
    
    try:
        b = await request.json()
    except Exception as e:
        return JSONResponse({"message": "Empty or malformed Json"}, 400)

    pin_calculation = PinBlock(pin="3232", pan=b.get("pan"), twk=b.get("twk"), tmk=b.get("tmk"))
    pin = pin_calculation.reverse_pin(b.get("pinblock"))
    return JSONResponse({"pin": pin}, 200)


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage, methods=["GET"]),
        Route("/", submit, methods=["POST"]),
        Route("/reverse", reverse, methods=["POST"]),
        Mount("/statics", statics, name="static"),

    ],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
