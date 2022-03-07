import asyncio
import datetime
import random
import requests
import os
import time


from client_factory import ClientFactory
from telethon import errors
from telethon import functions, types

from text_generator import generate_text


root_directory = os.path.dirname(os.path.abspath(__file__))

settings_obj = ClientFactory.create_client(session_name="report")
client = settings_obj['client']
host = settings_obj['host']

print('Bot started')


response = requests.get(host)

channel_list = response.json()['channels']

with open(os.path.join(root_directory, 'banned'), 'r') as f:
    banned_list = f.readlines()


async def main():
    number_of_channels_rep = 100
    number_completed = 0

    with open(os.path.join(root_directory, 'banned'), 'a') as f_ban:
        for telegram_channel in channel_list:
            if number_completed <= number_of_channels_rep:
                if "https://" in telegram_channel:
                    telegram_channel = telegram_channel.split('/')[-1]
                elif '@' in telegram_channel:
                    telegram_channel = telegram_channel[1:]
                if telegram_channel not in banned_list[0].split(' '):
                    f_ban.write(f'{telegram_channel} ')
                    try:
                        result = await client(functions.account.ReportPeerRequest(
                            peer=telegram_channel,
                            reason=types.InputReportReasonSpam(),
                            message=generate_text())
                        )
                        print(number_completed, telegram_channel.strip(), result)
                        number_completed += 1
                    except ValueError:
                        print("Channel not found")
                        requests.post(url=host, data=telegram_channel)
                    except errors.UsernameInvalidError:
                        print("Nobody is using this username, or the username is unacceptable")
                        requests.post(url=host, data=telegram_channel)
                    except errors.FloodWaitError as e:
                        seconds_left = e.seconds
                        while seconds_left > 0:
                            print("Flood wait error. Waiting for ", str(datetime.timedelta(seconds=seconds_left)))
                            seconds_left -= 60
                            await asyncio.sleep(60)

                    await asyncio.sleep(10 + 2 * random.randint(1, 30) + 2 * random.random())

            else:
                print("number of channel were exceeded, pls enter CTRL+C")
                time.sleep(600)
                break


with client:
    client.loop.run_until_complete(main())
