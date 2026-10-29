import pandas as pd

data = pd.read_csv("data/transactions.csv")

#print(data.head())

#data_old = pd.read_csv("data/old_ledger.txt", sep="\t", header=None)

#print("\n----------\n")

#print(data_old.head())

#data = pd.read_csv("data/transactions.csv", usecols=[0, 2,3])

#print(data.head())
#print("\n----------\n")
#print(data["hour"][0])
#print(data[2][0])

#print(data.qty[1:4])

#print(data["qty"][1:4])

#print(data.product)

#print(data["product"].head(15))

#print(data["hour"].describe())

#print(data["qty"].head(7))
#print(data.iloc[1]["product"])

#print((data["qty"] >= 3).head(7))

#print(data.head(7))
#print(data[data["qty"] >= 3].head(7))

#big = data[data["qty"] >= 3]

#big.index = range(len(big))

#print(big.head(7))

#print(data["qty"].describe())

#print(data.head())

#print(data.price.describe())

#print(data.groupby("product")["price"].mean())

#import calendar as cal

#data["dow"] = (data["day"] - 1) %5

#data["revenue"] = data["qty"] * data["product"]

#print(data.groupby("dow")["qty"].sum())

#print(data.groupby(["day","product"])["revenue"].sum().head(3))

#print(data.groupby("product")["revenue"].sum().idxmax())

#print(data.qty.describe())

#print(data.groupby("product")["qty"].mean())

#print(data["qty"].value_counts())