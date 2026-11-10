# Panduan Pemula gh0st-pi

Panduan ini ditulis untuk orang yang selama ini cuma memakai chatbot (ChatGPT, Claude, Gemini, dsb.)
dan belum pernah menjalankan AI di komputernya sendiri. Tidak ada istilah yang dipakai tanpa dijelaskan.
Detail teknis ada di [README.md](README.md).

---

## 1. Apa sebenarnya yang dipasang?

Bayangkan chatbot online itu seperti **bioskop**: filmnya diputar di tempat orang lain, lu cuma nonton.
Yang dipasang `gh0st-pi` itu seperti **pemutar film di rumah sendiri**: semuanya berjalan di laptop lu.

| Istilah | Artinya dalam bahasa biasa |
|---|---|
| **Model** | "Otak" AI. Wujudnya satu file besar (ekstensi `.gguf`, 2 sampai 5 GB). Seperti file film, tapi isinya pengetahuan. |
| **llama** | Pemutar model tadi. Program yang membaca file model lalu menjawab pertanyaan. |
| **AI lokal / offline** | AI yang jalan di laptop lu sendiri. Tidak butuh internet saat dipakai, dan pertanyaan lu tidak dikirim ke mana pun. |
| **Service** | Program yang berjalan di latar belakang, menunggu pertanyaan. Di sini namanya `llama`. |
| **Pi** | Asisten coding yang dipakai di terminal. Bedanya dengan chatbot: Pi bisa **membaca dan mengubah file** di komputer lu dan **menjalankan perintah**, kalau lu mengizinkan. |
| **MCP** | "Colokan standar" supaya AI bisa memakai alat dari luar, seperti kabel USB untuk AI. |
| **HexStrike** | Kotak alat keamanan yang bisa dicolok ke AI lewat MCP. Hanya untuk target milik sendiri atau yang berizin. |

**Terus apa bedanya dengan chatbot online?**

- Plus: privat, gratis, jalan tanpa internet, aman dipakai untuk kode atau file sensitif.
- Minus: model yang muat di laptop lu (4 sampai 8 miliar "parameter") **jauh lebih kecil** dari yang ada di
  chatbot online. Jawabannya lebih lambat dan sering kurang pintar. Anggap sebagai asisten magang yang
  cepat dan rajin, bukan ahli.

---

## 2. Cara pakai harian (3 langkah)

Semua perintah di terminal.

**Langkah 1. Nyalakan AI**

```sh
gh0st-ai start
```

Tunggu sampai muncul tulisan `SIAP`. Biasanya 10 sampai 90 detik, karena file model dimuat ke RAM.

**Langkah 2. Pilih cara ngobrol**

- **Lewat browser** (paling mudah, mirip ChatGPT): buka `http://127.0.0.1:8080`.
  Menurut dokumentasi llama, halaman chat ini disediakan servernya. Kalau halamannya tidak muncul, pakai
  cara berikutnya.
- **Lewat Pi** (untuk coding): buka terminal **baru**, ketik `pi`, lalu ketik `/models` dan pilih model.
- **Tes cepat**: `gh0st-ai test` mengajukan satu pertanyaan dan menampilkan jawabannya. Kalau ini
  berhasil, berarti AI-nya sehat.

**Langkah 3. Matikan kalau sudah selesai**

```sh
gh0st-ai stop
```

Ini penting karena model memakan RAM 3 sampai 6 GB. Laptop lu punya 16 GB dan perlu sisa untuk hal lain.

> AI **tidak** menyala sendiri saat laptop dihidupkan. Itu disengaja.

---

## 3. Perintah yang perlu lu hafal

| Perintah | Fungsinya |
|---|---|
| `gh0st-ai start` | Nyalakan AI |
| `gh0st-ai stop` | Matikan AI (RAM kembali bebas) |
| `gh0st-ai status` | Lihat nyala/mati dan model yang sedang dipakai |
| `gh0st-ai test` | Tanya satu pertanyaan, cek AI menjawab |
| `gh0st-ai model` | Lihat daftar model. Ganti: `gh0st-ai model 3` atau `gh0st-ai model qwen3-8b` |
| `gh0st-ai think off` / `on` | Mode "berpikir" (lihat di bawah) |
| `gh0st-ai log` | Lihat catatan kalau ada yang error (Ctrl+C untuk keluar) |
| `gh0st-ai help` | Daftar semua perintah |

Tidak perlu mengetik `sudo`. Perintahnya meminta sendiri kalau butuh.

---

## 4. Model mana yang dipilih?

Model yang diunduh ada empat. Hanya satu yang aktif pada satu waktu.

| Model | Kapan dipakai | Catatan |
|---|---|---|
| **Qwen3-4B** (bawaan) | Harian, tanya jawab, tugas ringan | Paling ringan dan paling cepat |
| **Qwen3-8B** | Soal yang lebih sulit | Lebih pintar, tapi lebih lambat dan lebih berat |
| **Qwen2.5-Coder-7B** | Menulis atau mengedit kode | Bagus untuk kode; sebagai agent di Pi biasanya kurang stabil dibanding Qwen3 |
| **Qwen2.5-Coder-3B** | Kode cepat dan ringan | Paling kecil |

Kecepatan di laptop lu (tanpa kartu grafis) kira-kira beberapa kata per detik. Ini **perkiraan**
dan bisa beda, jadi rasakan sendiri. Model 8B kira-kira separuh kecepatan model 4B.

**Mode "berpikir"**: beberapa model menulis "pikirannya" dulu sebelum menjawab. Hasilnya lebih teliti
tapi di laptop tanpa GPU bisa makan beberapa menit. Karena itu bawaannya **mati**.
Untuk soal yang benar-benar sulit: `gh0st-ai think on`. Kalau jawaban terasa lama sekali, kembalikan
dengan `gh0st-ai think off`.

---

## 5. Aturan aman (baca ini)

1. **Pi bisa mengubah dan menghapus file.** Jalankan hanya di dalam folder proyek.
   Pastikan proyeknya sudah di-`git commit`, supaya kalau ada yang salah bisa dikembalikan.
2. **Jangan menyalakan mode "setujui otomatis"** untuk perintah yang dijalankan AI kalau belum paham.
   Baca perintahnya dulu sebelum menekan setuju.
3. **Jangan percaya mentah-mentah.** Model kecil sering mengarang, terutama angka, alamat memori,
   nama fungsi, dan nomor versi. Verifikasi dengan tool asli.
4. **File dari luar bisa berisi "perintah tersembunyi"** untuk menipu AI. Kalau menganalisis file
   mencurigakan (malware, binary, dokumen aneh), lakukan di komputer atau VM terpisah.
5. **HexStrike** memberi AI kemampuan menjalankan tool keamanan. Pakai hanya untuk sistem milik sendiri,
   CTF, atau yang ada izin tertulisnya. Jalankan lewat `gh0st-hexstrike`.
   **Jangan** menjalankan `hexstrike_server.py` langsung: aslinya server itu terbuka untuk semua orang di
   WiFi yang sama dan bisa menjalankan perintah tanpa password.

---

## 6. Kalau ada masalah

| Gejala | Coba ini |
|---|---|
| `gh0st-ai start` lama sekali | Normal untuk model besar. Tunggu sampai 2 menit. Cek `gh0st-ai log`. |
| Tulisan "model tidak ada" | Unduhan belum selesai. Jalankan lagi `sudo sh setup.sh` dan unduhan akan dilanjutkan. |
| Jawaban sangat lambat | `gh0st-ai model` lalu pilih Qwen3-4B, dan pastikan `gh0st-ai think off`. Tutup program berat lain. |
| `pi: command not found` | Buka terminal **baru**. Kalau masih gagal, jalankan lagi `sudo sh setup.sh`. |
| Pi tidak menampilkan model | Pastikan sudah `gh0st-ai start` dan tunggu sampai `SIAP`, lalu ketik `/models` lagi. |
| Laptop terasa berat atau macet | `gh0st-ai stop`. Kemungkinan RAM habis. |
| Ada yang aneh dan tidak jelas | `gh0st-ai status`, lalu `gh0st-ai log`. Salin pesan errornya untuk ditanyakan. |

---

## 7. Kamus mini

- **Parameter (4B, 8B)**: ukuran "otak". B = miliar. Makin besar makin pintar, tapi makin berat dan lambat.
- **Q4_K_M**: cara memampatkan model supaya muat di laptop. Sedikit lebih bodoh, jauh lebih ringan.
- **Token**: potongan kata. "Kecepatan token per detik" kira-kira kecepatan AI mengetik.
- **Konteks (16384)**: seberapa banyak teks yang bisa "diingat" AI dalam satu percakapan.
- **Localhost / 127.0.0.1**: artinya "hanya dari komputer ini sendiri". Orang lain di jaringan tidak bisa menyentuhnya.
- **Terminal baru**: tutup terminal lama dan buka lagi, supaya pengaturan baru terbaca.
