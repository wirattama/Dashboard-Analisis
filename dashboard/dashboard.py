"""
Dashboard E-Commerce Brasil - Proyek Analisis Data
Menampilkan hasil analisis dataset E-Commerce Public Dataset (2017-2018)
"""

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
import branca.colormap as cm
from streamlit import components

st.set_page_config(page_title="E-Commerce Brasil Dashboard", page_icon="📊", layout="wide")

# Load data - cari file di folder dashboard
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load_data():
    try:
        main_df = pd.read_csv(os.path.join(DASHBOARD_DIR, "main_data.csv"))
        category_df = pd.read_csv(os.path.join(DASHBOARD_DIR, "category_data.csv"))
        rfm_df = pd.read_csv(os.path.join(DASHBOARD_DIR, "rfm_data.csv"))
        return main_df, category_df, rfm_df
    except FileNotFoundError:
        st.error("File data tidak ditemukan. Jalankan notebook terlebih dahulu atau run: python generate_data.py")
        return None, None, None


main_df, category_df, rfm_df = load_data()

if main_df is None:
    st.stop()

# Header
st.title("📊 Dashboard Analisis E-Commerce Brasil")
st.markdown("**Periode:** 2017-2018 | **Sumber:** E-Commerce Public Dataset")
st.caption("💡 **BRL** = Real Brasil (mata uang resmi Brasil). Semua nilai uang dalam dashboard dalam Real.")
st.divider()

# Sidebar
with st.sidebar:
    st.header("Nama: M Fajrin Wirattama")
    st.subheader("Email: fajrinwirattama21@gmail.com")
    st.subheader("ID Dicoding: wirattama")

    st.markdown("---")

page = st.sidebar.radio(
    "Pilih Halaman",
    ["Overview", "Volume & Ketepatan Pengiriman", "Review vs AOV", "RFM Analysis"],
)

# ---- Fitur interaktif: Filter berdasarkan Tahun dan State (memengaruhi visualisasi) ----
years_available = []
if "order_year" in main_df.columns:
    years_available = sorted(main_df["order_year"].dropna().unique().astype(int).tolist())
if "order_year" in main_df.columns:
    selected_years = st.sidebar.multiselect(
        "🔍 Filter Tahun",
        options=years_available,
        default=years_available,
        help="Memengaruhi Overview, Volume & Ketepatan, Review vs AOV (per kota), dan RFM Analysis.",
    )
    if not selected_years:
        selected_years = years_available
else:
    selected_years = None

if "customer_state" in main_df.columns:
    states = ["Semua"] + sorted(
        main_df["customer_state"].dropna().unique().astype(str).tolist()
    )
    selected_state = st.sidebar.selectbox(
        "🔍 Filter berdasarkan State",
        options=states,
        help="Pilih state untuk memfilter data. Memengaruhi Overview, Volume & Ketepatan, Review vs AOV (per kota), dan RFM Analysis.",
    )
else:
    selected_state = "Semua"

# Terapkan filter tahun dan state
if selected_years is not None and "order_year" in main_df.columns:
    df_by_year_city = main_df[main_df["order_year"].isin(selected_years)].copy()
else:
    df_by_year_city = main_df.copy()

if selected_state != "Semua" and "customer_state" in df_by_year_city.columns:
    df_by_year_city = df_by_year_city[df_by_year_city["customer_state"] == selected_state].copy()

# Agregasi per kota (gabungkan beberapa tahun jadi satu baris per kota untuk tampilan)
if "order_year" in df_by_year_city.columns and len(df_by_year_city) > 0:
    agg_map = {
        "total_orders": ("total_orders", "sum"),
        "on_time_count": ("on_time_count", "sum"),
        "customer_state": ("customer_state", "first"),
        "lat": ("lat", "first"),
        "lng": ("lng", "first"),
        "avg_review_score": ("avg_review_score", "mean"),
        "review_count": ("review_count", "sum"),
    }
    if "avg_order_value" in df_by_year_city.columns:
        agg_map["avg_order_value"] = ("avg_order_value", "mean")
    df_filtered = (
        df_by_year_city.groupby("customer_city")
        .agg(**agg_map)
        .reset_index()
    )
    df_filtered["on_time_pct"] = (
        df_filtered["on_time_count"] / df_filtered["total_orders"] * 100
    ).round(2)
    df_filtered = df_filtered.sort_values("total_orders", ascending=False)
else:
    df_filtered = df_by_year_city.sort_values("total_orders", ascending=False).copy()
    if len(df_filtered) > 0 and "on_time_count" in df_filtered.columns:
        df_filtered["on_time_pct"] = (
            df_filtered["on_time_count"] / df_filtered["total_orders"] * 100
        ).round(2)

if page == "Overview":
    st.header("Overview")
    filter_desc = []
    if selected_years is not None and years_available and len(selected_years) < len(years_available):
        filter_desc.append(f"Tahun: {', '.join(map(str, selected_years))}")
    if selected_state and selected_state != "Semua":
        filter_desc.append(f"State: {selected_state}")
    if filter_desc:
        st.caption(" | ".join(filter_desc))
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Kota", f"{len(df_filtered):,}")
    with col2:
        st.metric("Total Order (Semua Kota)", f"{df_filtered['total_orders'].sum():,}")
    with col3:
        top_city = df_filtered.iloc[0]
        st.metric("Kota Teratas", top_city["customer_city"].title())
    with col4:
        st.metric("Order Kota Teratas", f"{int(top_city['total_orders']):,}")

    st.subheader("Top 10 Kota by Volume Transaksi")
    top10 = df_filtered.head(10).copy()
    fig = px.bar(
        top10,
        x="total_orders",
        y="customer_city",
        orientation="h",
        title="Volume Transaksi per Kota",
        labels={"total_orders": "Jumlah Order", "customer_city": "Kota"},
        color="total_orders",
        color_continuous_scale="Blues",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
    fig.update_traces(
        hovertemplate="<b>Kota: %{y}</b><br>Jumlah order: %{x}<br>"
        "Ketepatan pengiriman: %{customdata[0]:.1f}%<extra></extra>",
        customdata=top10[["on_time_pct"]],
    )
    st.plotly_chart(fig, width="stretch")

    # Geospatial Analysis - Distribusi Transaksi berdasarkan Lokasi Geografis
    st.subheader("Geospatial Analysis - Distribusi Transaksi berdasarkan Lokasi Geografis")

    # Cek kolom yang ada (main_data.csv di Cloud bisa versi lama tanpa lat/lng/avg_review_score)
    has_lat_lng = "lat" in main_df.columns and "lng" in main_df.columns
    has_review = "avg_review_score" in main_df.columns
    has_review_count = "review_count" in main_df.columns

    if not has_lat_lng:
        st.info(
            "Peta geospatial membutuhkan kolom **lat** dan **lng** di `main_data.csv`. "
            "Generate ulang data dengan menjalankan `python generate_data.py` dari folder dashboard "
            "(dengan dataset E-Commerce di folder proyek), lalu commit & push file `main_data.csv` yang baru."
        )
    else:
        subset_cols = ["lat", "lng"]
        if has_review:
            subset_cols.append("avg_review_score")
        geo_df = df_filtered.dropna(subset=subset_cols).copy()
        geo_df = geo_df[geo_df["total_orders"] >= 100]

        if geo_df.empty:
            st.warning("Tidak ada data kota dengan koordinat dan minimal 100 order.")
        else:
            center_lat = geo_df["lat"].mean()
            center_lng = geo_df["lng"].mean()
            m = folium.Map(location=[center_lat, center_lng], zoom_start=4, tiles="CartoDB positron")

            if has_review:
                min_score = float(geo_df["avg_review_score"].min())
                max_score = float(geo_df["avg_review_score"].max())
                score_cmap = cm.LinearColormap(
                    ["red", "yellow", "green"], vmin=min_score, vmax=max_score
                )
                score_cmap.caption = "Rata-rata Review Score (1 = buruk, 5 = sangat puas)"
                score_cmap.add_to(m)

            for _, row in geo_df.iterrows():
                if has_review:
                    score = float(row["avg_review_score"])
                    color = score_cmap(score)
                    review_n = int(row["review_count"]) if (has_review_count and pd.notna(row.get("review_count", None))) else 0
                    tooltip_html = (
                        f"<b>{row['customer_city'].title()}</b><br>"
                        f"Jumlah order: {int(row['total_orders']):,}<br>"
                        f"Ketepatan pengiriman: {row['on_time_pct']:.1f}%<br>"
                        f"Rata-rata review: {score:.2f} / 5 (n={review_n} ulasan)"
                    )
                else:
                    color = "#3498db"
                    tooltip_html = (
                        f"<b>{row['customer_city'].title()}</b><br>"
                        f"Jumlah order: {int(row['total_orders']):,}<br>"
                        f"Ketepatan pengiriman: {row['on_time_pct']:.1f}%"
                    )

                folium.CircleMarker(
                    location=[row["lat"], row["lng"]],
                    radius=max(row["total_orders"] / 1000, 4),
                    popup=None,
                    tooltip=tooltip_html,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.75,
                ).add_to(m)

            components.v1.html(m._repr_html_(), height=520, scrolling=False)

elif page == "Volume & Ketepatan Pengiriman":
    st.header("Kota dengan Volume Tertinggi & Korelasi Ketepatan Pengiriman")
    st.markdown("""
    **Pertanyaan:** Kota mana di Brasil yang memiliki volume transaksi tertinggi, dan bagaimana korelasi antara jumlah order dengan persentase ketepatan pengiriman di kota tersebut selama 2017–2018?
    """)
    if selected_years is not None and years_available and len(selected_years) < len(years_available):
        st.caption(f"Filter aktif: **Tahun {selected_years}** — visualisasi mengikuti filter tahun dan state.")
    elif selected_state and selected_state != "Semua":
        st.caption(f"Filter aktif: **State {selected_state}** — visualisasi mengikuti filter.")
    top_city = df_filtered.iloc[0]
    st.success(f"**Kota dengan volume tertinggi:** {top_city['customer_city'].title()} dengan {int(top_city['total_orders']):,} order dan ketepatan pengiriman {top_city['on_time_pct']:.1f}%")
    
    col1, col2 = st.columns(2)
    with col1:
        top10 = df_filtered.head(10).copy()
        fig1 = px.bar(
            top10,
            x="total_orders",
            y="customer_city",
            orientation="h",
            color="on_time_pct",
            color_continuous_scale="RdYlGn",
            labels={"total_orders": "Jumlah Order", "customer_city": "Kota", "on_time_pct": "Ketepatan (%)"},
            title="Top 10 Kota berdasarkan Volume & Ketepatan Pengiriman",
        )
        fig1.update_layout(yaxis={"categoryorder": "total ascending"})
        fig1.update_traces(
            hovertemplate="<b>Kota: %{y}</b><br>"
            "Jumlah order: %{x}<br>"
            "Ketepatan pengiriman: %{marker.color:.1f}%<extra></extra>"
        )
        st.plotly_chart(fig1, width="stretch")
    
    with col2:
        corr = df_filtered["total_orders"].corr(df_filtered["on_time_pct"])
        fig2 = px.scatter(
            df_filtered,
            x="total_orders",
            y="on_time_pct",
            hover_data=["customer_city"],
            labels={"total_orders": "Jumlah Order", "on_time_pct": "Ketepatan Pengiriman (%)"},
            title=f"Korelasi Order vs Ketepatan Pengiriman (r={corr:.3f})",
        )
        fig2.update_traces(
            hovertemplate="<b>Kota: %{customdata[0]}</b><br>"
            "Jumlah order: %{x}<br>"
            "Ketepatan pengiriman: %{y:.1f}%<extra></extra>",
            customdata=df_filtered[["customer_city"]],
        )
        fig2.add_trace(
            go.Scatter(
                x=[top_city["total_orders"]],
                y=[top_city["on_time_pct"]],
                mode="markers",
                marker=dict(size=15, color="red", symbol="star"),
                name="Kota Teratas",
            )
        )
        st.plotly_chart(fig2, width="stretch")

elif page == "Review vs AOV":
    st.header("Review Score vs Average Order Value")
    st.markdown("""
    **Pertanyaan bisnis:** Bagaimana hubungan antara review score dengan Average Order Value (AOV) berdasarkan kota selama 2017–2018?  
    Kota yang ditampilkan mengikuti filter **Tahun** dan **State** di sidebar.
    """)
    if selected_state and selected_state != "Semua":
        st.caption(f"Menampilkan kota di **State: {selected_state}**.")
    
    has_aov = "avg_order_value" in df_filtered.columns
    if df_filtered.empty or "avg_review_score" not in df_filtered.columns:
        st.info("Tidak ada data kota dengan review score. Pastikan main_data.csv berisi kolom avg_review_score.")
    elif has_aov:
        city_review = df_filtered.dropna(subset=["avg_review_score", "avg_order_value"]).copy()
        city_review = city_review[city_review["total_orders"] >= 10]
        if not city_review.empty:
            corr_city = city_review["avg_review_score"].corr(city_review["avg_order_value"])
            fig_city = px.scatter(
                city_review,
                x="avg_review_score",
                y="avg_order_value",
                hover_name="customer_city",
                color="on_time_pct",
                color_continuous_scale="RdYlGn",
                size="review_count",
                labels={
                    "avg_review_score": "Rata-rata Review Score",
                    "avg_order_value": "AOV (BRL)",
                    "on_time_pct": "Ketepatan (%)",
                },
                title=f"Review Score vs AOV per Kota (korelasi r = {corr_city:.3f})",
            )
            fig_city.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>"
                "Review: %{x:.2f}<br>"
                "AOV: %{y:.2f} BRL<br>"
                "Ketepatan: %{marker.color:.1f}%<extra></extra>"
            )
            st.plotly_chart(fig_city, width="stretch")
            with st.expander("Tabel data kota"):
                show_cols = ["customer_city", "customer_state", "total_orders", "on_time_pct", "avg_review_score", "avg_order_value", "review_count"]
                show_cols = [c for c in show_cols if c in city_review.columns]
                st.dataframe(
                    city_review[show_cols].sort_values("total_orders", ascending=False).head(50),
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.warning("Tidak ada kota dengan minimal 10 order dan data review/AOV.")
    else:
        st.info(
            "Kolom **avg_order_value** belum ada di main_data.csv. "
            "Jalankan ulang `python generate_data.py` dari folder dashboard agar grafik Review vs AOV per kota menampilkan AOV."
        )

elif page == "RFM Analysis":
    st.header("RFM Analysis - Segmentasi Pelanggan")
    # Terapkan filter tahun dan state ke RFM
    rfm_filtered = rfm_df.copy()
    filter_parts = []
    if "order_year" in rfm_df.columns and selected_years is not None and len(selected_years) > 0:
        rfm_filtered = rfm_filtered[rfm_filtered["order_year"].astype(int).isin(selected_years)]
        filter_parts.append(f"Tahun: {selected_years}")
    if "customer_state" in rfm_df.columns and selected_state and selected_state != "Semua":
        rfm_filtered = rfm_filtered[rfm_filtered["customer_state"] == selected_state]
        filter_parts.append(f"State: {selected_state}")
    if filter_parts:
        st.caption(f"Menampilkan **{' | '.join(filter_parts)}** — {len(rfm_filtered):,} baris data (pelanggan-tahun). Ubah filter di sidebar untuk mengubah tampilan.")
    else:
        st.caption(f"Menampilkan semua data ({len(rfm_filtered):,} baris). Gunakan filter Tahun dan State di sidebar untuk mempersempit.")
    if "order_year" not in rfm_df.columns and selected_years is not None:
        st.info("Filter Tahun belum berlaku untuk RFM (data RFM belum memiliki kolom **order_year**). Jalankan ulang `python generate_data.py` untuk memperbarui.")
    
    st.markdown("""
    **Tujuan:** Mengelompokkan pelanggan berdasarkan Recency, Frequency, Monetary untuk strategi pemasaran.
    - **Champions:** Pelanggan paling loyal dengan transaksi terbaru, sering, dan bernilai tinggi.
    - **Potential Loyalists:** Pelanggan baru aktif yang berpotensi menjadi loyal.
    - **At Risk:** Pelanggan yang dulu aktif tetapi sudah lama tidak bertransaksi.
    - **Hibernating:** Pelanggan dengan aktivitas sangat rendah dan jarang bertransaksi.    
    - **Others:** Pelanggan dengan pola transaksi sedang atau tidak konsisten.
    """)
    
    segment_counts = rfm_filtered['Segment'].value_counts()
    col1, col2, col3, col4 = st.columns(4)
    for i, (seg, count) in enumerate(segment_counts.head(4).items()):
        with [col1, col2, col3, col4][i]:
            st.metric(seg, f"{count:,}")
    
    fig = px.pie(
        values=segment_counts.values,
        names=segment_counts.index,
        title="Distribusi Segment RFM"
        + (f" — Tahun {selected_years}" if selected_years and "order_year" in rfm_df.columns else "")
        + (f" — State {selected_state}" if selected_state and selected_state != "Semua" and "customer_state" in rfm_df.columns else ""),
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig.update_traces(
        hovertemplate="<b>Segment: %{label}</b><br>"
        "Jumlah pelanggan: %{value}<br>"
        "Persentase: %{percent:.1%}<extra></extra>"
    )
    st.plotly_chart(fig, width="stretch")

# Watermark di bagian bawah halaman
st.markdown(
    "<div style='text-align:center; font-size:11px; color:#888; margin-top:32px;'>"
    "© 2026 M Fajrin Wirattama &middot; E-Commerce Brasil Analysis Dashboard"
    "</div>",
    unsafe_allow_html=True,
)

st.sidebar.divider()
st.sidebar.caption("Proyek Analisis Data - M Fajrin Wirattama")
