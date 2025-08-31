import time
import pandas as pd

class CharmAlgorithm(object):
    set = set()

    def __init__(self):
        self.skipSet = set()
        self.closed_sets = {}

    # Sort dictionary
    def sortDict(self, dic):
        import collections
        sorted_aphal = dict(collections.OrderedDict(sorted(dic.items())))
        sorted_len = dict(sorted(sorted_aphal.items(), key=lambda i: len(i[1])))
        return sorted_len



    '''
        *Function to compute the union of two item sets - (Xi U Xj). Items are ordered lexicographically.
        *
        * @ param s1 - string
        * @ param s2 - string
        * @ return Xi U Xj
    '''
    def getStringUnion(self, s1, s2):
        strArray = [s1]
        strArray.append(s2)
        newStrArray = list()

        for idx in range(len(strArray)-1):
            if strArray[idx] != strArray[idx+1]:
                newStrArray.append(strArray[idx])

        newStrArray.append(strArray[len(strArray)-1])
        toStr = str(', '.join(newStrArray)).strip(', ')
        newStrUnique = sorted(list(set(toStr.split(', '))))
        newStrUnique = str(', '.join(newStrUnique)).strip(', ')

        return newStrUnique

    # def getStringUnion(self, s1, s2):
    #     if s1 == s2:
    #         newStrUnique = s1
    #     else:
    #         newStrUnique = ', '.join(sorted(set([s1, s2])))
    #     return newStrUnique

    '''
        *Function to replace Xi with X.
        *
        * @ param curr - string
        * @ param target - string
        * @ param dic - dict
    '''
    def replaceInItems(self, curr, target, dic):
        temp = list()

        # Identify the items to be replaced.
        for key in dic.keys():
            if all(element in key for element in curr):
                temp.append(key)

        # Update each item.
        for key in temp:
            val = set(dic.get(key))   
            key_lst = key.split(', ')
            curr_lst = curr.split(', ')
            target_lst = target.split(', ')

            dic.pop(key)

            key_lst = sorted(key_lst + list(set(curr_lst) ^ set(target_lst)))
            key = (', ').join(key_lst)

            # Sort the items in each set
            key = self.getStringUnion(key, "")
            dic.update({key: val})

    '''
        * Incorporating the 4 charm properties.
        *
        * @param xi - string
        * @param xj - string
        * @param y - set
        * @param minSup - int
        * @param nodes - dict
        * @param newN - dict
        * @return xi
    '''
    def charmProp(self, xi, xj, y, minSup, nodes, newN, total_trans):
        if len(y) >= total_trans * minSup / 100:
            trans_Xi = set(nodes.get(xi))
            trans_Xj = set(nodes.get(xj))

            if trans_Xi == trans_Xj:            # Property 1
                self.skipSet.add(xj)
                temp = self.getStringUnion(xi, xj)
                self.replaceInItems(xi, temp, newN)
                self.replaceInItems(xi, temp, nodes)
                return temp
            elif trans_Xi.issubset(trans_Xj):   # Property 2
                temp = self.getStringUnion(xi, xj)
                self.replaceInItems(xi, temp, newN)
                self.replaceInItems(xi, temp, nodes)
                return temp
            elif trans_Xj.issubset(trans_Xi):   # Property 3
                self.skipSet.add(xj)
                newN.update({self.getStringUnion(xi, xj): y})
            elif not trans_Xi == trans_Xj:
                newN.update({self.getStringUnion(xi, xj): y})

        return xi

    '''
        * Function to check if an item set is subsumed by the existing item sets.
        *
        * @param c - dict
        * @param y - set
        * @return true/false
    '''
    # def isSubsumed(self, c, y):
    #     y = set(y)

    #     for val in c.values():
    #         val = set(val)
    #         if val == y:
    #             return True

    #     return False

    # Hàm băm trên Tidset
    def hashTidset(self, tidset):
        return sum(tidset)

    # Kiểm tra bao hàm trước khi thêm
    def sub_sumption_checking(self, itemset, tidset):
        h = self.hashTidset(tidset)
        if h in self.closed_sets:
            for (iset, tset) in self.closed_sets[h]:
                if set(tset) == set(tidset):  # tidset bằng nhau ⇒ bị bao hàm
                    return False
        # Nếu chưa có ⇒ thêm mới
        self.closed_sets.setdefault(h, []).append((itemset, tidset))
        return True

    '''
        * Charm - Extended routine
        *
        * @param nodes - dict
        * @param c - dict
        * @param minSup - int
    '''
    def charmExtended(self, nodes, c, minSup, total_trans):
        nodes = self.sortDict(nodes)
        items = list(nodes.keys())

        for idx1 in range(len(items)):
            xi = items[idx1]

            if self.skipSet.__contains__(xi):
                continue

            x_prev = xi
            x = str()
            newN = dict()

            for idx2 in range(idx1 + 1, len(items)):
                xj = items[idx2]

                if(self.skipSet.__contains__(xj)):
                    continue

                x = self.getStringUnion(xi, xj)
                value_Xprev = nodes.get(xi)

                temp = list()

                for value in value_Xprev:
                    # if value not in temp:
                    temp.append(value)

                temp = sorted(list(set(temp) & set(nodes.get(xj, self.set))))

                xi = self.charmProp(xi, xj, temp, minSup, nodes, newN, total_trans)

            if len(newN) != 0:
                self.charmExtended(newN, c, minSup, total_trans)
            # if x_prev is not None and nodes.get(x_prev) is not None and not self.isSubsumed(c, nodes.get(x_prev)):
            #     c.update({x_prev: nodes.get(x_prev)})
            # if x is not None and nodes.get(x) is not None and not self.isSubsumed(c, nodes.get(x)):
            #     c.update({x: nodes.get(x)})


            if x_prev and nodes.get(x_prev) and self.sub_sumption_checking(x_prev, nodes.get(x_prev)):
                c.update({x_prev : nodes.get(x_prev)})
            if x and nodes.get(x) and self.sub_sumption_checking(x, nodes.get(x)):
                c.update({x : nodes.get(x)})
    '''
        * CHARM routine - Items are ordered lexicographically.
        *
        * @param ip - dict
        * @param minSup - int
        * @return c
    '''
    def charm(self, ip, minSup, total_trans):
        # Eliminate items that don't satisfy the min support property

        for key in list(ip.keys()):
            if len(ip.__getitem__(key)) < (minSup*total_trans)/100:
                ip.pop(key)

        # Generate the closed item sets
        c = dict()
        self.charmExtended(ip, c, minSup, total_trans)

        for key, val in c.items():
            support = round(float((len(val) / total_trans) * 100), 4)
            c.update({key: support})

        return c


if __name__ == '__main__':
    # charm = CharmAlgorithm()
    # data = pd.read_csv("D:/NCKH/CHARM/CHARM/Market_Basket_Optimisation.csv", header = None)

    # transaction_dict = {}
    # total_trans = len(data)

    # for i in range(len(data)):
    #     transaction_id = i + 1
    #     items = data.iloc[i].dropna()
    #     for item in items:
    #         if item not in transaction_dict:
    #             transaction_dict[item] = []
    #         transaction_dict[item].append(transaction_id)

    # #print(transaction_dict)

    # minSup = 10
    # closed_items = charm.charm(transaction_dict, minSup, total_trans)
    # closed_items_df = pd.DataFrame()
    # closed_items_df['itemset'] = closed_items.keys()
    # closed_items_df['support'] = closed_items.values()

    # print(closed_items_df)
    


    charm = CharmAlgorithm()
    ori = {'A': [1, 3, 4, 5], 'D': [2, 4, 5, 6], 'T': [1, 3, 5, 6], 'W': [1, 2, 3, 4, 5], 'C': [1, 2, 3, 4, 5, 6]}
    c = charm.charm(ori, 50, 6)

    print(c)
   
