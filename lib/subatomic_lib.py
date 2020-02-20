import platform
import os
import re
import slickrpc
import tkinter as tk
from tkinter import ttk
import subprocess
import json


# just to set custom timeout
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
            # TODO: convert timestamp to user readable data
            bids_list.insert("", "end", text=bid["id"], values=[bid["price"], bid["baseamount"], bid["relamount"],
                            bid["timestamp"], bid["hash"], orderbook_data["base"], orderbook_data["rel"], "bid"])


def refresh_asks_list(rpc_proxy, base, rel, asks_list):
    orderbook_data = get_orderbook_data(rpc_proxy, base, rel)
    asks_data = orderbook_data["asks"]
    print(orderbook_data)
    asks_list.delete(*asks_list.get_children())
    if len(asks_data) == 0:
        asks_list.insert("", "end", text="No orders yet")
    else:
        for ask in asks_data:
            # TODO: convert timestamp to user readable data`
            asks_list.insert("", "end", text=ask["id"], values=[ask["price"], ask["baseamount"], ask["relamount"],
                                                                ask["timestamp"], ask["hash"], orderbook_data["base"], orderbook_data["rel"], "ask"])


def refresh_orders_list(rpc_proxy, base, rel, bids_list, asks_list):
    refresh_bids_list(rpc_proxy, base, rel, bids_list)
    refresh_asks_list(rpc_proxy, base, rel, asks_list)


def start_subatomic_maker_loop(base, rel):
    command = "./subatomic " + rel + ' "" ' + base
    subatomic_handle = subprocess.Popen(command, shell=True)
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


def fill_bid(order_data, input_amount):
    print("filling bid")
    command = "./subatomic " + order_data["values"][5] + ' "" ' + str(order_data["text"]) + " " + str(input_amount)
    subatomic_handle = subprocess.Popen(command, shell=True)
    return subatomic_handle


def fill_ask(order_data, input_amount):
    print("filling ask")
    command = "./subatomic " + order_data["values"][6] + ' "" ' + str(order_data["text"]) + " " + str(input_amount)
    subatomic_handle = subprocess.Popen(command, shell=True)
    return subatomic_handle


def order_fill_popup(selected_order):
    order_info_string = "ID: " + str(selected_order["text"]) + "\n"
    # TODO: refactor me please by backward conversion function (see refresh_asks_list refresh_bids_list conversion)
    order_info_string += "Price: " + str(selected_order["values"][0]) + "\n"
    order_info_string += "Base amount: " + str(selected_order["values"][1]) + " " + selected_order["values"][5] +  "\n"
    order_info_string += "Rel amount: " + str(selected_order["values"][2]) + " " + selected_order["values"][6] +  "\n"
    order_info_string += "Timestamp: " + str(selected_order["values"][3]) + "\n"
    order_info_string += "Hash: " + str(selected_order["values"][4]) + "\n"
    popup = tk.Tk()
    popup.wm_title("Order fill as a taker")
    order_info_label = ttk.Label(popup, text="Order info:")

    amount_container = tk.Frame(popup)
    progress_container = tk.Frame(popup)
    order_info = tk.Text(popup, height=10)
    order_info.insert(100.0,  order_info_string)
    # ask filling case
    if selected_order["values"][7] == "ask":
        amount_input_label = ttk.Label(popup, text="Input amount to fill ask:")
        amount_input_label = ttk.Label(popup, text="Input " + selected_order["values"][6] + " amount to sell:")
        fill_order_button = ttk.Button(popup, text="Fill order", command=lambda: fill_ask(selected_order, amount_input.get()))
        # TODO: add dynamic calculation of second (non-input) amount
        # you'll get: ...
    # bid filling case
    elif selected_order["values"][7] == "bid":
        amount_input_label = ttk.Label(popup, text="Input " + selected_order["values"][5] + " amount to sell:")
        fill_order_button = ttk.Button(popup, text="Fill order", command=lambda: fill_bid(selected_order, amount_input.get()))
        # TODO: add dynamic calculation of second (non-input) amount
        # you'll get: ...
    amount_input = tk.Entry(popup)
    filling_progress_label = ttk.Label(popup, text="Trade progress:")
    filling_info_text = tk.Text(popup, height=15)
    close_button = ttk.Button(popup, text="Close", command=popup.destroy)

    order_info_label.pack(side="top", pady=10)
    order_info.pack(side="top", fill="x", pady=10)
    amount_input_label.pack(in_=amount_container, side="left", padx=8)
    amount_input.pack(in_=amount_container, side="left", padx=8)
    fill_order_button.pack(in_=amount_container, side="left", padx=8)
    amount_container.pack()

    filling_progress_label.pack(in_=progress_container)
    filling_info_text.pack(in_=progress_container,fill="x")
    progress_container.pack(pady=10)
    close_button.pack(side="bottom", pady=10)

    popup.mainloop()


def start_or_stop_selected_daemon(selected_daemon):
    print(selected_daemon)
    coin_ticker = selected_daemon["text"]
    starting_params = ["./komodod"]
    try:
        with open("assetchains.json") as assetchains_json:
            assetchains_data = json.load(assetchains_json)
    except Exception as e:
        print(e)
        print("assetchains,json in same dir is needed!")
    if selected_daemon["values"][0] == "offline":
        if coin_ticker == "KMD":
            starting_params.append("-daemon")
            subprocess.call(starting_params)
        elif coin_ticker == "DEX":
            # TODO:
            "Custom start is needed for DEX"
        else:
            for assetchain in assetchains_data:
                if coin_ticker == assetchain["ac_name"]:
                    for param in assetchain:
                        if param != "addnode":
                            starting_params.append("-" + param + "=" + assetchain[param])
                        # TODO: not for all ACs addnode match with this one - might not work for some daemons...
                        if "addnode" not in assetchain.keys():
                            starting_params.append("-addnode=95.213.238.98")
                        else:
                            for node in assetchain["addnode"]:
                                starting_params.append("-addnode="+node)
            starting_params.append("-daemon")
            print(starting_params)
            subprocess.call(starting_params)
    elif selected_daemon["values"][0] == "online":
        print("Stopping " + str(coin_ticker))
        temp_proxy = def_credentials(coin_ticker)
        temp_proxy.stop()
