"""app.py - aplikasi web Prioritas Poli Jantung (Streamlit).
Jalankan:  streamlit run app.py
"""
from pathlib import Path

import streamlit as st

from halaman_prediksi import tab_prediksi, tab_riwayat

st.set_page_config(page_title="Prioritas Poli Jantung", layout="wide",
                   initial_sidebar_state="collapsed")

NAMA_TAB = ["Beranda", "Prediksi", "Riwayat"]

# (inisial, nama, peran, tugas). Foto bisa ditambahkan nanti.
ANGGOTA = [
    ("AM", "Achmad Mauladi", "Koordinator, Pengembang data/model",
     "Unggah Drive Monitoring, Pipeline PyCaret, validasi silang, metrik, faktor berpengaruh, berkas model dan metrik.",
     "achmad"),
    ("ID", "Indah Dhiya Nabila H.", "Analis kasus dan rumusan masalah.",
     "analisis kebutuhan, etika data, rencana implementasi.",
     "indi"),
    ("SP", "Suci Pratiwi", "Desain UI/UX",
     "Perancangan desain dan prototipe awal.",
     "ciku"),
    ("AF", "A. Fahrul", "Perancang dan pengembang web",
     "Pengembangan website, antarmuka Streamlit, validasi input, riwayat prediksi, banner peringatan.",
     "fahrul"),
]

FOLDER_FOTO = Path(__file__).parent / "foto_pengembang"
EKSTENSI_FOTO = (".jpg", ".jpeg", ".png", ".webp")


@st.cache_data(show_spinner=False)
def _foto_uri(jalur, ubah):
    """Data URI foto, diperkecil agar halaman ringan.
    `ubah` (waktu ubah berkas) hanya kunci cache agar foto baru terbaca."""
    data = Path(jalur).read_bytes()
    tipe = {".png": "image/png", ".webp": "image/webp"}.get(
        Path(jalur).suffix.lower(), "image/jpeg")
    try:
        from io import BytesIO
        from PIL import Image, ImageOps
        gambar = ImageOps.exif_transpose(Image.open(BytesIO(data))).convert("RGB")
        gambar = ImageOps.fit(gambar, (240, 240))
        buf = BytesIO()
        gambar.save(buf, "JPEG", quality=88)
        data, tipe = buf.getvalue(), "image/jpeg"
    except Exception:   # gagal diperkecil: pakai berkas apa adanya
        pass
    import base64
    return f"data:{tipe};base64," + base64.b64encode(data).decode()


def _cari_foto(dasar):
    if not FOLDER_FOTO.is_dir():
        return None
    for f in FOLDER_FOTO.iterdir():
        if f.stem.lower() == dasar.lower() and f.suffix.lower() in EKSTENSI_FOTO:
            return f
    return None


def _avatar(inisial, nama, dasar):
    """Foto bila ada, kalau tidak inisial."""
    f = _cari_foto(dasar)
    if f:
        try:
            uri = _foto_uri(str(f), f.stat().st_mtime)
            return f'<div class="av"><img src="{uri}" alt="Foto {nama}"></div>'
        except Exception:
            pass
    return f'<div class="av" role="img" aria-label="Foto {nama}">{inisial}</div>'


def html(teks):
    """Gabungkan HTML jadi satu baris tanpa baris kosong, supaya tidak
    dibaca sebagai markdown (baris kosong memutus blok HTML)."""
    return " ".join(b.strip() for b in teks.splitlines() if b.strip())


def kartu(judul, isi, kelas=""):
    return f'<div class="kartu {kelas}"><h2>{judul}</h2>{isi}</div>'


CARA_PAKAI = html("""
<ol class="steps">
<li><b>Buka tab Prediksi</b> dan isi 13 data klinis pasien. Semua isian wajib
kecuali ca dan thal, dan nilai yang tidak masuk akal ditolak dengan pesan
yang jelas.</li>
<li><b>Tekan Prediksi.</b> Hasil muncul di samping form.</li>
<li><b>Baca hasilnya:</b> peluang ada penyakit jantung, kategori risiko
(rendah, sedang, tinggi), dan faktor yang paling berpengaruh pada model.</li>
<li><b>Lihat Riwayat</b> untuk memastikan prediksi tadi tersimpan.</li>
</ol>""")

ATURAN = html("""
<ul class="lim">
<li><b>Hasil bukan diagnosis</b> dan tidak boleh dipakai langsung untuk
keputusan klinis. Keputusan tetap pada tenaga kesehatan.</li>
<li><b>Hanya data fiktif.</b> Isian nama pasien hanya untuk nama rekaan atau
kode (misalnya Pasien A). Jangan memasukkan data, nama, atau nomor identitas
pasien sungguhan.</li>
<li>Nilai di luar rentang data latih membuat prediksi kurang dapat
diandalkan, dan aplikasi akan memberi peringatan.</li>
<li>Bila ca atau thal belum diperiksa, aplikasi memakai model yang lebih
sederhana dan hasilnya kurang akurat.</li>
<li>Model dilatih pada 303 pasien dari satu rumah sakit, jadi hasilnya bisa
berbeda pada populasi lain.</li>
<li>Hasil dipakai sebagai bahan pertimbangan prioritas, bukan pengganti
pemeriksaan.</li>
</ul>""")

FAKTA = html("""
<dl class="facts">
<div><dt>Pengguna</dt><dd>Tenaga kesehatan poli jantung</dd></div>
<div><dt>Data latih</dt><dd>UCI Heart Disease (Cleveland), 303 pasien</dd></div>
<div><dt>Model</dt><dd>Pohon keputusan</dd></div>
<div><dt>Keluaran</dt><dd>Peluang, kategori risiko, faktor berpengaruh</dd></div>
</dl>""")

TIM = kartu(
    "Tim pengembang",
    '<p class="catatan">Kelompok Kapita Selekta, Jurusan Teknik Informatika '
    'dan Komputer.</p><div class="team">'
    + "".join(
        f'<div class="mem">{_avatar(ini, nama, dasar)}<b>{nama}</b>'
        f'<span class="role">{peran}</span><p>{tugas}</p></div>'
        for ini, nama, peran, tugas, dasar in ANGGOTA)
    + "</div>")


def muat_gaya():
    css = (Path(__file__).parent / "gaya.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def buka_tab(nama):
    """Dipanggil dari on_click tombol: memindahkan ke tab lain.
    Nilai tab hanya boleh diubah lewat callback seperti ini."""
    st.session_state["tab_aktif"] = nama


def banner():
    with st.container(key="banner"):
        st.markdown(html("""
            <div class="peringatan" role="alert"><span>
            <strong>Hasil ini bukan diagnosis.</strong>
            Jangan dipakai langsung untuk keputusan klinis. Aplikasi ini
            prototipe akademik, dan keputusan tetap pada tenaga kesehatan.
            </span></div>"""), unsafe_allow_html=True)


def tab_beranda():
    st.markdown(html("""
        <div class="hero">
        <h1>Bantu memprioritaskan pasien poli jantung</h1>
        <p class="lead">Aplikasi ini memperkirakan risiko penyakit jantung dari
        13 data klinis dasar memakai model pohon keputusan. Tujuannya membantu
        menentukan pasien yang lebih dulu perlu pemeriksaan lanjut ketika
        antrean panjang.</p>
        </div>"""), unsafe_allow_html=True)

    with st.container(horizontal=True, gap="small", key="cta"):
        st.button("Mulai prediksi sekarang", type="primary", key="mulai_atas",
                  on_click=buka_tab, args=("Prediksi",))

    st.markdown('<div class="cols">'
                + kartu("Cara pakai", CARA_PAKAI)
                + kartu("Aturan penggunaan", ATURAN, "rule")
                + "</div>", unsafe_allow_html=True)

    with st.container(key="kartu_tentang"):
        st.markdown('<h2 class="kh">Tentang aplikasi</h2>' + FAKTA,
                    unsafe_allow_html=True)
        st.button("Mulai prediksi sekarang", type="primary", key="mulai_kartu",
                  on_click=buka_tab, args=("Prediksi",))

    st.markdown(TIM, unsafe_allow_html=True)


def tab_model():
    st.title("Tentang model")
    st.info("Metrik dan evaluasi model akan dibuat pada langkah berikutnya.")


def main():
    muat_gaya()
    banner()
    # Tab awal = Beranda (tab pertama). Navigasi lewat st.session_state["tab_aktif"].
    tabs = st.tabs(NAMA_TAB, key="tab_aktif", on_change="rerun")
    with tabs[0]:
        tab_beranda()
    with tabs[1]:
        tab_prediksi()
    with tabs[2]:
        tab_riwayat()


main()