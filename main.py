import requests
import re
import html as ht
import os
from concurrent.futures import ThreadPoolExecutor
MAX_WORKERS = min(32, os.cpu_count() * 4 + 1)
TABLE_PATTREN=re.compile(r'<table id="whatsnew-compact">.*?</table>',re.DOTALL)
TR_PATTREN=re.compile(r'<tr>.*?</tr>',re.DOTALL)
HREF_PATTERN = re.compile(r'href=[\'"].*?[\'"]', re.DOTALL)
DOWNLOAD_PATTERN = re.compile(r'<div id="appsummary">.*?</div>', re.DOTALL)
DOWNLOAD_LINK_PATTERN = re.compile(r'<a class="main-dlink".*?</a>', re.DOTALL)


seen=set()
download_page_url=[]
download_link=[]
cookies = {
    '_ga_EWWZQ61TLS': 'GS2.1.s1769086768$o1$g1$t1769087548$j21$l0$h0',
    '_ga': 'GA1.1.1691226360.1769086768',
    '__gads': 'ID=2090eb76dc3e26a9:T=1769086785:RT=1769087511:S=ALNI_Ma9YWY-V0W9JEWLk6RWzTgKfycW0g',
    '__gpi': 'UID=0000132d669074e3:T=1769086785:RT=1769087511:S=ALNI_MbDt4jCVjnpy2z6DFeaD94Xt72mlA',
    '__eoi': 'ID=17f33488ed335577:T=1769086785:RT=1769087511:S=AA-Afjb_8cGG8TS-5bRi7Pgt0Yht',
    'FCCDCF': '%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%2263eb12e4-b9ff-4b7d-8488-bc44b92a91df%5C%22%2C%5B1769086802%2C51000000%5D%5D%22%5D%5D%5D',
    'FCNEC': '%5B%5B%22AKsRol92565PbMgnuvZ2y0FZnv9PJp_9AQO-tyCZkepR2Agq7OEYtilPT--cTlmtjgu88jrqfMb9V3SlcQgy3LcweBInu3iymUL5EyPbaeqIsGE0emNBAfLFREmNe-hlfuiHX8cv6BSuFXU5ImLavjYhFls373VyUg%3D%3D%22%5D%5D',
    'cookieconsent_status': 'dismiss',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,zh-HK;q=0.7,en-US;q=0.6,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    # 'Cookie': '_ga_EWWZQ61TLS=GS2.1.s1769086768$o1$g1$t1769087548$j21$l0$h0; _ga=GA1.1.1691226360.1769086768; __gads=ID=2090eb76dc3e26a9:T=1769086785:RT=1769087511:S=ALNI_Ma9YWY-V0W9JEWLk6RWzTgKfycW0g; __gpi=UID=0000132d669074e3:T=1769086785:RT=1769087511:S=ALNI_MbDt4jCVjnpy2z6DFeaD94Xt72mlA; __eoi=ID=17f33488ed335577:T=1769086785:RT=1769087511:S=AA-Afjb_8cGG8TS-5bRi7Pgt0Yht; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%2263eb12e4-b9ff-4b7d-8488-bc44b92a91df%5C%22%2C%5B1769086802%2C51000000%5D%5D%22%5D%5D%5D; FCNEC=%5B%5B%22AKsRol92565PbMgnuvZ2y0FZnv9PJp_9AQO-tyCZkepR2Agq7OEYtilPT--cTlmtjgu88jrqfMb9V3SlcQgy3LcweBInu3iymUL5EyPbaeqIsGE0emNBAfLFREmNe-hlfuiHX8cv6BSuFXU5ImLavjYhFls373VyUg%3D%3D%22%5D%5D; cookieconsent_status=dismiss',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

def download_file(url, directory, filename=None):
    # 确保目录存在
    os.makedirs(directory, exist_ok=True)
    
    # 发送GET请求
    response = requests.get(url, stream=True)
    # 检查请求是否成功
    response.raise_for_status()
    
    # 如果未提供文件名，尝试从URL或响应头中获取
    if filename is None:
        # 从URL中获取文件名
        filename = url.split('/')[-1]
        # 如果URL中无文件名，则尝试从Content-Disposition头部获取
        if 'content-disposition' in response.headers:
            import re
            cd = response.headers['content-disposition']
            # 查找filename字段
            fname = re.findall('filename="?([^"]+)"?', cd)
            if fname:
                filename = fname[0]
    
    # 构建保存路径
    filepath = os.path.join(directory, filename)
    
    # 写入文件
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return filepath


def get_download_page(page):
    response = requests.get(f'https://www.snapfiles.com/features/portable-apps{page}.html', cookies=cookies, headers=headers)
    html=response.text
    matches=TABLE_PATTREN.findall(html)
    table=matches[0].replace("\r","").replace("\t","").replace("\n","")
    matches=TR_PATTREN.findall(table)
    for i in matches:
        href=HREF_PATTERN.findall(i)
        # print(i)
        uri=href[1][6:-1]

        if uri not in seen:
            seen.add(uri)
            download_page_url.append("https://www.snapfiles.com"+uri)
            print("https://www.snapfiles.com"+uri)



def get_download_link(url):
    response = requests.get(url, cookies=cookies, headers=headers)
    html=response.text
    matches=DOWNLOAD_PATTERN.findall(html)
    uri=HREF_PATTERN.findall(matches[0])[0][6:-1]
    uri=ht.unescape(uri)
    print("https://www.snapfiles.com"+uri)
    if "https://www.snapfiles.com"+uri not in download_link:
        download_link.append("https://www.snapfiles.com"+uri)


def get_download_link_direct(url):
    response = requests.get(url, cookies=cookies, headers=headers)
    html=response.text
    matches=DOWNLOAD_LINK_PATTERN.findall(html)
    url=HREF_PATTERN.findall(matches[0])[0][6:-1]
    if url.lower().endswith(".zip"):
        print(url)
        download_file(url,"download")

page_index=['']
[page_index.append(str(i)) for i in range(2,29)]
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    for i in page_index:
        # get_download_page(i)
        executor.submit(get_download_page,i)

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    for i in download_page_url:
        # get_download_link(i)
        executor.submit(get_download_link,i)

# with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#     for i in download_link:
#         # get_download_link_direct(i)
#         executor.submit(get_download_link_direct,i)


with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    for i in range(0,5000):
        # get_download_link("https://www.snapfiles.com/php/surpriseme.php")
        executor.submit(get_download_link,"https://www.snapfiles.com/php/surpriseme.php")

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    for i in download_link:
        # get_download_link_direct(i)
        executor.submit(get_download_link_direct,i)
