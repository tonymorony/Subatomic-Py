import tkinter as tk
from tkinter import ttk
from lib import subatomic_lib

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
tab_parent.add(tab2, text="Trade history")
tab_parent.pack(expand=True, fill="both")

# widgets creation
base_selector_text = ttk.Label(tab1, text="Select base: ")
base_combobox = ttk.Combobox(tab1)
base_combobox["values"] = supported_coins

rel_selector_text = ttk.Label(tab1, text="Select rel: ")
rel_combobox = ttk.Combobox(tab1)
rel_combobox["values"] = supported_coins

display_orderbook_button = ttk.Button(tab1, text="Display orderbook",
                                      command=lambda: subatomic_lib.refresh_orders_list(dex_proxy, base_combobox.get(),
                                                                                        rel_combobox.get(), bids, asks))

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

# widgets drawing
base_selector_text.grid(row=1, column=1, pady=(10,0), padx=(10, 0))
base_combobox.grid(row=1, column=2, pady=(10,0), padx=(10, 0))
rel_selector_text.grid(row=1, column=3, pady=(10,0), padx=(10, 0))
rel_combobox.grid(row=1, column=4, pady=(10,0), padx=(10, 0))

display_orderbook_button.grid(row=1, column=5, pady=(10,0), padx=(20, 10))

asks_top_label.grid(row=2, column=1, columnspan=5, padx=(10,10), pady=(30, 0))
asks.grid(row=3, column=1, columnspan=5, padx=(10,10), pady=(10, 0))

bids_top_label.grid(row=4, column=1, columnspan=5, padx=(10,10), pady=(10, 0))
bids.grid(row=5, column=1, columnspan=5, padx=(10,10), pady=(10, 0))

root.mainloop()
