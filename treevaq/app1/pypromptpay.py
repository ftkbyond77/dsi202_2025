# -*- coding: utf-8 -*-
import crc16
import json
import os
import pytz
import qrcode

from datetime import datetime

def get_datetimezone_now(currency:str = 'THB'):
    utc_now = datetime.utcnow()
    file_path = 'currency_timezone_dict.json'
    timezone = None
    
    # Check if the file exists and is a regular file
    if os.path.isfile(file_path):
        try:
            with open(file_path, 'r') as file:
                currency_timezone_dict = json.load(file)
                timezone = currency_timezone_dict.get(currency)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {file_path}: {e}")
    else:
        print(f"{file_path} is not a regular file or does not exist.")

    if timezone:
        # Convert UTC time to the desired timezone
        return utc_now.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))
    else:
        # Handle the case where the currency is not found in the dictionary
        print(f"Timezone for currency {currency} not found in {file_path}.")
        return utc_now.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Bangkok'))

def qr_code(account, one_time=True, path_qr_code="", country="TH", money="", currency="THB"):
    """
    qr_code(account, one_time=True, path_qr_code="", country="TH", money="", currency="THB")
    account is phone number or identification number.
    one_time : if you use once than it's True.
    path_qr_code : path save qr code.
    country : TH
    money : money (if have)
    currency : THB
    """
    Version = "0002"+"01" # Version of PromptPay
    if one_time: # one_time indicates whether the code is for single use
        one_time = "010212" # 12 for single use
    else:
        one_time = "010211" # 11 for multiple uses
    
    if len(account) == 10 or len(account) == 13: 
        merchant_account_information = "2937" # Seller info (phone number or national ID)
    else:
        merchant_account_information = "2939" # Seller info (reference number)
        
    merchant_account_information += "0016"+"A000000677010111" # PromptPay application ID
    if len(account) == 10: # If account is a phone number
        account = list(account)
        merchant_account_information += "011300" # 01 for phone number, length 13, starts with 00
        if country == "TH":
            merchant_account_information += "66" # Country code 66 for Thailand
        del account[0] # Remove leading 0 from phone number
        merchant_account_information += ''.join(account)
    elif len(account) == 13: # If account is a national ID
        merchant_account_information += "0213" + account.replace('-','')
    else: # Reference number
        merchant_account_information += "0315" + account + "5303764"
    country = "5802" + country # Country code
    if currency == "THB":
        currency = "5303" + "764" # "764" is Thai Baht per ISO 4217
    if money != "": # If amount is specified
        check_money = money.split('.') # Split by decimal point
        if len(check_money) == 1 or len(check_money[1]) == 1: # No decimal or one decimal place
            money = "54" + "0" + str(len(str(float(money))) + 1) + str(float(money)) + "0"
        else:
            money = "54" + "0" + str(len(str(float(money)))) + str(float(money)) # Full decimal
    check_sum = Version + one_time + merchant_account_information + country + currency + money + "6304" # Calculate checksum
    check_sum1 = hex(crc16.crc16xmodem(check_sum.encode('ascii'), 0xffff)).replace('0x', '')
    if len(check_sum1) < 4: # Pad checksum to 4 digits
        check_sum1 = ("0" * (4 - len(check_sum1))) + check_sum1
    check_sum += check_sum1
    if path_qr_code != "":
        img = qrcode.make(check_sum.upper())
        imgload = open(path_qr_code, 'wb')
        img.save(imgload, 'PNG')
        imgload.close()
        return True
    else:
        return check_sum.upper() # Return uppercase string