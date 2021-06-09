from telethon.sync import TelegramClient, events
from dotenv import load_dotenv, find_dotenv
from os import getenv
import time

load_dotenv(find_dotenv())

api_id = getenv("API_ID") or None
api_hash = getenv("API_HASH") or None
bot_token = getenv("BOT_TOKEN") or None

source_channel = int(getenv("SOURCE")) or None
target_channel = int(getenv("DESTINATION")) or None

max_skips = 10

def fetch_message(client, channel, i):
    return client.get_messages(channel, ids=i) or None

def fwd_message(client, channel, message):
    successful = False
    while not successful:
        try:
            if hasattr(message, 'text'):
                print(message.id,'->',message.text.partition('\n')[0])
            client.forward_messages(channel, message)
            successful = True
        except Exception as e:
            if hasattr(e, 'code'):
                if e.code == 420:
                    cooldown_wait(e.seconds)
            else:
                print("Not forwarding message: ", e)
                break

def fetch_and_fwd_message(client, src_channel, dst_channel, start_id=1):
    i = start_id
    skip_count = 0
    sleep_value = 0.5
    while True:
        msg = fetch_message(client, src_channel, i)

        if msg is not None:
            try:
                # print(msg.id, '-->', msg.text.partition('\n')[0])
                fwd_message(client, dst_channel, msg)
                sleep_value = 0.5
            except Exception as e:
                print("Excepton =>", e)
            finally:
                skip_count = 0
        else:
            print("Skipping [id:%d]: " % i, msg)
            # print("Skipping... %d" % skip_count, end='\r')
            skip_count += 1
            sleep_value = 0

        if skip_count >= max_skips:
            print(f"Skipped {max_skips} times in a row, should be the end of chat.")
            break

        i += 1
        time.sleep(sleep_value)

def cooldown_wait(seconds):
    while seconds >= 0:
        print("Waiting for cooldown... %d" % seconds)
        seconds -= 1
        time.sleep(1)
        print ("\033[A                                      \033[A")

def main():
    bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
    fetch_and_fwd_message(bot, source_channel, target_channel, 1)


if __name__ == '__main__':
    # cooldown_wait(100)
    main()
