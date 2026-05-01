import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestRegressor

# reading sales dataset
df=pd.read_csv("E:\\SALES_DATA.csv")

# making product list for dropdown
product=df["Model Name"].unique()
product=list(product)
product.sort()

# connecting sqlite database
conn=sqlite3.connect("sales_users.db")
cursor=conn.cursor()

# creating table for storing user records
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    product TEXT
)
""")

conn.commit()

def getting(product_name):
    # finding selected product from dataset
    data=df[df["Model Name"]==product_name]

    if len(data)==0:
        return None

    row=data.values[0]
    return row

def get(row):
    # collecting prices and months
    prices=[]
    months=[]

    column_names=list(df.columns)

    for col in range(3,len(column_names)):
        mon=column_names[col]
        price=row[col]

        if pd.isna(price):
            continue

        if price=="N/A":
            continue

        if price=="":
            continue

        prices.append(float(price))
        months.append(mon)

    return prices,months

def add_record():
    # adding user selected product into sqlite 
    user=entry.get()
    select=prod.get()

    if user=="":
        result.config(text="Please enter your name")
        return

    if select=="Select Product":
        result.config(text="Please select a product")
        return

    cursor.execute(
        "INSERT INTO user_data(name, product) VALUES(?, ?)",
        (user,select)
    )

    conn.commit()

    result.config(text="Added successfully")

def show_records():
    # showing save record in new window
    records=tk.Toplevel(root)
    records.title("Saved Records")

    table=ttk.Treeview(
        records,
        columns=("ID","Name","Product"),
        show="headings"
    )

    table.heading("ID",text="ID")
    table.heading("Name",text="Name")
    table.heading("Product",text="Product")

    table.column("ID",width=50)
    table.column("Name",width=150)
    table.column("Product",width=250)

    table.pack(fill="both",expand=True)

    cursor.execute("SELECT * FROM user_data")
    data=cursor.fetchall()

    for record in data:
        table.insert("","end",values=record)

def analysis():
    # analyze average, lowest and highest price in the last year and the current year
    user=entry.get()
    select=prod.get()

    if select=="Select Product":
        result.config(text="Please select a product")
        return

    row=getting(select)

    if row is None:
        result.config(text="Product not found")
        return

    prices,months=get(row)

    if len(prices)==0:
        result.config(text="No valid price data available")
        return

    average=sum(prices)/len(prices)
    lowest=min(prices)
    highest=max(prices)

    low_mon=months[prices.index(lowest)]
    high_mon=months[prices.index(highest)]

    res=""
    res+="User: "+user+"\n"
    res+="Product: "+select+"\n\n"
    res+="Average Price: "+str(round(average,2))+"\n"
    res+="Lowest Price: "+str(lowest)+" ("+low_mon+")\n"
    res+="Highest Price: "+str(highest)+" ("+high_mon+")"

    result.config(text=res)

def graph():
    # plot graph on the basis of price per month 
    select=prod.get()

    if select=="Select Product":
        result.config(text="Please select a product")
        return

    row=getting(select)

    if row is None:
        result.config(text="Product not found")
        return

    prices,months=get(row)

    if len(prices)==0:
        result.config(text="No data available for graph")
        return

    plt.figure(figsize=(8,5))
    plt.plot(months,prices,marker="o")

    plt.title(select+" Price Trend")
    plt.xlabel("Month")
    plt.ylabel("Price")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

def predict_price():
    # prediction of next month price
    select=prod.get()

    if select=="Select Product":
        result.config(text="Please select a product")
        return

    row=getting(select)

    if row is None:
        result.config(text="Product not found")
        return

    prices,months=get(row)

    if len(prices)<2:
        result.config(text="Not enough data to predict price")
        return

    month_numbers=[]

    for i in range(len(prices)):
        month_numbers.append(i)

    X=np.array(month_numbers).reshape(-1,1)
    y=np.array(prices)

    model=RandomForestRegressor(n_estimators=100,random_state=42)
    model.fit(X,y)

    next_month_number=len(prices)
    next=np.array([[next_month_number]])

    predicted_price=model.predict(next)[0]

    result.config(
        text="Predicted Next Month Price: "+str(round(predicted_price,2))
    )

# creating the python gui for project 
root=tk.Tk()
root.title("Sales Analyzer")
root.geometry("550x350")

title_label=tk.Label(root,text="Sales Analyzer Project",font=("Arial",16,"bold"))
title_label.grid(row=0,column=0,columnspan=2)

name=tk.Label(root,text="Enter Name")
name.grid(row=1,column=0)

entry=tk.Entry(root,width=35)
entry.grid(row=1,column=1)

product_label=tk.Label(root,text="Select Product")
product_label.grid(row=2,column=0)

prod=ttk.Combobox(root,values=product,width=32)
prod.grid(row=2,column=1)
prod.set("Select Product")

analyze=tk.Button(root,text="Analyze",width=15,command=analysis)
analyze.grid(row=3,column=0)

graph_button=tk.Button(root,text="Graph",width=15,command=graph)
graph_button.grid(row=3,column=1)

predict=tk.Button(root,text="Predict",width=15,command=predict_price)
predict.grid(row=4,column=0)

add_button=tk.Button(root,text="Add Record",width=15,command=add_record)
add_button.grid(row=4,column=1)

show_button=tk.Button(root,text="Show Records",width=15,command=show_records)
show_button.grid(row=5,column=0)

result=tk.Label(root,text="",justify="left",font=("Arial",10))
result.grid(row=6,column=0,columnspan=2)

root.mainloop()

conn.close()
