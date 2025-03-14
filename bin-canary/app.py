#!/usr/bin/env python3

__author__ = "Joseph Ryan-Palmer"
__version__ = "0.5"

import requests
import argparse
import os
import logging
import datetime
from time import sleep
from discord import Webhook, RequestsWebhookAdapter
from counciladaptors import mhclg


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def send_ntfy_message(url, message, title=None, priority=None, emoji=None):
    headers = {
        "Title": title,
        "Priority": str(priority) if priority else None,
        "Tags": emoji if emoji else None
    }
    headers = {key: value for key, value in headers.items() if value is not None}

    response = requests.post(url, data=message+ " Powered by Bin Canary.", headers=headers)

    if response.status_code == 200:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification. Status code: {response.status_code}")

def postcode_spacer(postcode):
    return postcode[:-3] + " " + postcode[-3:]


def parser_function():
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", help="Home address",
                    type=str, required='ADDRESS' not in os.environ, default=os.environ.get('ADDRESS'))
    parser.add_argument("--postcode", help="Home postcode",
                    type=str, required='POSTCODE' not in os.environ, default=os.environ.get('POSTCODE'))
    parser.add_argument("--council", help="Local Council",
                    type=str, required='COUNCIL' not in os.environ, default=os.environ.get('COUNCIL'))
    parser.add_argument("--interval", help="Checking interval (Hours)",
                    type=str, required='INTERVAL' not in os.environ, default=os.environ.get('INTERVAL'))
    parser.add_argument("--discord-hook", help="Discord webhook",
                    type=str, default=os.environ.get('DISCORD'))
    parser.add_argument("--ntfy-hook", help="NTFY webhook",
                    type=str, default=os.environ.get('NTFY'))
    parser.add_argument("--delay", help="Delay notification until 7 PM",
                    type=str, default=os.environ.get('DELAY', "True"))
    parser.add_argument(
    "--version",
    action="version",
    version="%(prog)s (version {version})".format(version=__version__))

    return parser.parse_args()

def tomorrow_or_not(bin_dates):
    tomorrow_arr = []
    for type, bin_date in bin_dates.items():
        logging.debug(bin_date)
        bin_date_obj = datetime.datetime.strptime(bin_date, "%d/%m/%Y").date()
        days_difference = (bin_date_obj - datetime.datetime.now().date()).days
        if days_difference < 2 and days_difference >= 1:
            tomorrow_arr.append(type)
        else:
            logging.debug(f"Bin type: {type}, Collection date: {bin_date}, Days until collection: {days_difference}")
    return tomorrow_arr

def check_for_valid_dates(bin_dates):
    for date in bin_dates.values():
        try:
            datetime.datetime.strptime(date, "%d/%m/%Y")
        except (ValueError, TypeError):
            logging.error("Invalid date format")
            return False
    return True

def lmk(council, address, postcode, interval, discord, ntfy, delay):
    while True:
        logging.info("Checking if bin due in next {} hours".format(interval))
        bin_dates = council.extract_bin_dates(address, postcode_spacer(postcode))
        while not check_for_valid_dates(bin_dates):
            logging.error("Invalid dates found, retrying...")
            bin_dates = council.extract_bin_dates(address, postcode_spacer(postcode))
        bin_type_arr = tomorrow_or_not(bin_dates)
        if len(bin_type_arr) > 0:
            message = ""
            if len(bin_type_arr) > 1:
                message = "Bins will be collected tomorrow - {}.".format(", ".join(bin_type_arr))
            elif len(bin_type_arr) == 1:
                message = "Bin will be collected tomorrow - {}.".format(bin_type_arr[0])
            logging.info("Bin due tomorrow - {}".format(bin_type_arr))
            logging.info("Sending notification")
            if delay:
                current_time = datetime.datetime.now()
                target_time = current_time.replace(hour=19, minute=0, second=0, microsecond=0)
                if current_time > target_time:
                    logging.info("Current time is after 7 PM, sending notification immediately.")
                else:
                    sleep_duration = (target_time - current_time).total_seconds()
                    logging.info(f"Sleeping until 7 PM, which is in {sleep_duration} seconds")
                    sleep(sleep_duration)
                logging.info(f"Sleeping until 7 PM, which is in {sleep_duration} seconds")
                sleep(sleep_duration)

            if discord:
                webhook = Webhook.from_url(discord, adapter=RequestsWebhookAdapter())
                webhook.send(message)
                logging.info("Discord Notification sent")
            if ntfy:
                send_ntfy_message(ntfy, message, "Bins due to be collected tomorrow", 1, "wastebasket")
                logging.info("NTFY Notification sent")

        if interval and int(interval) != 24:
            sleep_duration = int(interval) * 3600
            logging.info(f"Sleeping for {interval} hours")
        else:
            now = datetime.datetime.now()
            next_check = now.replace(hour=18, minute=0, second=0, microsecond=0)
            if now > next_check:
                next_check += datetime.timedelta(days=1)
                sleep_duration = (next_check - now).total_seconds()
                logging.info(f"Sleeping until next check at 6 PM, which is in {sleep_duration} seconds")
        sleep(sleep_duration)

def main():
    logging.info("Bin Canary v{}".format(__version__))
    arg = parser_function()
    council = mhclg.mhclg().council_finder(arg.council)
    logging.info("Extracting initial bin dates")
    bin_dates = council.extract_bin_dates(arg.address, postcode_spacer(arg.postcode))
    logging.info(bin_dates)
    lmk(council, arg.address, arg.postcode, arg.interval, arg.discord_hook if arg.discord_hook else None, arg.ntfy_hook if arg.ntfy_hook else None, False if arg.delay.lower() == "false" else True)

if __name__ == "__main__":
    main()
