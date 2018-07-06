from unittest import TestCase

from api import ini_serializer

EXPECTED_RESULT={
    "_meta": {
        "hostvars": {
            "host1": {
                "123": "45632",
                "567": "890",
                "port": "45632"
            },
            "host2": {
                "a": "b"
            },
            "host4": {
                "ansible_ssh_port": "2233"
            }
        }
    },
    "atlanta": {
        "hosts": [
            "host1",
            "host2"
        ]
    },
    "raleigh": {
        "hosts": [
            "host1",
            "host4",
            "host3"
        ]
    },
    "southeast": {
        "children": [
            "atlanta",
            "raleigh"
        ],
        "vars": {
            "some_server": "foo.southeast.example.com",
            "halon_system_timeout": "30",
            "self_destruct_countdown": "60",
            "escape_pods": "2"
        }
    },
    "usa": {
        "children": [
            "southeast",
            "northeast"
        ]
    }
}


class INITest(TestCase):
    def test_conversion(self):
        result = ini_serializer.serializer(ini_serializer.ini)
        self.assertDictEqual(result, EXPECTED_RESULT)

    def test_invalid_data(self):
        data = "123"
        with self.assertRaises(ValueError):
            ini_serializer.serializer(data)
