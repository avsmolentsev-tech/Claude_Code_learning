#!/usr/bin/env python3
"""
СЕО/ГЕО-аудит сайта: инструмент для урока М2-02.
Проверяет техническое SEO (title/meta/h1/schema/alt) и ГЕО-факторы
(доступ ИИ-краулеров через robots.txt, наличие llms.txt) одним запуском.

Использование: python3 seo-geo-audit.py https://example.com
"""
import sys
import json
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

TIMEOUT = 15
UA = "Mozilla/5.0 (compatible; SEO-GEO-Audit-Course/1.0)"

AI_BOTS = ["GPTBot", "ChatGPT-User", "ClaudeBot", "anthropic-ai", "Claude-Web",
           "PerplexityBot", "Google-Extended", "CCBot", "Applebot-Extended"]


def fetch(url, timeout=TIMEOUT):
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": UA}, allow_redirects=True)
        return r
    except requests.RequestException as e:
        return None


def check_robots(base_url):
    robots_url = urljoin(base_url, "/robots.txt")
    r = fetch(robots_url)
    result = {"url": robots_url, "found": False, "bots": {}, "sitemap": None}
    if not r or r.status_code != 200:
        return result
    result["found"] = True
    text = r.text
    sm = re.findall(r"(?im)^sitemap:\s*(\S+)", text)
    if sm:
        result["sitemap"] = sm[0]

    blocks = re.split(r"(?im)^user-agent:\s*", text)[1:]
    agent_rules = {}
    for block in blocks:
        lines = block.splitlines()
        agent = lines[0].strip()
        disallow_all = any(re.match(r"(?i)disallow:\s*/\s*$", l.strip()) for l in lines[1:6])
        agent_rules[agent] = "запрещено всё (/)" if disallow_all else "разрешено (или частично)"

    for bot in AI_BOTS:
        if bot in agent_rules:
            result["bots"][bot] = agent_rules[bot]
        elif "*" in agent_rules:
            result["bots"][bot] = agent_rules["*"] + " (по правилу *)"
        else:
            result["bots"][bot] = "нет явного правила — по умолчанию разрешено"
    return result


def check_llms_txt(base_url):
    url = urljoin(base_url, "/llms.txt")
    r = fetch(url)
    return {"url": url, "found": bool(r and r.status_code == 200)}


def audit_page(url):
    r = fetch(url)
    report = {"url": url, "ok": False}
    if not r:
        report["error"] = "не удалось загрузить (таймаут/недоступен)"
        return report
    report["status_code"] = r.status_code
    if r.status_code >= 400:
        report["error"] = f"HTTP {r.status_code}"
        return report

    soup = BeautifulSoup(r.text, "html.parser")
    report["ok"] = True

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    report["title"] = title
    report["title_len"] = len(title) if title else 0

    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc = meta_desc.get("content", "").strip() if meta_desc else None
    report["meta_description"] = desc
    report["meta_description_len"] = len(desc) if desc else 0

    canonical = soup.find("link", attrs={"rel": "canonical"})
    report["canonical"] = canonical.get("href") if canonical else None

    viewport = soup.find("meta", attrs={"name": "viewport"})
    report["mobile_viewport"] = bool(viewport)

    h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
    report["h1_count"] = len(h1s)
    report["h1_sample"] = h1s[:2]

    imgs = soup.find_all("img")
    report["images_total"] = len(imgs)
    report["images_missing_alt"] = sum(1 for i in imgs if not i.get("alt", "").strip())

    schema_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    schema_types = []
    for s in schema_scripts:
        try:
            data = json.loads(s.string or "{}")
            items = data if isinstance(data, list) else [data]
            for item in items:
                t = item.get("@type")
                if t:
                    schema_types.append(t if isinstance(t, str) else ",".join(t))
        except Exception:
            pass
    report["schema_types"] = schema_types

    links = soup.find_all("a", href=True)
    domain = urlparse(url).netloc
    internal = sum(1 for a in links if domain in a["href"] or a["href"].startswith("/"))
    external = len(links) - internal
    report["links_internal"] = internal
    report["links_external"] = external

    lang = soup.find("html").get("lang") if soup.find("html") else None
    report["lang"] = lang

    return report


def score_row(page_report, robots_report):
    issues = []
    if not page_report.get("title") or page_report.get("title_len", 0) < 10:
        issues.append("нет/короткий title")
    if page_report.get("title_len", 0) > 60:
        issues.append("title длиннее 60 симв. — обрежется в поиске")
    if not page_report.get("meta_description"):
        issues.append("нет meta description")
    if page_report.get("h1_count", 0) == 0:
        issues.append("нет H1")
    if page_report.get("h1_count", 0) > 1:
        issues.append(f"несколько H1 ({page_report['h1_count']})")
    if not page_report.get("mobile_viewport"):
        issues.append("нет viewport — не адаптирован")
    if page_report.get("images_missing_alt", 0) > 0:
        issues.append(f"{page_report['images_missing_alt']} картинок без alt")
    if not page_report.get("schema_types"):
        issues.append("нет структурированных данных (schema.org)")
    blocked_ai = [b for b, v in robots_report.get("bots", {}).items() if "запрещено всё" in v]
    if blocked_ai:
        issues.append(f"блокирует ИИ-краулеров: {', '.join(blocked_ai)}")
    return issues


def main():
    if len(sys.argv) < 2:
        print("Использование: python3 seo-geo-audit.py <url> [<url2> ...]")
        sys.exit(1)

    all_reports = []
    for url in sys.argv[1:]:
        print(f"\n=== {url} ===")
        page = audit_page(url)
        robots = check_robots(url)
        llms = check_llms_txt(url)
        issues = score_row(page, robots) if page.get("ok") else ["страница недоступна"]

        print(json.dumps({"page": page, "robots": robots, "llms_txt": llms, "issues": issues},
                          ensure_ascii=False, indent=2))
        all_reports.append({"url": url, "page": page, "robots": robots, "llms_txt": llms, "issues": issues})

    out_path = "seo-geo-audit-results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_reports, f, ensure_ascii=False, indent=2)
    print(f"\nСохранено: {out_path}")


if __name__ == "__main__":
    main()
