from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# =====================
# 🔧 Load ENV
# =====================
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

# =====================
# 🌐 Setup FastAPI
# =====================
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# 🔌 Supabase Client
# =====================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================
# 🔄 Fetch and Preprocess Data
# =====================
location_scaler = MinMaxScaler()
rating_review_scaler = MinMaxScaler()

def fetch_data():
    try:
        # Cek koneksi & ambil 1 row
        test_response = supabase.table("clinics").select("*").limit(1).execute()
        if test_response.data:
            msg = "Koneksi berhasil, data dari tabel 'clinics' ditemukan."
        else:
            msg = "Koneksi berhasil, tapi data dari tabel 'clinics' kosong."

        # Ambil data lengkap clinics
        response = supabase.table("clinics").select("*").execute()
        data = response.data
        df = pd.DataFrame(data)

        print(msg)
        print(f"Jumlah data clinics: {len(df)}")
        print("Kolom tersedia:", df.columns)
        print("Contoh data:", df.head())

        # Cek daftar tabel di schema public (perbaiki query)
        try:
            res = supabase.postgrest.from_("pg_catalog.pg_tables").select("tablename").eq("schemaname", "public").execute()
            tables = [t['tablename'] for t in res.data]
            print("Daftar tabel di schema 'public':", tables)
        except Exception as e2:
            print(f"Gagal mendapatkan daftar tabel: {e2}")

        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data dari Supabase: {e}")

def print_connection_info():
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Supabase Key: {SUPABASE_KEY[:8]}... (hidden for security)")

    try:
        response = supabase.table("clinics").select("*").limit(1).execute()
        if response.data:
            print("Koneksi ke tabel 'clinics' berhasil.")
            print(f"Contoh data: {response.data[0]}")
        else:
            print("Koneksi ke tabel 'clinics' berhasil, tapi data kosong.")
    except Exception as e:
        print(f"Gagal koneksi atau fetch data dari 'clinics': {e}")

    try:
        # Cek list tabel di schema public
        res = supabase.postgrest.from_("pg_tables").select("tablename").eq("schemaname", "public").execute()
        tables = [t['tablename'] for t in res.data]
        print("Daftar tabel di schema 'public':", tables)
    except Exception as e:
        print(f"Gagal mendapatkan daftar tabel: {e}")

# Panggil fungsi ini di awal program, misal setelah buat client
print_connection_info()


def preprocess_data(df: pd.DataFrame):
    required_cols = ['latitude', 'longitude', 'rating', 'review_count']
    if df.empty or not all(col in df.columns for col in required_cols):
        raise HTTPException(status_code=400, detail="Data tidak lengkap. Pastikan kolom latitude, longitude, rating, dan review_count tersedia.")

    try:
        location_scaled = location_scaler.fit_transform(df[['latitude', 'longitude']])
        rating_review_scaled = rating_review_scaler.fit_transform(df[['rating', 'review_count']])
        all_features_scaled = np.hstack([location_scaled, rating_review_scaled])

        weights = np.array([0.4, 0.4, 0.1, 0.1])
        weighted_features = all_features_scaled * weights
        return weighted_features
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kesalahan saat preprocessing: {e}")

# =====================
# 🔍 Endpoint Rekomendasi
# =====================
@app.get("/recommend")
def recommend(lat: float = Query(...), lon: float = Query(...), top_k: int = 5):
    df = fetch_data()
    features = preprocess_data(df)

    # Vektor user
    try:
        avg_rating = df['rating'].max()
        avg_review = df['review_count'].mean()
    except:
        raise HTTPException(status_code=400, detail="Kolom rating dan review_count tidak valid.")

    try:
        user_location_scaled = location_scaler.transform([[lat, lon]])
        user_rating_review_scaled = rating_review_scaler.transform([[avg_rating, avg_review]])
        user_vector = np.hstack([user_location_scaled, user_rating_review_scaled])[0]

        weights = np.array([0.4, 0.4, 0.1, 0.1])
        user_vector *= weights

        similarities = cosine_similarity([user_vector], features)[0]
        df['similarity'] = similarities

        top = df.sort_values(by='similarity', ascending=False).head(top_k)
        return top.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kesalahan saat menghitung rekomendasi: {e}")
