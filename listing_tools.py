"""분양 지도 목록(listings.json) 만들기 도우미 (2026-10-25).
types_from_post(글폴더): 티스토리 글(post_body.html)의 '타입별 분양가' 표(최저·최고 분양가 열)에서 평형별 분양가를 '8.38~9.21억' 꼴로 뽑는다. 경쟁률은 접수가 끝난 뒤 청약홈 API 값으로 채우고, 그 전에는 '-'."""
import re, html, pathlib
from decimal import Decimal, ROUND_HALF_UP
def won(s):
    m = re.search(r"(?:(\d+)억)?\s*(?:([\d,]+)만)?", s); eok = int(m.group(1) or 0); man = int((m.group(2) or "0").replace(",", ""))
    return Decimal(eok * 10000 + man) / Decimal(10000)   # 억 단위
def fmt(lo, hi):
    q = lambda d: str(d.quantize(Decimal("0.01"), ROUND_HALF_UP)).rstrip("0").rstrip(".")
    return f"{q(lo)}~{q(hi)}억" if lo != hi else f"{q(lo)}억"
def types_from_post(folder):
    t = (pathlib.Path(folder) / "tistory" / "post_body.html").read_text(encoding="utf-8")
    for m in re.finditer(r"<table.*?</table>", t, flags=re.S):
        rows = [[html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, flags=re.S)] for r in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(0), flags=re.S)]
        if rows and "타입" in rows[0][0] and "최저 분양가" in rows[0] and "최고 분양가" in rows[0]:
            a, b = rows[0].index("최저 분양가"), rows[0].index("최고 분양가")
            return [{"t": r[0], "p": fmt(won(r[a]), won(r[b])), "r": "-"} for r in rows[1:] if len(r) > b and re.match(r"\d", r[0])]
    return []
if __name__ == "__main__":
    import sys, json; print(json.dumps(types_from_post(sys.argv[1]), ensure_ascii=False))
