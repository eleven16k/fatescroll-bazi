#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fatescroll 排盘（Python 零外部依赖版，需 Python 3.8+）
与 Node 版 fatescroll_calc.cjs 及 Fatescroll App 同源算法：
四柱/十神/藏干/十二长生/纳音/神煞/五行加权/大运/每日卦象。
紫微斗数排盘仅 Node 版支持（依赖 iztro）；无 Node 时跳过紫微维度，仅以八字论之。

用法:
  python3 fatescroll_calc.py bazi     --date 1990-01-15 --hour 10 --gender male [--today 2026-09-24]
  python3 fatescroll_calc.py hexagram --date 2026-09-24
"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lunar_python import Solar  # noqa: E402  (vendored, MIT)

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEM_WUXING = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
               "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
ELEMENT_ORDER = ["金", "木", "水", "火", "土"]
GENERATOR = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
HIDE_WEIGHTS = [1.0, 0.5, 0.3]

# 神煞表 —— 与 Node 版/App bazi.ts 完全一致：
# 桃花/驿马/华盖/将星/劫煞/灾煞 以年支起三合局；天乙贵人/文昌 以日干起。
TAOHUA = {"申": "酉", "子": "酉", "辰": "酉", "巳": "午", "酉": "午", "丑": "午", "寅": "卯", "午": "卯", "戌": "卯", "亥": "子", "卯": "子", "未": "子"}
YIMA = {"申": "寅", "子": "寅", "辰": "寅", "巳": "亥", "酉": "亥", "丑": "亥", "寅": "申", "午": "申", "戌": "申", "亥": "巳", "卯": "巳", "未": "巳"}
HUAGAI = {"申": "辰", "子": "辰", "辰": "辰", "巳": "丑", "酉": "丑", "丑": "丑", "寅": "戌", "午": "戌", "戌": "戌", "亥": "未", "卯": "未", "未": "未"}
JIANGXING = {"申": "子", "子": "子", "辰": "子", "巳": "酉", "酉": "酉", "丑": "酉", "寅": "午", "午": "午", "戌": "午", "亥": "卯", "卯": "卯", "未": "卯"}
JIESHA = {"申": "巳", "子": "巳", "辰": "巳", "巳": "寅", "酉": "寅", "丑": "寅", "寅": "亥", "午": "亥", "戌": "亥", "亥": "申", "卯": "申", "未": "申"}
ZAISHA = {"申": "午", "子": "午", "辰": "午", "巳": "卯", "酉": "卯", "丑": "卯", "寅": "子", "午": "子", "戌": "子", "亥": "酉", "卯": "酉", "未": "酉"}
TIANYI = {"甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"], "乙": ["子", "申"], "己": ["子", "申"],
          "丙": ["亥", "酉"], "丁": ["亥", "酉"], "壬": ["卯", "巳"], "癸": ["卯", "巳"], "辛": ["寅", "午"]}
WENCHANG = {"甲": "巳", "乙": "午", "丙": "申", "戊": "申", "丁": "酉", "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯"}


def shensha_at(day_gan, zhi, year_zhi):
    out = []
    if zhi in TIANYI.get(day_gan, []):
        out.append("天乙贵人")
    if WENCHANG.get(day_gan) == zhi:
        out.append("文昌")
    if TAOHUA.get(year_zhi) == zhi:
        out.append("桃花")
    if YIMA.get(year_zhi) == zhi:
        out.append("驿马")
    if HUAGAI.get(year_zhi) == zhi:
        out.append("华盖")
    if JIANGXING.get(year_zhi) == zhi:
        out.append("将星")
    if JIESHA.get(year_zhi) == zhi:
        out.append("劫煞")
    if ZAISHA.get(year_zhi) == zhi:
        out.append("灾煞")
    return out


def wuxing_analysis(pillars, day_gan):
    score = {e: 0.0 for e in ELEMENT_ORDER}
    count = {e: 0 for e in ELEMENT_ORDER}
    for gan, hide_gan in pillars:
        g = STEM_WUXING[gan]
        score[g] += 1.0
        count[g] += 1
        for i, hg in enumerate(hide_gan):
            e = STEM_WUXING.get(hg)
            if e:
                score[e] += HIDE_WEIGHTS[i] if i < len(HIDE_WEIGHTS) else 0.3
                count[e] += 1
    total = sum(score.values()) or 1.0
    dm = STEM_WUXING[day_gan]
    # 半进位舍入，与 JS Math.round（App 口径）一致；Python 内建 round 为银行家舍入
    similar = int((score[dm] + score[GENERATOR[dm]]) / total * 100 + 0.5)
    different = 100 - similar
    missing = [e for e in ELEMENT_ORDER if count[e] == 0]
    if similar < 50:
        use_god, annoying_god = GENERATOR[dm], GENERATES[dm]
    else:
        use_god, annoying_god = CONTROLS[dm], GENERATOR[dm]
    pct = {e: int(score[e] / total * 100 + 0.5) for e in ELEMENT_ORDER}
    return pct, count, similar, different, missing, use_god, annoying_god


# ---------------------------------------------------------------------------
# 每日卦象（与 App hexagramDaily.ts 一致：dayOfYear % 64，文王卦序）
# ---------------------------------------------------------------------------
HEX_ORDER = ["乾", "坤", "屯", "蒙", "需", "讼", "师", "比", "小畜", "履", "泰", "否", "同人", "大有", "谦", "豫",
             "随", "蛊", "临", "观", "噬嗑", "贲", "剥", "复", "无妄", "大畜", "颐", "大过", "坎", "离", "咸", "恒",
             "遯", "大壮", "晋", "明夷", "家人", "睽", "蹇", "解", "损", "益", "夬", "姤", "萃", "升", "困", "井",
             "革", "鼎", "震", "艮", "渐", "归妹", "丰", "旅", "巽", "兑", "涣", "节", "中孚", "小过", "既济", "未济"]
HEX_SYMBOLS = {n: chr(0x4DC0 + i) for i, n in enumerate(HEX_ORDER)}
TRIGRAM_BITS = {"乾": "111", "兑": "110", "离": "101", "震": "100", "巽": "011", "坎": "010", "艮": "001", "坤": "000"}
TRI_ALIAS = {"天": "乾", "泽": "兑", "火": "离", "雷": "震", "风": "巽", "水": "坎", "山": "艮", "地": "坤"}
HEX_PILLARS = {
    "乾": ("乾", "乾"), "坤": ("坤", "坤"), "屯": ("坎", "震"), "蒙": ("艮", "坎"), "需": ("坎", "天"), "讼": ("天", "坎"), "师": ("坤", "水"), "比": ("水", "地"),
    "小畜": ("巽", "天"), "履": ("天", "兑"), "泰": ("地", "天"), "否": ("天", "地"), "同人": ("天", "火"), "大有": ("火", "天"), "谦": ("地", "山"), "豫": ("雷", "地"),
    "随": ("兑", "雷"), "蛊": ("山", "风"), "临": ("地", "泽"), "观": ("风", "地"), "噬嗑": ("火", "雷"), "贲": ("山", "火"), "剥": ("山", "地"), "复": ("地", "雷"),
    "无妄": ("天", "雷"), "大畜": ("山", "天"), "颐": ("山", "雷"), "大过": ("泽", "风"), "坎": ("坎", "坎"), "离": ("离", "离"), "咸": ("泽", "山"), "恒": ("雷", "风"),
    "遯": ("天", "山"), "大壮": ("雷", "天"), "晋": ("火", "地"), "明夷": ("地", "火"), "家人": ("风", "火"), "睽": ("火", "泽"), "蹇": ("水", "山"), "解": ("雷", "水"),
    "损": ("山", "泽"), "益": ("风", "雷"), "夬": ("泽", "天"), "姤": ("天", "风"), "萃": ("泽", "地"), "升": ("地", "风"), "困": ("泽", "水"), "井": ("水", "风"),
    "革": ("泽", "火"), "鼎": ("火", "风"), "震": ("震", "震"), "艮": ("艮", "艮"), "渐": ("风", "山"), "归妹": ("雷", "泽"), "丰": ("雷", "火"), "旅": ("火", "山"),
    "巽": ("巽", "巽"), "兑": ("兑", "兑"), "涣": ("风", "水"), "节": ("水", "泽"), "中孚": ("风", "泽"), "小过": ("雷", "山"), "既济": ("水", "火"), "未济": ("火", "水"),
}


def _bits(t):
    return TRIGRAM_BITS.get(t) or TRIGRAM_BITS[TRI_ALIAS.get(t, "")]


def _lines(name):
    up, down = HEX_PILLARS[name]
    return _bits(down) + _bits(up)


NAME_BY_LINES = {_lines(n): n for n in HEX_ORDER}


def daily_hexagram(y, m, d):
    day_of_year = (date(y, m, d) - date(y, 1, 1)).days
    name = HEX_ORDER[day_of_year % 64]
    ls = _lines(name)
    nuclear = NAME_BY_LINES.get(ls[1:4] + ls[2:5], name)
    return name, nuclear


def bazi_report(y, m, d, hour, gender, today):
    solar = Solar.fromYmdHms(y, m, d, hour, 0, 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()
    gender_num = 1 if gender == "male" else 0
    gender_title = "乾造(男)" if gender == "male" else "坤造(女)"
    yun = ec.getYun(gender_num)
    day_gan, year_zhi = lunar.getDayGan(), lunar.getYearZhi()

    defs = [
        ("年柱", lunar.getYearGan(), lunar.getYearZhi(), ec.getYearShiShenGan(), ec.getYearHideGan(), ec.getYearShiShenZhi(), ec.getYearDiShi(), lunar.getYearNaYin()),
        ("月柱", lunar.getMonthGan(), lunar.getMonthZhi(), ec.getMonthShiShenGan(), ec.getMonthHideGan(), ec.getMonthShiShenZhi(), ec.getMonthDiShi(), lunar.getMonthNaYin()),
        ("日柱", day_gan, lunar.getDayZhi(), "日主", ec.getDayHideGan(), ec.getDayShiShenZhi(), ec.getDayDiShi(), lunar.getDayNaYin()),
        ("时柱", lunar.getTimeGan(), lunar.getTimeZhi(), ec.getTimeShiShenGan(), ec.getTimeHideGan(), ec.getTimeShiShenZhi(), ec.getTimeDiShi(), lunar.getTimeNaYin()),
    ]

    L = ["## 四柱八字（确定性排盘，分析时须原样引用，严禁修改或另排）", ""]
    L.append(f"{gender_title}｜公历：{y:04d}-{m:02d}-{d:02d} {hour:02d}时｜农历：{lunar}｜年柱干支({ec.getYear()})｜生肖：{lunar.getYearShengXiao()}")
    L.append("")
    L.append("| 柱 | 天干 | 地支 | 五行 | 十神 | 藏干(十神) | 十二长生 | 纳音 | 神煞 |")
    L.append("|----|------|------|------|------|------------|----------|------|------|")
    pillars_w = []
    for name, gan, zhi, ss, hide, hide_ss, chang_sheng, nayin in defs:
        pillars_w.append((gan, hide))
        hide_str = "、".join(f"{g}({hide_ss[i]})" for i, g in enumerate(hide))
        ss_str = "—(日主)" if name == "日柱" else (ss or "—")
        sha = "、".join(shensha_at(day_gan, zhi, year_zhi)) or "—"
        L.append(f"| {name} | {gan} | {zhi} | {STEM_WUXING[gan]} | {ss_str} | {hide_str} | {chang_sheng} | {nayin} | {sha} |")
    L.append("")
    L.append(f"日主：{day_gan}（{STEM_WUXING[day_gan]}）｜空亡(旬空)：{ec.getDayXunKong()}｜胎元：{ec.getTaiYuan()}｜胎息：{ec.getTaiXi()}｜命宫：{ec.getMingGong()}｜身宫：{ec.getShenGong()}")
    L.append("")
    L.append("## 大运排盘（每运10年）")
    dys = yun.getDaYun()
    L.append(f"起运：{dys[0].getStartAge()}岁（{yun.getStartSolar().toYmd()} 起行大运）")
    for p in dys[1:11]:
        L.append(f"- {p.getStartAge()}-{p.getEndAge()}岁（{p.getStartYear()}-{p.getEndYear()}）：{p.getGanZhi()}大运")
    L.append("")
    L.append("## 五行分析（确定性加权：天干1.0，藏干按本气/中气/余气 1.0/0.5/0.3）")
    pct, count, similar, different, missing, use_god, annoying_god = wuxing_analysis(pillars_w, day_gan)
    L.append("五行个数：" + "、".join(f"{e}({count[e]}个)" for e in ELEMENT_ORDER))
    L.append("五行占比：" + " | ".join(f"{e}:{pct[e]}" for e in ELEMENT_ORDER) + "（总分100）")
    L.append(f"同类得分：{similar}（比劫+印）｜异类得分：{different}（食伤+财+官杀）")
    L.append("五行所缺：" + ("、".join(missing) if missing else "无明显所缺"))
    L.append(f"用神(最利)：{use_god}｜忌神(最不利)：{annoying_god}")
    L.append("")
    ty, tm, td = today
    name, nuclear = daily_hexagram(ty, tm, td)
    L.append(f"## 今日卦象（{ty:04d}-{tm:02d}-{td:02d}，按日序确定性取卦，文王卦序）")
    L.append(f"本卦：{HEX_SYMBOLS[name]} {name}；互卦：{HEX_SYMBOLS[nuclear]} {nuclear}。（卦象详解默认不推演，用户追问再展开）")
    return "\n".join(L)


def parse_args(argv):
    args = {"cmd": "all", "date": None, "hour": 10, "gender": "male", "today": None}
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--date" and i + 1 < len(argv):
            args["date"] = argv[i + 1]; i += 2
        elif a == "--hour" and i + 1 < len(argv):
            args["hour"] = int(argv[i + 1]); i += 2
        elif a == "--gender" and i + 1 < len(argv):
            args["gender"] = argv[i + 1]; i += 2
        elif a == "--today" and i + 1 < len(argv):
            args["today"] = argv[i + 1]; i += 2
        else:
            rest.append(a); i += 1
    if rest:
        args["cmd"] = rest[0]
    return args


def main():
    argv = sys.argv[1:]
    args = parse_args(argv)
    if args["cmd"] in ("help",) or not argv:
        print("用法: python3 fatescroll_calc.py <bazi|hexagram|all> --date YYYY-MM-DD --hour 0-23 --gender male|female [--today YYYY-MM-DD]")
        print("注：本 Python 版不含紫微斗数（需 Node 版 fatescroll_calc.cjs）；无 Node 时按八字单维推演。")
        return
    y, m, d = (int(x) for x in args["date"].split("-"))
    if args["today"]:
        ty, tm, td = (int(x) for x in args["today"].split("-"))
    else:
        today_ = date.today()
        ty, tm, td = today_.year, today_.month, today_.day
    if args["cmd"] == "hexagram":
        name, nuclear = daily_hexagram(y, m, d)
        print(f"{y:04d}-{m:02d}-{d:02d} 本卦：{HEX_SYMBOLS[name]} {name}；互卦：{HEX_SYMBOLS[nuclear]} {nuclear}")
        return
    if args["cmd"] == "ziwei":
        print("紫微斗数排盘需要 Node 运行时：请改用 node fatescroll_calc.cjs ziwei …；不可用时请仅以八字分析并在报告中说明。")
        return
    print(bazi_report(y, m, d, args["hour"], args["gender"], (ty, tm, td)))


if __name__ == "__main__":
    main()
