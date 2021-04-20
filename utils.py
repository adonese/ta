"""
return corresponding http errors
"""
import typesystem
import uuid 

# custom schema field
class HexNumber(typesystem.String):
    # add new error-code and error message 
    typesystem.String.errors['hex_number'] = 'Must be a hexadicimal number'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def validate(self, value, **kwargs):
        try:
            bytes.fromhex(value)
        except Exception as e:
            raise self.validation_error("hex_number")
        return super().validate(value, **kwargs)


class RequestFields(typesystem.Schema):
    pin = typesystem.String(title="PIN", max_length=4, min_length=4)
    pan = typesystem.String(title="PAN", max_length=19, min_length=16)
    twk = HexNumber(title="Working Key", max_length=16, min_length=16)
    tmk = HexNumber(title="Master Key", max_length=16, min_length=16)


def is_json_client(request):
    return request.headers["content-type"] == "application/json"

def get_cookies(request)->str:
    id = request.cookies.get("my_cookie")
    
    if not id:
        # the user is not registered
        id = str(uuid.uuid4())
    return id