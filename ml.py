import requests
import simplejson
import unidecode
import operator
import json
import sys
from IPython.core.display import display, HTML
import pandas as pd
from collections import OrderedDict
from datetime import date
import random

def path_to_image_html(path):
    '''
     This function essentially convert the image url to 
     '<img src="'+ path + '"/>' format. And one can put any
     formatting adjustments to control the height, aspect ratio, size etc.
     within as in the below example. 
    '''

    return '<img src="'+ path + '" style=max-height:80px;"/>'

def path_to_link_html(path):
    '''
     This function essentially convert the image url to 
     '<img src="'+ path + '"/>' format. And one can put any
     formatting adjustments to control the height, aspect ratio, size etc.
     within as in the below example. 
    '''

    return '<a href="'+ path + '">link</a>'


def check_ALL_list_in_title(list,string ):
# ALL NEEDS TO MATCH
    result = 1
    for item in list:
        if item.lower() in string.lower():
            result = 1
        else:
            result = 0
    return result


def check_ANY_list_in_title(list,string ):
# ANY NEEDS TO MATCH
    result = 0
    for item in list:
        #print ("item:",item,"str:",string)
        if item.lower() in string.lower() :
            result = 1
    return result



def search_mla_return_list(product,min_price,max_price):
    #print ("Returning complete MLA list for product",product)
    link = 'https://api.mercadolibre.com/sites/MLA/search?q=\'' + product + '\'' 
    price_filter = "&price=" + str(min_price) + "-" + str(max_price)
    link2 = link + '&offset=' + str(0) + '&limit=' + str(50) + price_filter
    r = requests.get(link2)
    #print (link2)
    c = r.json()
    #print (c['results'][0])
    c_orig = c
    c_partial = c['results']
    #print (c_partial)
    start =  c['paging']['offset']
    end =  c['paging']['limit']
    total =  c['paging']['total'] 
    total_saved = total
    total_c = c['results']
    maximum_sell = 0
    print ("Total found:",total," (limited to 1k no token) start:",start," end ",end," , range: ",min_price,"-",max_price)
    if total > 1000:
        total = 1000
    # TEMOPORARY
    num_new = 0
    num=0
    num_new = 0
    while ( total > 51 and end > 10 ): # and 0):  ## <--- full list instead of first 50
        start = start + end
        print (start,"..",end='')
        if ( (c['paging']['total'] - start) < end  ):
            end = c['paging']['total'] - 1 - start 
        link2 = link + '&offset=' + str(start) + '&limit=' + str(end) + price_filter
        #print ("requesting LINK:",link2)
        r = requests.get(link2)
        c = r.json()
        c_partial = 0
        #print ("Total:",c['paging']['total']," start:",start," limit ",end)
        total_c = total_c + c['results']
        total = total - end 
        num = num + 1 
    return total_c

def return_max_sold_from_list(list,product,min_price,max_price):
    #print ("----- Searching max sold...");
    product_list = product.split()
    maximum_sell = 0
    num_new = 0
    for x in list[:]:
        #print(c['site_id'], c['results']['title'],c['results']['sold_quantity'], "$",c['results']['price'],c['site_id'], c['results']['address']['city_name'])
        sold_qty = list[num_new]['sold_quantity']
        price = list[num_new]['price']
        #print ("sold qty",sold_qty,"num:",num)
        title = unidecode.unidecode(list[num_new]['title']).lower()
        if ( sold_qty > maximum_sell and check_ALL_list_in_title(product_list,title ) and not check_ALL_list_in_title(product_to_avoid.split(),title ) and ( int(price) >= int(min_price) and int(price) <= int(max_price) )):
            maximum_sell = sold_qty
            #print ("new max sell found",maximum_sell)
        num_new = num_new + 1
    #print ("....max units sold at this range: ",maximum_sell)
    return maximum_sell

def return_tuples_from_list(list,product,min_price,max_price):
    print ("----- Searching maximum units sold...")
    product_list = product.split()
    maximum_sell = 0
    num_new = 0
    for x in list[:]:
        #print(c['site_id'], c['results']['title'],c['results']['sold_quantity'], "$",c['results']['price'],c['site_id'], c['results']['address']['city_name'])
        sold_qty = list[num_new]['sold_quantity']
        price = list[num_new]['price']
        title = list[num_new]['title']
        title_list = title.split()
        title_short = title_list[0:3]
        #print ("Title short:",title_short)
        #print ("sold qty",sold_qty,"num:",num)
        title = unidecode.unidecode(list[num_new]['title']).lower()
        if ( sold_qty > maximum_sell and check_ALL_list_in_title(product_list,title ) and not check_ALL_list_in_title(product_to_avoid.split(),title ) and ( int(price) >= int(min_price) and int(price) <= int(max_price) )):
            maximum_sell = sold_qty
            #print ("Title short:",title_short) 
            #print ("new max sell found",maximum_sell)
        num_new = num_new + 1
    return maximum_sell

       
def return_products_from_list_pandas(total_c,product,condition,min_price,max_price):
    from operator import itemgetter
    import pandas as pd
    num = 0
    list_new = list()
    product_list = product.split()
    df = pd.DataFrame.from_dict(total_c)
    if (len(df)>0):
        df_resu = pd.DataFrame()
        df_temp = df.loc[:, ['title', 'price','sold_quantity','address','thumbnail','permalink','shipping','seller']].sort_values('sold_quantity',ascending=False)
        df_temp['city'] = df_temp['address'].apply(lambda x: x.get('city_name'))
        df_temp['seller_id'] = df_temp['seller'].apply(lambda x: x.get('id'))
        df_temp['free_shipping'] = df_temp['shipping'].apply(lambda x: x.get('free_shipping'))
        df_temp['state'] = df_temp['address'].apply(lambda x: x.get('state_name'))

        df_temp['total'] = df['price'] * df['sold_quantity']
        df_temp['title'] = df['title'].str.lower()
    return df_temp

def display_product(product,min_price_list,max_price_list,sell_condition,percentage_max_sell,other_locations,total):
    num = 0
    df_temp = ''
    df_temp = pd.DataFrame.from_dict([])
    for price in min_price_list:
        min_price = min_price_list[num]
        max_price = max_price_list[num]
        mla_list = search_mla_return_list(product,min_price,max_price)
        ranger = '$' + str(min_price) + '-$' + str(max_price)
        df = return_products_from_list_pandas(mla_list,product,sell_condition,min_price,max_price)

        for num2 in range(0,len(df)):
            df_value = df.iloc[num2]
            if ( int(df_value['total']) > total ):
                #print (df_value)
                df_temp = df_temp.append(df_value, ignore_index=True)
                   # df_final = df_final.to_html('df_final.html')
        if ( len(df_temp)>0):        
            display(HTML(df_temp.loc[:, ['title', 'price','sold_quantity','total','state','city','thumbnail','permalink','seller_id','free_shipping']].sort_values('total',ascending=False).to_html(border=1, escape=False ,formatters=dict(thumbnail=path_to_image_html,permalink=path_to_link_html))))
            #display(HTML(df_temp.to_html(border=1, escape=False ,formatters=dict(thumbnail=path_to_image_html,permalink=path_to_link_html))))
        num = num + 1
    return df_temp
        

def return_products_from_list_in_locations_pandas(total_c,product,sell_condition,locations,min_sell,min_price,max_price):
    #print ("----- Printing products from list in LOCATION..min $:",min_price," max $:",max_price)
    #sorted(total_c, key=lambda sold_quantity: sold_quantity[8])
    #sorted(total_c, key=operator.itemgetter(16) )
    df = pd.DataFrame.from_dict(total_c)
    df_resu = pd.DataFrame()
    df_temp = df.loc[:, ['title', 'price','sold_quantity','address','thumbnail','permalink']].sort_values('sold_quantity',ascending=False)
    df_temp['city'] = df_temp['address'].apply(lambda x: x.get('city_name'))
    df_temp['state'] = df_temp['address'].apply(lambda x: x.get('state_name'))
    df_temp2['title'] = df_temp2['title'].str.lower()

   
    for palabra in product.split(' '):
        df_temp2 = df_temp2[ df_temp2['title'].str.contains(palabra)]
        df_resu = df_resu.append(df_temp2)
    df_temp2 = df_resu[ df_resu['city'].str.contains(locations)]
    return df_temp2
