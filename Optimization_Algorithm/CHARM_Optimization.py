class Charm_Opt_Algorithm(object):
    set = set()

    def __init__(self):
        self.skipSet = set()

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
            val = dic.get(key)  # ?????

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
        * Function to check if an item set is subsumed by the existing item sets.
        *
        * @param c - dict
        * @param y - set
        * @return true/false
    '''
    def exist_Superset(self, c, y):
        y = set(y)

        for val in c.values():
            val = set(val)
            if val == y or y.issubset(val):
                return True

        return False

    '''
        * Charm - Extended routine
        *
        * @param nodes - dict
        * @param c - dict
        * @param minSup - int
    '''
    def newCharm_Extended(self, nodes, newClosed, minSup, total_trans):
        nodes = self.sortDict(nodes)
        items = list(nodes.keys())

        for idx1 in range(len(items)):
            xi = items[idx1]

            if self.skipSet.__contains__(xi):
                continue

            # x_prev = xi
            # x_next = str()
            x = str()
            newN = dict()

            for idx2 in range(idx1 + 1, len(items)):
                xj = items[idx2]
                # x_next = xj

                if(self.skipSet.__contains__(xj)):
                    continue

                x = self.getStringUnion(xi, xj)
                trans_Xi = set(nodes.get(xi))
                trans_Xj = set(nodes.get(xj))

                y = sorted(list(trans_Xi & trans_Xj))

                if len(y) >= (minSup*total_trans)/100:
                    if trans_Xi == trans_Xj:            # Property 1
                        self.skipSet.add(xj)
                        self.replaceInItems(xi, x, newN)
                        self.replaceInItems(xi, x, nodes)
                        xi = x
                    elif trans_Xi.issubset(trans_Xj):   # Property 2
                        self.replaceInItems(xi, x, newN)
                        self.replaceInItems(xi, x, nodes)
                        xi = x
                    elif trans_Xj.issubset(trans_Xi):   # Property 3
                        self.skipSet.add(xj)
                        if self.exist_Superset(newClosed, y)==False:
                            newN.update({x: y})
                    else:                               # Property 4
                        if self.exist_Superset(newClosed, y)==False:
                            newN.update({x: y})

            newN = self.sortDict(newN)

            if len(newN) != 0:
                closed = newClosed
                self.newCharm_Extended(newN, closed, minSup, total_trans)

            newClosed.update({xi: nodes.get(xi)})



    '''
        * CHARM routine - Items are ordered lexicographically.
        *
        * @param ip - dict
        * @param minSup - int
        * @return c
    '''
    def newCharm(self, D, minSup, total_trans):
        # Eliminate items that don't satisfy the min support property

        for key in list(D.keys()):
            if len(D.__getitem__(key)) < (minSup*total_trans)/100:
                D.pop(key)

        # Generate the closed item sets
        newClosed = dict()
        self.newCharm_Extended(D, newClosed, minSup, total_trans)

        for key, val in newClosed.items():
            support = round(float((len(val) / total_trans) * 100), 4)
            newClosed.update({key: support})

        return newClosed


if __name__ == '__main__':
    charm = Charm_Opt_Algorithm()

    # ori = {'A': [1, 3, 4, 5], 'D': [2, 4, 5, 6], 'T': [1, 3, 5, 6], 'W': [1, 2, 3, 4, 5], 'C': [1, 2, 3, 4, 5, 6]}
    # c = charm.newCharm(ori, 50, 6)

    ori = {'A': [1,2,3,6], 'B': [1,2,4,6], 'C': [1, 3, 5, 6], 'D': [1,4,5,7], 'E': [1,2,5,7]}
    c = charm.newCharm(ori, 10, 7)


    print(c)
