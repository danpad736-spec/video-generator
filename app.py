import os
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, VideoClip, CompositeAudioClip, AudioClip

st.set_page_config(page_title="AI Custom Video Generator Pro", page_icon="🎬", layout="centered")

st.title("🎬 AI Video Generator Pro (Multi-Shape Logo, SFX, & Sync VO)")
st.markdown("Upload Voice Over, pilih bentuk logo geometris berbasis kode, atur teks sinkron per fase, dan render otomatis!")

with st.form("video_form"):
    st.subheader("1. 🎙️ Upload Voice Over (VO)")
    audio_file = st.file_uploader("Pilih file audio (.wav atau .mp3)", type=["mp3", "wav"])
    
    st.subheader("2. 📝 Skrip Teks per Fase Waktu (Sinkronisasi)")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        text_fase_1 = st.text_input("Fase Awal (0s - 2s):", "Tahukah kamu?")
        text_fase_2 = st.text_input("Fase Kedua (2s - 5s):", "Otak manusia menghasilkan listrik")
    with col_t2:
        text_fase_3 = st.text_input("Fase Ketiga (5s - 8s):", "yang cukup untuk menyalakan lampu kecil!")
        text_fase_4 = st.text_input("Fase Akhir (8s - Selesai):", "Pintar banget ya?")
        
    st.subheader("3. 🎨 Logo Berbasis Kode & Visual")
    col1, col2 = st.columns(2)
    with col1:
        bg_color = st.color_picker("Warna Background", "#1e1e2f")
        logo_text = st.text_input("Inisial/Teks Logo:", "AI")
        logo_shape = st.selectbox(
            "Pilih Bentuk Logo Geometris", 
            ["Lingkaran (Circle)", "Kotak (Rectangle)", "Segitiga (Triangle)", "Bintang (Star / Polygon)"]
        )
    with col2:
        text_color = st.color_picker("Warna Teks Utama", "#00ffcc")
        logo_color = st.color_picker("Warna Bentuk Logo", "#ff5733")
        enable_sfx = st.checkbox("Aktifkan Efek Suara SFX (Tone di awal)", value=True)
        
    font_size = st.slider("Ukuran Font Teks", min_value=20, max_value=80, value=40)
    
    submit_btn = st.form_submit_button("🚀 Render Video Lengkap (Logo + SFX + Sync)")

if submit_btn:
    if not audio_file:
        st.warning("⚠️ Harap upload file Voice Over terlebih dahulu!")
    else:
        with st.spinner("⏳ Merakit bentuk logo, teks sinkron, efek suara, dan merender video..."):
            try:
                # Simpan audio utama
                audio_path = "temp_audio.wav"
                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                
                # Tambahkan Efek Suara (SFX) berbasis kode jika dicentang (misal: nada pendek di detik ke-0)
                if enable_sfx:
                    # Buat suara 'beep' pendek berdurasi 0.3 detik menggunakan formula matematika numpy
                    def sfx_make_frame(t):
                        # Nada frekuensi 440 Hz (A4) dengan fade out
                        val = np.sin(440 * 2 * np.pi * t) * max(0, (0.3 - t) / 0.3)
                        return np.array([val, val]).T
                    
                    sfx_clip = AudioClip(sfx_make_frame, duration=0.3).volumetrics(0.2)
                    # Gabungkan audio utama dengan SFX di detik ke-0
                    final_audio = CompositeAudioClip([audio_clip, sfx_clip.set_start(0)])
                else:
                    final_audio = audio_clip
                
                w, h = 720, 1280 # Resolusi vertikal 9:16
                
                def hex_to_rgb(hex_str):
                    hex_str = hex_str.lstrip('#')
                    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
                
                bg_rgb = hex_to_rgb(bg_color)
                txt_rgb = hex_to_rgb(text_color)
                logo_rgb = hex_to_rgb(logo_color)
                
                # Fungsi pembuat frame video per detik (t)
                def make_frame(t):
                    img = Image.new("RGB", (w, h), color=bg_rgb)
                    draw = ImageDraw.Draw(img)
                    
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                        font_logo = ImageFont.truetype("arial.ttf", 32)
                    except:
                        font = ImageFont.load_default()
                        font_logo = ImageFont.load_default()
                    
                    # --- 1. MENGGAMBAR BERBAGAI BENTUK LOGO BERBASIS KODE ---
                    cx, cy = w // 2, 220
                    size = 70
                    
                    if "Lingkaran" in logo_shape:
                        draw.ellipse([cx - size, cy - size, cx + size, cy + size], fill=logo_rgb)
                    elif "Kotak" in logo_shape:
                        draw.rectangle([cx - size, cy - size, cx + size, cy + size], fill=logo_rgb)
                    elif "Segitiga" in logo_shape:
                        points = [(cx, cy - size), (cx - size, cy + size), (cx + size, cy + size)]
                        draw.polygon(points, fill=logo_rgb)
                    elif "Bintang" in logo_shape:
                        # Membuat bentuk poligon bintang bersudut banyak via kode matematika
                        points = []
                        for i in range(10):
                            r = size if i % 2 == 0 else size // 2
                            angle = i * np.pi / 5 - np.pi / 2
                            points.append((cx + int(r * np.cos(angle)), cy + int(r * np.sin(angle))))
                        draw.polygon(points, fill=logo_rgb)
                    
                    # Tulis inisial di tengah logo
                    bbox_logo = draw.textbbox((0, 0), logo_text, font=font_logo)
                    lw = bbox_logo[2] - bbox_logo[0]
                    lh = bbox_logo[3] - bbox_logo[1]
                    draw.text((cx - lw // 2, cy - lh // 2), logo_text, fill=(255, 255, 255), font=font_logo)
                    
                    # --- 2. SINKRONISASI TEKS UTAMA PER FASE WAKTU ---
                    if t < 2.0:
                        active_text = text_fase_1
                    elif 2.0 <= t < 5.0:
                        active_text = text_fase_2
                    elif 5.0 <= t < 8.0:
                        active_text = text_fase_3
                    else:
                        active_text = text_fase_4
                    
                    # Efek animasi melayang tipis
                    offset_y = int(np.sin(t * 3) * 8)
                    text_y = (h // 2) + offset_y
                    
                    bbox = draw.textbbox((0, 0), active_text, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_x = (w - text_w) // 2
                    
                    draw.text((text_x, text_y), active_text, fill=txt_rgb, font=font)
                    return np.array(img)

                animation_clip = VideoClip(make_frame, duration=duration)
                final_video = animation_clip.set_audio(final_audio)
                
                output_path = "output_video_pro.mp4"
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec='libx264',
                    audio_codec='aac',
                    preset='ultrafast',
                    logger=None
                )
                
                st.success("🎉 Video Pro dengan Berbagai Pilihan Bentuk Logo, SFX, & Sync VO Berhasil Dibuat!")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Video MP4 Pro",
                        data=file,
                        file_name="video_pro_hasil.mp4",
                        mime="video/mp4"
                    )
                
                audio_clip.close()
                final_video.close()
                
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")
