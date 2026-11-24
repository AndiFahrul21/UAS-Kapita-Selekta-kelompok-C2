"""halaman_prediksi.py - isi tab Prediksi dan tab Riwayat."""
from html import escape

import streamlit as st

import riwayat
from bidang import CONTOH, GRUP, LABEL
from prediksi import (BATAS_RENDAH, BATAS_TINGGI, KOLOM_13,
                      muat_metrik, prediksi, validasi)

# Jalur keputusan tiap ujung pohon model v2, dicari lewat (pasien latih, sakit).
# Sesuai aturan pohon di models/metrics.json. Bila model dilatih ulang dan
# jumlahnya berubah, jalur tidak ditampilkan (tidak salah label).
JALUR = {
    (109, 84): "Uji thalium bukan normal (cacat tetap atau cacat reversibel).",
    (96, 10): "Uji thalium normal dan tidak ada pembuluh darah utama yang "
              "terlihat (0).",
    (26, 16): "Uji thalium normal, pembuluh darah utama 1 sampai 3, dan jenis "
              "nyeri dada bukan non-angina.",
    (10, 0): "Uji thalium normal, pembuluh darah utama 1 sampai 3, dan jenis "
             "nyeri dada non-angina.",
}                


def _html(teks):
    """Satukan HTML jadi satu baris (baris kosong memutus blok HTML)."""
    return " ".join(b.strip() for b in teks.splitlines() if b.strip())


def _pc(x, d=1):
    return f"{x * 100:.{d}f}".replace(".", ",") + "%"


def _buka_tab(nama):
    st.session_state["tab_aktif"] = nama


# ---------- state dan tombol bantu ----------
def _isi_contoh():
    for k in KOLOM_13:
        st.session_state[f"f_{k}"] = CONTOH[k]
    st.session_state["f_nama"] = "Pasien contoh"
    st.session_state["galat"] = {}


def _kosongkan():
    for k in KOLOM_13:
        st.session_state[f"f_{k}"] = None
    st.session_state["f_nama"] = ""
    st.session_state["galat"] = {}
    st.session_state["hasil_terakhir"] = None
    st.session_state["kesalahan"] = None


def _ambil_data():
    data = {}
    for k in KOLOM_13:
        data[k] = st.session_state.get(f"f_{k}")
    return data


# ---------- satu isian form ----------
def _bidang(f, galat):
    kunci = f"f_{f['id']}"
    if f["jenis"] == "angka":
        st.number_input(f["label"], value=None, step=f["step"],
                        format=f["format"], key=kunci, placeholder="Isi angka")
    elif f["jenis"] == "teks":
        st.text_input(f["label"], key=kunci, max_chars=60,
                      placeholder="Misalnya: Ajii")
    else:
        nama = dict(f["pilihan"])
        opsi = [k for k, _ in f["pilihan"]]
        if f["jenis"] == "radio":
            st.radio(f["label"], opsi, format_func=nama.get, index=None,
                     horizontal=True, key=kunci)
        else:
            st.selectbox(f["label"], opsi, format_func=nama.get, index=None,
                         placeholder="Pilih", key=kunci)
    if f.get("bantuan"):
        st.caption(f["bantuan"])
    if f["id"] in galat:
        st.markdown(f'<span class="err" role="alert">{galat[f["id"]]}</span>',
                    unsafe_allow_html=True)


# ---------- panel hasil ----------
def _panel(metrik):
    st.markdown('<h2 class="kh">Hasil prediksi</h2>', unsafe_allow_html=True)
    if st.session_state.get("kesalahan"):
        st.error(st.session_state["kesalahan"])
        return
    akhir = st.session_state.get("hasil_terakhir")
    if not akhir:
        st.markdown('<p class="empty">Hasil muncul di sini setelah semua '
                    'isian valid dan Anda menekan Prediksi.</p>',
                    unsafe_allow_html=True)
        return

    h = akhir["hasil"]
    p = h["peluang"]
    m = metrik[h["model"]]
    nama_html = escape(akhir.get("nama", ""))   # escape: nama diketik pengguna
    label = h["label"]
    kelas = {"rendah": "low", "sedang": "mid", "tinggi": "high"}[h["kategori"]]
    w1 = BATAS_RENDAH * 100
    w2 = (BATAS_TINGGI - BATAS_RENDAH) * 100
    w3 = 100 - w1 - w2
    pin = p * 100

    ujung = ""
    if h["ujung"]:
        u = h["ujung"]
        ujung = (f'<p class="ujung">{u["sakit"]} dari {u["n"]} pasien latih '
                 f'di kelompok ini sakit.</p>')
    catatan_model = (f'<p class="extra">{h["catatan_model"]}</p>'
                     if h["catatan_model"] else "")
    luar = ""
    if h["di_luar_rentang"]:
        nama = ", ".join(LABEL[k] for k in h["di_luar_rentang"])
        luar = (f'<p class="extra">Nilai {nama} berada di luar rentang data '
                f'latih. Prediksi pada nilai ini kurang dapat diandalkan.</p>')

    imp = [(k, v) for k, v in m["importance"].items() if v > 0][:7]
    maks = imp[0][1] or 1
    batang = "".join(
        f'<div class="bar"><span>{LABEL[k]}</span>'
        f'<i style="width:{v / maks * 100:.0f}%"></i>'
        f'<b>{round(v * 100)}%</b></div>' for k, v in imp)

    uji, cv = m["uji_ambang_0_5"], m["validasi_silang"]
    n_uji = m["data"]["n_uji"]
    sen, spe = _pc(uji["sensitivitas"]), _pc(uji["spesifisitas"])
    cv_sen = _pc(cv["sensitivitas"]["rata2"])
    cv_spe = _pc(cv["spesifisitas"]["rata2"])
    peringatan_rendah = ""
    if h["kategori"] == "rendah":
        lewat = _pc(1 - uji["sensitivitas"], 0)
        peringatan_rendah = (
            f'<p class="extra">Risiko rendah bukan berarti aman. Pada data '
            f'uji, model melewatkan sekitar {lewat} pasien sakit.</p>')
    tersimpan = (f"Tersimpan ke Riwayat ({riwayat.jumlah()} prediksi)."
                 if akhir["tersimpan"] else
                 "Prediksi tidak dapat disimpan ke Riwayat (berkas tidak "
                 "bisa ditulis).")

    st.markdown(_html(f"""
        <p class="catatan" style="margin:0 0 6px"><b>Pasien:</b> {nama_html}</p>
        <p class="catatan" style="margin:0">Perkiraan peluang ada penyakit jantung</p>
        <p class="pct">{_pc(p)}</p>
        <p class="cat {kelas}">{label}</p>
        <div class="track" aria-hidden="true">
          <span class="s1" style="width:{w1}%"></span>
          <span class="s2" style="width:{w2}%"></span>
          <span class="s3" style="width:{w3}%"></span>
          <i class="pin" style="left:{pin}%"></i>
        </div>
        <div class="scale" aria-hidden="true">
          <span style="width:{w1}%">Rendah</span>
          <span style="width:{w2}%">Sedang</span>
          <span style="width:{w3}%">Tinggi</span>
        </div>
        {ujung}{peringatan_rendah}{catatan_model}{luar}
        <p class="note">Gunakan sebagai bahan pertimbangan prioritas saja.
        Batas kategori (40% dan 65%) ditentukan dari ujung pohon pada data
        latih, bukan standar klinis.</p>
        <hr class="pisah">
        <p class="sub">Faktor paling berpengaruh pada model</p>
        <div class="bars">{batang}</div>
        <p class="note">Faktor yang paling sering dipakai pohon untuk memisahkan
        pasien pada data latih. Ini korelasi, bukan sebab-akibat, dan tidak
        menunjukkan arah pengaruh. Faktor ini sama untuk semua pasien, bukan
        alasan khusus pasien ini.</p>
        <p class="trust"><b>Kinerja model secara keseluruhan, sama untuk semua
        pasien dan bukan khusus pasien ini.</b> Pada data uji ({n_uji}
        pasien), model mendeteksi {sen} pasien sakit dan mengenali {spe}
        pasien sehat. Pada validasi silang angkanya {cv_sen} dan
        {cv_spe}.</p>
        """), unsafe_allow_html=True)
    st.markdown(f'<p class="note">{tersimpan}</p>', unsafe_allow_html=True)


# ---------- proses tombol Prediksi ----------
def _proses(metrik):
    data = _ambil_data()
    galat = validasi(data)
    st.session_state["galat"] = galat
    st.session_state["kesalahan"] = None
    st.session_state["hasil_terakhir"] = None
    if not galat:
        try:
            hasil = prediksi(data, metrik)
        except FileNotFoundError as e:
            st.session_state["kesalahan"] = str(e)
        except Exception as e:   # aplikasi tidak boleh berhenti
            st.session_state["kesalahan"] = f"Prediksi gagal: {e}"
        else:
            nama = (st.session_state.get("f_nama") or "").strip() or "Tanpa nama"
            ok = True
            try:
                riwayat.simpan(data, hasil, nama)
            except OSError:
                ok = False
            st.session_state["hasil_terakhir"] = {
                "data": data, "hasil": hasil, "tersimpan": ok, "nama": nama}
    st.rerun()


# ---------- tab Prediksi ----------
def tab_prediksi():
    st.title("Prediksi risiko penyakit jantung")
    st.markdown(
        '<p class="lead">Alat bantu prioritas untuk poli jantung. Isi data '
        'klinis pasien fiktif, lalu tekan Prediksi untuk melihat perkiraan '
        'risiko dan faktor yang paling berpengaruh.</p>',
        unsafe_allow_html=True)
    try:
        metrik = muat_metrik()
    except FileNotFoundError as e:
        st.error(str(e))
        return

    galat = st.session_state.get("galat", {})
    kiri, kanan = st.columns([1.3, 1], gap="large")

    with kiri:
        with st.form("form_prediksi", border=False):
            for i, (judul, daftar) in enumerate(GRUP):
                with st.container(key=f"grp_{i}"):
                    st.markdown(f'<span class="legend">{judul}</span>',
                                unsafe_allow_html=True)
                    kolom = st.columns(2)
                    for j, f in enumerate(daftar):
                        with kolom[j % 2]:
                            _bidang(f, galat)
            if galat:
                st.markdown(
                    f'<p class="sum" role="alert">Ada {len(galat)} isian yang '
                    f'perlu diperbaiki. Prediksi belum dijalankan.</p>',
                    unsafe_allow_html=True)
            with st.container(horizontal=True, key="aksi"):
                kirim = st.form_submit_button("Prediksi", type="primary")
                st.form_submit_button("Isi contoh pasien", on_click=_isi_contoh)
                st.form_submit_button("Kosongkan", on_click=_kosongkan)
        st.caption("Hanya data fiktif. Hasil ini bukan diagnosis dan tidak "
                   "boleh dipakai langsung untuk keputusan klinis.")

    with kanan:
        with st.container(key="panel_hasil"):
            _panel(metrik)

    if kirim:
        _proses(metrik)


# ---------- tab Riwayat ----------
def _hapus():
    try:
        riwayat.hapus()
    except OSError:
        pass


def tab_riwayat():
    st.title("Riwayat prediksi")
    st.markdown(
        '<p class="lead">Setiap prediksi tersimpan di berkas history.csv dan '
        'tetap ada setelah halaman dimuat ulang. Hanya data fiktif.</p>',
        unsafe_allow_html=True)
    df = riwayat.tabel()
    with st.container(key="kartu_riwayat"):
        if df.empty:
            st.markdown('<p class="empty">Belum ada prediksi. Buka tab '
                        'Prediksi, isi data, lalu tekan Prediksi.</p>',
                        unsafe_allow_html=True)
        else:
            st.dataframe(df, hide_index=True, width="stretch")
            with st.container(horizontal=True):
                try:
                    st.download_button(
                        "Unduh Excel (.xlsx)", riwayat.ke_excel(),
                        file_name="riwayat_prediksi.xlsx",
                        mime="application/vnd.openxmlformats-officedocument"
                             ".spreadsheetml.sheet")
                except ImportError:
                    st.caption("Pasang openpyxl untuk unduhan Excel.")
                st.download_button(
                    "Unduh CSV",
                    riwayat.baca().to_csv(index=False).encode("utf-8-sig"),
                    file_name="riwayat_prediksi.csv", mime="text/csv")
                st.button("Hapus riwayat", on_click=_hapus)