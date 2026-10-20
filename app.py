import os
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, VideoClip, CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip

st.set_page_config(page_title="AI Custom Video Generator", page_icon="🎬", layout="centered")

st.title("🎬 AI Video & Animation Generator with VO")
st.markdown("Upload Voice Over (.wav/.mp3), tulis instruksi atau kustomisasi animasi, dan rakit menjadi video pendek (9:16) secara otomatis!")

with st.form("video_generator_form"):
    st.subheader("1. 🎙️ Upload Voice Over (VO)")
    audio_file = st.file_uploader("Pilih file audio (.wav atau .mp3)", type=["mp3", "wav"])
    
    st.subheader("2. 📝 Teks Utama / Caption")
    video_text = st.text_area("Tulis teks yang ingin ditampilkan di video:", "Halo! Ini adalah video animasi otomatis yang disinkronkan dengan Voice Over.")
    
    st.subheader("3. 💻 Instruksi / Kode Kustom Animasi & Warna")
    st.markdown("Kamu bisa menuliskan instruksi gaya visual, atau parameter warna di sini:")
    
    col1, col2 = st.columns(2)
    with col1:
        bg_color = st.color_picker("Warna Background Utama", "#1e1e2f")
        animation_style = st.selectbox(
            "Pilih Efek Animasi Teks",
            ["Teks Diam di Tengah", "Efek Muncul Perlahan (Fade In)", "Teks Bergerak Naik (Scroll Up)"]
        )
    with col2:
        text_color = st.color_picker("Warna Teks", "#ffffff")
        font_size = st.slider("Ukuran Font", min_value=20, max_value=80, value=40)

    submit_btn = st.form_submit_button("🚀 Proses & Render Video Sekarang")

if submit_btn:
    if not audio_file:
        st.warning("⚠️ Harap upload file Voice Over (audio) terlebih dahulu!")
    else:
        with st.spinner("⏳ Sedang memproses audio, merakit animasi, dan merender video... Mohon tunggu ya..."):
            try:
                # Simpan audio sementara
                audio_path = "temp_audio.wav"
                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                
                # Load audio untuk ambil durasi
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                
                # Dimensi video vertikal 9:16 (TikTok/Reels)
                w, h = 720, 1280
                
                # Konversi warna HEX ke RGB tuple
                def hex_to_rgb(hex_str):
                    hex_str = hex_str.lstrip('#')
                    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
                
                bg_rgb = hex_to_rgb(bg_color)
                txt_rgb = hex_to_rgb(text_color)
                
                # Buat fungsi pembuatan frame video berdasarkan animasi yang dipilih
                def make_frame(t):
                    # Buat image kosong dengan warna background
                    img = Image.new("RGB", (w, h), color=bg_rgb)
                    draw = ImageDraw.Draw(img)
                    
                    # Pengaturan font dasar (menggunakan default PIL jika tidak ada font kustom)
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                    
                    # Logika posisi teks berdasarkan animasi
                    text_y = h // 2
                    if animation_style == "Efek Muncul Perlahan (Fade In)":
                        # Efek sederhana teks bergerak turun dikit
                        pass
                    elif animation_style == "Teks Bergerak Naik (Scroll Up)":
                        text_y = int((h // 2) - (t * 20)) % h
                    
                    # Format teks agar rapi (wrap sederhana)
                    max_chars_per_line = 25
                    words = video_text.split()
                    lines = []
                    current_line = ""
                    for word in words:
                        if len(current_line + " " + word) <= max_chars_per_line:
                            current_line += (" " + word) if current_line else word
                        else:
                            lines.append(current_line)
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    
                    # Gambar teks per baris ke tengah layar
                    total_text_height = len(lines) * (font_size + 10)
                    start_y = text_y - (total_text_height // 2)
                    
                    for i, line in enumerate(lines):
                        # Estimasi lebar teks untuk center alignment
                        bbox = draw.textbbox((0, 0), line, font=font)
                        text_w = bbox[2] - bbox[0]
                        text_x = (w - text_w) // 2
                        line_y = start_y + (i * (font_size + 10))
                        draw.text((text_x, line_y), line, fill=txt_rgb, font=font)
                        
                    return np.array(img)

                # Buat VideoClip dari fungsi frame dan gabungkan dengan audio
                animation_clip = VideoClip(make_frame, duration=duration)
                final_video = animation_clip.set_audio(audio_clip)
                
                # Render file output ke MP4
                output_path = "output_video_custom.mp4"
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec='libx264',
                    audio_codec='aac',
                    preset='ultrafast',
                    logger=None
                )
                
                st.success("🎉 Video animasi berhasil dibuat dan disinkronkan dengan VO!")
                st.video(output_path)
                
                # Tombol download
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Video MP4",
                        data=file,
                        file_name="hasil_video_ai.mp4",
                        mime="video/mp4"
                    )
                
                # Bersihkan memori klip
                audio_clip.close()
                final_video.close()
                
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat merender video: {e}")
