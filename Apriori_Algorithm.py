import pandas as pd

class AprioriAlgorithm(object):

    def prune(self, data, supp, total_trans):
        df = data[data.supp_count >= supp] 
        return df
        
    def count_itemset(self, transaction_df, itemsets, total_trans):
        count_item = {}
        for item_set in itemsets:
            set_A = set(item_set if isinstance(item_set, tuple) else [item_set])
            for row in transaction_df:
                set_B = set(row)
                if set_A.issubset(set_B): 
                    count_item[item_set] = count_item.get(item_set, 0) + 1
                    
        data = pd.DataFrame({
            'item_sets': list(count_item.keys()),
            'supp_count': [(v / total_trans) * 100 for v in count_item.values()]
        })
        return data

    def count_item(self, trans_items, total_trans):
        count_ind_item = {}
        for row in trans_items:
            for i in row:
                count_ind_item[i] = count_ind_item.get(i, 0) + 1
        
        data = pd.DataFrame({
            'item_sets': list(count_ind_item.keys()),
            'supp_count': [(v / total_trans) * 100 for v in count_ind_item.values()]
        })
        data = data.sort_values('item_sets')
        return data

    def join(self, list_of_items):
        itemsets = []
        i = 1
        for entry in list_of_items:
            proceding_items = list_of_items[i:]
            for item in proceding_items:
                if isinstance(item, str):
                    if entry != item:
                        itemsets.append((entry, item))
                else:
                    if entry[0:-1] == item[0:-1]:
                        itemsets.append(entry + (item[-1],))
            i = i + 1
        return itemsets if itemsets else None
    
    
    def apriori(self, trans_data, supp, total_trans):
        results = []  # list để lưu các DataFrame nhỏ
        
        # bước 1: đếm item đơn lẻ
        df = self.count_item(trans_data, total_trans)

        while len(df) != 0:
            # prune theo min-supp
            df = self.prune(df, supp, total_trans)

            if not df.empty:
                results.append(df)  # thay vì concat ngay, mình lưu vào list

            # tạo candidate itemset mới
            itemsets = self.join(df.item_sets.tolist())
            if itemsets is None:
                break  # không tạo được itemset mới thì dừng

            # đếm support cho các itemset mới
            df = self.count_itemset(trans_data, itemsets, total_trans)

        # cuối cùng concat một lần duy nhất
        if results:
            freq = pd.concat(results, ignore_index=True)
        else:
            freq = pd.DataFrame(columns=['item_sets', 'supp_count'])

        return freq

            
if __name__ == '__main__':
    apriori = AprioriAlgorithm()

    data = pd.read_csv("D:/NCKH/CHARM/CHARM/Market_Basket_Optimisation.csv", header = None)
    transaction_list = []
    for i in range( len(data)):
        items = data.iloc[i].dropna().tolist()
        transaction_list.append(items)

    min_sup = 5
    total_trans = len(data)
    fre_items = apriori.apriori(transaction_list, min_sup, total_trans)
    print(fre_items.to_string(index=False))




    # dữ liệu dạng list các giao dịch
    # ori = [
    #     ['A', 'T', 'W', 'C'],
    #     ['D', 'W', 'C'],
    #     ['A', 'T', 'W', 'C'],
    #     ['A', 'D', 'W', 'C'],
    #     ['A', 'D', 'T', 'W', 'C'],
    #     ['D', 'T', 'C']
    # ]
    # a = apriori.apriori(ori, 50, len(ori))
    # print(a)