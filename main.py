import tkinter as tk
from tkinter import ttk
from lib import subatomic_lib

'''
TODO: 
- daemons management
- balances tracking
- checks that user control all needed addresses
- receiving t/z addr in app settings
- my open orders (tab2)
- trades history (tab2) - split by analogy with tab1
'''

dex_proxy = subatomic_lib.def_credentials("DEX")

# main window
root = tk.Tk()
root.title("Subatomic GUI")
root.geometry("1200x640")
root.resizable(False, False)
supported_coins = ["KMD", "PIRATE"]

# tabs control
tab_parent = ttk.Notebook(root)
tab1 = ttk.Frame(tab_parent)
tab2 = ttk.Frame(tab_parent)
tab_parent.add(tab1, text="Orderbook")
tab_parent.add(tab2, text="Create order")
tab_parent.pack(expand=True, fill="both")

# widgets creation
# tab 1
base_selector_orderbook = ttk.Label(tab1, text="Select base: ")
base_combobox_orderbook = ttk.Combobox(tab1)
base_combobox_orderbook["values"] = supported_coins

rel_selector_orderbook = ttk.Label(tab1, text="Select rel: ")
rel_combobox_orderbook = ttk.Combobox(tab1)
rel_combobox_orderbook["values"] = supported_coins

display_orderbook_button = ttk.Button(tab1, text="Display orderbook",
                                      command=lambda: subatomic_lib.refresh_orders_list(dex_proxy, base_combobox_orderbook.get(),
                                                                                        rel_combobox_orderbook.get(), bids, asks))

orders_columns = ["price", "baseamount", "relamount", "timestamp", "hash"]

asks_top_label = ttk.Label(tab1, text="Asks: ")
asks = ttk.Treeview(tab1, columns=orders_columns)
asks.heading('#0', text='ID')

bids_top_label = ttk.Label(tab1, text="Bids: ")
bids = ttk.Treeview(tab1, columns=orders_columns)
bids.heading('#0', text='ID')

for i in range(1, len(orders_columns)+1):
    asks.heading("#"+str(i), text=orders_columns[i-1])
    bids.heading("#" + str(i), text=orders_columns[i - 1])

# tab 2
base_selector_order_creation = ttk.Label(tab2, text="Select coin you want to buy: ")
base_combobox_order_creation = ttk.Combobox(tab2)
base_combobox_order_creation["values"] = supported_coins

rel_selector_order_creation = ttk.Label(tab2, text="Select coin you want to sell: ")
rel_combobox_order_creation = ttk.Combobox(tab2)
rel_combobox_order_creation["values"] = supported_coins

base_amount = ttk.Spinbox(tab2, from_=0.0, to_=10000000)
base_amount_label = ttk.Label(tab2, text="amount: ")
rel_amount = ttk.Spinbox(tab2, from_=0.0, to_=10000000)
rel_amount_label = ttk.Label(tab2, text="amount: ")

receiving_address_label = ttk.Label(tab2, text="Receiving address: ")
receiving_address = ttk.Entry(tab2)

place_order_button = ttk.Button(tab2, text="Place order", command=lambda: subatomic_lib.update_text_widget_content(order_creation_text, str(subatomic_lib.place_buy_order(dex_proxy, base_combobox_order_creation.get(), rel_combobox_order_creation.get(),
                                                                                                        base_amount.get(), rel_amount.get(), receiving_address.get()))))

order_creation_text = tk.Text(tab2, width=100, height=10)
order_creation_text.configure(state='disabled')

# widgets drawing
# tab1
base_selector_orderbook.grid(row=1, column=1, pady=(10,0), padx=(10, 0))
base_combobox_orderbook.grid(row=1, column=2, pady=(10,0), padx=(10, 0))
rel_selector_orderbook.grid(row=1, column=3, pady=(10,0), padx=(10, 0))
rel_combobox_orderbook.grid(row=1, column=4, pady=(10,0), padx=(10, 0))

display_orderbook_button.grid(row=1, column=5, pady=(10,0), padx=(20, 10))

asks_top_label.grid(row=2, column=1, columnspan=5, padx=(10,10), pady=(30, 0))
asks.grid(row=3, column=1, columnspan=5, padx=(10,10), pady=(10, 0))

bids_top_label.grid(row=4, column=1, columnspan=5, padx=(10,10), pady=(10, 0))
bids.grid(row=5, column=1, columnspan=5, padx=(10,10), pady=(10, 0))

# tab2
base_selector_order_creation.grid(row=1, column=1, pady=(10,0), padx=(10, 0))
base_combobox_order_creation.grid(row=1, column=2, pady=(10,0), padx=(10, 0))
base_amount_label.grid(row=1, column=3, pady=(10,0), padx=(10, 0))
base_amount.grid(row=1, column=4, pady=(10,0), padx=(10, 0))
receiving_address_label.grid(row=1, column=5, pady=(10,0), padx=(10, 0))
receiving_address.grid(row=1, column=6, pady=(10,0), padx=(10, 0))
rel_selector_order_creation.grid(row=2, column=1, pady=(10,0), padx=(10, 0))
rel_combobox_order_creation.grid(row=2, column=2, pady=(10,0), padx=(10, 0))
rel_amount_label.grid(row=2, column=3, pady=(10,0), padx=(10, 0))
rel_amount.grid(row=2, column=4, pady=(10,0), padx=(10, 0))
place_order_button.grid(row=3, column=1, pady=(10,0), padx=(10, 0))
order_creation_text.grid(row=4, column=1, columnspan=5, pady=(10,0), padx=(10, 0))

root.mainloop()
