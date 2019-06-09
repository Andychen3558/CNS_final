#coding:UTF-8
import requests
from bs4 import BeautifulSoup
from random import randint

def get_img(word):
	#requests.get('https://github.com/', timeout=0.001)

	payload = {'q': word, 'tbm': 'isch'}
	count=0
	r = None
	while count<5 :
		try:
			headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'}

			r = requests.get('https://www.google.com.tw/search', params=payload,headers=headers, timeout=2)
			break
		except:
			count+=1
			#print(count)
	
	if not r:
		return "http://p1.pstatp.com/large/26e900008138d3c21cb2"
	#print(r.text)
	return parse_html(r.text)

def parse_html(html_doc):
	soup = BeautifulSoup(html_doc, 'html.parser')	
	#print(soup.find_all('a'))
	#print(soup.find_all('img')[rand].get('src'))
	image_set=[]
	for link in soup.find_all('img'):
		if link.get('data-src') is not None:
			image_set.append(link) 
			#print(link.get('data-src'))
	len_result=len(image_set)
	rand=randint(0, min(len_result,10)-1)

	return str(image_set[rand].get('data-src'))
	#print(str(link))


if __name__=="__main__":
	a='bear'
	print(get_img(a))

