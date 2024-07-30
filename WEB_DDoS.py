from flask import Flask, request, jsonify
import aiohttp
import asyncio
from faker import Faker

app = Flask(__name__)
fake = Faker()

async def fetch(session, url, user_agent):
    headers = {'User-Agent': user_agent}
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def send_requests(url, num_requests):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_requests):
            user_agent = fake.user_agent()
            tasks.append(fetch(session, url, user_agent))
        responses = await asyncio.gather(*tasks)
        return responses

@app.route('/send_requests', methods=['POST'])
def send_requests_endpoint():
    data = request.json
    url = data.get('url')
    num_requests = data.get('num_requests')

    if not url or not num_requests:
        return jsonify({'error': 'Missing url or num_requests'}), 400

    try:
        num_requests = int(num_requests)
    except ValueError:
        return jsonify({'error': 'num_requests must be an integer'}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    responses = loop.run_until_complete(send_requests(url, num_requests))
    loop.close()

    return jsonify({'responses': responses})

if __name__ == '__main__':
    app.run(debug=True)