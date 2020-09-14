import requests
from lxml import etree
import re
import os

target_dir=r"D:\AllDowns\newbooks"

fetch_error_dir=r"D:\AllDowns\newbooks\notFound"

if not os.path.exists(fetch_error_dir):
    os.makedirs(fetch_error_dir)



douban_url1="https://www.douban.com/search?cat=1001&q="
douban_url2="https://www.douban.com/search?q="
douban_url=douban_url1

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}

def get_keyword_str(book_name_with_pdf):
    assert book_name_with_pdf.endswith(".pdf")
    book_name_without_pdf = book_name_with_pdf[:-4]

    patt_delims="[_|-|——|(| ]"
    keyword_str=re.sub(patt_delims,"+",book_name_without_pdf,re.S)

    # 特殊补充1,长串数字排除SS号

    keyword_str = re.sub(r"\d{8}", "", keyword_str, re.S)

    # 特殊补充2, “”换成""

    keyword_str=keyword_str.replace("“","\"")
    keyword_str=keyword_str.replace("”","\"")

    print(f"Keyword str:{keyword_str}")
    return keyword_str

def get_new_name(book_name_with_pdf, isbn):
    assert book_name_with_pdf.endswith(".pdf")
    if not os.sep in book_name_with_pdf:
        book_name_with_pdf=f"{target_dir}{os.sep}{book_name_with_pdf}"
    book_name_without_pdf=book_name_with_pdf[:-4]
    new_name=f"{book_name_without_pdf}{'isbnisbn'}{isbn}{'.pdf'}"
    print(f"New name:{new_name}")
    return new_name

def get_items_from_fetch(keyword_str):
    url=f"{douban_url}{keyword_str}"
    # print(url)
    page_text=requests.get(url,headers=headers).text
    # print(page_text)
    html=etree.HTML(page_text)
    patt_info="//span[@class='subject-cast']//text()"
    patt_link="//a[@class='nbg']//@href"
    infos=html.xpath(patt_info)
    links=html.xpath(patt_link)
    # print(infos)
    # print(links)
    # assert infos!=[] and links!=[]
    return infos,links

def btf_print_infos(infos):
    for idx,info in enumerate(infos,1):
        print(info,idx,sep="\t"*3)
        # print("")

def pickIdx_from_infos(infos):
    btf_print_infos(infos)
    pick_idx=int(input("Pick it(one base):\t"))-1
    assert pick_idx>=0
    if pick_idx<=len(infos)-1:
        print("Your choice:",infos[pick_idx])
        return pick_idx
    else:
        return 114514

def fetch_isbn_from_link(book_link):
    page_text=requests.get(book_link,headers=headers).text
    patt_isbn="<span class=\"pl\">ISBN:</span> (.*?)<br/>"
    isbns=re.findall(patt_isbn,page_text)
    assert len(isbns)==1
    return isbns[0]

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
            this_infos,this_links=get_items_from_fetch(this_keyword_str)
            if this_infos==[] and this_links==[]:
                move_when_fetch_empty(this_book_name_with_pdf)
                continue
            pick_idx=pickIdx_from_infos(this_infos)
            if pick_idx<=len(this_infos):
                pick_link=this_links[pick_idx]
            else:
                move_when_fetch_empty(this_book_name_with_pdf)
                continue
            isbn=fetch_isbn_from_link(pick_link)
            print(f"ISBN:{isbn}")
            new_name=get_new_name(this_book_name_with_pdf,isbn)
            this_book_name_with_pdf=f"{target_dir}{os.sep}{this_book_name_with_pdf}"
            os.rename(this_book_name_with_pdf,new_name)
    print("done.")

if __name__ == '__main__':
    main()



