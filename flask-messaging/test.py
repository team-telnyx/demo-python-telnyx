from _future_ import absolute_import, division, print_function
from telnyx import Webhook
import json
public_key = "****"
data = {
    "event_type": "conference.created",
    "id": "2417da8b-40db-4cff-aa64-2e99ae622a0b",
    "occurred_at": "2020-09-09T16:42:36.970189Z",
    "payload": {
      "call_control_id": "v2:dzXVmMm8tSSjHiV31PR7kfEvbnTqfsVFWcRZvovzXvUkVTzF4LmINA",
      "call_leg_id": "76e14842-f2bb-11ea-ad61-02420a0f6c68",
      "call_session_id": "76e159ea-f2bb-11ea-a796-02420a0f6c68",
      "client_state": "N2Y1NDAyOGEtYzE5Mi00YjVhLTgxZmMtY2FjYmM0NWNiZThm",
      "conference_id": "d97bf063-2111-4457-9f9c-dad4c25f90ff",
      "connection_id": "1447945888356894473"
    },
    "record_type": "event"
  }
def webhooks():
    body = json.dumps(data)
    signature = "ee8Uh8z9km7VYwb+cdPB8O74DBtvEzrrsC6o7UNWNZ4u7mSk3a7NGrUVqG7zTCjBS1HxmdkX4DAR3o8Z13qFDA=="
    timestamp = "1599669757"
    Webhook.construct_event(body, signature, timestamp, 300000)
    return "", 200
webhooks()



from __future__ import absolute_import, division, print_function
import base64
import json
import time
from nacl.encoding import Base64Encoder
from nacl.signing import VerifyKey
#import telnyx
#from telnyx import er
class Webhook(object):
    DEFAULT_TOLERANCE = 30000
    @staticmethod
    def construct_event(
        payload, signature_header, timestamp, tolerance=DEFAULT_TOLERANCE, api_key=None
    ):
        if WebhookSignature.verify(payload, signature_header, timestamp, tolerance):
            data = json.loads(payload)
         # event = telnyx.Event.construct_from(data, api_key)
            return "event"
class WebhookSignature(object):
    @classmethod
    def verify(cls, payload, signature, timestamp, tolerance=None):
        if hasattr(timestamp, "encode"):
            timestamp = timestamp.encode("utf-8")
        if hasattr(payload, "encode"):
            payload = payload.encode("utf-8")
        signed_payload = timestamp + b"|" + payload
        public_key = "*****"
        # verify the data
        key = VerifyKey(public_key, encoder=Base64Encoder)
        if not key.verify(signed_payload, signature=base64.b64decode(signature)):
            raise error.SignatureVerificationError(
                "Signature is invalid and does not match the payload",
                signature,
                payload,
            )
        if tolerance and int(timestamp) < time.time() - tolerance:
            raise error.SignatureVerificationError(
                "Timestamp outside the tolerance zone (%s)" % timestamp,
                signature,
                payload,
            )
        return True