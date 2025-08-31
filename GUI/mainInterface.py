import time

import Processing_Data.ProcessingData as handle
import Preserving_Privacy_AR.Hidden_Rule as hide
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
import pandas as pd

hd = hide.Hidden()
hand = handle.procData()


def style_tv(tv, rows_data):
    style = ttk.Style()
    style.configure("Treeview",
                    background="white",
                    foreground="black",
                    fieldbackground="white")

    tv.tag_configure('oddrow', background='lightblue')

    count = 0
    for record in rows_data:
        if not count % 2 == 0:
            tv.insert(parent='', index='end', iid=count, text="",
                      values=(record[i] for i in range(len(record))),
                      tags=('oddrow',))


def clear_data(tv):
    tv.delete(*tv.get_children())


def show_tv(tv, input, columns=['Itemset', 'Support']):
    clear_data(tv)
    # hd = hide.hidden()
    if type(input) == pd.DataFrame:
        columns = [hd.replace_character(str(input.index.names))]
        columns = columns.__add__(list(input.columns))

    tv['column'] = columns
    tv['show'] = 'headings'

    for column in tv['columns']:
        tv.heading(column, text=column)

    if type(input) == pd.DataFrame:
        trans = list(input.index)
        input_rows = input.to_numpy().tolist()
        row = 0
        for val_row in input_rows:
            val_row.insert(0, trans[row])
            row += 1
    else:
        input_rows = []
        for key, val in input.items():
            temp = [key, val]
            input_rows.append(temp)

    for row in input_rows:
        tv.insert('', 'end', values=row)

    for col in columns:
        tv.column(col, minwidth=0, width=100, anchor='w')

    style_tv(tv, input_rows)


def show_rule(tv, rule_set):
    columns = ['Antecedents', 'Consequents', 'Support', 'Confidence', 'Lift']

    clear_data(tv)
    tv['column'] = columns

    for col in columns:
        tv.column(col, minwidth=0, width=90, stretch=True, anchor=tk.CENTER)

    tv['show'] = 'headings'

    for column in tv['columns']:
        tv.heading(column, text=column)

    rule_rows = []

    for rule, info in rule_set.items():
        temp = hd.convertToList(rule)
        for i in range(1, len(info)):
            temp.append(info[i])
        rule_rows.append(temp)

    for row in rule_rows:
        tv.insert('', 'end', values=row)


def handle_file():
    index = cbx_list.get()
    attribute = cbx_listAttribute.get()
    url = lbl_path['text']
    df = hand.handleFiletoDF(url, index, attribute)

    show_tv(tv_data, df)

    return df


def closedItemset_and_assRule():
    import CHARM_Algorithm as CHARM
    import Association_Rule as AR
    df = handle_file()

    total_trans = hand.total_transaction(df)
    minSupp = float(txt_minSupp.get())
    minConf = float(txt_minConf.get())

    start = time.time()
    charmObj = CHARM.CharmAlgorithm()
    c = charmObj.charm(hand.handleFiletoApplyCHARM(df), minSupp, total_trans)

    lbl_time['text'] = 'Time: ' + str(round(time.time() - start, 5)) + 's'

    # show closed itemset:
    show_tv(tv_closed, c)

    lbl_count['text'] = 'Closed Itemsets: ' + str(len(c.keys()))

    # Show association rule:
    assRule = AR.AssociationRules()
    rule_set = assRule.AssRules(c, minSupp, minConf, hand.handleFiletoApplyCHARM(df))

    show_rule(tv_rule, rule_set)

    return rule_set


def sensRule():
    rule_set = closedItemset_and_assRule()
    sens_rule = hd.sensitive_rule(rule_set)

    show_rule(tv_sensRule, sens_rule)
    lbl_cntSen['text'] = 'Sensitive Rules: ' + str(len(sens_rule.keys()))

    return sens_rule


def hidden():
    rule_set = closedItemset_and_assRule()
    df = handle_file()
    oriDB = hand.handleFiletoApplyCHARM(df)
    minConf = int(txt_minConf.get())

    db = hd.SuppReduction(rule_set, oriDB, minConf, df)

    # show db in treeview tb_db:
    hidden_df = hand.handleDictToDF(db)
    show_tv(tv_db, hidden_df)

    return hidden_df


def load_CSV_data():
    filePath = lbl_path['text']
    try:
        ori_df = pd.read_csv(filePath)
    except ValueError:
        tk.messagebox.showerror('Information', 'The file you have chosen is invalid')
        return None
    except FileNotFoundError:
        tk.messagebox.showerror('Information', f'No such file as {filePath}')
        return None


    return ori_df


def show_data_TV():
    ori_df = load_CSV_data()

    show_tv(tv_data, ori_df)

    # options to select index:
    columns = list(ori_df.columns)
    cbx_list['values'] = columns

    # options to select attribute:
    cbx_listAttribute['values'] = columns


def load_combobox():
    df = load_CSV_data()

    # options to select index:
    columns = list(df.columns)
    cbx_list['values'] = columns

    # options to select attribute:
    cbx_listAttribute['values'] = columns


def open_file():
    filePath = filedialog.askopenfilename(initialdir='/', title='Select A File',
                                          filetypes=(("csv files", "*.csv"), ("All files", "*.*")))
    lbl_path['text'] = filePath

    show_data_TV()


def save():
    import csv

    files = [('All Files', '*.*'),
             ('CSV Files', '*.csv'),
             ('Text Document', '*.txt')]
    file = filedialog.asksaveasfile(mode='w', filetypes=files, defaultextension=files)
    ori_df = load_CSV_data()
    hidden_df = hidden()
    final_data = hand.handleDFtoCSV(ori_df, hidden_df, cbx_list.get(), cbx_listAttribute.get())
    field_names = list(final_data[0].keys())

    print(file.name)

    with open(file.name, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for data in final_data:
            writer.writerow(data)
        csvfile.close()

    file.close()


root = tk.Tk()
root.title('CHARM Algorithm')
root.geometry("800x{0}+0+0".format(root.winfo_screenheight()-75))
root.pack_propagate(False)
root.resizable(0, 0)


# Tabcontrol:
tabControl = ttk.Notebook(root)

tab_CHARM = ttk.Frame(tabControl)
tabControl.add(tab_CHARM, text='CHARM Algorithm')

tabControl.pack(expand=1, fill='both')

'''
    Open file dialog
'''
# label for open file dialog
lbl = tk.Label(tab_CHARM, text='Open File:')
lbl.place(rely=0.025, relx=0.01)

lbl_path = tk.Label(tab_CHARM, width=65, bg='white', borderwidth=2, relief="groove")
lbl_path.place(rely=0.025, relx=0.1)


# Frame for Treeview:
fr_showdata = tk.LabelFrame(tab_CHARM, text='Data')
fr_showdata.place(height=250, width=800, rely=0.07)

# Treeview Widget
tv_data = ttk.Treeview(fr_showdata)
tv_data.place(relheight=1, relwidth=1)

treescrolly = tk.Scrollbar(fr_showdata, orient='vertical', command=tv_data.yview)
treescrollx = tk.Scrollbar(fr_showdata, orient='horizontal', command=tv_data.xview)
tv_data.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
treescrollx.pack(side='bottom', fill='x')
treescrolly.pack(side='right', fill='y')

# Button Browse file:

btn_Browse = tk.Button(tab_CHARM, text='Browse A File', command=open_file)
btn_Browse.place(rely=0.02, relx=0.70)

'''
    ** Processing data
'''
# LabelFrame Processing data:
fr_processData = tk.LabelFrame(tab_CHARM, text='Processing Data')
fr_processData.place(height=80, width=300, rely=0.46, relx=0.015)

# Combobox list to Select index:
opt = tk.StringVar()
cbx_list = ttk.Combobox(fr_processData, width=12, textvariable=opt, postcommand=load_combobox)
cbx_list['values'] = ['Select index']
cbx_list.place(rely=0.04, relx=0.08)
cbx_list.current(0)
cbx_list.configure(state='readonly')

# Combobox list to Select index:
chosen = tk.StringVar()
cbx_listAttribute = ttk.Combobox(fr_processData, width=15, textvariable=chosen, postcommand=load_combobox)
cbx_listAttribute['values'] = ['Select attribute']
cbx_listAttribute.place(rely=0.04, relx=0.48)
cbx_listAttribute.current(0)
cbx_listAttribute.configure(state='readonly')

# Button Handle file to dataframe:
btn_HandleToDF = tk.Button(fr_processData, text='Handle File', command=handle_file)
btn_HandleToDF.place(rely=0.45, relx=0.7)


'''
    Hanlde data to create frequency closed itemsets
'''
# labelFrame frequency closed itemsets:
fr_closedItemset = tk.LabelFrame(tab_CHARM, text='Frequency Closed Itemsets')
fr_closedItemset.place(height=55, width=450, rely=0.46, relx=0.42)

# Min Support:
lbl_minSupp = tk.Label(fr_closedItemset, text='MinSupport:')
lbl_minSupp.place(rely=0.07, relx=0.05)
txt_minSupp = tk.Entry(fr_closedItemset, text='', width=10)
txt_minSupp.place(rely=0.07, relx=0.22)

# Min Confidence:
lbl_minConf = tk.Label(fr_closedItemset, text='MinConfidence:')
lbl_minConf.place(rely=0.07, relx=0.42)
txt_minConf = tk.Entry(fr_closedItemset, text='', width=10)
txt_minConf.place(rely=0.07, relx=0.64)

#label_count itemset
lbl_count = tk.Label(tab_CHARM, text='', font='bold')
lbl_count.place(rely=0.55, relx=0.45)

#label time
lbl_time = tk.Label(tab_CHARM, text='', font='bold')
lbl_time.place(rely=0.55, relx=0.8)

# Button Closed
btn_Create = tk.Button(fr_closedItemset, text='Create', command=closedItemset_and_assRule)
btn_Create.place(rely=0.07, relx=0.85)




'''
    Show result: closed itemset, association rule
'''

# Labelframe to show result:
fr_showResult = tk.LabelFrame(tab_CHARM)
fr_showResult.place(height=265, relwidth=1, rely=0.6)
# Labelframe to show closed itemsets:
fr_showItemset = tk.LabelFrame(fr_showResult, text='Closed Itemsets')
fr_showItemset.place(relheight=1, width=255)

# Labelframe to show association rule:
fr_showRule = tk.LabelFrame(fr_showResult, text='Association Rule')
fr_showRule.place(relheight=1, width=530, relx=0.33)

# Treeview Show closed itemset
tv_closed = ttk.Treeview(fr_showItemset)
tv_closed.place(relheight=1, relwidth=1)

closed_scrolly = tk.Scrollbar(fr_showItemset, orient='vertical', command=tv_closed.yview)
closed_scrollx = tk.Scrollbar(fr_showItemset, orient='horizontal', command=tv_closed.xview)
tv_closed.configure(xscrollcommand=closed_scrollx.set, yscrollcommand=closed_scrolly.set)
closed_scrollx.pack(side='bottom', fill='x')
closed_scrolly.pack(side='right', fill='y')

# Treeview Show association rule:
tv_rule = ttk.Treeview(fr_showRule)
tv_rule.place(relheight=1, relwidth=1)

rule_scrolly = tk.Scrollbar(fr_showRule, orient='vertical', command=tv_rule.yview)
rule_scrollx = tk.Scrollbar(fr_showRule, orient='horizontal', command=tv_rule.xview)
tv_rule.configure(xscrollcommand=rule_scrollx.set, yscrollcommand=rule_scrolly.set)
rule_scrollx.pack(side='bottom', fill='x')
rule_scrolly.pack(side='right', fill='y')


'''=====================SENSITIVE RULES====================='''
tab_Secure = ttk.Frame(tabControl)
tabControl.add(tab_Secure, text='Hidden Sensitive Rule')

# Labelframe to show sensitive rules:
fr_sensRule = tk.LabelFrame(tab_Secure, text='Sensitive Rules')
fr_sensRule.place(height=250, width=800, rely=0.01)

# Treeview Show sensitive rule:
tv_sensRule = ttk.Treeview(fr_sensRule)
tv_sensRule.place(relheight=1, relwidth=1)

sens_scrolly = tk.Scrollbar(fr_sensRule, orient='vertical', command=tv_sensRule.yview)
sens_scrollx = tk.Scrollbar(fr_sensRule, orient='horizontal', command=tv_sensRule.xview)
tv_sensRule.configure(xscrollcommand=sens_scrollx.set, yscrollcommand=sens_scrolly.set)
sens_scrollx.pack(side='bottom', fill='x')
sens_scrolly.pack(side='right', fill='y')

#label_count sensitve rule
lbl_cntSen = tk.Label(tab_Secure, text='', font='bold')
lbl_cntSen.place(rely=0.41, relx=0.75)

# Button Sensitive Rules:
btn_sensRule = tk.Button(tab_Secure, text='Sensitive Rule', command=sensRule)
btn_sensRule.place(rely=0.41, relx=0.6)



'''=====================HIDE SENSITIVE RULES====================='''
# Labelframe to show data after hidden:
fr_DB = tk.LabelFrame(tab_Secure, text='Data After Hidden Sensitive Rules')
fr_DB.place(height=300, width=800, rely=0.45)

# Treeview Show data after hidden:
tv_db = ttk.Treeview(fr_DB)
tv_db.place(relheight=1, relwidth=1)

db_scrolly = tk.Scrollbar(fr_DB, orient='vertical', command=tv_db.yview)
db_scrollx = tk.Scrollbar(fr_DB, orient='horizontal', command=tv_db.xview)
tv_db.configure(xscrollcommand=db_scrollx.set, yscrollcommand=db_scrolly.set)
db_scrollx.pack(side='bottom', fill='x')
db_scrolly.pack(side='right', fill='y')

# Button hiding rule:
btn_hide = tk.Button(tab_Secure, text='Hide Rules', command=hidden)
btn_hide.place(rely=0.92, relx=0.5)

# Button save:
btn_save = tk.Button(tab_Secure, text='Save as', command=save)
btn_save.place(rely=0.92, relx=0.8)



root.mainloop()


