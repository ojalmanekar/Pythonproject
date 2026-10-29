import pandas as pd
import numpy as np

data = pd.read_csv("data/transactions.csv")

#print(data.head())

#print(type(data))

#data_old = pd.read_csv("data/old_ledger.txt", sep="\t", header=None)

#print(data_old.head())

#data_prod_qty = pd.read_csv("data/transactions.csv", usecols=[2,3])

#print(data_prod_qty.head())

#print(data_prod_qty["product"][1])

#data_old = pd.read_csv("data/old_ledger.txt")

#print(data_old.head())

#print(data.head())
#print("---")
#print(data.qty[1:4])
#print("----")
#print(data["qty"][1:4])


#print("---")
#print(data.product[1:4])
#print("----")
#print(data["product"][1:4])

#print(data["price"].describe())

#print(data["qty"].describe())

#print((data["qty"] > 3).head(15))

big = data[data["qty"] >= 3]

#print(big.head(10))

#print(big.loc[6])
#print(big.iloc[6])

#big.index = range(len(big))

#print(big.head(5))

#print(np.where(data["qty"] > 3))

#int("ashgdkashkjdhj")

#try:
#    int("ashgdkashkjdhj")
#except ValueError:
#    print("bad")


#print(data.head(6))

#print(big.head(6))

#data["revenue"] = data["qty"] * data["price"]

#print(data.head(6))

#by_product = data.groupby("product")["revenue"]

#print(by_product)

#by_product_count = by_product.sum()

#print(by_product_count)

#by_product_count_index = by_product.sum().sort_index()

#print(by_product_count_index)

