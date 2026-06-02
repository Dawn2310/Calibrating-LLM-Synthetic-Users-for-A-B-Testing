"""
CSUP Human-Anchored Validation
------------------------------
Compares N human A/B choices against CSUP's LLM-side SURS reliability scores.

INPUTS (point these at your REAL files):
  human_responses.jsonl : one JSON object per participant, original survey format:
        {"_pid":..., "_freq":..., "responses":{"UI-01":{"chosen_sem":"A"}, ...}}
  surs_scores.csv       : from the CSUP repo (analysis/csup_results/surs_scores.csv)
  domain_breakdown_summary.csv : from repo (analysis/tables/)

OUTPUT: console stats + human_validation_figure.png
NOTE: re-run on the *exact* released human export before quoting numbers in the paper.
"""
import json, csv, math, statistics as st

HUMAN="survey/responses.jsonl"
SURS="analysis/csup_results/surs_scores.csv"
DOMB="analysis/tables/domain_breakdown_summary.csv"

# ---- load humans ----
rows=[json.loads(l) for l in open(HUMAN) if l.strip()]
N=len(rows)
tests=sorted({t for r in rows for t in r["responses"]})
def dom(t): return "UI" if t.startswith("UI") else "COPY" if t.startswith("COPY") else "REC"
paH={}; consH={}
for t in tests:
    a=sum(1 for r in rows if r["responses"].get(t,{}).get("chosen_sem")=="A")
    n=sum(1 for r in rows if t in r["responses"])
    paH[t]=a/n; consH[t]=abs(a/n-0.5)*2

# ---- load SURS (base cases) ----
surs={}; flag={}
for r in csv.DictReader(open(SURS)):
    if "-V" in r["test_id"]: continue
    surs[r["test_id"]]=float(r["SURS"]); flag[r["test_id"]]=r["flag"]
common=[t for t in tests if t in surs]
X=[surs[t] for t in common]; Y=[consH[t] for t in common]

def pearson(x,y):
    n=len(x);mx=sum(x)/n;my=sum(y)/n
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
def ranks(v):
    s=sorted(range(len(v)),key=lambda i:v[i]);r=[0]*len(v);i=0
    while i<len(v):
        j=i
        while j+1<len(v) and v[s[j+1]]==v[s[i]]: j+=1
        for k in range(i,j+1): r[s[k]]=(i+j)/2+1
        i=j+1
    return r

print(f"N participants = {N};  base cases matched to SURS = {len(common)}")
print(f"\n[1] SURS (LLM reliability) vs HUMAN consensus:")
print(f"    Pearson r   = {pearson(X,Y):.3f}")
print(f"    Spearman rho= {pearson(ranks(X),ranks(Y)):.3f}")
print(f"\n[2] Human consensus by SURS tier:")
for tier in ["High","Moderate","Low"]:
    g=[consH[t] for t in common if flag[t]==tier]
    if g: print(f"    {tier:9s} n={len(g):2d}  mean human consensus={sum(g)/len(g):.3f}")

# ---- domain directional validity ----
db={}
for r in csv.DictReader(open(DOMB)):
    d=r["domain"]; db.setdefault(d,[0,0]); db[d][0]+=int(r["A"]); db[d][1]+=int(r["total"])
nm={"UI/UX":"UI","Copywriting":"COPY","Recommendation":"REC"}
print(f"\n[3] Domain directional validity (LLM ensemble vs human):")
domrows=[]
for d,(a,tot) in db.items():
    dd=nm[d]; idx=[t for t in tests if dom(t)==dd]; h=sum(paH[t] for t in idx)/len(idx); llm=a/tot
    domrows.append((dd,llm,h))
    print(f"    {dd:4s} LLM A={llm:.2f}  human A={h:.2f}  same direction={ (llm>0.5)==(h>0.5) }")

print(f"\n[4] Reliability-without-validity cases (SURS>=0.78, humans within 45-55%):")
for t in common:
    if surs[t]>=0.78 and abs(paH[t]-0.5)<0.12:
        print(f"    {t}: SURS={surs[t]:.3f}  humanP(A)={paH[t]:.2f}")

# ---- figure 1: Scatter Plot ----
try:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    
    col={"High":"#2ca02c","Moderate":"#ff9800","Low":"#d62728"}
    
    plt.figure(figsize=(6, 5))
    for t in common:
        plt.scatter(surs[t],consH[t],c=col[flag[t]],s=65,edgecolor="k",linewidth=.4,zorder=3)
    for t in ["UI-01","COPY-09","UI-09","COPY-05"]:
        if t in common: plt.annotate(t,(surs[t],consH[t]),fontsize=8,xytext=(5,5),textcoords="offset points")
    plt.axvline(0.6,ls="--",c="grey",lw=.8); plt.axvline(0.8,ls="--",c="grey",lw=.8)
    plt.xlabel("SURS  (LLM-side reliability)"); plt.ylabel("Human consensus  |2·P(A)−1|")
    plt.title(f"SURS vs human decisiveness (r={pearson(X,Y):.2f})")
    plt.legend(handles=[Line2D([0],[0],marker='o',ls='',mfc=c,mec='k',label=k) for k,c in col.items()],fontsize=9,loc="upper left")
    plt.tight_layout(); plt.savefig("human_validation_figure_1.png",dpi=160)
    plt.close()
    print("saved human_validation_figure_1.png")

# ---- figure 2: Bar Chart ----
    plt.figure(figsize=(6, 5))
    dd=[r[0] for r in domrows]; lv=[r[1] for r in domrows]; hv=[r[2] for r in domrows]
    x=range(len(dd)); w=.38
    plt.bar([i-w/2 for i in x],lv,w,label="LLM ensemble",color="#1f77b4")
    plt.bar([i+w/2 for i in x],hv,w,label="Human (n=%d)"%N,color="#9467bd")
    plt.axhline(.5,ls="--",c="grey",lw=.8); plt.xticks(list(x), dd)
    plt.ylabel("P(choose Variant A)"); plt.title("Directional validity by domain"); plt.legend(fontsize=9)
    plt.tight_layout(); plt.savefig("human_validation_figure_2.png",dpi=160)
    plt.close()
    print("saved human_validation_figure_2.png")
except Exception as e:
    print("figure skipped:",e)
