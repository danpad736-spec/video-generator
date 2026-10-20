import os
import streamlit as st
from moviepy.editor import TextClip, AudioFileClip, CompositeVideoClip, ColorClip
from PIL import Image

st.set_page_config(page_title="Generator Video Pendek AI", page_icon="🎬", layout="centered")

st.title("🎬 Generator Video Pendek Otomatis")
st.write("Upload Voice Over (VO) dan masukkan teks, lalu biarkan aplikasi merakit video pendekmu (9:16)!")

# Bagian Input Pengguna
with st.form("video_form"):
    st.subheader("1. Masukkan Skrip Teks")
    video_text = st.text_area("Tulis teks/caption yang ingin muncul di video:", "Halo! Ini adalah contoh video pendek otomatis menggunakan Streamlit dan MoviePy.")
    
    st.subheader("2. Upload Voice Over (Audio)")
    audio_file = st.file_uploader("Pilih file audio (.mp3 atau .wav)", type=["mp3", "wav"])
    
    st.subheader("3. Pengaturan Visual")
    bg_color = st.color_picker("Pilih Warna Background", "#1e1e2f")
    text_color = st.color_picker("Pilih Warna Teks", "#ffffff")
    
    submit_btn = st.form_submit_button("🚀 Buat Video Sekarang")

if submit_btn:
    if not audio_file:
        st.warning("⚠️ Harap upload file Voice Over (audio) terlebih dahulu!")
    else:
        with st.spinner("Sedang merakit video... Mohon tunggu sebentar ya..."):
            try:
                # Simpan audio yang di-upload ke file sementara
                audio_path = "temp_audio.mp3"
                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                
                # Muat audio untuk mendeteksi durasinya
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                
                # Buat ukuran video vertikal (9:16 untuk TikTok/Reels)
                # Menggunakan resolusi 720x1280 agar proses render lebih cepat dan ringan di cloud
                w, h = 720, 1280
                
                # Konversi hex color (misal: #1e1e2f) ke RGB tuple
                bg_rgb = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                
                # Buat klip background warna solid
                background = ColorClip(size=(w, h), color=bg_rgb).set_duration(duration)
                
                # Buat klip teks (pastikan sistem support font dasar, atau biarkan default moviepy)
                txt_clip = TextClip(
                    video_text, 
                    fontsize=40, 
                    color=text_color, 
                    size=(w - 100, None), # Batasi lebar teks dengan margin kiri-kanan
                    method='caption',
                    align='center'
                ).set_duration(duration).set_position('center')
                
                # Gabungkan background, teks, dan audio
                video = CompositeVideoClip([background, txt_clip]).set_audio(audio_clip)
                video = video.set_duration(duration)
                
                # Render video ke file output MP4
                output_path = "output_video.mp4"
                video.write_videofile(
                    output_path, 
                    fps=24, 
                    codec='libx264', 
                    audio_codec='aac',
                    preset='ultrafast',
                    logger=None
                )
                
                st.success("🎉 Video berhasil dibuat!")
                
                # Tampilkan preview video dan tombol download
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Video MP4",
                        data=file,
                        file_name="video_pendek_hasil.mp4",
                        mime="video/mp4"
                    )
                
                # Bersihkan file sementara
                audio_clip.close()
                video.close()
                
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat membuat video: {e}")
                st.info("Catatan: Pastikan ImageMagick terkonfigurasi jika teks mengalami kendala render, atau gunakan teks singkat.")
