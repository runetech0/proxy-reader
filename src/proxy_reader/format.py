
lines = open("proxies.txt").readlines()


proxies = []

for l in lines:
    proxies.append(l.split(";")[0])


with open("output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(proxies))
