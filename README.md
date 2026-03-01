# Proyek Analisis Data: E-Commerce Public Dataset

Proyek ini menganalisis dataset E-Commerce Brasil untuk menjawab pertanyaan bisnis terkait:

- **Volume transaksi per kota dan ketepatan pengiriman**
- **Hubungan antara review score dengan Average Order Value (AOV) per kategori produk**

Selain itu, proyek dilengkapi **dashboard interaktif** berbasis Streamlit untuk menyajikan hasil analisis.

---

## Struktur Direktori

```text
submission/
├── dashboard/
│   ├── main_data.csv        # Agregasi kota (volume, on-time, review, geospatial)
│   ├── category_data.csv    # Agregasi kategori produk (review, AOV)
│   ├── rfm_data.csv         # Segmentasi pelanggan (RFM)
│   ├── dashboard.py         # Aplikasi Streamlit utama
│   └── generate_data.py     # Skrip generator data untuk dashboard
├── E-commerce-public-dataset/
│   └── E-Commerce Public Dataset/*.csv   # Dataset asli (orders, customers, dll.)
├── Proyek_Analisis_Data.ipynb            # Notebook analisis lengkap
├── requirements.txt
├── README.md
└── url.txt                               # URL dashboard Streamlit Cloud (setelah deploy)
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

Pastikan folder `E-commerce-public-dataset/E-Commerce Public Dataset/` berisi seluruh file CSV dataset publik E-Commerce.

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
  - **Per kota**: total order, on-time delivery, rata-rata review score, jumlah ulasan, koordinat lat/lng.
  - **Per kategori produk**: rata-rata review score, AOV, jumlah order.
  - **Per pelanggan (RFM)**: Recency, Frequency, Monetary, serta segmentasi (Champions, dll.).

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
  Kota mana di Brasil yang memiliki volume transaksi tertinggi, dan bagaimana korelasi antara jumlah order dengan persentase ketepatan pengiriman?

- **Insight utama:**
  - Kota **São Paulo** memiliki volume transaksi tertinggi selama 2017–2018.
  - Ketepatan pengiriman di kota dengan volume besar relatif **tetap tinggi dan stabil**, menunjukkan proses logistik yang cukup matang.
  - Korelasi antara jumlah order dan ketepatan pengiriman secara umum **tidak negatif secara ekstrem** (volume tinggi tidak otomatis menurunkan performa pengiriman).

### 2. Review Score vs Average Order Value (AOV) per Kategori

- **Pertanyaan:**  
  Apakah kategori produk dengan review score tertinggi juga memiliki AOV yang lebih tinggi dibandingkan kategori dengan review score rendah?

- **Insight utama:**
  - Kategori dengan **review score tinggi** tidak selalu memiliki **AOV tertinggi**.
  - Beberapa kategori dengan **AOV tinggi** justru memiliki review score yang **lebih moderat**, misalnya elektronik dan produk bernilai tinggi lainnya.
  - Strategi bisnis: fokuskan peningkatan pengalaman pelanggan pada kategori **high-AOV** untuk mengurangi risiko review negatif, dan pertahankan kualitas pada kategori dengan review tinggi.

---

## Teknik Analisis Lanjutan

- **RFM Analysis**
  - Mengelompokkan pelanggan berdasarkan:
    - **Recency**: seberapa baru transaksi terakhir.
    - **Frequency**: seberapa sering bertransaksi.
    - **Monetary**: total nilai transaksi.
  - Segmentasi utama:
    - **Champions**
    - **Potential Loyalists**
    - **At Risk**
    - **Hibernating**

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
