"""
return corresponding http errors
"""
import typesystem
import uuid 

class RequestFields(typesystem.Schema):
    pin = typesystem.String(title="PIN", max_length=4, min_length=4)
    pan = typesystem.String(title="PAN", max_length=19, min_length=16)
    twk = typesystem.String(title="Working Key", max_length=16, min_length=16)
    tmk = typesystem.String(title="Master Key", max_length=16, min_length=16)

class http_errors_or_ok:
    """
    returns dict of {"field": "error_message"}
    pin length should be 4 (perhaps six?)
    pan length: 16 or 19
    twk, tmk: hex, 16
    """
    def __init__(self, request: dict):
        self.request = request

    def validate_common(self, field, **kwargs):
        errors = {}
        length = kwargs.get("length")
        if self.request.get(field) == None:
            errors[field] = "This field should not be empty"
            return errors

        if not isinstance(length, list):
            length = list([length])

        if not len(self.request.get(field)) in length:
            errors[field] = f"{field} length should be in range {length}"
            return errors

    def handle_keys(self, field, **kwargs):
        length = kwargs.get("length")
        errors = {}
        if self.request.get(field) == None:
            errors[field] = "This field should not be empty"
            return errors

        if not isinstance(length, list):
            length = list([length])

        if not len(self.request.get(field)) in length:
            errors[field] = f"{field} length should be in range {length}"
            return errors
        try:
            bytes.fromhex(self.request.get(field))
        except ValueError:
            errors[field] = "This field should be all hex"
            return errors

    def errors(self)->list:
        pin_error = self.validate_common("pin", length=4)
        pan_error = self.validate_common("pan", length=[19, 16])
        twk_error = self.handle_keys("twk", length=16)
        tmk_error = self.handle_keys("tmk", length=16)
        errors = []
        for err in [pin_error, pan_error, twk_error, tmk_error]:
            if err:
                errors.append(err)
        return errors
    
    def has_errors(self):
        if self.errors():
            return True
        return False

def wants_json(request):
    if request.headers["content-type"] == "application/json":
        return True
    return False

#TODO add this to typesystem when they support custom validator fields
def is_hex(hex_string: str) -> (bool):
    try:
        bytes.fromhex(hex_string)
        return True
    except Exception as e:
        return False


def get_cookies(request)->str:
    id = request.cookies.get("my_cookie")
    
    if not id:
        # the user is not registered
        id = str(uuid.uuid4())
    return id