import itertools


class AssociationRules(dict):
    def __init__(self):
        self.rules = dict()

    def getUnionString(self, s1, s2):
        newStrArray = list(set(s1).union(s2))

        for i in range(len(newStrArray)):
            temp = [newStrArray[i]]
            newStrArray.pop(i)
            newStrArray.insert(i, temp)

        return newStrArray

    def toString(self, lst):
        leng = len(lst)
        if leng == 1:
            newStr = ''.join(lst)
        else:
            newStr = ', '.join(lst)

        return newStr

    # def createSubItemset(self, itemset):
    #     from collections import OrderedDict

    #     itemset = sorted(itemset)
    #     subset = list()

    #     if len(itemset) > 2:
    #         for item in itemset:
    #             subset.append([item])
    #         for start in range(len(itemset) - 1):
    #             leng = 1
    #             while leng < len(itemset) - 1:
    #                 xi = list()
    #                 for idx1 in range(start, len(itemset)):
    #                     xi.append(itemset[idx1])
    #                     if len(xi) == leng and len(xi) < len(itemset):
    #                         for idx2 in range(idx1 + 1, len(itemset)):
    #                             xj = [itemset[idx2]]
    #                             x = self.getUnionString(xi, xj)
    #                             subset.append(x)

    #                # reserve:
    #                 xi = list()
    #                 for idx1 in range(len(itemset) - 1, start, -1):
    #                     xi.append(itemset[idx1])
    #                     if len(xi) == leng and len(xi) < len(itemset):
    #                         for idx2 in range(idx1-1, start - 1, -1):
    #                             xj = [itemset[idx2]]
    #                             x = self.getUnionString(xi, xj)
    #                             subset.append(x)
    #                             for i in subset:
    #                                 i = (str(i).replace(',', ''))
    #                                 subset = list(map(list, OrderedDict.fromkeys(map(tuple, i))))

    #                 leng += 1

    #     return subset

    import itertools

    def createSubItemset(self,itemset):
        itemset = sorted(itemset)
        n = len(itemset)
        subset = []
        if n > 2:
            for r in range(1, n):  # 1..n-1
                for comb in itertools.combinations(itemset, r):
                    subset.append(list(comb))
        return subset


    def totalTransaction(self, oriDict):
        transaction = set()
        for transset in oriDict.values():
            for trans in transset:
                transaction.add(trans)

        total_trans = len(transaction)

        return total_trans

    def getUnionTransaction(self, x, oriDict):
        if len(x[0]) == 1:
            x[0] = self.toString(x[0])
            uniTrans = set(oriDict.__getitem__(x[0]))
        else:
            uniTrans = set(self.getUnionTransaction(x[0], oriDict))


        for idx in range(1, len(x)):
            if len(x[idx]) == 1:
                x[idx] = self.toString(x[idx])
                uniTrans = uniTrans & set(oriDict.__getitem__(x[idx]))
            else:
                uniTrans = uniTrans & set(self.getUnionTransaction(x[idx], oriDict))

        uniTrans = sorted(uniTrans)

        return uniTrans

    def Support(self, x, oriDict):
        length = len(x)

        # Compute total transaction in DB
        total_trans = self.totalTransaction(oriDict)

        # Compute support
        if length == 1:
            countX = len(oriDict.__getitem__(self.toString(x)))
            suppX = countX / total_trans
        else:
            uniTrans = self.getUnionTransaction(x, oriDict)
            countX = len(uniTrans)
            suppX = countX / total_trans

        return round(suppX, 4)

    def Confidence(self, xi, xj, oriDict):
        rule = self.getUnionString(xi, xj)
        supp_xi = self.Support(xi, oriDict)
        supp_xj = self.Support(xj, oriDict)
        supp_rule = self.Support(rule, oriDict)

        if supp_xi > 0 and supp_xj > 0:
            conf_rule = round(float(supp_rule / supp_xi), 4)
            lift = round(float(conf_rule / supp_xj), 4)

        return conf_rule, lift, supp_rule

    def check_rule(self, xi, xj, minConf, minSupp, oriDict):
        # check rule: Xi --> Xj
        conf_rule, lift, supp_rule = self.Confidence(xi, xj, oriDict)
        x = self.getUnionString(xi, xj)
        uniTrans = self.getUnionTransaction(x, oriDict)

        rule = '[' + self.toString(xi) + ']' + ' --> ' + '[' + self.toString(xj) + ']'
        info = [uniTrans, supp_rule, conf_rule, lift]
        rule_dict = {rule: info}

        if supp_rule >= minSupp / 100 and conf_rule >= minConf / 100:
            return rule_dict

        return {}

    def AssRules(self, closedset, minSupp, minConf, oriDict):
        rule_list = dict()

        for key in list(closedset.keys()):
            key = key.split(', ')

            if len(key) == 2:
                xi = [key[0]]
                xj = [key[1]]
                rule = self.check_rule(xi, xj, minConf, minSupp, oriDict)
                rule_list.update(rule)

                # reverse:
                rule_reverse = self.check_rule(xj, xi, minConf, minSupp, oriDict)
                rule_list.update(rule_reverse)

            if len(key) > 2:
                sub = self.createSubItemset(key)
                for idx1 in range(len(sub)):
                    xi = sub[idx1]
                    for idx2 in range(idx1 + 1, len(sub)):
                        xj = sub[idx2]
                        len_rule = len(xi) + len(xj)
                        x = self.getUnionString(xi, xj)

                        if len_rule == len(x) == len(key):
                            rule = self.check_rule(xi, xj, minConf, minSupp, oriDict)
                            rule_list.update(rule)

                            # reverse:
                            rule_reverse = self.check_rule(xj, xi, minConf, minSupp, oriDict)
                            rule_list.update(rule_reverse)

        return rule_list

if __name__ == '__main__':
    AR = AssociationRules()
    import pandas as pd
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

    import CharmAlgorithm_v2 as charm
    charm = charm.CharmAlgorithm()
    minSup = 5
    minCon = 3
    closed = charm.charm(transaction_dict, minSup, total_trans)
    rules = AR.AssRules(closed, minSup, minCon, transaction_dict)
    print(rules)

    print("\n=== Association Rules ===")
    for rule, info in rules.items():
        transactions_list, supp, conf, lift = info
        print(f"{rule} | Support: {supp*100:.2f}% | Confidence: {conf*100:.2f}% | Lift: {lift:.2f}")    

    import pandas as pd

    # rule là dict đã có sẵn từ AssRules
    ruleDf = pd.DataFrame([
        {
            "antecedents": k.split("-->")[0].strip()[1:-1].split(", "),   # tách vế trái
            "consequents": k.split("-->")[1].strip()[1:-1].split(", "),   # tách vế phải
            "support": v[1],       # giá trị support
            "confidence": v[2],    # giá trị confidence
            "lift": v[3]           # giá trị lift
        }
        for k, v in rules.items()
    ])

    print(ruleDf)


    # AR = AssociationRules()
    # ori = {'A': ['1', '3', '4', '5'], 'D': ['2', '4', '5', '6'], 'T': ['1', '3', '5', '6'], 'W': ['1', '2', '3', '4', '5'], 'C': ['1', '2', '3', '4', '5', '6']}
    # closed = {'A, C, T, W': 60.0, 'A, C, W': 80.0, 'C, D, W': 60.0, 'C, D': 80.0, 'C, T': 80.0, 'C, W': 100.0, 'C': 100.0}
    # rule = AR.AssRules(closed, 50, 80, ori)