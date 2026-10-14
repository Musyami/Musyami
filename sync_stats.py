import os, re, json, ssl, urllib.request
from datetime import datetime

USERNAME = "Musyami"
SVG_PATH = "nintendo_stats.svg"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0"}

print(f"Fetching live stats for {USERNAME}...")

# 1. Tarik Data Live dari GitHub Stats API
stats_url = f"https://github-readme-stats.vercel.app/api?username={USERNAME}"
req = urllib.request.Request(stats_url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    stats_svg = resp.read().decode()

desc_match = re.search(r'<desc id="descId">([^<]+)</desc>', stats_svg)
if desc_match:
    desc = desc_match.group(1)
    stars = re.search(r'Total Stars Earned:\s*(\d+)', desc).group(1)
    commits = re.search(r'Total Commits\s*\(last year\)\s*:\s*(\d+)', desc).group(1)
    prs = re.search(r'Total PRs:\s*(\d+)', desc).group(1)
    issues = re.search(r'Total Issues:\s*(\d+)', desc).group(1)
    contribs = re.search(r'Contributed to \(last year\):\s*(\d+)', desc).group(1)
else:
    stars, commits, prs, issues, contribs = "0", "24", "0", "0", "0"

rank_match = re.search(r'Rank:\s*([A-Za-z\+\-]+)', stats_svg)
rank = rank_match.group(1) if rank_match else "C"

# 2. Tarik Data Live dari Streak Stats API
streak_url = f"https://streak-stats.demolab.com/?user={USERNAME}&type=json"
req = urllib.request.Request(streak_url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    streak_data = json.loads(resp.read().decode())

total_contribs = str(streak_data.get("totalContributions", 20))
curr_streak = str(streak_data.get("currentStreak", {}).get("length", 3))
curr_start = streak_data.get("currentStreak", {}).get("start", "")
curr_end = streak_data.get("currentStreak", {}).get("end", "")

long_streak = str(streak_data.get("longestStreak", {}).get("length", 3))
long_start = streak_data.get("longestStreak", {}).get("start", "")
long_end = streak_data.get("longestStreak", {}).get("end", "")

first_contrib = streak_data.get("firstContribution", "2025-06-25")

def fmt_date(d_str):
    if not d_str: return ""
    try:
        dt = datetime.strptime(d_str, "%Y-%m-%d")
        return dt.strftime("%b %d")
    except:
        return d_str

def fmt_month_year(d_str):
    if not d_str: return ""
    try:
        dt = datetime.strptime(d_str, "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except:
        return d_str

curr_date_range = f"{fmt_date(curr_start)} - {fmt_date(curr_end)}" if curr_start else "Oct 12 - Oct 14"
long_date_range = f"{fmt_date(long_start)} - {fmt_date(long_end)}" if long_start else "Oct 12 - Oct 14"
contrib_date_range = f"{fmt_month_year(first_contrib)} - Present"

print(f"Stats Live: Stars={stars}, Commits={commits}, PRs={prs}, Issues={issues}, Contribs={contribs}, Rank={rank}")
print(f"Streak Live: Total={total_contribs}, Current={curr_streak} ({curr_date_range}), Longest={long_streak}")

# 3. Tulis Angka Terbaru ke dalam file nintendo_stats.svg
if os.path.exists(SVG_PATH):
    with open(SVG_PATH, "r", encoding="utf-8") as f:
        svg_content = f.read()

    svg_content = re.sub(r'(<text x="22" y="11">Total Stars Earned:</text>\s*<text x="212" y="11"[^>]*>)\d+(</text>)', rf'\g<1>{stars}\2', svg_content)
    svg_content = re.sub(r'(<text x="22" y="11">Total Commits \(last year\):</text>\s*<text x="212" y="11"[^>]*>)\d+(</text>)', rf'\g<1>{commits}\2', svg_content)
    svg_content = re.sub(r'(<text x="22" y="11">Total PRs:</text>\s*<text x="212" y="11"[^>]*>)\d+(</text>)', rf'\g<1>{prs}\2', svg_content)
    svg_content = re.sub(r'(<text x="22" y="11">Total Issues:</text>\s*<text x="212" y="11"[^>]*>)\d+(</text>)', rf'\g<1>{issues}\2', svg_content)
    svg_content = re.sub(r'(<text x="22" y="11">Contributed to \(last year\):</text>\s*<text x="212" y="11"[^>]*>)\d+(</text>)', rf'\g<1>{contribs}\2', svg_content)

    svg_content = re.sub(r'(<!-- Huruf Rank "[^"]*" [^>]*-->\s*<text [^>]*>)\s*[A-Za-z\+\-]+\s*(</text>)', rf'\g<1>\n      {rank}\n    \2', svg_content)

    svg_content = re.sub(r'(<!-- SEKSI 1: Total Contributions -->\s*<g transform="[^"]*">\s*<text [^>]*font-size="34"[^>]*>)\s*\d+\s*(</text>)', rf'\g<1>\n      {total_contribs}\n    \2', svg_content)
    svg_content = re.sub(r'(<!-- SEKSI 1: Total Contributions -->[\s\S]*?<text [^>]*fill="#777777"[^>]*>)\s*[^<]+\s*(</text>)', rf'\g<1>\n      {contrib_date_range}\n    \2', svg_content)

    svg_content = re.sub(r'(<!-- Angka Current Streak: \d+ -->\s*<text [^>]*font-size="34"[^>]*>)\s*\d+\s*(</text>)', rf'\g<1>\n      {curr_streak}\n    \2', svg_content)
    svg_content = re.sub(r'(<!-- Label: Current Streak -->[\s\S]*?<text [^>]*fill="#777777"[^>]*>)\s*[^<]+\s*(</text>)', rf'\g<1>\n      {curr_date_range}\n    \2', svg_content)

    svg_content = re.sub(r'(<!-- SEKSI 3: Longest Streak -->\s*<g transform="[^"]*">\s*<text [^>]*font-size="34"[^>]*>)\s*\d+\s*(</text>)', rf'\g<1>\n      {long_streak}\n    \2', svg_content)
    svg_content = re.sub(r'(<!-- SEKSI 3: Longest Streak -->[\s\S]*?<text [^>]*fill="#777777"[^>]*>)\s*[^<]+\s*(</text>)', rf'\g<1>\n      {long_date_range}\n    \2', svg_content)

    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print("SVG nintendo_stats.svg berhasil diperbarui!")
