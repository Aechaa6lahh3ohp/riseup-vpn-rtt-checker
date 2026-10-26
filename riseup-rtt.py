#!/usr/bin/env python
# #!/data/data/com.termux/files/usr/bin/env python
import argparse, json, re, subprocess
from urllib.request import urlopen
#==================================
# Color collection
#==================================
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"
GOOD_MS = 200

#==================================
# Based
#==================================

URL = "https://api.black.riseup.net/3/config/eip-service.json"
CACHE = "gateways.json"

#==================================
# 引数定義
#==================================

parser = argparse.ArgumentParser()
parser.add_argument("-u","--update", action="store_true")
parser.add_argument("-b", "--benchmark", action="store_true")
args = parser.parse_args()

#==================================
# 引数動作定義
#==================================

if args.update:
    data = json.load(urlopen(URL))
    with open(CACHE, "w") as f:
        json.dump(data, f)
elif args.benchmark:
    with open(CACHE) as f:
        data = json.load(f)
else:
    parser.print_help()
    raise SystemExit

# ベンチマークの機構
if args.benchmark:
    for gateway in data["gateways"]:
        output = subprocess.run(
            ["ping", "-n", "-c", "3", "-W", "2", gateway["ip_address"]],
            capture_output=True, text=True
        ).stdout
        times = re.findall(r"time[=<]([\d.]+)\s*ms", output)
        rtt = f"{sum(map(float, times)) / len(times):.2f} ms" if times else "timeout"
        label = f'{gateway["host"]} {gateway.get("location", "")} {rtt}'
        # もうちょっとうまくやｒたい
        if not times:
            print(f"{RED}[X] {RESET}{label} -> {RED}{rtt}{RESET}")
        elif sum(map(float, times)) / len(times) <= GOOD_MS:
            print(f"{GREEN}[+] {RESET}{label} -> {GREEN}{rtt}{RESET}")
        else:
            print(f"[i] {label}")
