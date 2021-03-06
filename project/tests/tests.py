import json
import socket
import subprocess
import time
import unittest
from pathlib import Path

TCP_IP = '127.0.0.1'
TCP_PORT = 5555
BUFFER_SIZE = 512


class TestsBase:
    def setUp(self):
        binary = Path(__file__).absolute().parents[1] / Path('./app/server.py')
        start_command = 'exec python {} {} {}'.format(binary, TCP_PORT, self.report_format)
        self.process = subprocess.Popen(start_command, stdout=subprocess.PIPE, shell=True)
        time.sleep(0.1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((TCP_IP, TCP_PORT))

    def tearDown(self):
        self.sock.close()
        self.process.stdout.close()
        self.process.kill()
        self.process.wait()


class JsonTaxReportTests(TestsBase, unittest.TestCase):
    report_format = 'json'

    def test_sending_tax_report_succeeds(self):
        request = json.dumps({'payer': 100, 'tax': 'Corporate Income Tax', 'amount': 25000, 'year': 2020})

        self.sock.send(request.encode())
        response = self.sock.recv(BUFFER_SIZE)

        self.assertEqual(json.loads(response.decode()), {'status': 'OK'})

    def test_sending_tax_report_fails_due_to_missing_data(self):
        request = json.dumps({
            'payer': 100,
            'tax': 'Corporate Income Tax',
        })

        self.sock.send(request.encode())
        response = self.sock.recv(BUFFER_SIZE)
        self.assertEqual(json.loads(response.decode()), {'status': 'NOK'})

    def test_sending_tax_report_fails_due_to_invalid_format_of_data(self):
        request = 'Something not JSON'

        self.sock.send(request.encode())
        response = self.sock.recv(BUFFER_SIZE)

        self.assertEqual(json.loads(response.decode()), {'status': 'NOK'})


class XmlTaxReportTests(TestsBase, unittest.TestCase):
    report_format = 'xml'

    def test_sending_tax_report_succeeds(self):
        request = """<report><payer>100</payer><tax>Corporate Income Tax</tax>
                        <amount>25000</amount><year>2020</year></report>"""

        self.sock.send(request.encode())
        response = self.sock.recv(BUFFER_SIZE)

        self.assertEqual(response.decode(), '<status>OK</status>')

    def test_sending_tax_report_fails_due_to_missing_data(self):
        request = """<report>
                        <payer>100</payer>
                        <tax>Corporate Income Tax</tax>
                    </report>"""

        self.sock.send(request.encode())
        response = self.sock.recv(BUFFER_SIZE)
        self.assertEqual(response.decode(), '<status>NOK</status>')

    def test_sending_tax_report_fails_due_to_invalid_format_of_data(self):
        request = 'Something not XML'

        self.sock.send(request.encode())
        response = self.sock.recv(BUFFER_SIZE)

        self.assertEqual(response.decode(), '<status>NOK</status>')


if __name__ == '__main__':
    unittest.main()
