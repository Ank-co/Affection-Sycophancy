import csv, itertools, statistics as st
from pathlib import Path
HERE = Path(__file__).resolve().parent  # run from anywhere: python ratings/court/analyze.py
from collections import defaultdict, Counter
exec((HERE / "answers.py").read_text())
rows=list(csv.DictReader(open(HERE / "cle_questionnaires_NE_PAS_MONTRER.csv", encoding="utf-8")))
R={"A":A,"B":B,"C":C}
by=defaultdict(dict); meta={}
for r in rows:
    by[r["code"]][r["version"]]=R[r["version"]][int(r["numero"])-1]; meta[r["code"]]=r
codes=sorted(by)
def alpha(data, metric):
    # data: list of lists of ratings per unit (no missing)
    vals=sorted({v for u in data for v in u})
    n_c=Counter(v for u in data for v in u); N=sum(n_c.values())
    def d(a,b):
        if metric=="interval": return (a-b)**2
        if metric=="nominal": return 0 if a==b else 1
        lo,hi=min(a,b),max(a,b)
        s=sum(n_c[g] for g in vals if lo<=g<=hi)-(n_c[a]+n_c[b])/2
        return s**2
    Do=0
    for u in data:
        m=len(u)
        for i,j in itertools.permutations(range(m),2): Do+=d(u[i],u[j])/(m-1)
    Do/=N
    De=sum(n_c[a]*n_c[b]*d(a,b) for a in vals for b in vals)/(N*(N-1))
    return 1-Do/De
data=[[by[c][v] for v in "ABC"] for c in codes]
print("alpha ordinal %.3f  interval %.3f  nominal %.3f"%(alpha(data,"ordinal"),alpha(data,"interval"),alpha(data,"nominal")))
# by level
LV=["0","C","1","2","3","4"]; target={"0":0,"C":0,"1":1,"2":2,"3":3,"4":4}
print("level | mean A B C | mean all | exact match share")
for lv in LV:
    cs=[c for c in codes if meta[c]["level"]==lv]
    per=[st.mean(by[c][v] for c in cs) for v in "ABC"]
    allv=[by[c][v] for c in cs for v in "ABC"]
    exact=sum(1 for x in allv if x==target[lv])/len(allv)
    print(f"{lv:>3} | {per[0]:.1f} {per[1]:.1f} {per[2]:.1f} | {st.mean(allv):.2f} | {exact:.0%} | dist {sorted(Counter(allv).items())}")
# pairwise ordering checks
means={lv:st.mean(by[c][v] for c in codes if meta[c]["level"]==lv for v in "ABC") for lv in LV}
print("ordered 0<1<2<3<4:", means["0"]<means["1"]<means["2"]<means["3"]<means["4"], "C vs 0:", round(means["C"],2), round(means["0"],2))
# flagged items: median deviates >=1.5 from target
print("\nitems with median >= 1.5 away from target, or raters spread >= 3:")
for c in codes:
    r=[by[c][v] for v in "ABC"]; m=meta[c]; med=st.median(r)
    if abs(med-target[m["level"]])>=1.5 or max(r)-min(r)>=3:
        print(m["level"], m["storyline"], m["turn"], m["source"][:14], r, "|", m["sentence"][:85])
