
import asyncio
import aiohttp
import time
import re
import os
from console.utils import set_title
from colorama import Fore, Style, init
init(autoreset=True)

TEST_URL = "http://ip-api.com/json"
TIMEOUT = 5
CONCURRENT = 200

if os.name == "nt":
    os.system("cls")
else:
    os.system("clear")

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

proxy_sources = {
    'http': [
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all',
        'https://spys.me/proxy.txt',
        'https://www.proxy-list.download/api/v1/get?type=http',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
        'https://proxyspace.pro/http.txt',
        'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt'
    ],
    'https': [
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=10000&country=all',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
        'https://www.proxy-list.download/api/v1/get?type=https',
        'https://proxyspace.pro/https.txt',
        'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt'
    ],
    'socks4': [
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',
        'https://www.proxy-list.download/api/v1/get?type=socks4',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
        'https://proxyspace.pro/socks4.txt',
        'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt'
    ],
    'socks5': [
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
        'https://www.proxy-list.download/api/v1/get?type=socks5',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
        'https://proxyspace.pro/socks5.txt',
        'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt'
    ]
}

proxy_names = {
    1: "http",
    2: "https",
    3: "socks4",
    4: "socks5"
}

proxy_re = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+)")

valid = 0
invalid = 0
checked = 0

async def fetch_source(session, url):
    try:
        async with session.get(url, timeout=15) as r:
            text = await r.text()
            return proxy_re.findall(text)
    except:
        return []

async def fetch_all(proxytype):
    proxies = []

    protocol = proxy_names.get(proxytype)
    if protocol is None:
        print(Fore.RED + "Invalid proxy type")
        return []

    connector = aiohttp.TCPConnector(ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []

        print(Fore.YELLOW + f"[+] Fetching {protocol.upper()} Proxies...")

        for url in proxy_sources[protocol]:
            tasks.append(fetch_source(session, url))

        results = await asyncio.gather(*tasks)

    for r in results:
        proxies.extend(r)

    return sorted(set(proxies))

async def check(proxy, sem, proxytype):
    global valid, invalid, checked

    async with sem:
        start = time.perf_counter()

        protocol = proxy_names[proxytype]
        proxy_url = f"{protocol}://{proxy}"

        try:
            timeout = aiohttp.ClientTimeout(total=TIMEOUT)

            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(TEST_URL, proxy=proxy_url) as r:
                    if r.status == 200:
                        data = await r.json()

                        latency = int((time.perf_counter() - start) * 1000)

                        ip = data.get("query", "Unknown")
                        country = data.get("country", "Unknown")

                        valid += 1

                        valid_file = f"{protocol}_valid.txt"
                        fast_file = f"fast_{protocol}_valid.txt"    

                        with open(f"{RESULTS_DIR}/{valid_file}", "a") as f:
                            f.write(proxy + "\n")
                        
                        # Fast Proxy (under 200ms)
                        if latency <= 200:
                            with open(f"{RESULTS_DIR}/{fast_file}", "a") as f:
                                f.write(proxy + "\n")

                        print(
                            Fore.GREEN +
                            f"[VALID] {proxy} | {country} | {latency} ms"
                        )   
                    else:
                        invalid += 1
                        print(Fore.RED + f"[INVALID] {proxy}")

        except:
            invalid += 1
            print(Fore.RED + f"[INVALID] {proxy}")

        checked += 1

        if os.name == "nt":
            set_title(f"NINJA Proxy Generator + Checker | Checked:{checked} Valid:{valid} Invalid:{invalid}")

async def main():
    banner = f"""
{Fore.RED}███╗   ██╗██╗███╗   ██╗     ██╗ █████╗     ████████╗ ██████╗  ██████╗ ██╗     ███████╗
{Fore.RED}████╗  ██║██║████╗  ██║     ██║██╔══██╗    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
{Fore.RED}██╔██╗ ██║██║██╔██╗ ██║     ██║███████║       ██║   ██║   ██║██║   ██║██║     ███████╗
{Fore.RED}██║╚██╗██║██║██║╚██╗██║██   ██║██╔══██║       ██║   ██║   ██║██║   ██║██║     ╚════██║
{Fore.RED}██║ ╚████║██║██║ ╚████║╚█████╔╝██║  ██║       ██║   ╚██████╔╝╚██████╔╝███████╗███████║
{Fore.RED}╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚════╝ ╚═╝  ╚═╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝

{Fore.CYAN}                     ⚡ PROXY GENERATOR + CHECKER BY DISHANT ⚡

{Fore.GREEN}══════════════════════════════════════════════════════════════════════════════════════════
    """
    print(banner)

    print(Fore.CYAN + "[1] HTTP")
    print(Fore.CYAN + "[2] HTTPS")
    print(Fore.CYAN + "[3] SOCKS4")
    print(Fore.CYAN + "[4] SOCKS5")

    proxytype = int(input(Fore.BLUE + Style.BRIGHT + "\nSelect Proxy Type: "))

    if proxytype not in proxy_names:
        print(Fore.RED + "Invalid Proxy Type!")
        return

    proxies = await fetch_all(proxytype)

    print(Fore.CYAN + f"\nFetched: {len(proxies)} unique {proxy_names[proxytype].upper()} proxies")
    print("=" * 60)

    sem = asyncio.Semaphore(CONCURRENT)
    await asyncio.gather(*(check(p, sem, proxytype) for p in proxies))

    print("\n" + "=" * 60)
    print(Fore.CYAN + Style.BRIGHT + "SUMMARY")
    print("=" * 60)
    print(Fore.YELLOW + f"Proxy Type : {proxy_names[proxytype].upper()}")
    print(Fore.GREEN + f"Valid      : {valid}")
    print(Fore.RED + f"Invalid    : {invalid}")
    print(Fore.CYAN + f"Checked    : {checked}")

if __name__ == "__main__":
    asyncio.run(main())
