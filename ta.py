from starlette.applications import Starlette
from starlette.responses import JSONResponse, RedirectResponse
import uvicorn
from pin import PinBlock
from utils import http_errors_or_ok
from utils import RequestFields, wants_json
from starlette.templating import Jinja2Templates
import typesystem

# templates dir
forms = typesystem.Jinja2Forms(package="bootstrap4")
templates = Jinja2Templates(directory="templates")

app = Starlette(debug=True)

@app.route("/", methods=["GET"])
async def homepage(request):
    form = forms.Form(RequestFields)
    context = {"request": request, "form": form}
    return templates.TemplateResponse("index.html", context)

@app.route("/", methods=["POST"])
async def submit(request):
    if wants_json(request):
        try:
            b = await request.json()
        except Exception as e:
            return JSONResponse({"message": "Empty or malformed Json"}, 400, media_type="application/json")
        data, errors = RequestFields.validate_or_error(b)
    
        if errors:
            return JSONResponse(dict(errors), 400, media_type="application/json")
        pin_calculation = PinBlock(b.get("pin"), b.get("pan"), b.get("twk"), b.get("tmk"))
        pin = pin_calculation.encrypted_pin_block()
        return JSONResponse({"pin_block": pin}, 200, media_type="application/json")

    form = await request.form()
    data, errors = RequestFields.validate_or_error(form)
    print(errors)
    if errors:
        form = forms.Form(RequestFields, values=data, errors=errors)
        context = {"request": request, "form": form}
        return templates.TemplateResponse("index.html", context)

    pin_calculation = PinBlock(form.get("pin"), form.get("pan"), form.get("twk"), form.get("tmk"))
    pin = pin_calculation.encrypted_pin_block()       
    context = {"request": request, "form": form, "pin": pin}
    return templates.TemplateResponse("success.html", context)

@app.route("/success", methods=["GET"])
async def success(request):
    context = {"request": request}
    return templates.TemplateResponse("success.html", context)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
