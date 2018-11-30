import uuid
import base64


def get_uid():
    return str(base64.urlsafe_b64encode(uuid.uuid4().bytes+uuid.uuid4().bytes))[2:-2]