# gh0st-pi

> Provisioning satu-skrip untuk T4n OS / Void Linux (glibc) berbasis runit + xbps.
> Fokus: **AI coding lokal-dulu**, **inferensi offline via llama**, **reverse engineering (REA)**, dan **otomasi keamanan (HexStrike AI MCP)**.

Baru mengenal AI lokal? Mulai dari **[PANDUAN.md](PANDUAN.md)** (bahasa awam). Dokumen ini adalah referensi teknisnya.

Prinsip: **minimal by default**, artefak berat di `/opt`, kredensial tidak pernah disimpan, service **tanpa hak root**, versi dikunci, dan tool keamanan yang berisiko tidak dipasang diam-diam.

## Daftar Isi

- [Mulai cepat](#mulai-cepat)
- [Ringkasan](#ringkasan)
- [Desain keamanan](#desain-keamanan)
- [Prasyarat](#prasyarat)
- [Instalasi](#instalasi)
- [Variabel konfigurasi](#variabel-konfigurasi)
- [Perintah `gh0st-ai`](#perintah-gh0st-ai)
- [Pi + llama lokal](#pi--llama-lokal)
- [REA](#rea)
- [HexStrike AI MCP](#hexstrike-ai-mcp)
- [Multi-model / llama-swap](#multi-model--llama-swap)
- [Tata letak penyimpanan SSD / HDD](#tata-letak-penyimpanan-ssd--hdd)
- [Troubleshooting](#troubleshooting)
- [Uninstall](#uninstall)
- [Keamanan, etika, legalitas](#keamanan-etika-legalitas)
- [Struktur direktori](#struktur-direktori)
- [Kredit dan lisensi](#kredit-dan-lisensi)

---

## Mulai cepat

```sh
sudo sh setup.sh        # pasang (bisa diulang kapan saja; unduhan model dilanjutkan)
gh0st-ai start          # nyalakan AI
gh0st-ai test           # pastikan AI menjawab
# ngobrol lewat browser: http://127.0.0.1:8080   |   agent coding: buka terminal baru, ketik: pi
gh0st-ai stop           # matikan, bebaskan RAM
```

> **Penting (CRLF):** semua skrip harus berakhiran baris **LF**. File yang berakhiran CRLF (umum bila
> tersentuh Windows pada dual-boot) gagal dengan error aneh seperti `Bad fd number`. Cek dengan
> `file setup.sh` (tidak boleh ada "CRLF"); perbaiki dengan `sed -i 's/\r$//' setup.sh src/*.sh bin/* uninstall.sh install.sh`.
> Repo ini menyertakan `.gitattributes` yang memaksa LF.

---

## Ringkasan

| Komponen | Fungsi | Status provisioning |
|---|---|---|
| **llama (`llama serve`)** | Inferensi model GGUF lokal | Otomatis via installer resmi `llama.app`, dijalankan **tanpa root** |
| **Model GGUF** | Qwen3-4B (default), Qwen3-8B, Qwen2.5-Coder-7B/3B | Otomatis, bisa dilanjutkan, diverifikasi SHA256 |
| **runit service `llama`** | Menjalankan server localhost-only sebagai user `_llama` | Otomatis, **tidak nyala saat boot** secara default |
| **`gh0st-ai`** | Perintah start / stop / ganti model / tes | Otomatis |
| **Pi** (`@earendil-works/pi-coding-agent`) | Coding agent di terminal | Otomatis, dipasang sebagai **user biasa**, versi dikunci |
| **pi-llama-cpp** | Ekstensi Pi untuk server llama | Otomatis, versi dikunci. Ekstensi lain = opt-in |
| **HexStrike AI** | MCP server untuk orkestrasi tool keamanan | Otomatis (commit dikunci), on-demand lewat `gh0st-hexstrike` |
| **REA** | Reverse engineering | Manual (`npx rea-agents setup`) |
| **uv** | Frontend Python venv/pip | Default OFF |

Skrip ini **tidak** menyimpan API key, tidak memasang driver NVIDIA, dan tidak memasang tool ofensif HexStrike.

### Pilar

1. **Pi + llama lokal**: inferensi offline. Default `Qwen3-4B-Q4_K_M`, `http://127.0.0.1:8080`, konteks 16384, backend `cpu`. Cocok untuk kode sensitif, sampel malware, lab offline.
2. **Pi + REA**: reverse engineering, inspeksi binary/Electron/APK/firmware. Setup manual/interaktif, butuh Node modern.
3. **Pi untuk ekosistem T4n Labs**: model online konteks besar untuk refactor besar; llama lokal untuk kode sensitif; mode RPC/JSON Pi untuk pipeline lokal.
4. **HexStrike AI MCP**: orkestrasi tool keamanan, on-demand (bukan service runit), hanya untuk target berizin.

---

## Desain keamanan

Versi sebelumnya memiliki rantai eskalasi ke root: service dijalankan sebagai root, sementara `chown -R` menyerahkan
seluruh `/opt/gh0st-pi` (termasuk binari yang dieksekusi root) ke user biasa. Proses apa pun milik user (ekstensi Pi
berbahaya, agent yang terkena prompt injection, HexStrike) bisa menimpa binari itu dan menjadi root saat service restart/boot.
Desain sekarang:

| Aspek | Sekarang |
|---|---|
| Service llama | Jalan sebagai user sistem `_llama` (tanpa login, tanpa hak root) lewat `chpst -u` |
| Binari llama | Dipasang oleh installer **sebagai `_llama`** di folder sementara, lalu **disalin sebagai milik root** ke `$LLAMA_HOME/bin/llama`. `_llama` pun tidak bisa menimpanya |
| Installer eksternal | Diunduh ke **file** (bukan `curl \| sh`), SHA256 dicatat; bisa dikunci via `GH0ST_LLAMA_INSTALLER_SHA256` |
| `/opt/gh0st-pi` | Milik root. Hanya `workspace/` dan source+venv+cache HexStrike yang milik user |
| Pi, HexStrike, pip, git | Dijalankan sebagai **user biasa**, tidak pernah sebagai root |
| Versi | Pi `1.3.0`, `pi-llama-cpp@0.17.0`, HexStrike per commit `d689933…`; semuanya dipilih yang sudah beredar >14 hari |
| Model GGUF | Header `GGUF` + SHA256 dibandingkan dengan `x-linked-etag` dari Hugging Face; file rusak ditolak |
| Ekstensi Pi tambahan | **Opt-in** (`GH0ST_PI_EXT_EXTRA`); belum diaudit kodenya |
| Jaringan | llama bind `127.0.0.1`. HexStrike lewat peluncur yang memaksa `127.0.0.1` (lihat di bawah) |
| Telemetry | `PI_TELEMETRY=0` di env block (mematikan ping versi anonim Pi) |

**Temuan HexStrike (diverifikasi pada commit yang dikunci):** `hexstrike_server.py` memanggil
`app.run(host="0.0.0.0", ...)`. Variabel `HEXSTRIKE_HOST` dibaca tetapi tidak dipakai untuk bind. Endpoint `POST /api/command`
mengeksekusi perintah shell dari request, dan tidak ada autentikasi. Dijalankan langsung (seperti pada panduan lama),
siapa pun di WiFi/LAN yang sama dapat menjalankan perintah sebagai user kamu. Karena itu dipasang `gh0st-hexstrike`,
peluncur yang mengimpor `app` lalu menjalankannya dengan `host="127.0.0.1"` dan `debug=False`, tanpa mengubah source upstream.
**Jangan menjalankan `hexstrike_server.py` langsung.**

---

## Prasyarat

- T4n OS / Void Linux glibc, dengan `xbps-install` dan runit (`sv`, `chpst`), plus `useradd` (paket `shadow`) dan `sha256sum`.
- Akun biasa yang menjalankan `sudo` (bukan login root langsung; langkah per-user Pi/HexStrike/env dilewati bila root).
- Internet untuk: installer llama, model GGUF (Hugging Face), HexStrike (GitHub), npm (Pi, ekstensi).
- RAM 16 GB cukup untuk model 4B/8B. SSD disarankan untuk `/opt`. Keempat model memakan sekitar 15 GB.
- **Node.js >= 22.19** untuk Pi (REA: 22.x >= 22.19 / 24.x >= 24.11 / 26+). Skrip memeriksa dan memberi peringatan.
- GPU opsional (NVIDIA: CUDA; AMD/Intel: Vulkan/ROCm). Default `cpu`, aman untuk 16 GB.
- Paket `zstd` sangat disarankan (lihat [Troubleshooting](#binari-llama-0-byte--rusak)).

---

## Instalasi

```sh
sudo sh setup.sh                              # default: CPU, Qwen3-4B, Pi + HexStrike
sudo env GH0ST_BACKEND=cpu sh setup.sh        # backend eksplisit
sudo sh setup.sh gpu-check                    # hanya laporan GPU, tidak mengubah sistem
sudo env LLAMA_VERSION=b<NOMOR> sh setup.sh   # kunci build llama (nomor build terlihat di output 'llama version')
sudo env HF_TOKEN=hf_xxx sh setup.sh          # token HF utk installer llama (bukan utk unduhan model)
sudo env GH0ST_INSTALL_HEXSTRIKE=0 sh setup.sh   # tanpa HexStrike (pip-nya berat)
sudo env GH0ST_INSTALL_PI=0 sh setup.sh          # tanpa Pi
```

Aman diulang: yang sudah ada dilewati, unduhan model dilanjutkan, pilihan model/thinking dipertahankan.

Kegagalan di Pi, HexStrike, uv, unduhan model, atau tes service **tidak** menghentikan setup; semuanya dicatat dan diringkas di akhir. Hanya kegagalan memasang llama (komponen inti) yang menghentikannya.

Urutan kerja: cek root/xbps/runit, validasi konfigurasi, tulis state file, pasang dependensi, laporan GPU, pasang llama, unduh model
(default lebih dulu), env shell, service (tes nyala-lalu-mati), `gh0st-ai`, Pi, uv (opsional), HexStrike, rapikan hak akses.

### Yang dipasang

1. **Dependensi inti (xbps, `-y`)**: `git pkg-config curl ca-certificates nodejs python3 procps-ng`; opsional: `zstd`, `pciutils`.
2. **llama**: installer resmi, dijalankan sebagai `_llama` di `$LLAMA_STATE/stage`; binari disalin ke `$LLAMA_HOME/bin/llama`
   (milik root); symlink `$BIN_DIR/llama`. Installer memasang build **nightly terbaru** kecuali `LLAMA_VERSION` diisi.
   Flag server (`--jinja`, `--reasoning`, `--threads`, `--n-gpu-layers`) dipakai **hanya bila disebut di `llama serve --help`** versi terpasang.
3. **Model GGUF** (urutan unduh = urutan daftar): `Qwen3-4B`, `Qwen3-8B`, `Qwen2.5-Coder-7B-Instruct`, `Qwen2.5-Coder-3B-Instruct` (semua `Q4_K_M`, repo `unsloth/*-GGUF`).
4. **Service runit `llama`**: `$SV/{run,conf,log/run,down}`; link di `$RN/llama`. Log lewat `svlogd` ke `/var/log/llama/current`.
   File `down` membuat service **tidak nyala saat boot** (`GH0ST_AUTOSTART=1` menghapusnya). Setup menyalakan sekali untuk tes `/v1/models`, lalu mematikannya lagi.
5. **Env user** (`~/.bashrc`, `~/.zshrc`, fish bila ada), satu blok bertanda `# gh0st-pi-llama-env`: `LLAMA_MODELS`, `LLAMA_SERVER_URL`, `PI_TELEMETRY=0`. Backup `*.gh0stbak.<epoch>`.
6. **Pi**: `npm install -g --prefix ~/.local @earendil-works/pi-coding-agent@1.3.0` sebagai user; symlink `$BIN_DIR/pi`; lalu `pi install npm:pi-llama-cpp@0.17.0`.
7. **HexStrike**: git di commit terkunci, venv + pip sebagai user, peluncur aman `gh0st-hexstrike`. Bila pip gagal, dicoba sekali lagi setelah memasang `python3-devel gcc libffi-devel`.
8. **uv** (opsional, `GH0ST_INSTALL_UV=1`): diinstal sebagai `_llama`, disalin ke `$UV_HOME/bin` (milik root), symlink bila belum ada.

### Yang TIDAK dipasang otomatis

Driver NVIDIA/DKMS, toolchain C++ (hanya untuk fallback build), tool keamanan eksternal HexStrike (nmap, sqlmap, dst.), browser agent
(Chromium/chromedriver), Ghidra/IDA/Hopper, REA, API key/kredensial, ekstensi Pi di luar `pi-llama-cpp`.

---

## Variabel konfigurasi

Semua dibaca dari environment: `sudo env NAMA=nilai sh setup.sh`. Nilai path harus absolut, tanpa spasi dan kutip.

| Variabel | Default | Fungsi |
|---|---|---|
| `GH0ST_ROOT` | `/opt/gh0st-pi` | Akar artefak |
| `LLAMA_MODELS` | `$GH0ST_ROOT/models` | Folder model (boleh di HDD; `_llama` harus bisa membacanya) |
| `GH0ST_DEFAULT_MODEL` | `Qwen3-4B-Q4_K_M.gguf` | Model aktif awal |
| `MODELS_LIST` | 4 model Qwen | Baris `repo\|file`; urutan = urutan unduh |
| `GH0ST_PORT` / `GH0ST_CTX` | `8080` / `16384` | Port dan ukuran konteks |
| `GH0ST_THREADS` | otomatis (`nproc`-2) | Jumlah thread inferensi |
| `GH0ST_THINKING` | `off` | `on` / `off`. `off` menambah `--reasoning off` bila didukung |
| `GH0ST_AUTOSTART` | `0` | `1` = nyala otomatis saat boot |
| `GH0ST_BACKEND` | `cpu` | `cpu` / `cuda` / `rocm` / `vulkan` / `auto` |
| `GH0ST_NGPU` | otomatis (`0` utk cpu/auto, `99` utk lain) | Jumlah layer ke GPU |
| `GH0ST_REINSTALL` | `0` | `1` = pasang ulang llama (`FORCE_BUILD` lama tetap dikenali) |
| `GH0ST_SKIP_INSTALL` | `0` | `SKIP_INSTALL=1` ke installer llama |
| `LLAMA_VERSION`, `LLAMA_BUCKET`, `HF_TOKEN` | kosong | Diteruskan ke installer llama |
| `GH0ST_LLAMA_INSTALLER_SHA256` | kosong | Kunci hash installer llama |
| `GH0ST_INSTALL_PI` | `1` | Pasang Pi |
| `PI_VERSION`, `PI_PKG`, `PI_EXT_LIST` | `1.3.0`, `@earendil-works/pi-coding-agent`, `pi-llama-cpp@0.17.0` | Pin Pi dan ekstensi |
| `GH0ST_PI_EXT_EXTRA` | kosong | Ekstensi tambahan (opt-in, belum diaudit) |
| `GH0ST_INSTALL_HEXSTRIKE` | `1` | Pasang HexStrike |
| `HEX_REF`, `REPO_HEX`, `HEX_PORT` | commit `d689933…`, repo upstream, `8888` | Pin dan port HexStrike |
| `GH0ST_INSTALL_UV` | `0` | Pasang uv |
| `GH0ST_READY_TIMEOUT` | `180` | Detik menunggu server siap |
| `SV`, `RN`, `SVLOG_DIR`, `BIN_DIR`, `LLAMA_USER`, `LLAMA_STATE` | `/etc/sv/llama`, `/etc/runit/runsvdir/default`, `/var/log/llama`, `/usr/local/bin`, `_llama`, `/var/lib/llama` | Lokasi sistem |

Contoh:

```sh
# model ke HDD
sudo env LLAMA_MODELS=/mnt/hdd/gh0st-models sh setup.sh
# hanya satu model, tanpa HexStrike (instalasi ringan)
sudo env MODELS_LIST='unsloth/Qwen3-4B-GGUF|Qwen3-4B-Q4_K_M.gguf' GH0ST_INSTALL_HEXSTRIKE=0 sh setup.sh
```

---

## Perintah `gh0st-ai`

`gh0st-ai start | stop | restart | status | test | model [nomor\|nama] | think on\|off | url | log | help`.
Meminta `sudo`/`doas` sendiri. Mengubah `$SV/conf` (model, thinking) lalu memuat ulang bila AI sedang nyala.

`$SV/conf` berisi `MODEL_FILE`, `MODELS_DIR`, `LLAMA_BIN`, `SERVE_SUBCMD`, `PORT`, `CTX`, `EXTRA_FLAGS`, `HAS_REASONING`, `THINK`.
Perubahan manual: edit file itu lalu `gh0st-ai restart`. Jangan mengedit `run`.

---

## Pi + llama lokal

```sh
gh0st-ai start
pi                       # di terminal baru
```

Di dalam Pi, `/models` menampilkan model dari server lokal. `pi --list-models llama` (non-interaktif) menampilkan provider
berbentuk `llama-server=http://127.0.0.1:8080` bila server nyala. Status `Sleeping` hanya muncul pada mode router dengan `--sleep-idle-seconds`.

Provider online (DeepSeek, Qwen/DashScope, GLM/Z.AI, OpenRouter): isi kunci lewat `/login` di Pi. Skrip tidak menyimpan kredensial.
Strategi: online konteks besar untuk refactor/repo raksasa; llama offline untuk sampel malware, kode sensitif, dan lab tanpa jaringan.

Ekstensi opsional (belum diaudit kodenya, pasang dengan sadar):
`sudo env GH0ST_PI_EXT_EXTRA="pi-agent-modes@0.3.0 pi-manage-todo-list@0.4.0" sh setup.sh`.

---

## REA

REA (`morluto/rea`) bersifat manual/interaktif. Skrip ini tidak mengaudit atau menguji REA.

```sh
node -v                  # 22.x >= 22.19, 24.x >= 24.11, atau 26+
npx rea-agents setup     # pilih agent yang kompatibel, review, approve; lalu restart Pi
```

Analisis native opsional: Ghidra / Hopper / IDA; Android: JDK + JADX headless; firmware: Binwalk / Unblob.
Linux butuh `ps` kompatibel procps di PATH (paket `procps-ng` dicoba dipasang).

---

## HexStrike AI MCP

On-demand, **bukan** service runit. Jalankan hanya lewat peluncur aman:

```sh
gh0st-hexstrike            # port default 8888, hanya 127.0.0.1; meminta konfirmasi bila interaktif
curl -fsS http://127.0.0.1:8888/health
```

Peluncur menolak dijalankan sebagai root. Mode debug Flask sengaja dimatikan (debugger Werkzeug = eksekusi kode).
Konfigurasi klien MCP (klien hanya menyambung ke URL server, tidak butuh bind lain):

```json
{
  "mcpServers": {
    "hexstrike-ai": {
      "command": "/opt/gh0st-pi/tools/hexstrike-ai/hexstrike-env/bin/python",
      "args": ["/opt/gh0st-pi/tools/hexstrike-ai/hexstrike_mcp.py", "--server", "http://localhost:8888"],
      "timeout": 300,
      "disabled": false
    }
  }
}
```

(VS Code: `servers.hexstrike` dengan `type: "stdio"` dan `command`/`args` yang sama. Cursor, Roo Code, 5ire, dll. serupa.)

Catatan:

- README HexStrike tidak menjamin integrasi ke Pi. Menyambungkannya ke Pi butuh registrasi MCP manual di sisi Pi; jangan berasumsi `pi` otomatis melihat tool-nya.
- Tool eksternal tidak dipasang. Contoh subset (verifikasi nama paket di repo): `sudo xbps-install -S nmap masscan gobuster ffuf sqlmap nikto hydra john hashcat radare2 binwalk`. Pasang hanya yang kamu pahami dan berwenang uji.
- Browser agent butuh Chromium/Chrome + driver; tidak dipasang otomatis.
- Batasi `alwaysAllow` pada klien MCP.

---

## Multi-model / llama-swap

Default: single-model, ganti dengan `gh0st-ai model`. Untuk router multi-model / swap, baca dokumentasi upstream
(llama.cpp, pi-llama-cpp, llama-swap); format `presets.ini` dan konfigurasi llama-swap **berubah antar versi** dan tidak diuji di sini.
Garis besar: pada `$SV/run`, ganti argumen `--model "$MODEL"` dengan `--models-preset <file>` dan tambahkan `--sleep-idle-seconds 300`
agar model idle dilepas dari RAM (sangat disarankan di 16 GB), lalu `gh0st-ai restart`. Skrip `run` akan tertimpa saat `setup.sh` diulang;
simpan salinannya.

---

## Tata letak penyimpanan SSD / HDD

Semua artefak berat di `/opt` (SSD). Model adalah kandidat pertama untuk dipindah ke HDD (dibaca sekali saat load, bukan dieksekusi berulang).

```sh
sudo env LLAMA_MODELS=/mnt/hdd/gh0st-models sh setup.sh
```

Syarat: user `_llama` harus bisa **membaca** foldernya, termasuk semua folder induk (`chmod o+x` pada induk bila perlu).
Model di dalam `/home` yang tertutup biasanya gagal; setup memeriksanya dan memberi peringatan.

Opsional (manual, lakukan saat Pi tidak jalan dan backup dulu):

```sh
mv ~/.pi /opt/gh0st-pi/pi && ln -s /opt/gh0st-pi/pi ~/.pi    # risiko: bila /opt tak termount, Pi rusak
npm config set cache /opt/gh0st-pi/npm-cache                  # cache npm (pi install, npx rea-agents)
```

---

## Troubleshooting

### AI tidak siap / service gagal

```sh
gh0st-ai status
gh0st-ai log                       # = tail -f /var/log/llama/current
sudo sv status /etc/sv/llama
```

Setup menampilkan 15 baris terakhir log bila tes nyala gagal. Penyebab umum: model belum terunduh, RAM habis, flag tidak dikenal versi llama terpasang.

### `/health` 200 tapi Pi tidak melihat model

Gerbang yang benar adalah `curl -fsS http://127.0.0.1:8080/v1/models` (harus mengandung `"data"`). Jika tidak,
`llama serve` mungkin tidak kompatibel dengan `pi-llama-cpp`. Gunakan fallback build `llama-server`.

### Fallback: build `llama-server` dari source

Satu-satunya jalur yang butuh toolchain C++:

```sh
sudo xbps-install -S cmake make gcc
git clone --depth 1 https://github.com/ggml-org/llama.cpp /opt/llama/src
cd /opt/llama/src && cmake -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/llama
cmake --build build -j"$(nproc)" && sudo cmake --install build
```

Lalu di `/etc/sv/llama/conf` ubah dua baris (llama-server dipanggil **tanpa** subcommand `serve`), dan restart:

```sh
LLAMA_BIN='/opt/llama/bin/llama-server'
SERVE_SUBCMD=''
```

`EXTRA_FLAGS` hasil deteksi dibuat dari `llama serve --help`; sesuaikan dengan `llama-server --help` bila ada flag yang tak dikenal.
Pastikan `/opt/llama` milik root (`sudo chown -R root:root /opt/llama`).

### Binari llama 0 byte / rusak

Installer resmi punya laporan bug yang bisa menghasilkan binari 0 byte tanpa error, terutama tanpa `zstd`. Skrip menolak binari < 1 MB.
Pasang `sudo xbps-install -S zstd`, lalu `sudo env GH0ST_REINSTALL=1 sh setup.sh`.

### Model tidak bisa dibaca `_llama`

Folder model (atau induknya) tertutup untuk user lain. Pindahkan ke `/opt/gh0st-pi/models` atau beri izin telusur pada folder induk.

### Unduhan model gagal

Jalankan ulang `sudo sh setup.sh`: unduhan yang terputus **dilanjutkan** (`curl -C -`), file yang gagal verifikasi (header/SHA256) diunduh ulang.
Bila SHA256 resmi tak tersedia dari server, hanya header GGUF yang dicek (ada peringatan). Unduh manual: `curl -fL -C - -o <file> <url>`.

### HexStrike

- *clone/fetch gagal*: cek jaringan dan `REPO_HEX`; ulangi `sudo sh setup.sh`. Checkout ke `HEX_REF` yang tak ada akan ditolak.
- *pip gagal*: skrip mencoba lagi setelah memasang `python3-devel gcc libffi-devel`. Manual: `<venv>/bin/pip install -r <dir>/requirements.txt`. Verifikasi nama paket di repo distro.
- Memperbarui ke commit lain: `sudo env HEX_REF=<sha> sh setup.sh` setelah **meninjau** perubahannya.

### Node terlalu tua / `ps` tidak ada

Pi butuh Node >= 22.19 (REA punya daftar sendiri). Upgrade nodejs, lalu jalankan ulang setup. Untuk REA cek `command -v ps` dan paket `procps-ng`.

### `pi: command not found`

Buka terminal baru. Cek `ls -l /usr/local/bin/pi` dan `~/.local/bin/pi`. Pasang manual sebagai user: `npm install -g --prefix ~/.local @earendil-works/pi-coding-agent@1.3.0`.
Paket lama `@mariozechner/pi-coding-agent` sudah deprecated dan tidak kompatibel dengan `pi-llama-cpp` terbaru.

### Memaksa pasang ulang / melewati installer

```sh
sudo env GH0ST_REINSTALL=1 sh setup.sh      # pasang ulang llama
sudo env GH0ST_SKIP_INSTALL=1 sh setup.sh   # SKIP_INSTALL=1 ke installer resmi
```

Dengan `SKIP_INSTALL` + `LLAMA_VERSION`, upstream tidak memverifikasi pin secara ketat.

---

## Uninstall

```sh
sudo sh uninstall.sh --dry-run          # lihat dulu, tidak mengubah apa pun
sudo sh uninstall.sh                    # default: model dihapus, workspace disimpan
sudo sh uninstall.sh --keep-models -y
sudo sh uninstall.sh --purge-all -y     # hapus seluruh /opt/gh0st-pi dan /opt/llama
```

Lokasi dibaca dari `/opt/gh0st-pi/.gh0st-pi-state` (milik root), jadi path custom (mis. model di HDD) ikut dibersihkan, dan **hanya file model yang dikenal** dihapus, bukan seluruh folder.
Yang dilakukan: matikan dan lepas service (urutan benar: matikan, lepas link, tunggu, hapus direktori), hapus user `_llama` + state + log, hapus `gh0st-ai`/`gh0st-hexstrike`,
bersihkan env block (hanya baris milik gh0st-pi; baris lain di rc aman), hapus llama/uv/HexStrike/cache.
**Tidak** dihapus: Pi dan `/usr/local/bin/pi`, `~/.pi`, tool eksternal, workspace (kecuali `--purge-workspace`/`--purge-all`).
Lepas ekstensi Pi: `--try-pi-uninstall`. Hapus Pi: `npm uninstall -g --prefix ~/.local @earendil-works/pi-coding-agent`.

`install.sh` (varian Ollama) tidak punya uninstaller; langkah manual: `sudo sv down /etc/sv/ollama; sudo rm -f /etc/runit/runsvdir/default/ollama; sleep 6; sudo rm -rf /etc/sv/ollama /opt/ollama /var/lib/ollama /var/log/ollama; sudo userdel _ollama`,
lalu hapus blok `# ollama-env` dari rc.

---

## Keamanan, etika, legalitas

Stack ini dapat mengakses tool keamanan, analisis binary, pemindaian web, framework exploit, dan agent otomatis.

Gunakan hanya untuk: sistem milik sendiri; pentest dengan izin tertulis; bug bounty dalam scope; CTF; riset keamanan yang sah;
red team dengan persetujuan organisasi; interoperabilitas; pelestarian software; analisis malware di lingkungan terisolasi.
Jangan untuk akses tidak sah, perusakan, pencurian data, atau serangan tanpa izin.

Rekomendasi operasional:

- Analisis sampel tak tepercaya di VM/lab terpisah, **tanpa** akses ke `~/.ssh` dan kredensial. String di dalam binary/dokumen bisa berisi instruksi yang dibaca agent (prompt injection).
- Jangan auto-approve perintah `bash` dari agent. Model 4B-8B sering mengarang offset/alamat/nama fungsi; verifikasi dengan tool.
- Jangan ekspos port `8080` dan `8888` ke jaringan luar. Remote: SSH tunnel.
- llama tanpa `--api-key`: situs web di browser lokal pada prinsipnya bisa memanggil `127.0.0.1:8080`. Server hanya menghasilkan teks (tanpa akses file/shell), tetapi tutup tab asing saat AI menyala.
- Pasang ekstensi Pi hanya setelah ditinjau; ekstensi berjalan dengan hak penuh user kamu.
- Simpan bukti/hasil scan dengan aman; patuhi rules of engagement.

---

## Struktur direktori

```text
repo/
├── setup.sh                  # entry point
├── uninstall.sh
├── install.sh                # varian Ollama (terpisah, service non-root)
├── PANDUAN.md                # panduan pemula
├── bin/
│   ├── gh0st-ai              # template; dipasang ke $BIN_DIR
│   ├── gh0st-hexstrike       # template; dipasang ke $BIN_DIR
│   └── hexstrike_local.py    # peluncur HexStrike khusus 127.0.0.1
└── src/                      # common config preflight gpu deps llama models env uv service helpers pi hexstrike finalize

/opt/gh0st-pi/                # milik root
├── .gh0st-pi-state           # lokasi terpasang (dibaca uninstall.sh)
├── llama/bin/llama           # milik root
├── models/*.gguf
├── uv/bin/                   # opsional
├── tools/
│   ├── hexstrike_local.py    # milik root
│   └── hexstrike-ai/         # source + hexstrike-env (milik user)
├── .cache/pip                # milik user
└── workspace/                # milik user

/etc/sv/llama/{run,conf,down,log/run}    # milik root
/var/log/llama/current                   # log service
/var/lib/llama/                          # HOME user _llama
~/.local/bin/pi  (+ symlink /usr/local/bin/pi)
```

---

## Kredit dan lisensi

Berdiri di atas: T4n OS, Void Linux, runit, XBPS, llama.cpp, installer llama.app, Pi coding agent, pi-llama-cpp, REA / morluto,
HexStrike AI, Astral uv, Hugging Face, Unsloth GGUF, serta seluruh maintainer paket dan tool keamanan yang dipakai secara terpisah.

Lisensi: lihat [LICENSE](LICENSE).
