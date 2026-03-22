import streamlit as st
import pandas as pd
import io
import time
import os
from extractor import GeminiExtractor
from prompts import BCA_MODE_PROMPT, GENERAL_MODE_PROMPT

# ==========================================
# 1. KONFIGURASI & API KEY
# ==========================================
API_KEY = os.environ.get("GEMINI_API_KEY", "MASUKIN API KEY ENTE")

st.set_page_config(page_title="AI Data Extractor", page_icon="📑", layout="wide")

# Inisialisasi Session State
if 'all_results' not in st.session_state:
    st.session_state.all_results = []

# ==========================================
# 2. SIDEBAR: KONFIGURASI PROMPT & OUTPUT
# ==========================================
with st.sidebar:
    st.header("⚙️ Konfigurasi")

    # Pilih Mode
    mode = st.radio(
        "Pilih Mode Ekstraksi:",
        ["BCA Mode", "General"],
        horizontal=True
    )

    st.divider()

    # Edit Prompt
    st.subheader("📝 Edit Prompt")
    default_prompt = BCA_MODE_PROMPT if mode == "BCA Mode" else GENERAL_MODE_PROMPT
    custom_prompt = st.text_area(
        "Sesuaikan instruksi AI:",
        value=default_prompt,
        height=300,
        help="Instruksi ini akan dikirim ke AI untuk memandu ekstraksi data."
    )

    # Edit Kolom Output (Hanya untuk BCA Mode)
    st.subheader("📋 Kolom Output")
    if mode == "BCA Mode":
        default_cols = "Nama File, Tanggal, Keterangan, Mutasi DB, Mutasi CR, Saldo DB, Saldo CR"
        output_cols_str = st.text_input("Urutan kolom (pisahkan koma):", value=default_cols)
        output_cols = [c.strip() for c in output_cols_str.split(",")]
    else:
        st.info("Mode General akan menampilkan semua kolom yang ditemukan AI.")
        output_cols = None

# ==========================================
# 3. UI UTAMA
# ==========================================
st.title("📑 AI Data Extractor (Modular)")
st.markdown("Ekstrak data mutasi BCA atau struk umum ke CSV dengan kontrol penuh.")

# Upload File
uploaded_files = st.file_uploader(
    "Unggah file (JPG, PNG, PDF):",
    type=["jpg", "jpeg", "png", "pdf"],
    accept_multiple_files=True
)

# Tombol Reset
if st.session_state.all_results:
    if st.button("🗑️ Reset Data"):
        st.session_state.all_results = []
        st.rerun()

# ==========================================
# 4. PROSES EKSTRAKSI
# ==========================================
if uploaded_files:
    if st.button("🚀 MULAI EKSTRAKSI", width="stretch"):
        if API_KEY == "YOUR_API_KEY_HERE" and not os.environ.get("GEMINI_API_KEY"):
            st.error("API Key belum diatur! Silakan masukkan API Key di dalam kode.")
        else:
            # Inisialisasi Extractor
            extractor = GeminiExtractor(api_key=API_KEY)

            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, file in enumerate(uploaded_files):
                status_text.text(f"Memproses ({i+1}/{len(uploaded_files)}): {file.name}...")
                try:
                    file_bytes = file.getvalue()

                    # Panggil logic ekstraksi dari module extractor
                    results = extractor.extract_table(
                        file_bytes=file_bytes,
                        mime_type=file.type,
                        prompt=custom_prompt
                    )

                    # Tambahkan metadata nama file
                    for row in results:
                        row["Nama File"] = file.name
                        st.session_state.all_results.append(row)

                except Exception as e:
                    st.error(f"Error pada {file.name}: {str(e)}")

                progress_bar.progress((i + 1) / len(uploaded_files))
                time.sleep(0.1)

            status_text.text("✅ Selesai!")

# ==========================================
# 5. TAMPILKAN HASIL & DOWNLOAD
# ==========================================
if st.session_state.all_results:
    st.divider()
    st.subheader("📊 Hasil Ekstraksi")

    df = pd.DataFrame(st.session_state.all_results)

    # Reorder/Filter kolom jika dikonfigurasi
    if output_cols:
        # Pastikan kolom yang diminta ada di DataFrame
        existing_cols = [c for c in output_cols if c in df.columns]
        df = df[existing_cols]
    else:
        # Untuk General Mode, pastikan Nama File ada di depan
        if "Nama File" in df.columns:
            cols = ["Nama File"] + [c for c in df.columns if c != "Nama File"]
            df = df[cols]

    # Tampilkan Tabel
    st.dataframe(df, width="stretch")

    # Tombol Download
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv_buffer.getvalue(),
        file_name=f"ekstraksi_{mode.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        width="stretch"
    )

