lines = open("proxies.txt", encoding="utf-8").readlines()

formatted: list[str] = []

for line in lines:
    s_line = line.strip().split(":")
    p = f"{s_line[2]}:{s_line[3]}@{s_line[0]}:{s_line[1]}"
    formatted.append(p)


with open("formatted.txt", encoding="utf-8", mode="w") as f:
    f.write("\n".join(formatted))
