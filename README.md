# API Rekomendasi Klinik Psikologi dengan FastAPI dan Supabase

Proyek ini menyediakan API rekomendasi untuk klinik psikologi di Indonesia. API ini memungkinkan pengguna untuk menemukan klinik terdekat yang relevan berdasarkan lokasi (garis lintang dan garis bujur) serta mempertimbangkan rating dan jumlah ulasan klinik. Data klinik disimpan dan diambil dari Supabase.

## Daftar Isi

- [Gambaran Umum Proyek](#gambaran-umum-proyek)
- [Fitur Utama](#fitur-utama)
- [Model Rekomendasi](#model-rekomendasi)
- [Pengaturan Lingkungan (.env)](#pengaturan-lingkungan-env)
- [Instalasi dan Penggunaan](#instalasi-dan-penggunaan)
- [Endpoints API](#endpoints-api)
- [Struktur Proyek](#struktur-proyek)
- [Dependensi](#dependensi)

## Gambaran Umum Proyek

API ini dirancang untuk membantu pengguna menemukan klinik psikologi yang paling sesuai dengan kebutuhan mereka. Dengan mengirimkan lokasi pengguna, API akan mengembalikan daftar klinik yang direkomendasikan, diurutkan berdasarkan kemiripan lokasi serta rating dan jumlah ulasan. Data klinik dikelola dan diakses melalui Supabase, sebuah platform *backend-as-a-service*.

## Fitur Utama

* **API Rekomendasi**: Menyediakan *endpoint* API untuk mendapatkan rekomendasi klinik.
* **Integrasi Supabase**: Mengambil data klinik langsung dari database Supabase.
* **Faktor Lokasi**: Menggunakan garis lintang dan garis bujur pengguna untuk menemukan klinik terdekat.
* **Faktor Kualitas**: Menggabungkan rating dan jumlah ulasan klinik dalam logika rekomendasi.
* **Normalisasi Fitur**: Menggunakan `MinMaxScaler` untuk menormalisasi fitur lokasi serta rating dan ulasan.
* **Kemiripan Kosinus**: Menghitung kemiripan antara preferensi pengguna dan klinik menggunakan kemiripan kosinus.
* **Pengelolaan CORS**: Mengizinkan permintaan *cross-origin* untuk integrasi yang mudah dengan aplikasi *frontend*.
* **Manajemen Variabel Lingkungan**: Menggunakan file `.env` untuk mengelola *credentials* Supabase dengan aman.

## Model Rekomendasi

Model rekomendasi berbasis konten ini menggunakan pendekatan kemiripan fitur. Fitur-fitur yang dipertimbangkan adalah:

* **Garis Lintang (latitude)**
* **Garis Bujur (longitude)**
* **Rating**
* **Jumlah Ulasan (review_count)**

Fitur-fitur ini dinormalisasi menggunakan `MinMaxScaler` dan kemudian digabungkan dengan bobot tertentu (40% untuk garis lintang, 40% untuk garis bujur, 10% untuk rating, dan 10% untuk jumlah ulasan). Untuk input pengguna, rating dan jumlah ulasan diasumsikan sebagai nilai maksimum rating dan rata-rata jumlah ulasan dari seluruh dataset, yang merepresentasikan preferensi untuk klinik berkualitas tinggi secara umum.

Kemiripan antara vektor pengguna dan vektor klinik dihitung menggunakan **kemiripan kosinus**. Klinik dengan skor kemiripan tertinggi akan direkomendasikan.

## Pengaturan Lingkungan (.env)

Sebelum menjalankan aplikasi, Anda perlu membuat file `.env` di direktori *root* proyek Anda dan menambahkan *credentials* Supabase Anda:

```

SUPABASE\_URL="[https://your-supabase-url.supabase.co](https://www.google.com/search?q=https://your-supabase-url.supabase.co)"
SUPABASE\_KEY="your-supabase-anon-key"

````

Pastikan untuk mengganti `your-supabase-url` dan `your-supabase-anon-key` dengan *credentials* Supabase Anda yang sebenarnya.

## Instalasi dan Penggunaan

Untuk menjalankan API ini secara lokal di komputer Anda:

1.  **Kloning repositori:**
    ```bash
    git clone <URL_REPOSITORI_ANDA>
    cd <nama_folder_repositori>
    ```

2.  **Buat dan aktifkan lingkungan virtual (disarankan):**
    ```bash
    python -m venv venv
    # Di Windows
    .\venv\Scripts\activate
    # Di macOS/Linux
    source venv/bin/activate
    ```

3.  **Instal dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan aplikasi FastAPI:**
    ```bash
    uvicorn main:app --reload
    ```

    API akan berjalan di `http://127.0.0.1:8000`. Anda dapat mengakses dokumentasi API interaktif di `http://127.0.0.1:8000/docs` atau `http://127.0.0.1:8000/redoc`.

## Endpoints API

### `GET /recommend`

Mengembalikan daftar klinik psikologi yang direkomendasikan berdasarkan lokasi pengguna.

**Parameter Kueri:**

* `lat` (float, **wajib**): Garis lintang (latitude) lokasi pengguna.
* `lon` (float, **wajib**): Garis bujur (longitude) lokasi pengguna.
* `top_k` (int, opsional, default: 5): Jumlah rekomendasi teratas yang akan dikembalikan.

**Contoh Permintaan:**

````

GET [http://127.0.0.1:8000/recommend?lat=-6.2088\&lon=106.8456\&top\_k=3](https://www.google.com/search?q=http://127.0.0.1:8000/recommend%3Flat%3D-6.2088%26lon%3D106.8456%26top_k%3D3)

````

**Contoh Respons (JSON):**

```json
[
  {
    "id": "e63beac6-3dcf-4862-8d51-5f745b2c6465",
    "name": "Darunnisa Psychological Services",
    "category": "Psychologist",
    "addres_full": "darunnisa psychological services, jl. cibiru h...",
    "website": "[https://www.instagram.com/darunnisa](https://www.instagram.com/darunnisa)",
    "phone_number": "+62 819-1008-8911",
    "rating": 5.0,
    "review_count": 12.0,
    "longitude": 107.722601,
    "latitude": -6.936937,
    "provinsi": "Jawa Barat",
    "similarity": 0.999989
  },
  {
    "id": "24b21fbf-9f8f-4248-bf01-2649ea27c8e3",
    "name": "Poli Psikologi, Rumah Sakit Harapan Keluarga (Anahata)",
    "category": "Psychologist",
    "addres_full": "poli psikologi, rumah sakit harapan keluarga (...",
    "website": "tidak diketahui",
    "phone_number": "+62 821-3868-1319",
    "rating": 5.0,
    "review_count": 5.0,
    "longitude": 107.762887,
    "latitude": -6.949763,
    "provinsi": "Jawa Barat",
    "similarity": 0.999981
  },
  {
    "id": "44598d23-1cd8-4d8b-ac42-1f70badec471",
    "name": "Insight Psikotes",
    "category": "Psychologist",
    "addres_full": "insight psikotes, jl. antanila i no.9, cisaran...",
    "website": "tidak diketahui",
    "phone_number": "+62 853-2050-3038",
    "rating": 5.0,
    "review_count": 2.0,
    "longitude": 107.679313,
    "latitude": -6.935846,
    "provinsi": "Jawa Barat",
    "similarity": 0.999980
  }
]
````

## Struktur Proyek

```
.
├── main.py             # Kode utama aplikasi FastAPI dan logika rekomendasi.
├── requirements.txt    # Daftar dependensi Python.
├── .env                # File untuk variabel lingkungan (SUPABASE_URL, SUPABASE_KEY).
└── README.md           # File ini.
```

## Dependensi

Proyek ini membutuhkan pustaka Python berikut, yang dapat ditemukan di `requirements.txt`:

  * `fastapi`
  * `uvicorn`
  * `pandas`
  * `numpy`
  * `scikit-learn`
  * `python-dotenv`
  * `supabase`
