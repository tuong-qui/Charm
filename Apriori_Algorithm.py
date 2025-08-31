import pandas as pd
import numpy as np
import math

class AprioriAlgorithm(object):
    set = set()

    # def __init__(self):
    #     self.skipSet() = set()

    
    def prune(self, data, supp):
    
        df = data[data.supp_count >= supp] 
        return df
        
    def count_itemset(self, transaction_df, itemsets):
        
        count_item = {}
        for item_set in itemsets:
            set_A = set(item_set)
            for row in trans_df:
                set_B = set(row)
            
                if set_B.intersection(set_A) == set_A: 
                    if item_set in count_item.keys():
                        count_item[item_set] += 1
                    
                    else:
                        count_item[item_set] = 1
                    
        data = pd.DataFrame()
        data['item_sets'] = count_item.keys()
        data['supp_count'] = count_item.values()
        
        return data

    def count_item(self, trans_items):
        
        count_ind_item = {}
        for row in trans_items:
            for i in range(len(row)):
                if row[i] in count_ind_item.keys():
                    count_ind_item[row[i]] += 1
                else:
                    count_ind_item[row[i]] = 1
        
        data = pd.DataFrame()
        data['item_sets'] = count_ind_item.keys()
        data['supp_count'] = count_ind_item.values()
        data = data.sort_values('item_sets')
        return data


    def join(self,list_of_items):
        itemsets = []
        i = 1
        for entry in list_of_items:
            proceding_items = list_of_items[i:]
            for item in proceding_items:
                if(type(item) is str):
                    if entry != item:
                        tuples = (entry, item)
                        itemsets.append(tuples)
                else:
                    if entry[0:-1] == item[0:-1]:
                        tuples = entry+item[1:]
                        itemsets.append(tuples)
            i = i+1
        if(len(itemsets) == 0):
            return None
        return itemsets
    
    def apriori(self, trans_data, supp, con):
        freq = pd.DataFrame()
        
        df = self.count_item(trans_data)
    
        while(len(df) != 0):
            
            df = self.prune(df, supp)
        
            if len(df) > 1 or (len(df) == 1 and int(df.supp_count >= supp)):
                freq = df
            
            itemsets = self.join(df.item_sets)
        
            if(itemsets is None):
                return freq
        
            df = self.count_itemset(trans_data, itemsets)
        return df
            
if __name__ == '__main__':
    apriori = AprioriAlgorithm()
    ori = {'A': [1, 3, 4, 5], 'D': [2, 4, 5, 6], 'T': [1, 3, 5, 6], 'W': [1, 2, 3, 4, 5], 'C': [1, 2, 3, 4, 5, 6]}
    a = apriori.apriori(ori, 50, 0.3)

    print(a)