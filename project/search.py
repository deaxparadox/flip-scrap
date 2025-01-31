from urllib.parse import urlencode, quote_plus, unquote_plus
import re

class SearchMobile:
    phone = r"(phone|phones)"
    branch = r"(apple-iphone|apple|mi|lg|samsung|htc|honor|motorola|apple|oppo|realme|nothing)"


def main():
    brand = re.compile(SearchMobile.branch)
    phone = re.compile(SearchMobile.phone)
    with open("file1.txt", 'r') as f:
        for l in f.readlines():
            line = unquote_plus(l.strip())
            s = phone.search(line)
            r = brand.search(line)
            if s and r: print(line)
            
if __name__ == "__main__":
    main()