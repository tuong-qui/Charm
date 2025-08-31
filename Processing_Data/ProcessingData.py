import pandas as pd

class procData():
    def __init__(self):
        pass

    def sortByAphal(self, dic):
        import collections
        sorted_aphal = dict(collections.OrderedDict(sorted(dic.items())))
        return sorted_aphal

    def sortDict(self, dic):
        sorted_aphal = self.sortByAphal(dic)
        sorted_len = dict(sorted(sorted_aphal.items(), key=lambda i: len(i[1])))
        return sorted_len

    def encode_units(self, x):
        if int(x) <= 0:
            return 0
        if int(x) >= 1:
            return 1

    def total_transaction(self, df):
        return len(df.index)

    def handleFiletoDF(self, url, trans, item):
        df = pd.read_csv(url)
        df.head()
        columns = list(df.columns)
        for col in columns:
            if col != trans and col != item:
                del df[col]

        df[item] = df[item].str.strip()
        df.dropna(axis=0, subset=[trans], inplace=True)

        df = df.groupby([trans, item])[item].count().unstack().reset_index().fillna('0').set_index(trans)
        df_sets = df.applymap(self.encode_units)

        return df_sets

    def handleFiletoApplyCHARM(self, df):
        columns = list(df.columns)
        dataset = dict()

        for col in columns:
            transSet = []
            row_number = 0
            for val in df[col]:
                row_number += 1
                if val == 1:
                    trans = df.index.values[row_number-1]
                    transSet.append(trans)
                dataset.update({col: transSet})

        dataset = self.sortDict(dataset)

        return dataset

    def handleDictToDF(self, dic):
        dic = self.sortByAphal(dic)
        df = pd.DataFrame(columns=list(dic.keys()))
        df.head()

        transaction = set()
        for trans in dic.values():
            for i in trans:
                transaction.add(i)

        transaction = sorted(list(transaction))
        df['Transaction'] = transaction
        df.set_index('Transaction')

        df = df.groupby(['Transaction']).count()

        for col in df.columns:
            col_idx = list(df.columns).index(col)
            for trans in transaction:
                row_idx = list(df.index).index(trans)
                if trans in list(dic.__getitem__(col)):
                    df.iat[row_idx, col_idx] = 1

        return df

    def handleDFtoCSV(self, ori_df, res_df, col1, col2):
        ori_data = ori_df.to_dict('records')
        final_data = []

        res_data = []
        transaction = list(res_df.index)

        for trans in transaction:
            row_idx = list(res_df.index).index(trans)

            for item in res_df.columns:
                col_idx = list(res_df.columns).index(item)
                val_cell = res_df.iat[row_idx, col_idx]
                if val_cell == 1:
                    temp = {col1: trans, col2: item}
                    res_data.append(temp)

        # remove record don't exist in final_data:
        for i in range(len(ori_data)):
            trans = ori_data[i][col1]
            item = ori_data[i][col2]

            for j in range(len(res_data)):
                res_trans = res_data[j][col1]
                res_item = res_data[j][col2]
                if trans == res_trans and item == res_item:
                    final_data.append(ori_data[i])

        return final_data
