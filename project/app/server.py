import argparse
import asyncio
import json
from enum import Enum
from xml.etree.ElementTree import fromstring


class ReportFormat(Enum):
    JSON = 0
    XML = 1


REPORT_FORMATS = {'json': ReportFormat.JSON, 'xml': ReportFormat.XML}


def store_report(report_dict):
    # TODO: implement storage of reports
    pass


def validate_report(report_dict):
    if set(report_dict.keys()) != {'payer', 'tax', 'amount', 'year'}:
        raise Exception('Invalid report')


class Session:
    def __init__(self, format_name):
        self.report_format = REPORT_FORMATS[format_name]
        self._max_length = 512

    async def handle(self, reader, writer):
        try:
            data = await reader.read(self._max_length)
            request = data.decode()
            response = None
            print(f"Received {request!r}")

            if self.report_format == ReportFormat.JSON:
                response = self.handle_json_report(request)

            elif self.report_format == ReportFormat.XML:
                response = self.handle_xml_report(request)

            if response is not None:
                print(f"Sent: {response!r}")
                writer.write(response.encode())
                await writer.drain()

        except Exception as e:
            print(e)

        print("Close the connection")
        writer.close()

    def handle_json_report(self, report):
        try:
            report = json.loads(report)
            validate_report(report)
            store_report(report)
            return json.dumps({'status': 'OK'})
        except Exception as e:
            print(e)
            return json.dumps({'status': 'NOK'})

    def handle_xml_report(self, report):
        try:
            tree = fromstring(report)
            report = ({child.tag: child.text for child in tree})
            validate_report(report)
            store_report(report)
            return '<status>OK</status>'
        except Exception as e:
            print(e)
            return '<status>NOK</status>'


async def run_server(port, format_name):
    server = await asyncio.start_server(Session(format_name).handle, '127.0.0.1', port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Service to receive tax reports')
    parser.add_argument('Port', metavar='port', type=int, help='Port number for the server')
    parser.add_argument('Format', metavar='format', type=str, help='Format of tax reports (json or xml)')
    args = parser.parse_args()
    return args.Port, args.Format


if __name__ == '__main__':
    asyncio.run(run_server(*parse_arguments()))
