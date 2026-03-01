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

if page == "Overview":
    st.header("Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Kota", f"{len(main_df):,}")
    with col2:
        st.metric("Total Order (Semua Kota)", f"{main_df['total_orders'].sum():,}")
    with col3:
        top_city = main_df.iloc[0]
        st.metric("Kota Teratas", top_city["customer_city"].title())
    with col4:
        st.metric("Order Kota Teratas", f"{int(top_city['total_orders']):,}")

    st.subheader("Top 10 Kota by Volume Transaksi")
    top10 = main_df.head(10).copy()
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
        geo_df = main_df.dropna(subset=subset_cols).copy()
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
    
    top_city = main_df.iloc[0]
    st.success(f"**Kota dengan volume tertinggi:** {top_city['customer_city'].title()} dengan {int(top_city['total_orders']):,} order dan ketepatan pengiriman {top_city['on_time_pct']:.1f}%")
    
    col1, col2 = st.columns(2)
    with col1:
        top10 = main_df.head(10).copy()
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
        corr = main_df["total_orders"].corr(main_df["on_time_pct"])
        fig2 = px.scatter(
            main_df,
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
            customdata=main_df[["customer_city"]],
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
    **Pertanyaan:** Apakah kategori produk dengan review score tertinggi juga memiliki Average Order Value yang lebih tinggi dibandingkan kategori dengan review score rendah selama 2017–2018?
    """)
    
    top5_review = category_df.nlargest(5, 'avg_review_score')
    low5_review = category_df.nsmallest(5, 'avg_review_score')
    aov_high = top5_review['avg_order_value'].mean()
    aov_low = low5_review['avg_order_value'].mean()
    
    if aov_high > aov_low:
        st.info(f"Kategori review tinggi memiliki AOV rata-rata **{aov_high:.2f} BRL** vs review rendah **{aov_low:.2f} BRL**")
    else:
        st.warning(f"Kategori review tinggi AOV: **{aov_high:.2f} BRL** vs review rendah: **{aov_low:.2f} BRL** - Tidak selalu berkorelasi positif")
    
    fig = px.scatter(
        category_df,
        x="avg_review_score",
        y="avg_order_value",
        size="order_count",
        hover_name="product_category_name_english",
        labels={"avg_review_score": "Rata-rata Review Score", "avg_order_value": "AOV (BRL = Real Brasil)"},
        title="Review Score vs AOV per Kategori Produk",
        color="avg_review_score",
        color_continuous_scale="RdYlGn",
    )
    fig.update_traces(
        hovertemplate="<b>Kategori: %{hovertext}</b><br>"
        "Rata-rata review: %{x:.2f}<br>"
        "AOV: %{y:.2f} BRL<br>"
        "Jumlah order: %{marker.size:.0f}<extra></extra>"
    )
    st.plotly_chart(fig, width="stretch")

elif page == "RFM Analysis":
    st.header("RFM Analysis - Segmentasi Pelanggan")
    st.markdown("""
    **Tujuan:** Mengelompokkan pelanggan berdasarkan Recency, Frequency, Monetary untuk strategi pemasaran.
    - **Champions:** Pelanggan paling loyal dengan transaksi terbaru, sering, dan bernilai tinggi.
    - **Potential Loyalists:** Pelanggan baru aktif yang berpotensi menjadi loyal.
    - **At Risk:** Pelanggan yang dulu aktif tetapi sudah lama tidak bertransaksi.
    - **Hibernating:** Pelanggan dengan aktivitas sangat rendah dan jarang bertransaksi.    
    - **Others:** Pelanggan dengan pola transaksi sedang atau tidak konsisten.
    """)
    
    segment_counts = rfm_df['Segment'].value_counts()
    col1, col2, col3, col4 = st.columns(4)
    for i, (seg, count) in enumerate(segment_counts.head(4).items()):
        with [col1, col2, col3, col4][i]:
            st.metric(seg, f"{count:,}")
    
    fig = px.pie(
        values=segment_counts.values,
        names=segment_counts.index,
        title="Distribusi Segment RFM",
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
