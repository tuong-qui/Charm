import time
import pandas as pd

class CharmAlgorithm(object):
    def __init__(self):
        self.skipSet = set()
        self.closedSet = {}

    def hash_tidset(self, tidset):
        return sum(tidset)
    
    def sub_sumption_checking(self, itemset, tidset):
        h = self.hash_tidset(tidset)
        if h in self.closedSet:
            for (iset, tset) in self.closedSet[h]:
                if set(tset) == set (tidset):
                    return False
        self.closedSet.setdefault(h, []).append((itemset, tidset))
        return True
    
    def sort_dict(self, dic):
        import collections
        sorted_alpha = dict(collections.OrderedDict(sorted(dic.items())))
        sorted_len = dict(sorted(sorted_alpha.items(), key=lambda i: len(i[1])))
        return sorted_len
    
    
    def get_string_union(self, s1, s2):
        str_array = [s1, s2]
        to_string = ', '.join(filter(None, str_array))
        new_string_unique = sorted(list(set(to_string.split(', '))))
        return ', '.join(new_string_unique).strip(', ')
    
    def replace_in_items(self, curr, target, dic):
        temp = []
        for key in list(dic.keys()):
            if all (element in key for element in curr.split(', ')):
                temp.append(key)

        for key in temp:
            val = set(dic.get(key))   
            key_lst = key.split(', ')
            curr_lst = curr.split(', ')
            target_lst = target.split(', ')

            dic.pop(key)

            key_lst = sorted(key_lst + list(set(curr_lst) ^ set(target_lst)))
            key = (', ').join(key_lst)

            # Sort the items in each set
            key = self.get_string_union(key, "")
            dic.update({key: val})


    def charm_prop(self, xi, xj, y, min_sup, nodes, newN, total_trans):
        if len(y) >= total_trans * min_sup / 100:
            trans_xi = set(nodes.get(xi))
            trans_xj = set(nodes.get(xj))

            if trans_xi == trans_xj:
                self.skipSet.add(xj)
                temp = self.get_string_union(xi, xj)
                self.replace_in_items(xi, temp, newN)
                self.replace_in_items(xi, temp, nodes)
            elif trans_xi.issubset(trans_xj):
                temp = self.get_string_union(xi, xj)
                self.replace_in_items(xi, temp, newN)
                self.replace_in_items(xi, temp, nodes)
            elif trans_xj.issubset(trans_xi):
                self.skipSet.add(xj)
                newN.update({self.get_string_union(xi, xj): y})
            elif not trans_xi == trans_xj:
                newN.update({self.get_string_union(xi, xj): y})

        return xi
    
    def charm_extended(self, nodes, c, min_sup, total_trans):
        nodes = self.sort_dict(nodes)
        items = list(nodes.keys())

        for idx1 in range(len(items)):
            xi = items[idx1]

            if xi in self.skipSet:
                continue

            x_prev = xi
            x = str()
            newN = dict()

            for idx2 in range(idx1 + 1, len(items)):
                xj = items[idx2]

                if xj in self.skipSet:
                    continue

                x = self.get_string_union(xi, xj)

                temp = sorted(list(set(nodes.get(xi, [])) & set(nodes.get(xj, []))))
                xi= self.charm_prop(xi, xj, temp, min_sup, nodes, newN, total_trans)

            if len(newN) != 0:
                self.charm_extended(newN, c, min_sup, total_trans)
            if x_prev and nodes.get(x_prev) and self.sub_sumption_checking(x_prev, nodes.get(x_prev)):
                c.update({x_prev : nodes.get(x_prev)})
            if x and nodes.get(x) and self.sub_sumption_checking(x, nodes.get(x)):
                c.update({x : nodes.get(x)})

        
    def charm(self, ip, min_sup, total_trans):
        for key in list(ip.keys()):
            if len(ip[key]) < (min_sup * total_trans) / 100:
                del ip[key]

        c = dict()
        self.charm_extended(ip, c, min_sup, total_trans)

        for key, val in c.items():
            support = round(float((len(val) / total_trans) * 100), 4)
            c.update({key: support})

        return c
    
if __name__ == '__main__':
    charm = CharmAlgorithm()
    data = pd.read_csv("D:/NCKH/CHARM/CHARM/Market_Basket_Optimisation.csv", header = None)

    transaction_dict = {}
    total_trans = len(data)

    for i in range(len(data)):
        transaction_id = i + 1
        items = data.iloc[i].dropna()
        for item in items:
            if item not in transaction_dict:
                transaction_dict[item] = []
            transaction_dict[item].append(transaction_id)

    min_sup = 5
    closed_items = charm.charm(transaction_dict, min_sup, total_trans)
    closed_items_df = pd.DataFrame()
    closed_items_df['itemset'] = closed_items.keys()
    closed_items_df['support'] = closed_items.values()

    print(closed_items_df)
    


    # charm = CharmAlgorithm()
    # ori = {'A': [1, 3, 4, 5], 'D': [2, 4, 5, 6], 'T': [1, 3, 5, 6], 'W': [1, 2, 3, 4, 5], 'C': [1, 2, 3, 4, 5, 6]}
    # c = charm.charm(ori, 50, 6)

    # print(c)
   







