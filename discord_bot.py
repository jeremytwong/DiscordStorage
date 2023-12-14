import asyncio
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import io
import discord
from discord.ext import commands
from flask import Flask, request
import os
import threading
import base64

app = Flask(__name__)

client = discord.Client()

executor = ThreadPoolExecutor(max_workers=5)

@app.route('/send_file', methods=['POST'])
def send_file():
    file = request.files['file']
    file_data = file.read()  # read file data
    base64_data = base64.b64encode(file_data).decode()  # convert to base64
    client.loop.create_task(send_file_to_discord(base64_data, file.filename))
    return 'File sent to Discord successfully'

async def send_file_to_discord(base64_data, filename):
    channel_id = ''  # replace with your channel id
    channel = client.get_channel(int(channel_id))
    
    chunk_size = 24 * 1024 * 1024 * 3//4  # 18MB, to account for base64 overhead
    for i in range(0, len(base64_data), chunk_size):
        chunk = base64_data[i:i+chunk_size]
        try:
            # Save the chunk as a binary file in memory
            file = io.BytesIO(chunk.encode())
            discord_file = discord.File(file, filename=f'{filename}_{i//chunk_size + 1}.txt')
            
            # Upload the text file to Discord
            await channel.send(file=discord_file)
            print(f'Sent chunk {i//chunk_size + 1}')
        except Exception as e:
            print(f'Error sending chunk {i//chunk_size + 1}: {e}')


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

def run_flask():
    app.run(port=5001, debug=True, use_reloader=False)

if __name__ == '__main__':
    # Run Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Run Discord bot
    client.run('') # replace with your bot token