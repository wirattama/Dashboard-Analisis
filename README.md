# Proyek Analisis Data: E-Commerce Public Dataset

Proyek ini menganalisis dataset E-Commerce Brasil untuk menjawab pertanyaan bisnis terkait:

- **Volume transaksi per kota dan ketepatan pengiriman**
- **Hubungan antara review score dengan Average Order Value (AOV) berdasarkan kota**

Selain itu, proyek dilengkapi **dashboard interaktif** berbasis Streamlit untuk menyajikan hasil analisis (dengan filter tahun dan state).

---

## Struktur Direktori

```text
Submission-Proyek Analisis Data/
├── dashboard/
│   ├── main_data.csv        # Agregasi kota (volume, on-time, review, AOV, geospatial)
│   ├── category_data.csv    # Agregasi kategori produk (review, AOV) — referensi
│   ├── rfm_data.csv         # Segmentasi pelanggan per tahun (RFM + state/kota)
│   ├── dashboard.py         # Aplikasi Streamlit utama
│   └── generate_data.py     # Skrip generator data untuk dashboard
├── data/                    # Dataset mentah E-Commerce (CSV)
│   ├── orders_dataset.csv
│   ├── customers_dataset.csv
│   └── ... (file CSV lainnya)
├── Proyek_Analisis_Data.ipynb
├── requirements.txt
├── README.md
└── url.txt                  # URL dashboard Streamlit Cloud
```

---

## Persiapan Lingkungan

1. **Buat environment (opsional tapi disarankan)**  
   Contoh dengan `venv`:

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

Pastikan folder **`data/`** di root proyek berisi seluruh file CSV dataset E-Commerce (mis. `orders_dataset.csv`, `customers_dataset.csv`, `order_items_dataset.csv`, `order_reviews_dataset.csv`, `products_dataset.csv`, `product_category_name_translation.csv`, `order_payments_dataset.csv`, `geolocation_dataset.csv`). Jika dataset Anda berada di lokasi lain (mis. `E-commerce-public-dataset/`), salin atau tautkan file-file tersebut ke dalam folder `data/`.

---

## Menjalankan Notebook Analisis

1. Buka file `Proyek_Analisis_Data.ipynb` di Jupyter / VS Code / Colab.
2. Jalankan seluruh sel dari atas sampai bawah secara berurutan:
   - **Import & Gathering Data**
   - **Assessing & Cleaning Data**
   - **Exploratory Data Analysis (EDA)**
   - **Visualization & Explanatory Analysis**
   - **Analisis Lanjutan (RFM & Geospatial)**
3. Di bagian akhir notebook, data agregat akan disimpan ke folder `dashboard/` (atau dapat digenerate ulang via `generate_data.py`).

---

## Menjalankan Dashboard Streamlit (Lokal)

### Opsi A – Dari root proyek

```bash
cd "Submission-Proyek Analisis Data"
streamlit run dashboard/dashboard.py
```

### Opsi B – Langsung dari folder dashboard

```bash
cd "Submission-Proyek Analisis Data/dashboard"
streamlit run dashboard.py
```

Dashboard akan tersedia di browser pada `http://localhost:8501`.

---

## Generate Ulang Data untuk Dashboard

Jika file CSV (`main_data.csv`, `category_data.csv`, `rfm_data.csv`) belum ada atau ingin direfresh:

```bash
cd "Submission-Proyek Analisis Data/dashboard"
python generate_data.py
```

Skrip ini akan:

- Memuat dataset mentah (orders, customers, order_items, reviews, payments, geolocation).
- Membuat agregasi:
  - **Per kota (dan per tahun):** total order, on-time delivery, rata-rata review score, **rata-rata AOV (avg_order_value)**, jumlah ulasan, koordinat lat/lng.
  - **Per kategori produk:** rata-rata review score, AOV, jumlah order (untuk referensi).
  - **Per pelanggan per tahun (RFM):** Recency, Frequency, Monetary, segmentasi (Champions, Potential Loyalists, At Risk, Hibernating, Others), serta state dan kota—agar dashboard dapat memfilter RFM berdasarkan tahun dan state.

---

## Deploy ke Streamlit Cloud

1. Push seluruh proyek ke GitHub (termasuk folder `dashboard/` dan dataset yang diperlukan).
2. Buka `https://share.streamlit.io` dan login menggunakan akun GitHub.
3. Klik **New app** lalu pilih:
   - Repository: repo proyek ini
   - Branch: `main`
   - **Main file path**: `dashboard/dashboard.py`
4. Klik **Deploy** dan tunggu proses selesai.
5. Setelah berhasil, salin URL aplikasi (misal: `https://nama-app.streamlit.app`) dan tempelkan ke file `url.txt`.

---

## Ringkasan Pertanyaan Bisnis & Insight

### 1. Volume Transaksi & Ketepatan Pengiriman per Kota

- **Pertanyaan:**  
  Kota mana di Brasil yang memiliki volume transaksi tertinggi, dan bagaimana korelasi antara jumlah order dengan persentase ketepatan pengiriman di kota tersebut selama 2017–2018?

- **Insight utama:**
  - Kota **São Paulo** memiliki volume transaksi tertinggi selama 2017–2018.
  - Ketepatan pengiriman di kota dengan volume besar relatif **tetap tinggi dan stabil**, menunjukkan proses logistik yang cukup matang.
  - Korelasi antara jumlah order dan ketepatan pengiriman secara umum **tidak negatif secara ekstrem**—volume tinggi tidak otomatis menurunkan performa pengiriman.

### 2. Review Score vs Average Order Value (AOV) berdasarkan Kota

- **Pertanyaan:**  
  Bagaimana hubungan antara review score dengan Average Order Value (AOV) berdasarkan kota selama 2017–2018?

- **Insight utama:**
  - Hubungan antara review score dan AOV **tidak linier**—kota dengan review score tinggi tidak selalu memiliki AOV tertinggi, dan sebaliknya.
  - Kepuasan pelanggan (review) dan nilai transaksi rata-rata (AOV) dipengaruhi oleh **faktor yang berbeda per wilayah**.
  - **Rekomendasi:** (1) Di kota dengan AOV tinggi, prioritaskan kualitas layanan agar review tetap baik. (2) Di kota dengan review tinggi tetapi AOV rendah, pertimbangkan upsell atau promosi untuk meningkatkan nilai order. (3) Gunakan analisis per kota (dan filter per state di dashboard) untuk menyesuaikan strategi pemasaran dan operasional per wilayah.

---

## Teknik Analisis Lanjutan

- **RFM Analysis**
  - Mengelompokkan pelanggan berdasarkan:
    - **Recency**: seberapa baru transaksi terakhir (dihitung per tahun).
    - **Frequency**: seberapa sering bertransaksi dalam tahun tersebut.
    - **Monetary**: total nilai transaksi dalam tahun tersebut.
  - Segmentasi utama: **Champions**, **Potential Loyalists**, **At Risk**, **Hibernating**, **Others**.
  - Di dashboard, RFM dapat difilter berdasarkan **tahun** dan **state** untuk analisis per wilayah dan periode.

- **Geospatial Analysis**
  - Menggunakan data geolokasi untuk memetakan:
    - Distribusi order per kota di seluruh Brasil.
    - **Ketepatan pengiriman** per kota.
    - **Rata-rata review score** per kota (direpresentasikan dengan warna marker pada peta).

---

## Informasi Pembuat

- **Nama:** M Fajrin Wirattama  
- **Email:** fajrinwirattama21@gmail.com  
- **ID Dicoding:** wirattama  
