# SAP Cloud Shift dashboard - run in Google Colab (one cell)
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap

# ---------- 1. DATA (EUR m, SAP quarterly statements; operating profit = IFRS, FCF = non-IFRS) ----------
rows = [
 ("Q1'25", 9013, 4993, 2945, 1075, 18202, 2333, 3583, 4033, 3665, 1315),
 ("Q2'25", 9027, 5130, 2835, 1061, 18052, 2456, 2357, 4158, 3554, 1315),
 ("Q3'25", 9076, 5290, 2726, 1060, 18839, 2487, 1266, 4245, 3546, 1285),
 ("Q4'25", 9684, 5610, 3008, 1066, 21052, 2554, 1034, 4589, 3734, 1361),
 ("Q1'26", 9555, 5962, 2586, 1007, 21932, 2741, 3248, 4479, 3716, 1359),
 ("Q2'26", 9878, 6281, 2570, 1027, 22929, 2643, 3002, 4603, 3881, 1394),
 ("Q3'26", 10270, 6668, 2581, 1021, 24144, 2930, 1718, 4768, 4035, 1467),
]
df = pd.DataFrame(rows, columns=["q","rev","cloud","sw","serv","backlog","op","fcf","emea","amer","apj"])
df["share"] = df.cloud / df.rev * 100
assert ((df.cloud + df.sw + df.serv - df.rev).abs() <= 1).all(), "revenue types do not add up"
assert ((df.emea + df.amer + df.apj - df.rev).abs() <= 1).all(), "regions do not add up"

# ---------- 3. STYLE ----------
BLUE, LIGHT, PALE, GREY, NAVY, BG, INK = "#0057D2", "#5AB1FF", "#A8D2FF", "#C3CCDA", "#0B2A5B", "#EAF0F9", "#3B4F6B"
plt.rcParams["font.family"] = "DejaVu Sans"

def draw(SELECTED, footer=True):
    ALL = SELECTED == "All 7 quarters"
    Q = df.q.iloc[-1] if ALL else SELECTED          # the sidebar cards show the latest quarter in the "All" view
    i = int(df.index[df.q == Q][0]); cur = df.loc[i]
    prev = df.loc[i-4] if i >= 4 else None   # same quarter last year; none for 2025 quarters
    fig = plt.figure(figsize=(16, 9), dpi=200, facecolor=BG)

    def gradient(ax, c1, c2, vertical=True, clip=None, z=0):
        g = np.linspace(0,1,256); g = g.reshape(-1,1) if vertical else g.reshape(1,-1)
        im = ax.imshow(g, cmap=LinearSegmentedColormap.from_list("g",[c1,c2]), aspect="auto",
                       extent=[0,1,0,1], origin="upper" if vertical else "lower", transform=ax.transAxes, zorder=z)
        if clip is not None: im.set_clip_path(clip)

    def panel(rect, color="white", rad=0.016, shadow=True, grad=None):
        ax = fig.add_axes(rect); ax.set_axis_off(); ax.set_xlim(0,1); ax.set_ylim(0,1)
        if shadow:
            sh = fig.add_axes([rect[0]+0.0015, rect[1]-0.003, rect[2], rect[3]], zorder=ax.get_zorder()-0.5); sh.set_axis_off()
            sh.add_patch(FancyBboxPatch((0,0),1,1,boxstyle=f"round,pad=0,rounding_size={rad}",fc="#0B2A5B",alpha=0.10,ec="none",
                         transform=sh.transAxes,mutation_aspect=0.56))
        p = FancyBboxPatch((0,0),1,1,boxstyle=f"round,pad=0,rounding_size={rad}",fc=color,ec="none",transform=ax.transAxes,mutation_aspect=0.56)
        ax.add_patch(p)
        if grad: gradient(ax, grad[0], grad[1], vertical=False, clip=p, z=2)
        return ax

    def card(rect, title, sub=None):
        ax = panel(rect)
        ax.text(0.045,0.93,title,fontsize=12,fontweight="bold",color=NAVY,va="top",transform=ax.transAxes,linespacing=1.15)
        if sub: ax.text(0.045,0.80,sub,fontsize=8,color="#6B7C96",va="top",transform=ax.transAxes)
        return ax

    def chart(rect):
        ax = fig.add_axes(rect); ax.set_facecolor("none")
        for s in ["top","right","left"]: ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(GREY); ax.tick_params(left=False,labelleft=False,colors=INK,labelsize=8.5,length=0)
        return ax

    # ---------- 4. SIDEBAR ----------
    side = fig.add_axes([0,0,0.175,1]); side.set_axis_off(); side.set_xlim(0,1); side.set_ylim(0,1)
    gradient(side, "#0A63E8", "#00419F")
    side.text(0.08,0.955,"FINANCIAL PERFORMANCE",color="#CFE3FF",fontsize=8.5,fontweight="bold",transform=side.transAxes)
    side.text(0.08,0.885,"SAP Cloud\nShift",color="white",fontsize=27,fontweight="bold",va="center",linespacing=1.0,transform=side.transAxes)
    side.text(0.08,0.80,"Quarterly results\nQ1 2025 to Q3 2026",color="#DCE8FF",fontsize=9.5,va="center",transform=side.transAxes)
    side.text(0.08,0.735,"Quarter",color="#CFE3FF",fontsize=9,transform=side.transAxes)
    side.add_patch(FancyBboxPatch((0.08,0.675),0.84,0.04,boxstyle="round,pad=0,rounding_size=0.01",fc="white",ec="none",transform=side.transAxes))
    side.text(0.12,0.695,SELECTED,color=NAVY,fontsize=11,fontweight="bold",va="center",transform=side.transAxes)
    side.text(0.86,0.695,"▾",color=BLUE,fontsize=11,ha="center",va="center",transform=side.transAxes)

    def chg(col, kind="pct"):
        if prev is None: return None
        return (cur[col]-prev[col]) if kind=="pp" else (cur[col]/prev[col]-1)*100
    kpis = [
     ("Total revenue",            f"€{cur.rev:,.0f}m",     chg("rev"),     "%",  "rev"),
     ("Cloud revenue",            f"€{cur.cloud:,.0f}m",   chg("cloud"),   "%",  "cloud"),
     ("Cloud share of revenue",   f"{cur.share:.1f}%",     chg("share","pp"), "pp","share"),
     ("Current cloud backlog",    f"€{cur.backlog:,.0f}m", chg("backlog"), "%",  "backlog"),
     ("Operating profit (IFRS)",  f"€{cur.op:,.0f}m",      chg("op"),      "%",  "op"),
     ("Free cash flow (non-IFRS)",f"€{cur.fcf:,.0f}m",     chg("fcf"),     "%",  "fcf"),
    ]
    top, h, gap = 0.645, 0.085, 0.010
    for k,(lab,val,ch,unit,col) in enumerate(kpis):
        y = top - (k+1)*h - k*gap
        side.add_patch(FancyBboxPatch((0.08,y),0.84,h,boxstyle="round,pad=0,rounding_size=0.012",fc="white",alpha=0.13,ec="none",transform=side.transAxes))
        side.add_patch(FancyBboxPatch((0.08,y),0.012,h,boxstyle="round,pad=0,rounding_size=0.004",fc=LIGHT,ec="none",transform=side.transAxes))
        side.text(0.14,y+h-0.019,lab,color="#DCE8FF",fontsize=8.8,va="center",transform=side.transAxes)
        side.text(0.14,y+0.026,val,color="white",fontsize=16.5,fontweight="bold",va="center",transform=side.transAxes)
        if ch is not None:
            txt = f"{'▲' if ch>=0 else '▼'} {abs(ch):.0f}%" if unit=="%" else f"{'▲' if ch>=0 else '▼'} {abs(ch):.1f} pp"
            side.text(0.89,y+h-0.019,txt,color=BLUE,fontsize=8.5,fontweight="bold",ha="right",va="center",transform=side.transAxes,
                      bbox=dict(boxstyle="round,pad=0.25",fc="white",ec="none"))
        sp = fig.add_axes([0.1, y+0.006, 0.05, h*0.42]); sp.set_axis_off()
        sp.plot(range(7), df[col], color="white", lw=1.6, alpha=0.9)
        sp.scatter([i],[df[col][i]], s=14, color=LIGHT, zorder=3); sp.margins(x=0.05,y=0.15)
    note = f"{Q}, change vs {prev.q}" if prev is not None else f"{Q}: no prior-year quarter in data"
    side.text(0.08,0.035,note+"\nLine = trend Q1'25 to Q3'26",color="#CFE3FF",fontsize=8,transform=side.transAxes,linespacing=1.5)

    # ---------- 5. BANNER ----------
    ban = panel([0.195,0.855,0.785,0.115],NAVY,grad=("#0B2A5B","#0057D2"))
    ban.text(0.025,0.5,"55%",color=LIGHT,fontsize=40,fontweight="bold",va="center",transform=ban.transAxes)
    ban.text(0.148,0.5,"→",color="white",fontsize=28,va="center",transform=ban.transAxes)
    ban.text(0.19,0.5,"65%",color="white",fontsize=40,fontweight="bold",va="center",transform=ban.transAxes)
    ban.text(0.33,0.66,"Cloud is now 65% of SAP's revenue",color="white",fontsize=18,fontweight="bold",va="center",transform=ban.transAxes)
    ban.text(0.33,0.32,"Up from 55% in Q1 2025. Current cloud backlog is up 33% to €24.1 billion.",color="#DCE8FF",fontsize=11.5,va="center",transform=ban.transAxes)

    # ---------- ALL 7 QUARTERS VIEW (table) ----------
    if ALL:
        tb = card([0.195,0.045,0.785,0.79],"All 7 quarters at a glance")
        tb.text(0.03,0.875,"Darker blue = higher value within that row.  Operating profit is IFRS, free cash flow is non-IFRS.",fontsize=8.5,color="#6B7C96",va="top",transform=tb.transAxes)
        trows = [("Total revenue (EUR m)","rev","{:,.0f}"),("Cloud revenue (EUR m)","cloud","{:,.0f}"),
                 ("Software licenses and support (EUR m)","sw","{:,.0f}"),("Services (EUR m)","serv","{:,.0f}"),
                 ("Cloud share of revenue (%)","share","{:.1f}"),("Current cloud backlog (EUR m)","backlog","{:,.0f}"),
                 ("Operating profit, IFRS (EUR m)","op","{:,.0f}"),("Free cash flow, non-IFRS (EUR m)","fcf","{:,.0f}"),
                 ("EMEA (EUR m)","emea","{:,.0f}"),("Americas (EUR m)","amer","{:,.0f}"),("APJ (EUR m)","apj","{:,.0f}")]
        cmap = LinearSegmentedColormap.from_list("t",["#F4F8FF","#6FB3FF"])
        x0, cw = 0.36, 0.088
        rh = 0.066; ytop = 0.80
        for k,q in enumerate(df.q):
            tb.text(x0+cw*k+cw/2, ytop+0.035, q, ha="center", va="center", fontsize=10.5,
                    fontweight="bold", color=BLUE if k==6 else NAVY, transform=tb.transAxes)
        for r,(lab,col,fmt) in enumerate(trows):
            y = ytop - (r+1)*rh
            tb.text(0.03, y+rh/2, lab, fontsize=10, va="center", color=NAVY, fontweight="bold" if col in ("rev","cloud","share") else "normal", transform=tb.transAxes)
            v = df[col].values; lo, hi = v.min(), v.max()
            for k in range(7):
                t = (v[k]-lo)/(hi-lo) if hi>lo else 0
                tb.add_patch(plt.Rectangle((x0+cw*k+0.003, y+0.003), cw-0.006, rh-0.006, fc=cmap(t), ec="none", transform=tb.transAxes))
                tb.text(x0+cw*k+cw/2, y+rh/2, fmt.format(v[k]), ha="center", va="center", fontsize=9.5, color=NAVY,
                        fontweight="bold" if k==6 else "normal", transform=tb.transAxes)
        fig.text(0.195,0.018,"Dataset: SAP quarterly statements, Q1 2025 to Q3 2026   ·   Tool: Python (pandas, matplotlib) in Google Colab",fontsize=8.5,color="#4A5B78")
        fig.text(0.98,0.018,"Created by Iswarya Subburaj",fontsize=9.5,color=NAVY,ha="right",fontweight="bold")
        return fig

    # ---------- 6. REVENUE BY TYPE ----------
    card([0.195,0.455,0.5,0.385],"Revenue by type (EUR m)")
    ax = chart([0.215,0.49,0.46,0.25])
    ax.bar(df.q,df.cloud,color=BLUE,width=0.6,label="Cloud")
    ax.bar(df.q,df.sw,bottom=df.cloud,color=LIGHT,width=0.6,label="Software licenses and support")
    ax.bar(df.q,df.serv,bottom=df.cloud+df.sw,color=GREY,width=0.6,label="Services")
    for x,t,s in zip(df.q,df.rev,df.share):
        ax.text(x,t+170,f"{t:,}",ha="center",fontsize=8.8,fontweight="bold",color=NAVY)
    for x,c_,s in zip(df.q,df.cloud,df.share):
        ax.text(x,c_/2,f"{s:.0f}%",ha="center",va="center",fontsize=9.5,fontweight="bold",color="white")
    ax.set_ylim(0,12600); ax.legend(loc="lower center",bbox_to_anchor=(0.5,1.0),ncol=3,frameon=False,fontsize=8.8)

    # ---------- 7. DONUT ----------
    card([0.71,0.455,0.27,0.385],f"Revenue by region, {SELECTED}")
    ax = fig.add_axes([0.735,0.565,0.22,0.24])
    vals=[cur.emea,cur.amer,cur.apj]; labs=["EMEA","Americas","APJ"]
    ax.pie(vals,colors=[BLUE,LIGHT,GREY],startangle=90,counterclock=False,wedgeprops=dict(width=0.36,edgecolor="white",linewidth=2))
    ax.text(0,0.08,f"€{cur.rev:,.0f}m",ha="center",fontsize=12.5,fontweight="bold",color=NAVY)
    ax.text(0,-0.14,SELECTED,ha="center",fontsize=8.5,color=INK)
    ax.legend([f"{l}  {v/cur.rev*100:.1f}%" for l,v in zip(labs,vals)],loc="upper center",bbox_to_anchor=(0.5,0.0),ncol=1,frameon=False,fontsize=9)

    # ---------- 8. ROW 2 ----------
    W = 0.19; xs = [0.195, 0.395, 0.595, 0.795]; y0, hh = 0.045, 0.39
    xl = [q[:2]+"\n"+q[-2:] for q in df.q]

    card([xs[0],y0,W,hh],"Cloud share of\nrevenue (%)")
    ax = chart([xs[0]+0.012,y0+0.04,W-0.024,0.25])
    ax.fill_between(range(7),df.share,40,color=PALE,alpha=0.35)
    ax.plot(range(7),df.share,color=BLUE,lw=2.8,marker="o",ms=6,mfc="white",mew=2)
    ax.scatter([i],[df.share[i]],s=70,color=BLUE,zorder=4)
    for x,v in enumerate(df.share): ax.text(x,v+(1.3 if x!=3 else -3.0),f"{v:.1f}",ha="center",fontsize=8,fontweight="bold",color=NAVY)
    ax.annotate("seasonal licence\nrevenue",xy=(3,df.share[3]-0.4),xytext=(3.3,51.5),fontsize=6.8,color="#6B7C96",ha="left",
                arrowprops=dict(arrowstyle="-",color="#9AA8BD",lw=0.8))
    ax.text(0.0,68.8,f"+{df.share.iloc[-1]-df.share.iloc[0]:.1f} pp since Q1'25",fontsize=8.5,fontweight="bold",color=BLUE)
    ax.set_ylim(48,70.5); ax.set_xticks(range(7)); ax.set_xticklabels(xl,fontsize=7.5)

    card([xs[1],y0,W,hh],"Current cloud backlog\n(EUR bn)")
    ax = chart([xs[1]+0.012,y0+0.04,W-0.024,0.25])
    b = df.backlog/1000
    ax.fill_between(range(7),b,color=PALE,alpha=0.55); ax.plot(range(7),b,color=BLUE,lw=2.8)
    ax.scatter([i],[b[i]],s=70,color=BLUE,zorder=4)
    for x,v in enumerate(b): ax.text(x,v+1.0,f"{v:.1f}",ha="center",fontsize=8,fontweight="bold",color=NAVY)
    ax.text(0.0,29.0,f"+{(b.iloc[-1]/b.iloc[0]-1)*100:.0f}% since Q1'25",fontsize=8.5,fontweight="bold",color=BLUE)
    ax.set_ylim(0,31); ax.set_xticks(range(7)); ax.set_xticklabels(xl,fontsize=7.5)

    card([xs[2],y0,W,hh],"Operating profit, IFRS\n(EUR bn)")
    ax = chart([xs[2]+0.012,y0+0.04,W-0.024,0.25])
    c = [PALE]*7; c[i] = BLUE
    ax.bar(range(7),df.op/1000,color=c,width=0.66)
    for x,v in enumerate(df.op/1000): ax.text(x,v+0.06,f"{v:.1f}",ha="center",fontsize=8,fontweight="bold",color=NAVY)
    ax.set_ylim(0,3.6); ax.set_xticks(range(7)); ax.set_xticklabels(xl,fontsize=7.5)

    card([xs[3],y0,0.185,hh],"Free cash flow, non-IFRS\n(EUR bn)")
    ax = chart([xs[3]+0.04,y0+0.03,0.135,0.215])
    c = [PALE]*7; c[i] = BLUE
    ax.barh(range(7),df.fcf/1000,color=c,height=0.66); ax.invert_yaxis()
    for y,v in enumerate(df.fcf/1000): ax.text(v+0.05,y,f"{v:.1f}",va="center",fontsize=8,fontweight="bold",color=NAVY)
    ax.set_yticks(range(7)); ax.set_yticklabels(df.q,fontsize=8); ax.tick_params(left=False,labelleft=True)
    ax.spines["bottom"].set_visible(False); ax.set_xticks([]); ax.set_xlim(0,4.4)
    fig.text(0.805,0.345,"Q1'26 is after a €408m litigation payout",fontsize=7.5,color="#6B7C96")

    # ---------- 9. FOOTER ----------
    if footer:
        fig.text(0.195,0.018,"Dataset: SAP quarterly statements, Q1 2025 to Q3 2026   ·   Tool: Python (pandas, matplotlib) in Google Colab",fontsize=8.5,color="#4A5B78")
        fig.text(0.98,0.018,"Created by Iswarya Subburaj",fontsize=9.5,color=NAVY,ha="right",fontweight="bold")

    return fig

# ---------- 4. FULL PAGE = charts dashboard + all-7-quarters table, stacked in one tall image ----------
from PIL import Image
def to_array(fig):
    fig.canvas.draw()
    a = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
    plt.close(fig)
    return a

def full_page(q=None):
    q = q or df.q.iloc[-1]
    top = to_array(draw(q, footer=False))              # charts dashboard (no footer)
    tab = to_array(draw("All 7 quarters"))             # table view
    H, W = tab.shape[:2]
    bottom = tab[int(H*0.155):, :].copy()              # keep the table card + footer, drop the banner
    side_w = int(W*0.175)
    bottom[:, :side_w] = top[-1, 10, :]                # continue the blue sidebar colour
    return Image.fromarray(np.vstack([top, bottom]))

# ---------- 5. FILTER (dropdown + save button) ----------
import ipywidgets as widgets
from IPython.display import display, clear_output

FULL = "Full page (all 7 quarters)"
dropdown = widgets.Dropdown(options=[FULL]+list(df.q), value=FULL, description="View:", layout=widgets.Layout(width="320px"))
save_btn = widgets.Button(description="Save PNG", button_style="primary", icon="download")
out = widgets.Output()
state = {"img": None}

def refresh(change=None):
    with out:
        clear_output(wait=True)
        if dropdown.value == FULL:
            state["img"] = full_page()
        else:
            state["img"] = to_array_img = Image.fromarray(to_array(draw(dropdown.value)))
        display(state["img"])

def save(_):
    v = dropdown.value
    name = "sap_cloud_shift_full_page.png" if v == FULL else f"sap_cloud_shift_{v.replace(chr(39),'')}.png"
    state["img"].save(name)
    with out: print("Saved:", name, "(Files panel on the left)")

dropdown.observe(refresh, names="value")
save_btn.on_click(save)
display(widgets.HBox([dropdown, save_btn]), out)
refresh()
