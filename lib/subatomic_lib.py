import platform
import os
import re
import slickrpc
import tkinter as tk
from tkinter import ttk
from subprocess import Popen


class CustomProxy(slickrpc.Proxy):
    def __init__(self,
                 service_url=None,
                 service_port=None,
                 conf_file=None,
                 timeout=3000):
        config = dict()
        if conf_file:
            config = slickrpc.ConfigObj(conf_file)
        if service_url:
            config.update(self.url_to_conf(service_url))
        if service_port:
            config.update(rpcport=service_port)
        elif not config.get('rpcport'):
            config['rpcport'] = 7771
        self.conn = self.prepare_connection(config, timeout=timeout)


def def_credentials(chain):
    rpcport = ''
    ac_dir = ''
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Win64' or operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    with open(coin_config_file, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    if len(rpcport) == 0:
        if chain == 'KMD':
            rpcport = 7771
        else:
            print("rpcport not in conf file, exiting")
            print("check "+coin_config_file)
            exit(1)

    return CustomProxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))


def get_orderbook_data(rpc_proxy, base, rel):
    orderbook_data = rpc_proxy.DEX_orderbook("", "0", base, rel)
    return orderbook_data


def refresh_bids_list(rpc_proxy, base, rel, bids_list):
    orderbook_data = get_orderbook_data(rpc_proxy, base, rel)
    bids_data = orderbook_data["bids"]
    print(orderbook_data)
    bids_list.delete(*bids_list.get_children())
    if len(bids_data) == 0:
        bids_list.insert("", "end", text="No orders yet")
    else:
        for bid in bids_data:
            bids_list.insert("", "end", text=bid["id"], values=[bid["price"], bid["baseamount"], bid["relamount"], bid["timestamp"], bid["hash"]])


def refresh_asks_list(rpc_proxy, base, rel, asks_list):
    orderbook_data = get_orderbook_data(rpc_proxy, base, rel)
    asks_data = orderbook_data["asks"]
    print(orderbook_data)
    asks_list.delete(*asks_list.get_children())
    if len(asks_data) == 0:
        asks_list.insert("", "end", text="No orders yet")
    else:
        for ask in asks_data:
            asks_list.insert("", "end", text=ask["id"], values=[ask["price"], ask["baseamount"], ask["relamount"], ask["timestamp"], ask["hash"]])


def refresh_orders_list(rpc_proxy, base, rel, bids_list, asks_list):
    refresh_bids_list(rpc_proxy, base, rel, bids_list)
    refresh_asks_list(rpc_proxy, base, rel, asks_list)


def start_subatomic_maker_loop(base, rel):
    command = "./subatomic " + base + ' " " '  + rel
    subatomic_handle = Popen(command, shell=True)
    return subatomic_handle


def place_buy_order(rpc_proxy, base, rel, base_amount, rel_amount, receiving_address, is_subatomic_maker_start_needed):
    print(base)
    print(rel)
    print(base_amount)
    print(rel_amount)
    print(receiving_address)
    dex_pubkey = rpc_proxy.DEX_stats()["publishable_pubkey"]
    order_data = rpc_proxy.DEX_broadcast(receiving_address, "5", base, rel, dex_pubkey, str(base_amount), str(rel_amount))
    print(order_data)
    if is_subatomic_maker_start_needed:
        start_subatomic_maker_loop(base, rel)
    return order_data


def update_text_widget_content(text_widget, string_to_put):
    text_widget.configure(state='normal')
    text_widget.replace("1.0", "100.0", string_to_put)
    text_widget.configure(state='disabled')


def fetch_daemons_status(daemons_list):
    daemons_info = {}
    for ticker in daemons_list:
        daemons_info[ticker] = {}
        try:
            temp_proxy = def_credentials(ticker)
            getinfo_output = temp_proxy.getinfo()
            daemons_info[ticker]["status"] = "online"
            if ticker == "PIRATE":
                daemons_info[ticker]["balance"] = temp_proxy.z_gettotalbalance()["total"]
            else:
                daemons_info[ticker]["balance"] = getinfo_output["balance"]
            daemons_info[ticker]["blocks"] = getinfo_output["blocks"]
            daemons_info[ticker]["longestchain"] = getinfo_output["longestchain"]
            if getinfo_output["blocks"] == getinfo_output["longestchain"]:
                daemons_info[ticker]["is_synced"] = "True"
            else:
                daemons_info[ticker]["is_synced"] = "False"
        except Exception as e:
            print(e)
            daemons_info[ticker]["status"] = "offline"
            daemons_info[ticker]["balance"] = "N/A"
            daemons_info[ticker]["blocks"] = "N/A"
            daemons_info[ticker]["longestchain"] = "N/A"
            daemons_info[ticker]["is_synced"] = "N/A"
    print(daemons_info)
    return daemons_info


def fill_daemons_statuses_table(statuses_table, daemons_status_info):
    statuses_table.delete(*statuses_table.get_children())
    for ticker in daemons_status_info:
        statuses_table.insert("", "end", text=ticker, values=[daemons_status_info[ticker]["status"], daemons_status_info[ticker]["balance"],
                                                              daemons_status_info[ticker]["blocks"], daemons_status_info[ticker]["longestchain"],
                                                              daemons_status_info[ticker]["is_synced"]])


def order_fill_popup(selected_order):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=selected_order)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()