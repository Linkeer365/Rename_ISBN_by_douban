import requests
from lxml import etree
import re
import os
import sys
import time


target_dir=r"D:\AllDowns\newbooks"

fetch_error_dir=r"D:\AllDowns\newbooks\notFound"

if not os.path.exists(fetch_error_dir):
    os.makedirs(fetch_error_dir)

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}

# 现在豆瓣要登录才能fetch了...那我就登录一下

# 用于维持登录会话，requests高级用法

# # 登录
# def login():
#     s = requests.Session()
#     url = 'https://accounts.douban.com/j/mobile/login/basic'
#     data = {
#         'ck': '',
#         "name":'13959253604',
#         "password":'xm111737',
#         'remember': 'true',
#     }
#     html = s.post(url,headers=headers,data=data)
#     return s,html
  

# # 获取个人信息
# def get_user_data(s):
#     url = 'https://www.douban.com/people/169098269/'
#     html = s.get(url).text
#     #print(html)
#     return html

# s,html1 = login()
# html2 = get_user_data(s)
# print(html2)
# sys.exit(0)



douban_url1="https://www.douban.com/search?cat=1001&q="
douban_url2="https://www.douban.com/search?q="
douban_url=douban_url1

def get_keyword_str(book_name_with_pdf):
    assert book_name_with_pdf.endswith(".pdf")
    book_name_without_pdf = book_name_with_pdf[:-4]

    patt_delims="[_|-|——|(| |\.]"
    keyword_str=re.sub(patt_delims,"+",book_name_without_pdf,re.S)

    # 特殊补充1,长串数字排除SS号

    keyword_str = re.sub(r"\d{8}", "", keyword_str, re.S)

    # 特殊补充2, “”换成""

    keyword_str=keyword_str.replace("“","\"")
    keyword_str=keyword_str.replace("”","\"")

    print(f"raw str:{book_name_without_pdf}")

    print("\n=== === === ===\n")
    print(f"Keyword str:{keyword_str}")
    return keyword_str

def get_new_name(book_name_with_pdf, isbn):
    assert book_name_with_pdf.endswith(".pdf")
    if not os.sep in book_name_with_pdf:
        book_name_with_pdf=f"{target_dir}{os.sep}{book_name_with_pdf}"
    book_name_without_pdf=book_name_with_pdf[:-4]
    if len(isbn)==13:
        new_name=f"{book_name_without_pdf}{'isbnisbn'}{isbn}{'.pdf'}"
    else:
        new_name=f"{book_name_without_pdf}{'dbdb'}{isbn}{'.pdf'}"
    print(f"New name:{new_name}")
    return new_name

def get_items_from_fetch(keyword_str):
    url=f"{douban_url}{keyword_str}"
    # print(url)
    page_text=requests.get(url,headers=headers).text
    time.sleep(1)
    # print(page_text)
    html=etree.HTML(page_text)
    patt_info="//span[@class='subject-cast']//text()"
    patt_link="//a[@class='nbg']//@href"
    patt_title="//a[@class='nbg']//@title"
    infos=html.xpath(patt_info)
    links=html.xpath(patt_link)
    titles=html.xpath(patt_title)
    # print("infos:\t",infos)
    # print("links:\t",links)
    # assert infos!=[] and links!=[]
    return infos,links,titles

def btf_print_infos(infos,titles):
    for idx,info in enumerate(infos,1):
        title=titles[idx-1]
        print(f"\n《{title}》")
        print(info,idx,sep="\t"*3)
        # print("")

def pickIdx_from_infos(infos,titles):
    btf_print_infos(infos,titles)
    pick_idx=int(input("Pick it(one base):\t"))-1
    assert pick_idx>=0
    if pick_idx<=len(infos)-1:
        print("Your choice:",infos[pick_idx])
        return pick_idx
    else:
        return 114514

def fetch_isbn_from_link(book_link):
    page_text=requests.get(book_link,headers=headers).text
    time.sleep(1)
    patt_isbn="<span class=\"pl\">ISBN:</span> (.*?)<br/>"
    isbns=re.findall(patt_isbn,page_text)
    if len(isbns)==1:
        return isbns[0]
    elif len(isbns)==2:
        print("ISBN List:\t",isbns)
        return [each for each in isbns if len(each)==13 or len(each)==10][0]

def move_when_fetch_empty(book_name_with_pdf):
    assert book_name_with_pdf.endswith(".pdf")
    if os.sep in book_name_with_pdf:
        book_path=book_name_with_pdf
        book_name_with_pdf=book_name_with_pdf.rsplit(os.sep,maxsplit=1)[1]
    else:
        book_path=f"{target_dir}{os.sep}{book_name_with_pdf}"
    new_path=f"{fetch_error_dir}{os.sep}{book_name_with_pdf}"
    os.rename(book_path,new_path)
    print(f"Fetch Error! Move to:{new_path}")

    with open(f"{fetch_error_dir}{os.sep}fetch_errors.txt","a",encoding="utf-8") as f:
        f.write(new_path+"\t"+"\n")
        print("One Written.")

def main():
    # 按照修改时间排序，最早的最先出现
    books=sorted(os.listdir(target_dir),key=lambda x: os.path.getmtime(os.path.join(target_dir, x)),reverse=True)
    for each in books:
        if each.endswith(".pdf") and (not "isbnisbn" in each):
            this_book_name_with_pdf=each
            this_keyword_str=get_keyword_str(this_book_name_with_pdf)
            this_infos,this_links,this_titles=get_items_from_fetch(this_keyword_str)
            if this_infos==[] and this_links==[]:
                move_when_fetch_empty(this_book_name_with_pdf)
                continue
            pick_idx=pickIdx_from_infos(this_infos,this_titles)
            if pick_idx<=len(this_infos)-1:
                pick_link=this_links[pick_idx]
            else:
                move_when_fetch_empty(this_book_name_with_pdf)
                continue
            isbn=fetch_isbn_from_link(pick_link)
            print(f"ISBN:{isbn}")
            if isbn==None:
                print(pick_link)
                isbn=re.findall("%2Fsubject%2F(\d+)%2F&query=",pick_link)[0]
            new_name=get_new_name(this_book_name_with_pdf,isbn)
            this_book_name_with_pdf=f"{target_dir}{os.sep}{this_book_name_with_pdf}"
            os.rename(this_book_name_with_pdf,new_name)
    for each in os.listdir(target_dir):
        if "None" in each:
            move_when_fetch_empty(each)
    print("done.")

if __name__ == '__main__':
    main()



