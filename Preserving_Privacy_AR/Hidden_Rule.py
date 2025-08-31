from Association_Rule import *
from Processing_Data.ProcessingData import *


class Hidden(dict):
    def __init__(self):
        self.db = dict()

    def sortDictbyValue(self, dic, reverse=False):
        import collections
        sorted_aphal = dict(collections.OrderedDict(sorted(dic.items())))

        sorted_dict = {}
        sorted_keys = sorted(sorted_aphal, key=sorted_aphal.get, reverse=reverse)

        for i in sorted_keys:
            sorted_dict[i] = sorted_aphal[i]

        return sorted_dict

    def replace_character(self, x):
        x = x.replace('[', '')
        x = x.replace(']', '')
        s = ' --> '
        c = '\''

        if c in x:
            x = x.replace('\'', '')

        if s in x:
            x = x.split(s)

        return x


    def convertToList(self, x):
        x = self.replace_character(x)
        character = ', '
        if type(x) == list:
            for i in range(len(x)):
                x[i] = [x[i]]
                str_xi = str(x[i])
                if character in str_xi:
                    str_xi = self.replace_character(str_xi)
                    x[i] = str_xi.split(', ')
        else:
            x = x.split(character)

        return x


    def sensitive_rule(self, rule_set):
        sensitive_ruleset = dict()

        for rule, info in rule_set.items():
            consequents = self.convertToList(rule)[1]
            liftRule = info[-1]
            if liftRule > 1 and len(consequents) == 1:
                sensitive_ruleset.update({rule: info})

        return sensitive_ruleset


    def SuppReduction(self, rule_set, oriDB, minConf, df):
        sens_rule = self.sensitive_rule(rule_set)

        for rule, info in sens_rule.items():
            transRule = info[0]
            numOfItem = dict()

            for t in transRule:
                count = 0
                for item, trans in oriDB.items():
                    if t in oriDB.__getitem__(item):
                        count += 1
                    numOfItem.update({t: count})
                    numOfItem = self.sortDictbyValue(numOfItem)

            trans_sorted = list(numOfItem.keys())
            confRule = info[2]

            while confRule >= (minConf)/100:
                # Choose the first transaction in trans_sorted:
                t = trans_sorted[0]

                # sort dict for support
                dic_Support = dict()
                AR = AssociationRules()
                rule_lst = self.convertToList(rule)

                for item in rule_lst:
                    supp = AR.Support(item, oriDB)
                    item = AR.toString(item)
                    dic_Support.update({item: supp})
                dic_Support = self.sortDictbyValue(dic_Support, True)

                # Choose the item j in rule with the highest minsup
                j = self.convertToList(list(dic_Support.keys())[0])
                prev_j = self.convertToList(list(dic_Support.keys())[1])

                # replace a '0' mark for the place of j in t:
                # get index of t and j:
                if len(j) == 1:
                    col_idx = list(df.columns).index(j[0])
                    row_idx = list(df.index).index(t)
                    print(str(row_idx) + ':' + str(t), '\t', str(col_idx) + ': ' + str(j[0]), '\t',
                          df.iat[row_idx, col_idx], 'replace', end='')
                    df.iat[row_idx, col_idx] = 0
                    print(df.iat[row_idx, col_idx])

                # Recompute minsup and minconf:
                handle = procData()
                oriDB = handle.handleFiletoApplyCHARM(df)

                # check j in antecedents or consequents:
                if j == rule_lst[0]:    # j is antecedents
                    suppXi = AR.Support(j, oriDB)
                else:
                    suppXi = AR.Support(prev_j, oriDB)

                suppRule = AR.Support(rule_lst, oriDB)
                if suppXi > 0:
                    confRule = round(float(suppRule / suppXi), 4)

                # Recompute the minconf of other affected rules:
                for r, infomation in rule_set.items():
                    r = self.convertToList(r)
                    if r != rule_lst:
                        if j in r:
                            antecedent = r[0]
                            consequent = r[1]
                            confDifRule, liftDifRule, suppDifRule = AR.Confidence(antecedent, consequent, oriDB)
                            infomation[1] = suppDifRule
                            infomation[2] = confDifRule
                            infomation[3] = liftDifRule

                # remove t from TransRule:
                trans_sorted.remove(t)

            # Remove rule from Rule set:
            rule_set.pop(rule)

        return oriDB
