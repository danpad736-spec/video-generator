import os
import streamlit as st
from moviepy.editor import AudioFileClip, ColorClip, CompositeVideoClip, TextClip
from PIL import Image

st.set_page_config(page_title="Generator Video Pendek AI", page_icon="🎬", layout="centered")

st.title("🎬 Generator Video Pendek Otomatis")
st.write("Upload Voice Over (VO) dan masukkan teks, lalu biarkan aplikasi merakit video pendekmu (9:16)!")

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
                audio_path = "temp_audio.mp3"
                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                
                w, h = 720, 1280
                bg_rgb = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                
                background = ColorClip(size=(w, h), color=bg_rgb).set_duration(duration)
                
                # Menggunakan penanganan aman untuk TextClip
                try:
                    txt_clip = TextClip(
                        video_text, 
                        fontsize=40, 
                        color=text_color, 
                        size=(w - 100, None),
                        method='caption',
                        align='center'
                    ).set_duration(duration).set_position('center')
                    video = CompositeVideoClip([background, txt_clip]).set_audio(audio_clip)
                except Exception:
                    # Fallback jika ImageMagick/TextClip bermasalah di cloud
                    video = background.set_audio(audio_clip)
                    st.info("ℹ️ Video dibuat dengan background dan audio (teks dilewati karena batasan sistem server cloud).")

                video = video.set_duration(duration)
                
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
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Video MP4",
                        data=file,
                        file_name="video_pendek_hasil.mp4",
                        mime="video/mp4"
                    )
                
                audio_clip.close()
                video.close()
                
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat membuat video: {e}")
