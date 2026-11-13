"""Bounded same-host crawler. Administrator allowlist and public IP checks mitigate SSRF."""

import os, socket, ipaddress, time
from urllib.parse import urlparse, urljoin, urldefrag
from urllib.robotparser import RobotFileParser
import httpx
from bs4 import BeautifulSoup


def validate_url(url):
    p = urlparse(url)
    allowed = {
        h.strip().lower()
        for h in os.getenv("CRAWL_ALLOWED_HOSTS", "").split(",")
        if h.strip()
    }
    if (
        p.scheme not in {"http", "https"}
        or not p.hostname
        or p.username
        or p.password
        or p.port not in {None, 80, 443}
    ):
        raise ValueError("Only standard public HTTP(S) URLs are accepted")
    if p.hostname.lower() not in allowed:
        raise ValueError(
            "Host not enabled. Set CRAWL_ALLOWED_HOSTS on the server first."
        )
    for addr in socket.getaddrinfo(p.hostname, p.port or 443, type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(addr[4][0]).is_global:
            raise ValueError("Private and non-public addresses are blocked")
    return p


def fetch(url):
    validate_url(url)
    with httpx.stream(
        "GET",
        url,
        timeout=10,
        follow_redirects=False,
        trust_env=False,
        headers={"User-Agent": "LumenPortfolioBot/1.0"},
    ) as response:
        response.raise_for_status()
        if 300 <= response.status_code < 400:
            raise ValueError("Redirects are disabled")
        if not any(
            t in response.headers.get("content-type", "")
            for t in ("text/html", "text/plain")
        ):
            raise ValueError("Only HTML and text supported")
        data = b""
        for chunk in response.iter_bytes():
            data += chunk
            if len(data) > 1_000_000:
                raise ValueError("Page exceeds 1 MB limit")
        return data.decode("utf-8", errors="replace")


def crawl(seed, store, max_pages=5):
    p = validate_url(seed)
    base = f"{p.scheme}://{p.netloc}"
    robots = RobotFileParser()
    robots.parse(fetch(base + "/robots.txt").splitlines())
    queue = [seed]
    seen = set()
    saved = []
    errors = []
    while queue and len(seen) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        if not robots.can_fetch("LumenPortfolioBot", url):
            errors.append({"url": url, "error": "Disallowed by robots.txt"})
            continue
        try:
            soup = BeautifulSoup(fetch(url), "html.parser")
            title = soup.title.get_text(" ", strip=True) if soup.title else url
            links = [
                urldefrag(urljoin(url, a["href"]))[0] for a in soup.select("a[href]")
            ]
            for node in soup(["script", "style", "nav", "footer", "header"]):
                node.decompose()
            text = soup.get_text(" ", strip=True)
            store.add(url, title, text)
            saved.append(url)
            queue.extend(
                u for u in links if urlparse(u).netloc == p.netloc and u not in seen
            )
        except (ValueError, httpx.HTTPError) as exc:
            errors.append({"url": url, "error": str(exc)})
        time.sleep(0.25)
    return {"indexed": len(saved), "urls": saved, "errors": errors}
