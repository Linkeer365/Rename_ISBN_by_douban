import os

target_dir=r"D:\AllDowns\newbooks\notFound"
target_dir2=r"D:\刺头书"

with open(f"{target_dir}{os.sep}fetch_errors.txt","r",encoding="utf-8") as f:
	lines=f.readlines()

lines=[each.strip("\n") for each in lines]

for each in lines:
	old_name,isbn=each.split("\t")
	new_dir,old_name2=old_name.rsplit(os.sep,maxsplit=1)
	old_name2=old_name2[:-4]
	back_dir=new_dir.rsplit(os.sep,maxsplit=1)[0]
	if isbn:
		new_name=f"{back_dir}{os.sep}{old_name2}"
		new_name=f"{new_name}isbnisbn{isbn}.pdf"
		os.rename(old_name,new_name)
	else:
		new_name=f"{target_dir2}{os.sep}{old_name2}.pdf"
		os.rename(old_name,new_name)

print("done.")