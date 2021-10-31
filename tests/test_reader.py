import urllib.request


def check_proxy(pip):
    try:
        proxy_handler = urllib.request.ProxyHandler({'https': pip})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        # change the url address here
        sock = urllib.request.urlopen('https://www.myip.com/')
    except urllib.error.HTTPError as e:
        return False
    except Exception:
        return False
    return True


print(check_proxy(f"http://kyleG2:P6r4UdO@50.114.85.144:34512"))
