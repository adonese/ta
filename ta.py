from starlette.applications import Starlette
from starlette.responses import JSONResponse
import uvicorn
from pin import PinBlock
from utils import http_errors_or_ok
from utils import RequestFields


app = Starlette(debug=True)

@app.route("/pin", methods=["POST"])
@app.route("/", methods=["POST"])
async def pin_service(request):
    b = await request.json()
    errors = RequestFields.validate_or_error(b)
 
    if errors.error:
        return JSONResponse({"error": errors}, 400, media_type="application/json")
    pin_calculation = PinBlock(b.get("pin"), b.get("pan"), b.get("twk"), b.get("tmk"))
    pin = pin_calculation.encrypted_pin_block()
    return JSONResponse({"pin_block": pin}, 200, media_type="application/json")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
