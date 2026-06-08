import json
import os
import unittest
from unittest.mock import patch

from app import CLIENT_FRAME_TYPES, TELNYX_FRAME_TYPES, app, initial_text_frames, parse_message, text_frame


class ConversationRelayTestAppTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_instruction_fetch_returns_conversation_relay(self):
        env = {
            **os.environ,
            "CONVERSATION_RELAY_WS_URL": "wss://example.com/ws/conversation-relay",
            "CONVERSATION_RELAY_ACTION_URL": "https://example.com/callbacks/conversation-relay",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch("builtins.print"):
                response = self.client.post("/texml/inbound", data={"CallSid": "call-1"})

        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/xml")
        self.assertIn("<Connect", body)
        self.assertIn("<ConversationRelay", body)
        self.assertIn('url="wss://example.com/ws/conversation-relay"', body)
        self.assertIn('action="https://example.com/callbacks/conversation-relay"', body)
        self.assertNotIn("<Gather", body)
        self.assertNotIn("<Say", body)

    def test_instruction_fetch_derives_action_url(self):
        env = {
            key: value
            for key, value in os.environ.items()
            if key != "CONVERSATION_RELAY_ACTION_URL"
        }
        env["TELNYX_PUBLIC_BASE_URL"] = "https://example.com"

        with patch.dict(os.environ, env, clear=True):
            with patch("builtins.print"):
                response = self.client.post("/texml/inbound")

        body = response.get_data(as_text=True)

        self.assertIn('action="https://example.com/callbacks/conversation-relay"', body)

    def test_action_callback_accepts_json(self):
        with patch("builtins.print"):
            response = self.client.post(
                "/callbacks/conversation-relay",
                json={"event": "conversation_relay.ended", "callSid": "call-1"},
            )

        self.assertEqual(response.status_code, 204)

    def test_action_callback_accepts_form_data(self):
        with patch("builtins.print"):
            response = self.client.post(
                "/callbacks/conversation-relay",
                data={"CallSid": "call-1", "ConversationRelayStatus": "completed"},
            )

        self.assertEqual(response.status_code, 204)

    def test_parse_known_json_message(self):
        parsed = parse_message('{"type":"prompt","voicePrompt":"hello","lang":"en","last":true}')

        self.assertEqual(parsed["frame_type"], "prompt")
        self.assertEqual(parsed["direction"], "telnyx-to-client")
        self.assertEqual(parsed["payload"]["voicePrompt"], "hello")

    def test_parse_unknown_json_message(self):
        parsed = parse_message('{"event":"custom.event","value":1}')

        self.assertEqual(parsed["frame_type"], "custom.event")
        self.assertEqual(parsed["direction"], "unknown")
        self.assertEqual(parsed["payload"]["value"], 1)

    def test_parse_non_json_text_frame(self):
        parsed = parse_message("not json")

        self.assertEqual(
            parsed,
            {"frame_type": "text_frame", "direction": "unknown", "payload": {"text": "not json"}},
        )

    def test_parse_binary_frame(self):
        parsed = parse_message(b"abc")

        self.assertEqual(parsed, {"frame_type": "binary", "direction": "unknown", "payload": {"bytes": 3}})

    def test_text_frame_shape(self):
        self.assertEqual(json.loads(text_frame("hello", last=True)), {"type": "text", "token": "hello", "last": True})

    def test_initial_text_frames_shape(self):
        frames = initial_text_frames()

        self.assertEqual(frames[0]["type"], "text")
        self.assertFalse(frames[0]["last"])
        self.assertEqual(frames[1]["type"], "text")
        self.assertTrue(frames[1]["last"])

    def test_parse_all_asyncapi_telnyx_frame_types(self):
        for frame_type in TELNYX_FRAME_TYPES:
            with self.subTest(frame_type=frame_type):
                parsed = parse_message(json.dumps({"type": frame_type}))
                self.assertEqual(parsed["frame_type"], frame_type)
                self.assertEqual(parsed["direction"], "telnyx-to-client")

    def test_parse_all_asyncapi_client_frame_types(self):
        for frame_type in CLIENT_FRAME_TYPES:
            with self.subTest(frame_type=frame_type):
                parsed = parse_message(json.dumps({"type": frame_type}))
                self.assertEqual(parsed["frame_type"], frame_type)
                self.assertEqual(parsed["direction"], "client-to-telnyx")


if __name__ == "__main__":
    unittest.main()
