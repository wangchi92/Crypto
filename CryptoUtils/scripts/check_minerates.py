import json

from coins.BTC import BTC


def get_meta_info():
    with open("coins\coins_info_sheet.json") as meta_info_file:
        meta_info = json.load(meta_info_file)
        meta_info_file.close()
        return meta_info


info = get_meta_info()
btc = BTC(info['btc'])
btc.print_header()
