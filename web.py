from bs4 import BeautifulSoup
import requests
import re
import argparse
ap = argparse.ArgumentParser()
ap.add_argument('-i','--product', required=True, help="value")
ap.add_argument('-j','--start', required=True, help="value")
ap.add_argument('-k','--end', required=True, help="value")

args = vars(ap.parse_args())
product = args['product']
start_price =int(args['start'])
end_price =int(args['end'])

###
link1 = "https://www.flipkart.com/search?q="
link2 = "&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
# product = input("Please Write Product Name")
product= str(product)
product = product.replace(" ","-")
link = link1+str(product)+link2

print(link)
del link1,link2,product

# In[373]:


def next_slide(flag):
    flag=str(flag)
    page = link+"&page="+flag
    res = requests.get(page)
    htmlContent = res.content
    soup = BeautifulSoup(htmlContent,features="html.parser")
    containers = soup.find_all("div" ,class_="_1-2Iqu row")
    page_end = soup.find_all("div",{"class":"_2zg3yZ"})
    page_end= page_end[0].text
    page_end = page_end.split('of ')[1]
    last_page = page_end[0:2]
    #print(page)
    return containers,last_page


# In[372]:


import pandas as pd
df_col = pd.DataFrame(index = None) 

flag=1
page_end=2
while(flag<=page_end):
    try:
        containers,last_page = next_slide(flag)
        page_end = int(last_page)
        load = int((flag/page_end)*100)
    except:
        pass
    
    print("loading  "+str(load) +" %")
        
    flag=flag+1
    for container in containers:
        try:
                #Branding  
                feature_container  = container.find_all("ul",class_ = "vFw0gD")
                feature_container =str(feature_container)
                feature_container = feature_container.split('</li>')
        
                for i in range(0,5):                          
                    feature_container[i] = feature_container[i].split("tVe95H")[1]
                    feature_container[i] = str(feature_container[i])
                    feature_container[i] = feature_container[i].replace(",","")
                    feature_container[i] = feature_container[i].split(">")[1]
            
                #feature_container[i] = feature_container[i].split(">")
            
                product_name = container.find_all("div",{"class":"_3wU53n"})
                product_name= product_name[0].text
                Brand_name = product_name.split(' ')[0]
            #price
                price_container = container.find_all("div", {"class": "_1vC4OE _2rQ-NK"})
                price = price_container[0].text
                price = price.split('₹')[1]
                #Features
                  
                feature_0= feature_container[0]
                feature_1 = feature_container[1]
                feature_2 = feature_container[2]    
                feature_3 = feature_container[3] 
                feature_4 = feature_container[4]
                #print(str(Brand_name)+","+str(feature_0)+","+str(feature_1)+","+str(feature_2)+","+str(feature_3)+","+str(feature_4)+","+price.replace(",","")+"\n")     
                df_temp = pd.DataFrame({"Brand_name":[Brand_name], 
                         "feature_0":[feature_0],
                         "feature_1":[feature_1],
                         "feature_2":[feature_2],
                         "feature_3":[feature_3],
                         "feature_4":[feature_4],
                         "price":[price.replace(",","")]
                        } )
                df_col=df_col.append(df_temp, ignore_index=True)
                del Brand_name,feature_0,feature_1,feature_2,feature_3,feature_4,price
                
        except:
            pass
del containers,container,flag,df_temp,page_end,last_page,price_container,link,feature_container,load,i,product_name

# In[374]:

#training
try:
    import pandas as pd
    import numpy as np
    temp  = df_col.price.to_numpy()
    temp=temp.astype(np.int32) 
    df_col.price = temp.reshape((len(temp),1))
    lq = df_col.price.quantile(0.1)
    hq= df_col.price.quantile(0.98)
    IQR = hq - lq
    lower = lq 
    higher = lq +1.5*IQR
    lower,higher,IQR,lq
    df_col = df_col[(df_col.price>lq) & (df_col.price<hq)]
    data = df_col
    data['feature_0'] = data['feature_0'].fillna(data['feature_0'].mode()[0])
    data['feature_1'] = data['feature_1'].fillna(data['feature_1'].mode()[0])
    data['feature_2'] = data['feature_2'].fillna(data['feature_2'].mode()[0])
    data['feature_3'] = data['feature_3'].fillna(data['feature_3'].mode()[0])
    data['feature_4'] = data['feature_4'].fillna(data['feature_4'].mode()[0])

    filtered = data.groupby('Brand_name')['Brand_name'].filter(lambda x: len(x) >= 5)
    data = data[data['Brand_name'].isin(filtered)]
    filtered = data.groupby('feature_0')['feature_0'].filter(lambda x: len(x) >= 10)
    data = data[data['feature_0'].isin(filtered)]
    filtered = data.groupby('feature_1')['feature_1'].filter(lambda x: len(x) >= 5) 
    data = data[data['feature_1'].isin(filtered)]

    X = data.iloc[:,  0:-1].values
    y = data.iloc[:, 6:7].values
    y = y.astype(np.int32)
    from sklearn.preprocessing import LabelEncoder
    label = LabelEncoder()
    X[:,0] = label.fit_transform(X[:,0])
    X[:, 1] = label.fit_transform(X[:, 1])
    X[:,2] = label.fit_transform(X[:,2])
    X[:,3] = label.fit_transform(X[:,3])
    X[:, 4] = label.fit_transform(X[: , 4])
    X[:, 5] = label.fit_transform(X[: , 5])
    from sklearn.preprocessing import OneHotEncoder
    ohe = OneHotEncoder()
    X = ohe.fit_transform(X).toarray()
    X = pd.DataFrame(X)
   

    from sklearn.linear_model import LinearRegression
    regressor = LinearRegression()
   #from sklearn.svm import SVR 
    #regressor = SVR()
    regressor.fit(X,y)
    y_pred = regressor.predict(X)

    y_pred =y_pred.astype(np.int32)
   #print(y_pred)
    y = y.astype(np.int32)

    res = y_pred-y
    res = pd.DataFrame(res)
    df_col['Profit'] = res
    df_col=df_col.sort_values('Profit',ascending = False)
    #start_price = 10000
    #end_price = 20000
    m = df_col.price.to_numpy()
    array = m.astype(np.int32)
    array = array.reshape((len(array),1))
    data = df_col[array <= end_price]
    m = data.price.to_numpy()
    array = m.astype(np.int32)
    array = array.reshape((len(array),1))
    data= data[array >= start_price]
    data = data.iloc[:, 0:7]
    data =data.head(10)
    data.to_csv("sample.csv",index=False)
except:
    pass        
