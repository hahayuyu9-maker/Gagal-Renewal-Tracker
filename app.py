import streamlit as st
import pandas as pd
from datetime import date, datetime
import json
import os

st.set_page_config(page_title="Renewal Tracker Jabar", page_icon="📡", layout="wide")

DATA_FILE = "data_sites.json"

DEFAULT_SITES = [
    {"nama":"Jl. Somiari","end_sewa":"2025-11-27","ext_sewa":"2026-02-27","tenant":"Tsel","tgl_email":"2025-10-07","bai":True,"wo":True,"progres":"Plan pindah 27 April '26","status":"RFI"},
    {"nama":"Malebet Utara","end_sewa":"2026-02-14","ext_sewa":"2026-06-14","tenant":"Tsel","tgl_email":"2025-04-25","bai":True,"wo":True,"progres":"Hard comcase, LL kooperatif, pengamanan warga (+)","status":"Validasi"},
    {"nama":"Soreang Timur - ds. Sadu","end_sewa":"2026-04-04","ext_sewa":"2026-05-10","tenant":"3 tenant","tgl_email":"2025-11-14","bai":True,"wo":True,"progres":"Extend s/d Mei, plan bongkar 1/5/26","status":"CME"},
    {"nama":"Bajakarekes MD","end_sewa":"2026-03-14","ext_sewa":"2026-04-06","tenant":"Tsel","tgl_email":"2025-10-03","bai":True,"wo":True,"progres":"Soil test, plan extend by drajat, plan bongkar 25/5","status":"RFI"},
    {"nama":"Ciganitri","end_sewa":"2026-02-03","ext_sewa":"2026-03-05","tenant":"Tsel","tgl_email":"2025-11-05","bai":False,"wo":False,"progres":"BAI proses, plan combat akhir April, plan bongkar 26 April","status":"Combat"},
    {"nama":"Gempol MB","end_sewa":"2026-05-11","ext_sewa":"","tenant":"3 tenant","tgl_email":"2025-05-14","bai":True,"wo":True,"progres":"Rehunting - pengajuan next by Handika, cancel s/d found","status":"Rehunting"},
    {"nama":"Jl. Leuwisari","end_sewa":"2026-04-24","ext_sewa":"2026-07-24","tenant":"Tsel","tgl_email":"2026-04-07","bai":False,"wo":False,"progres":"BAI waiting kandidat","status":"Validasi"},
    {"nama":"Parakan Muncang","end_sewa":"2026-07-13","ext_sewa":"","tenant":"Tsel","tgl_email":"2025-12-01","bai":True,"wo":True,"progres":"Validasi done, BAI proses","status":"Validasi"},
    {"nama":"Sukahurip MD","end_sewa":"2026-02-25","ext_sewa":"","tenant":"Tsel, IOH","tgl_email":"2025-06-17","bai":False,"wo":True,"progres":"Sitac done, SRF1","status":"Sitac"},
    {"nama":"Alun-alun Banjaran","end_sewa":"2026-09-03","ext_sewa":"","tenant":"IOH","tgl_email":"2026-03-13","bai":False,"wo":False,"progres":"LLwill, proses nego ext 1th, BAI waiting kandidat","status":"Rehunting"},
    {"nama":"Juvante Hotel","end_sewa":"2026-12-31","ext_sewa":"2027-03-30","tenant":"Tsel","tgl_email":"2026-04-14","bai":False,"wo":False,"progres":"Hold dual, BAI waiting kandidat","status":"Hunting"},
    {"nama":"Cipitung - Bojongsoang","end_sewa":"2026-06-21","ext_sewa":"2027-06-21","tenant":"XL","tgl_email":"2026-03-10","bai":False,"wo":False,"progres":"BAI waiting kandidat","status":"Hunting"},
    {"nama":"Puncak Raya Cianjur","end_sewa":"2027-08-07","ext_sewa":"","tenant":"IOH, XL","tgl_email":"2026-02-23","bai":False,"wo":False,"progres":"BAI waiting kandidat","status":"Hunting"},
    {"nama":"Sindang Rasa","end_sewa":"2027-03-02","ext_sewa":"","tenant":"Tsel, IOH","tgl_email":"2026-04-07","bai":False,"wo":False,"progres":"Lahan akan jd RS Jantung, bs pindah ke lahan milik LL 120 meter","status":"Hunting"},
    {"nama":"Luragung","end_sewa":"2024-03-10","ext_sewa":"2026-07-10","tenant":"IOH","tgl_email":"2025-01-01","bai":True,"wo":True,"progres":"LL sdh tidak mau ext tambahan, comcase warga, tenant minta 4 shelter dipertahankan, JE tower dibongkar","status":"Sitac"},
]

STATUS_LIST = ["Hunting","Rehunting","Validasi","Combat","Sitac","RFI","CME","Selesai"]
TENANT_LIST = ["Tsel","IOH","XL","3 tenant","Tsel, IOH","Tsel, IOH, XL","IOH, XL","Lainnya"]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r") as f:
            return json.load(f)
    return DEFAULT_SITES.copy()

def save_data(data):
    with open(DATA_FILE,"w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None

def sisa_hari(site):
    ref = site.get("ext_sewa") or site.get("end_sewa")
    d = parse_date(ref)
    if not d:
        return None
    return (d - date.today()).days

def urgency_label(days):
    if days is None:
        return "—"
    if days < 0:
        return f"🔴 {abs(days)}h lalu"
    if days <= 90:
        return f"🟡 {days} hari"
    return f"🟢 {days} hari"

def urgency_sort(site):
    d = sisa_hari(site)
    return d if d is not None else 9999

if "sites" not in st.session_state:
    st.session_state.sites = load_data()
if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None

sites = st.session_state.sites

# ── HEADER ──
st.title("📡 Renewal Tracker — Jabar")
st.caption(f"Per hari ini: {date.today().strftime('%d %B %Y')}")

# ── METRICS ──
total = len(sites)
overdue = sum(1 for s in sites if (sisa_hari(s) or 0) < 0)
soon = sum(1 for s in sites if sisa_hari(s) is not None and 0 <= sisa_hari(s) <= 90)
aman = total - overdue - soon

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Site", total)
c2.metric("🔴 Overdue", overdue)
c3.metric("🟡 ≤ 90 Hari", soon)
c4.metric("🟢 Aman", aman)

st.divider()

# ── FILTER & TAMBAH ──
col_f, col_add = st.columns([3,1])
with col_f:
    filter_opt = st.selectbox("Filter", ["Semua","Overdue","≤ 90 Hari","Aman"], label_visibility="collapsed")
    search = st.text_input("Cari nama site...", label_visibility="collapsed", placeholder="🔍 Cari nama site...")

with col_add:
    if st.button("➕ Tambah Site", use_container_width=True):
        st.session_state.edit_idx = "new"

# ── FORM TAMBAH / EDIT ──
if st.session_state.edit_idx is not None:
    is_new = st.session_state.edit_idx == "new"
    existing = {} if is_new else sites[st.session_state.edit_idx]
    
    with st.form("form_site"):
        st.subheader("➕ Tambah Site Baru" if is_new else f"✏️ Edit: {existing.get('nama','')}")
        
        fa, fb = st.columns(2)
        with fa:
            nama = st.text_input("Nama Site *", value=existing.get("nama",""))
            end_sewa = st.text_input("End Sewa (YYYY-MM-DD) *", value=existing.get("end_sewa",""))
            ext_sewa = st.text_input("Extend Sewa (YYYY-MM-DD)", value=existing.get("ext_sewa",""))
        with fb:
            tenant_val = existing.get("tenant","Tsel")
            if tenant_val not in TENANT_LIST:
                TENANT_LIST.append(tenant_val)
            tenant = st.selectbox("Tenant", TENANT_LIST, index=TENANT_LIST.index(tenant_val))
            tgl_email = st.text_input("Tgl Email (YYYY-MM-DD)", value=existing.get("tgl_email",""))
            status_val = existing.get("status","Hunting")
            status = st.selectbox("Status", STATUS_LIST, index=STATUS_LIST.index(status_val) if status_val in STATUS_LIST else 0)

        fc, fd = st.columns(2)
        with fc:
            bai = st.checkbox("BAI ✓", value=existing.get("bai", False))
        with fd:
            wo = st.checkbox("WO ✓", value=existing.get("wo", False))

        progres = st.text_area("Update Progres", value=existing.get("progres",""), height=80)

        s1, s2, s3 = st.columns([1,1,2])
        submitted = s1.form_submit_button("💾 Simpan", use_container_width=True)
        cancelled = s2.form_submit_button("Batal", use_container_width=True)

        if submitted:
            if not nama or not end_sewa:
                st.error("Nama site dan End Sewa wajib diisi.")
            else:
                entry = {"nama":nama,"end_sewa":end_sewa,"ext_sewa":ext_sewa,
                         "tenant":tenant,"tgl_email":tgl_email,"bai":bai,
                         "wo":wo,"progres":progres,"status":status}
                if is_new:
                    st.session_state.sites.append(entry)
                else:
                    st.session_state.sites[st.session_state.edit_idx] = entry
                save_data(st.session_state.sites)
                st.session_state.edit_idx = None
                st.rerun()

        if cancelled:
            st.session_state.edit_idx = None
            st.rerun()

st.divider()

# ── TABEL ──
filtered = sorted(sites, key=urgency_sort)

if search:
    filtered = [s for s in filtered if search.lower() in s["nama"].lower()]

if filter_opt == "Overdue":
    filtered = [s for s in filtered if (sisa_hari(s) or 0) < 0]
elif filter_opt == "≤ 90 Hari":
    filtered = [s for s in filtered if sisa_hari(s) is not None and 0 <= sisa_hari(s) <= 90]
elif filter_opt == "Aman":
    filtered = [s for s in filtered if sisa_hari(s) is not None and sisa_hari(s) > 90]

for i, s in enumerate(filtered):
    real_idx = sites.index(s)
    days = sisa_hari(s)
    
    urgency_icon = "🔴" if (days is not None and days < 0) else ("🟡" if (days is not None and days <= 90) else "🟢")
    
    with st.expander(f"{urgency_icon} **{s['nama']}** — {s['status']} | {urgency_label(days)}"):
        r1, r2, r3, r4 = st.columns(4)
        r1.markdown(f"**End Sewa**\n\n{s.get('end_sewa','—')}")
        r2.markdown(f"**Extend Sewa**\n\n{s.get('ext_sewa','—') or '—'}")
        r3.markdown(f"**Tenant**\n\n{s.get('tenant','—')}")
        r4.markdown(f"**Tgl Email**\n\n{s.get('tgl_email','—')}")

        r5, r6, r7 = st.columns(3)
        r5.markdown(f"**BAI**: {'✅' if s.get('bai') else '❌'}")
        r6.markdown(f"**WO**: {'✅' if s.get('wo') else '❌'}")
        r7.markdown(f"**Status**: `{s.get('status','—')}`")

        st.markdown(f"**Update Progres**")
        st.info(s.get("progres","—"))

        ea, eb = st.columns([1,5])
        if ea.button("✏️ Edit", key=f"edit_{real_idx}"):
            st.session_state.edit_idx = real_idx
            st.rerun()
        if eb.button("🗑️ Hapus", key=f"del_{real_idx}"):
            st.session_state.sites.pop(real_idx)
            save_data(st.session_state.sites)
            st.rerun()

# ── EXPORT ──
st.divider()
if st.button("📥 Export ke Excel"):
    rows = []
    for s in sites:
        rows.append({
            "Nama Site": s["nama"],
            "End Sewa": s["end_sewa"],
            "Extend Sewa": s.get("ext_sewa",""),
            "Tenant": s["tenant"],
            "Tgl Email": s.get("tgl_email",""),
            "BAI": "✓" if s.get("bai") else "—",
            "WO": "✓" if s.get("wo") else "—",
            "Sisa Hari": sisa_hari(s),
            "Update Progres": s.get("progres",""),
            "Status": s.get("status",""),
        })
    df = pd.DataFrame(rows)
    st.download_button("⬇️ Download Excel", df.to_csv(index=False).encode("utf-8"),
                       "renewal_tracker_jabar.csv", "text/csv")
