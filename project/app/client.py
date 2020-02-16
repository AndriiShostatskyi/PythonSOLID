import asyncio
import json


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


# request = """<report><payer>100</payer><tax>Corporate Income Tax</tax><amount>25000</amount><year>2020</year></report>"""
# asyncio.run(tcp_echo_client(request))

report = {'payer': 1, 'tax': 'VAT', 'amount': 1500, 'year': 2020}
asyncio.run(tcp_echo_client(json.dumps(report)))
