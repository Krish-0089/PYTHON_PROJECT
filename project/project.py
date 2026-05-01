import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestRegressor

df=pd.read_csv("E:\\SALES_DATA.csv")

product_list=df["Model Name"].unique()
product_list=list(product_list)
product_list.sort()

connection=sqlite3.connect("sales_users.db")
cursor=connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    product TEXT
)
""")

connection.commit()

def get_product_data(product_name):
    product_data=df[df["Model Name"]==product_name]

    if len(product_data)==0:
        return None

    row=product_data.values[0]
    return row

def get_prices_and_months(row):
    prices=[]
    months=[]

    column_names=list(df.columns)

    for column_number in range(3,len(column_names)):
        month_name=column_names[column_number]
        price_value=row[column_number]

        if pd.isna(price_value):
            continue

        if price_value=="N/A":
            continue

        if price_value=="":
            continue

        prices.append(float(price_value))
        months.append(month_name)

    return prices,months

def add_record():
    user_name=name_entry.get()
    selected_product=product_combo.get()

    if user_name=="":
        result_label.config(text="Please enter your name")
        return

    if selected_product=="Select Product":
        result_label.config(text="Please select a product")
        return

    cursor.execute(
        "INSERT INTO user_data(name, product) VALUES(?, ?)",
        (user_name,selected_product)
    )

    connection.commit()

    result_label.config(text="Added successfully")

def show_records():
    record_window=tk.Toplevel(root)
    record_window.title("Saved Records")

    table=ttk.Treeview(
        record_window,
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
    records=cursor.fetchall()

    for record in records:
        table.insert("","end",values=record)

def analyze_product():
    user_name=name_entry.get()
    selected_product=product_combo.get()

    if selected_product=="Select Product":
        result_label.config(text="Please select a product")
        return

    row=get_product_data(selected_product)

    if row is None:
        result_label.config(text="Product not found")
        return

    prices,months=get_prices_and_months(row)

    if len(prices)==0:
        result_label.config(text="No valid price data available")
        return

    average_price=sum(prices)/len(prices)
    lowest_price=min(prices)
    highest_price=max(prices)

    lowest_price_month=months[prices.index(lowest_price)]
    highest_price_month=months[prices.index(highest_price)]

    result_text=""
    result_text+="User: "+user_name+"\n"
    result_text+="Product: "+selected_product+"\n\n"
    result_text+="Average Price: "+str(round(average_price,2))+"\n"
    result_text+="Lowest Price: "+str(lowest_price)+" ("+lowest_price_month+")\n"
    result_text+="Highest Price: "+str(highest_price)+" ("+highest_price_month+")"

    result_label.config(text=result_text)

def show_graph():
    selected_product=product_combo.get()

    if selected_product=="Select Product":
        result_label.config(text="Please select a product")
        return

    row=get_product_data(selected_product)

    if row is None:
        result_label.config(text="Product not found")
        return

    prices,months=get_prices_and_months(row)

    if len(prices)==0:
        result_label.config(text="No data available for graph")
        return

    plt.figure(figsize=(8,5))
    plt.plot(months,prices,marker="o")

    plt.title(selected_product+" Price Trend")
    plt.xlabel("Month")
    plt.ylabel("Price")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

def predict_price():
    selected_product=product_combo.get()

    if selected_product=="Select Product":
        result_label.config(text="Please select a product")
        return

    row=get_product_data(selected_product)

    if row is None:
        result_label.config(text="Product not found")
        return

    prices,months=get_prices_and_months(row)

    if len(prices)<2:
        result_label.config(text="Not enough data to predict price")
        return

    month_numbers=[]

    for i in range(len(prices)):
        month_numbers.append(i)

    X=np.array(month_numbers).reshape(-1,1)
    y=np.array(prices)

    model=RandomForestRegressor(n_estimators=100,random_state=42)
    model.fit(X,y)

    next_month_number=len(prices)
    next_month=np.array([[next_month_number]])

    predicted_price=model.predict(next_month)[0]

    result_label.config(
        text="Predicted Next Month Price: "+str(round(predicted_price,2))
    )

root=tk.Tk()
root.title("Sales Analyzer")
root.geometry("550x350")

title_label=tk.Label(root,text="Sales Analyzer Project",font=("Arial",16,"bold"))
title_label.grid(row=0,column=0,columnspan=2)

name_label=tk.Label(root,text="Enter Name")
name_label.grid(row=1,column=0)

name_entry=tk.Entry(root,width=35)
name_entry.grid(row=1,column=1)

product_label=tk.Label(root,text="Select Product")
product_label.grid(row=2,column=0)

product_combo=ttk.Combobox(root,values=product_list,width=32)
product_combo.grid(row=2,column=1)
product_combo.set("Select Product")

analyze_button=tk.Button(root,text="Analyze",width=15,command=analyze_product)
analyze_button.grid(row=3,column=0)

graph_button=tk.Button(root,text="Graph",width=15,command=show_graph)
graph_button.grid(row=3,column=1)

predict_button=tk.Button(root,text="Predict",width=15,command=predict_price)
predict_button.grid(row=4,column=0)

add_button=tk.Button(root,text="Add Record",width=15,command=add_record)
add_button.grid(row=4,column=1)

show_button=tk.Button(root,text="Show Records",width=15,command=show_records)
show_button.grid(row=5,column=0)

result_label=tk.Label(root,text="",justify="left",font=("Arial",10))
result_label.grid(row=6,column=0,columnspan=2)

root.mainloop()

connection.close()
