# gh0st-Pi

> One-shot provisioning script untuk T4n OS / Void Linux (glibc) berbasis runit + xbps.  
> Fokus: **local-first AI coding**, **offline inference via llama.cpp**, **reverse engineering dengan REA**, dan **security automation dengan HexStrike AI MCP**.

`gh0st-pi` dirancang sebagai installer non-interaktif yang menyiapkan beberapa pilar utama secara deterministik, dengan prinsip **minimal by default**: artefak berat ditaruh di `/opt` (SSD), konfigurasi user tetap di `$HOME`, kredensial tidak disimpan otomatis, dan tool eksternal yang berisiko/legal-sensitive tidak dipasang diam-diam.

---

## Daftar Isi

- [Ringkasan](#ringkasan)
- [Pilar yang Disediakan](#pilar-yang-disediakan)
- [Prinsip Desain](#prinsip-desain)
- [Prasyarat](#prasyarat)
- [Instalasi Cepat](#instalasi-cepat)
- [Variabel Konfigurasi](#variabel-konfigurasi)
- [Apa yang Dipasang](#apa-yang-dipasang)
- [Apa yang TIDAK Dipasang Otomatis](#apa-yang-tidak-dipasang-otomatis)
- [Pasca Instalasi](#pasca-instalasi)
- [Menggunakan Pi + llama.cpp Lokal](#menggunakan-pi--llamacpp-lokal)
- [Menggunakan REA](#menggunakan-rea)
- [Menggunakan HexStrike AI MCP](#menggunakan-hexstrike-ai-mcp)
- [Upgrade ke Multi-Model / llama-swap](#upgrade-ke-multi-model--llama-swap)
- [Tata Letak Penyimpanan SSD / HDD](#tata-letak-penyimpanan-ssd--hdd)
- [Troubleshooting](#troubleshooting)
- [Uninstall Manual](#uninstall-manual)
- [Keamanan, Etika, dan Legalitas](#keamanan-etika-dan-legalitas)
- [Struktur Direktori](#struktur-direktori)
- [Kredit](#kredit)
- [Lisensi](#lisensi)

---

## Ringkasan

`gh0st-pi` adalah skrip provisioning untuk membangun workstation/lab AI-assisted security research berbasis T4n OS / Void Linux.

Stack utama yang disiapkan:

| Komponen | Fungsi | Status Provisioning |
|---|---|---|
| **llama.cpp / llama server** | Inference model GGUF secara lokal | Otomatis via installer resmi `llama.app` |
| **Pi** | Coding agent / MCP client / automation | Manual/integrasi per-user |
| **pi-llama-cpp** | Ekstensi Pi untuk terhubung ke llama.cpp server | Best-effort otomatis |
| **REA** | Reverse engineering & binary/app analysis | Setup manual via `npx rea-agents setup` |
| **HexStrike AI** | MCP server untuk Orchestration security tools | Best-effort otomatis, on-demand |
| **runit service `llama`** | Menjalankan llama server localhost-only | Otomatis |
| **uv** | Opsional, frontend Python venv/pip | Default OFF |

Skrip ini **tidak** menyimpan API key, tidak menginstal driver NVIDIA secara otomatis, dan tidak memasang seluruh tool offensif HexStrike secara default.

---

## Pilar yang Disediakan

### [1] Pi + llama.cpp lokal

Menyediakan inference lokal melalui llama.cpp agar Pi dapat bekerja offline atau semi-offline.

- Model default: `Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf`
- Endpoint: `http://127.0.0.1:8080`
- Context default: `16384`
- Backend default: `cpu`
- Service: runit `llama`

Cocok untuk:

- Coding tanpa mengirim kode ke cloud
- Analisis sampel malware / data sensitif
- Lab offline
- Penghematan biaya API

### [2] Pi + REA

REA digunakan untuk reverse engineering, inspect binary, JavaScript/Electron app, APK, firmware, dan analisis bukti-level rendah.

- Setup REA bersifat manual/interaktif
- Membutuhkan Node.js modern
- Native analysis dapat memakai Ghidra/Hopper/IDA jika tersedia
- Linux membutuhkan `ps` yang compatible procps untuk ownership check

Cocok untuk:

- Bug hunting
- Malware analysis
- Software preservation
- Interoperability research
- Analisis aplikasi yang kamu miliki atau berwenang periksa

### [3] Pi untuk coding hardcore / ekosistem T4n Labs

Pi digunakan sebagai coding agent utama, baik dengan model online maupun lokal.

Strategi yang disarankan:

- Model online context besar untuk refactor besar / repo raksasa
- llama.cpp lokal untuk kode sensitif / privasi / no-network
- Mode RPC/JSON Pi untuk automation dan pipeline lokal

### [4] HexStrike AI MCP

HexStrike AI dipasang sebagai MCP server on-demand, bukan service runit.

- Direktori source: `/opt/gh0st-pi/tools/hexstrike-ai`
- Virtualenv: `/opt/gh0st-pi/tools/hexstrike-ai/hexstrike-env`
- Port default: `8888`
- Status: best-effort

Penting:

- HexStrike AI memberikan akses tool keamanan yang kuat kepada AI agent
- Jalankan hanya di lingkungan terisolasi
- Gunakan hanya pada target yang kamu miliki atau punya izin tertulis
- Tool eksternal seperti nmap, sqlmap, ffuf, ghidra, dll. tidak dipasang otomatis


## Prinsip Desain

### Minimal by Default

Skrip hanya memasang komponen inti yang diperlukan untuk provisioning. Tool eksternal, driver proprietary, browser agent berat, dan dependensi build C++ tidak dipasang kecuali benar-benar dibutuhkan atau diaktifkan secara eksplisit.

### Heavy Artifacts di SSD

Semua artefak berat diarahkan ke `/opt/gh0st-pi`:

- llama binary
- GGUF models
- HexStrike source + venv
- pip cache HexStrike
- workspace T4n Labs

Konfigurasi user tetap di `$HOME` karena shell harus membacanya dari home directory.

### Tidak Menyimpan Kredensial

Skrip tidak menulis API key ke file konfigurasi. Provider online seperti DeepSeek, Qwen, GLM/Z.AI, OpenRouter, dll. harus diisi manual melalui mekanisme login agent.

### Localhost-First

LLama server dan HexStrike MCP server default bind ke `127.0.0.1`.

Jangan ekspos port ini ke LAN/internet tanpa authentication, TLS, SSH tunnel, atau kontrol jaringan yang jelas.

## Prasyarat

### Sistem Operasi

- T4n OS
- Void Linux glibc variant
- Memiliki `xbps-install`
- Menggunakan runit

### Akses

- Root / sudo
- Koneksi internet untuk download:
  - installer resmi llama
  - model GGUF dari Hugging Face
  - repository HexStrike AI
  - npm package untuk Pi extensions / REA

### Hardware

- Disarankan SSD untuk `/opt`
- RAM minimal 16 GB untuk model 7B Q4_K_M secara nyaman
- GPU opsional:
  - NVIDIA untuk backend CUDA
  - AMD/Intel untuk Vulkan/ROCm tergantung dukungan llama.cpp
- Backend default adalah `cpu` agar aman di mesin 16 GB

### Versi Node.js untuk REA

REA membutuhkan Node.js:

- 22.x >= 22.19, atau
- 24.x >= 24.11, atau
- 26+

Skrip akan memeriksa versi Node dan memberi warning jika tidak memenuhi syarat.

## Instalasi Cepat

### Jalankan skrip sebagai root

```sh
sudo ./setup.sh
```

### Dengan backend CPU eksplisit

```sh
sudo env GH0ST_BACKEND=cpu ./setup.sh
```

### Cek GPU tanpa mengubah sistem

Mode ini tidak membutuhkan root dan tidak memasang apa pun:

```sh
./setup.sh gpu-check
```

atau:

```sh
GPU_CHECK_ONLY=1 ./setup.sh
```

### Pin versi llama tertentu

Jika kamu ingin reproducible build/download:

```sh
sudo env LLAMA_VERSION=<version> ./setup.sh
```

Contoh:

```sh
sudo env LLAMA_VERSION=b6056 ./setup.sh
```

> Catatan: pin versi sangat disarankan untuk lab produksi/repeatable research.

### Menggunakan Hugging Face token

Untuk menghindari rate limit atau mengakses private/restricted repo:

```sh
sudo env HF_TOKEN=hf_xxx ./setup.sh
```

## Variabel Konfigurasi

Semua variabel dapat dilewatkan melalui `sudo env VAR=value ./setup.sh`.

| Variabel | Default | Deskripsi |
|---|---:|---|
| `GH0ST_ROOT` | `/opt/gh0st-pi` | Akar seluruh artefak gh0st-pi |
| `LLAMA_MODELS` | `$GH0ST_ROOT/models` | Direktori model GGUF |
| `UV_HOME` | `$GH0ST_ROOT/uv` | Direktori install uv bila diaktifkan |
| `HEX_DIR` | `$GH0ST_ROOT/tools/hexstrike-ai` | Direktori source HexStrike AI |
| `HEX_ENV` | `$HEX_DIR/hexstrike-env` | Virtualenv HexStrike AI |
| `HEX_PORT` | `8888` | Port default HexStrike MCP server |
| `PORT` | `8080` | Port llama server untuk pi-llama-cpp |
| `CTX` | `16384` | Context size llama server |
| `NGPU` | `0` | Jumlah layer GPU; 0 = CPU-only |
| `GH0ST_BACKEND` | `cpu` | Backend llama: `cpu`, `cuda`, `rocm`, `vulkan`, `auto` |
| `FORCE_BUILD` | `0` | Paksa install ulang binari llama |
| `GH0ST_SKIP_INSTALL` | `0` | Set `SKIP_INSTALL=1` untuk installer resmi llama |
| `GH0ST_INSTALL_UV` | `0` | Pasang uv; default OFF |
| `REPO_HEX` | `https://github.com/0x4m4/hexstrike-ai.git` | Repo HexStrike AI |
| `MODELS_LIST` | daftar model Qwen | Daftar model GGUF format `repo|filename` |
| `DEFAULT_MODEL_FILE` | `Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf` | Model default service |
| `HF_TOKEN` | kosong | Token Hugging Face |
| `LLAMA_VERSION` | kosong | Pin versi installer llama |
| `LLAMA_BUCKET` | `ggml-org/install.sh` | Bucket installer llama |
| `GPU_CHECK_ONLY` | `0` | Hanya deteksi GPU |

### Contoh konfigurasi umum

#### CPU-only, aman untuk 16 GB

```sh
sudo env GH0ST_BACKEND=cpu ./setup.sh
```

#### Coba backend auto-detect

```sh
sudo env GH0ST_BACKEND=auto ./setup.sh
```

#### Pasang uv secara opsional

```sh
sudo env GH0ST_INSTALL_UV=1 ./setup.sh
```

#### Pindahkan model ke HDD

```sh
sudo env LLAMA_MODELS=/mnt/hdd/gh0st-models ./setup.sh
```

## Apa yang Dipasang

### 1. Dependensi inti via xbps

Skrip mencoba memasang:

```sh
git
pkg-config
curl
ca-certificates
nodejs
python3
procps-ng
```

Opsional:

```sh
zstd
```

Jika `zstd` tidak ada, installer resmi llama akan mencoba mengunduh helper `unzstd` sendiri.

### 2. llama.cpp via installer resmi

Installer resmi:

```sh
https://llama.app/install.sh
```

Artefak:

- `$GH0ST_ROOT/llama/.llama-app/llama`
- symlink global: `/usr/local/bin/llama`

Backend dipilih berdasarkan `GH0ST_BACKEND`.

Default:

```sh
GH0ST_BACKEND=cpu
```

Ini berarti installer akan mencoba menghindari CUDA/ROCm/Vulkan dan mengambil build CPU sesuai FEATCODE.

### 3. Model GGUF

Model diunduh dari Hugging Face ke:

```sh
$LLAMA_MODELS
```

Default list:

```text
unsloth/Qwen2.5-Coder-7B-Instruct-GGUF|Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
unsloth/Qwen2.5-Coder-3B-Instruct-GGUF|Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf
unsloth/Qwen3-8B-GGUF|Qwen3-8B-Q4_K_M.gguf
unsloth/Qwen3-4B-GGUF|Qwen3-4B-Q4_K_M.gguf
```

Model default yang dijalankan service:

```text
Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
```

> Selalu verifikasi nama file model di Hugging Face sebelum dipakai di produksi.

### 4. Runit service llama

Service dibuat di:

```sh
/etc/sv/llama
```

Dan ditautkan ke:

```sh
/etc/runit/runsvdir/default/llama
```

Service menjalankan:

```sh
llama serve --model ... --host 127.0.0.1 --port 8080 ...
```

Endpoint:

```text
http://127.0.0.1:8080
```

### 5. Environment user

Skrip menambahkan blok env ke shell rc user dengan marker:

```text
gh0st-pi-llama-env
```

File yang disentuh bila ada:

- `~/.bashrc`
- `~/.zshrc`
- `~/.config/fish/config.fish`

Isinya hanya pointer, misalnya:

```sh
export LLAMA_MODELS=/opt/gh0st-pi/models
export LLAMA_SERVER_URL=http://127.0.0.1:8080
```

### 6. Ekstensi Pi

Skrip mencoba memasang ekstensi berikut bila command `pi` tersedia:

```text
pi-llama-cpp
pi-agent-modes
pi-themes
pi-manage-todo-list
pi-redteam
pi-security-analysis
```

Untuk `pi-llama-cpp`, terdapat fallback GitHub:

```sh
pi install https://github.com/gsanhueza/pi-llama-cpp
```

Pemasangan ekstensi bersifat best-effort. Jika gagal, ulangi manual sebagai user:

```sh
pi install npm:<extension-name>
```

### 7. HexStrike AI

HexStrike AI dipasang secara best-effort:

- Clone repo ke `$HEX_DIR`
- Buat virtualenv di `$HEX_ENV`
- Install `requirements.txt` via pip dalam venv

Jika berhasil:

```text
HEX_OK=1
```

Jika gagal, skrip tetap lanjut dan memberi peringatan.

### 8. uv opsional

uv **default OFF**.

Aktifkan dengan:

```sh
sudo env GH0ST_INSTALL_UV=1 ./setup.sh
```

uv dipasang unmanaged ke:

```sh
$UV_HOME/bin
```

dan dibuat symlink global bila memungkinkan:

```text
/usr/local/bin/uv
/usr/local/bin/uvx
```

## Apa yang TIDAK Dipasang Otomatis

Skrip ini sengaja tidak memasang:

- Pi core
- API key / kredensial provider online
- Driver NVIDIA
- Tool eksternal HexStrike seperti:
  - nmap
  - masscan
  - gobuster
  - ffuf
  - sqlmap
  - nikto
  - hydra
  - john
  - hashcat
  - radare2
  - binwalk
  - pwntools
  - ghidra
- Chromium / ChromeDriver untuk browser agent HexStrike
- Ghidra / IDA / Hopper untuk REA native analysis
- JADX / JDK untuk Android analysis REA
- Build toolchain C++ kecuali kamu menjalankan fallback manual

Alasannya:

- Minim by default
- Beberapa tool memiliki implikasi legal/etis
- Beberapa dependensi berat dan jarang dibutuhkan semua pengguna
- Installer resmi / upstream bisa berubah
- Nama paket di Void/T4n OS harus diverifikasi sebelum dipasang

## Pasca Instalasi

 Setelah instalasi selesai, reload shell:

```sh
source ~/.bashrc
```

atau buka terminal baru.

Cek service llama:

```sh
sudo sv status llama
```

Cek log:

```sh
sudo sv log llama
```

Cek endpoint model:

```sh
curl -fsS http://127.0.0.1:8080/v1/models
```

Respons idealnya mengandung `"data"`.

Cek health HexStrike bila sudah dijalankan:

```sh
curl -fsS http://127.0.0.1:8888/health
```

## Menggunakan Pi + llama.cpp Lokal

### 1. Pastikan env sudah ter-load

```sh
echo "$LLAMA_SERVER_URL"
echo "$LLAMA_MODELS"
```

Expected:

```text
http://127.0.0.1:8080
/opt/gh0st-pi/models
```

### 2. Jalankan Pi

```sh
pi
```

### 3. Buka daftar model

Di dalam Pi:

```text
/models
```

Provider yang diharapkan:

```text
Llama.cpp
```

Model yang tersedia tergantung server:

- Qwen2.5-Coder-7B-Instruct
- Qwen2.5-Coder-3B-Instruct
- Qwen3-8B
- Qwen3-4B

### 4. Pilih model

Gunakan perintah `/models` untuk:

- Load model
- Switch model
- Unload model
- Lihat status:
  - Loaded
  - Loading
  - Failed
  - Sleeping
  - Unloaded

Catatan:

- Status `Sleeping` hanya muncul jika server dijalankan dengan `--sleep-idle-seconds`
- Mode single-model default tidak mendukung unload

### 5. Atur thinking level

Untuk tugas reasoning/CTF/RE kompleks, naikkan thinking level:

```text
high
xhigh
max
```

Sesuaikan dengan konteks dan sumber daya mesin.

## Menggunakan REA

REA adalah komponen manual/interaktif.

### 1. Pastikan Node.js memenuhi syarat

```sh
node -v
```

Syarat REA:

- 22.x >= 22.19
- 24.x >= 24.11
- 26+

### 2. Jalankan setup REA

```sh
npx rea-agents setup
```

Pilih agent yang kompatibel, misalnya Pi/Claude-compatible agent, lalu approve perubahan konfigurasi.

REA akan membuat backup konfigurasi yang ada.

### 3. Restart agent

Setelah setup, restart Pi atau agent yang kamu gunakan.

### 4. Native analysis opsional

Untuk analisis binary mendalam, siapkan salah satu:

- Ghidra
- Hopper
- IDA

REA dapat menggunakan instalasi yang sudah ada.

Untuk Android:

- JDK
- JADX headless

Untuk firmware:

- Binwalk
- Unblob

Linux membutuhkan `ps` compatible procps di PATH REA untuk proses ownership check. Paket `procps-ng` sudah dicoba dipasang oleh skrip.

### 5. Contoh penggunaan

Ajukan permintaan seperti:

```text
Inspect binary ini, tunjukkan bukti, dan jelaskan logika entrypoint-nya.
```

atau:

```text
Analisis aplikasi Electron ini, temukan modul, import, IPC boundary, dan jelaskan fitur search-nya.
```

## Menggunakan HexStrike AI MCP

HexStrike AI dijalankan sebagai MCP server on-demand, bukan service runit.

### 1. Start server

Opsi A — activate venv:

```sh
cd /opt/gh0st-pi/tools/hexstrike-ai
source hexstrike-env/bin/activate
python3 hexstrike_server.py --port 8888
```

Opsi B — panggil interpreter venv langsung:

```sh
/opt/gh0st-pi/tools/hexstrike-ai/hexstrike-env/bin/python \
  /opt/gh0st-pi/tools/hexstrike-ai/hexstrike_server.py \
  --port 8888
```

Debug:

```sh
python3 hexstrike_server.py --port 8888 --debug
```

### 2. Cek health

```sh
curl -fsS http://127.0.0.1:8888/health
```

### 3. Hubungkan ke MCP client

Contoh konfigurasi Claude Desktop:

```json
{
  "mcpServers": {
    "hexstrike-ai": {
      "command": "/opt/gh0st-pi/tools/hexstrike-ai/hexstrike-env/bin/python",
      "args": [
        "/opt/gh0st-pi/tools/hexstrike-ai/hexstrike_mcp.py",
        "--server",
        "http://localhost:8888"
      ],
      "timeout": 300,
      "disabled": false
    }
  }
}
```

Contoh konfigurasi VS Code:

```json
{
  "servers": {
    "hexstrike": {
      "type": "stdio",
      "command": "/opt/gh0st-pi/tools/hexstrike-ai/hexstrike-env/bin/python",
      "args": [
        "/opt/gh0st-pi/tools/hexstrike-ai/hexstrike_mcp.py",
        "--server",
        "http://localhost:8888"
      ]
    }
  }
}
```

Agent lain yang mendukung MCP seperti Cursor, Roo Code, 5ire, dll. dapat dikonfigurasi serupa.

### 4. Catatan integrasi Pi

README HexStrike AI tidak secara eksplisit menjamin integrasi langsung ke Pi. Menyambungkan HexStrike ke Pi memerlukan registrasi MCP manual di sisi Pi dan bergantung pada dukungan client tersebut.

Jangan berasumsi `pi` otomatis melihat tool HexStrike hanya karena server HexStrike berjalan.

### 5. Tool eksternal HexStrike

HexStrike MCP menyediakan wrapper terhadap banyak tool keamanan, tetapi tool eksternalnya tidak dipasang otomatis.

Contoh subset yang mungkin kamu butuhkan:

```sh
sudo xbps-install -S nmap masscan gobuster ffuf sqlmap nikto hydra john hashcat radare2 binwalk
```

Namun:

- Verifikasi nama paket di repository T4n OS / Void Linux
- Hanya install tool yang kamu pahami
- Hanya gunakan pada target berizin

### 6. Browser agent

Browser agent HexStrike membutuhkan Chromium/Chrome dan driver terkait. Ini tidak dipasang otomatis karena berat dan opsional.

## Upgrade ke Multi-Model / llama-swap

Secara default service berjalan single-model.

Jika kamu ingin multi-model routing atau swap, baca dokumentasi upstream terlebih dahulu:

- llama.cpp
- pi-llama-cpp
- llama-swap

Format `presets.ini` dan konfigurasi llama-swap dapat berubah antar versi.

### Konsep upgrade

Edit `/etc/sv/llama/run`, ganti bagian:

```sh
--model $LLAMA_MODELS/$DEFAULT_MODEL_FILE
```

menjadi mode router, misalnya:

```sh
--models-preset $LLAMA_MODELS/presets.ini
```

Tambahkan jika ingin model idle dilepas dari RAM:

```sh
--sleep-idle-seconds 300
```

Contoh fragment:

```sh
exec $LLAMA_BIN serve \
  --models-preset /opt/gh0st-pi/models/presets.ini \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 16384 \
  --n-gpu-layers 0 \
  --sleep-idle-seconds 300
```

Lalu restart:

```sh
sudo sv restart llama
```

> Penting: di mesin 16 GB, sleep/unload model idle sangat disarankan agar RAM tidak penuh.

## Tata Letak Penyimpanan SSD / HDD

Skrip menempatkan artefak berat di `/opt`.

### Pindahkan model GGUF ke HDD

Jika SSD 256 GB sesak, model adalah kandidat pertama untuk dipindah ke HDD, karena model umumnya dibaca saat load, bukan dieksekusi berulang seperti binary.

Saat instalasi:

```sh
sudo env LLAMA_MODELS=/mnt/hdd/gh0st-models ./setup.sh
```

Atau manual setelah instalasi:

1. Pindahkan file model ke HDD
2. Edit `/etc/sv/llama/run`
3. Edit rc user yang berisi `LLAMA_MODELS`
4. Restart service:

```sh
sudo sv restart llama
```

### Pindahkan konfigurasi Pi ke SSD

Direktori `~/.pi` bisa membesar saat coding/RE intensif.

Backup dulu, lalu:

```sh
mv ~/.pi /opt/gh0st-pi/pi
ln -s /opt/gh0st-pi/pi ~/.pi
```

Lakukan saat Pi tidak berjalan.

Risiko:

- Jika `/opt` tidak termount atau permission salah, Pi bisa rusak
- Pastikan mount SSD stabil

### Pindahkan npm cache ke SSD

Digunakan oleh:

```sh
npx rea-agents
pi install npm:...
```

Perintah:

```sh
npm config set cache /opt/gh0st-pi/npm-cache
```

## Troubleshooting

### Service llama tidak ready

Cek status:

```sh
sudo sv status llama
```

Cek log:

```sh
sudo sv log llama
```

Kemungkinan penyebab:

- Model default belum terunduh
- Nama file model salah
- Disk penuh
- Backend tidak cocok dengan mesin
- Binari llama tidak bisa dieksekusi karena linking/library

Cek model:

```sh
ls -lh /opt/gh0st-pi/models
```

Pastikan file default ada:

```text
Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
```

### `/health` 200 tapi Pi tidak melihat model

Gerbang sebenarnya untuk pilar `[1]` adalah:

```sh
curl -fsS http://127.0.0.1:8080/v1/models
```

Respons harus mengandung `"data"`.

Jika `/health`返回 200 tetapi `/v1/models` tidak mengembalikan daftar model, kemungkinan binari `llama serve` tidak kompatibel dengan API yang diharapkan `pi-llama-cpp`.

Solusi: gunakan fallback build `llama-server` dari source.

### Fallback build llama-server dari source

Ini adalah satu-satunya jalur yang secara eksplisit membutuhkan toolchain C++.

```sh
sudo xbps-install -S cmake make gcc

git clone --depth 1 https://github.com/ggml-org/llama.cpp /opt/llama/src
cd /opt/llama/src

cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/opt/llama

cmake --build build -j"$(nproc)"
cmake --install build
```

Lalu edit `/etc/sv/llama/run` agar memakai:

```sh
/opt/llama/bin/llama-server
```

Contoh:

```sh
exec /opt/llama/bin/llama-server \
  --model /opt/gh0st-pi/models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 16384 \
  --n-gpu-layers 0
```

Restart:

```sh
sudo sv restart llama
```

Catatan penting:

- `llama-server` dijalankan langsung
- Jangan tambahkan subcommand `serve` jika menggunakan binary `llama-server` hasil build source
- Binary `llama` dari installer resmi tetap bisa dipakai untuk CLI manual/pilar lain

### HexStrike pip install gagal build C-extension

Penyebab umum:

- Kurang `python3-devel`
- Kurang compiler
- Kurang header libffi/openssl/etc.
- Versi Python tidak cocok
- Jaringan terputus saat download wheel/source

Coba instal dependensi build setelah memverifikasi nama paket di repo T4n OS / Void:

```sh
sudo xbps-install -S python3-devel gcc libffi-devel
```

Lalu ulangi install requirements di venv HexStrike:

```sh
/opt/gh0st-pi/tools/hexstrike-ai/hexstrike-env/bin/pip install -r /opt/gh0st-pi/tools/hexstrike-ai/requirements.txt
```

> Jangan menebak nama paket. Verifikasi di package index distro kamu.

### Clone HexStrike gagal

Cek:

- Jaringan
- Akses GitHub
- URL repo
- Proxy/DNS

URL default:

```text
https://github.com/0x4m4/hexstrike-ai.git
```

Ulangi provisioning:

```sh
sudo ./setup.sh
```

### Node.js terlalu tua untuk REA

Skrip akan memberi warning jika Node tidak memenuhi syarat REA.

Upgrade Node sesuai mekanisme distro/T4n OS kamu, lalu jalankan:

```sh
npx rea-agents setup
```

### `ps` tidak ditemukan walau procps-ng dipasang

REA di Linux membutuhkan `ps` compatible procps pada PATH untuk cek kepemilikan proses.

Cek:

```sh
command -v ps
ps --version
```

Jika hilang, verifikasi paket `procps-ng` atau nama setara di repo T4n OS.

### Model download gagal

Skrip retry 3x per model. Jika masih gagal, unduh manual.

Contoh:

```sh
curl -fL -o /opt/gh0st-pi/models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
```

Lalu restart service:

```sh
sudo sv restart llama
```

### Ingin memaksa install ulang llama

```sh
sudo env FORCE_BUILD=1 ./setup.sh
```

### Ingin skip installer internal llama

```sh
sudo env GH0ST_SKIP_INSTALL=1 ./setup.sh
```

Catatan:

- Ini mengatur `SKIP_INSTALL=1` pada installer resmi
- Skrip tetap membuat symlink `/usr/local/bin/llama`
- Jika dikombinasikan dengan `LLAMA_VERSION`, upstream mungkin tidak memverifikasi pin secara ketat

## Uninstall Manual

Skrip ini tidak menyediakan `uninstall.sh` khusus. Berikut prosedur manual.

> Peringatan: perintah di bawah menghapus artefak di `/opt/gh0st-pi`, termasuk model GGUF dan venv HexStrike. Backup dulu jika diperlukan.

### 1. Stop dan hapus service llama

```sh
sudo sv stop llama
sudo rm -f /etc/runit/runsvdir/default/llama
sudo rm -rf /etc/sv/llama
```

### 2. Hapus artefak gh0st-pi

```sh
sudo rm -rf /opt/gh0st-pi
```

Jika kamu memakai path custom `GH0ST_ROOT`, hapus path tersebut.

### 3. Hapus symlink global

```sh
sudo rm -f /usr/local/bin/llama
sudo rm -f /usr/local/bin/uv
sudo rm -f /usr/local/bin/uvx
```

Hanya hapus symlink yang memang dibuat oleh skrip.

### 4. Bersihkan rc user

Hapus blok dengan marker:

```text
gh0st-pi-llama-env
```

dari file:

```text
~/.bashrc
~/.zshrc
~/.config/fish/config.fish
```

Backup rc biasanya dibuat oleh skrip dengan nama:

Contoh:

```text
~/.bashrc.gh0stbak.1760000000
```

### 5. Hapus fallback build llama jika ada

Jika kamu pernah menjalankan fallback source build:

```sh
sudo rm -rf /opt/llama
```

## Keamanan, Etika, dan Legalitas

Stack ini dapat mengakses tool keamanan, binary analysis, web scanning, exploit framework, dan automation agent.

Gunakan hanya untuk:

- Sistem milik sendiri
- Penetration testing dengan izin tertulis
- Bug bounty dalam scope program
- CTF competition
- Security research yang sah
- Red team exercise dengan persetujuan organisasi
- Interoperability research
- Software preservation
- Analisis malware di lingkungan terisolasi

Jangan gunakan untuk:

- Akses tidak sah
- Perusakan sistem
- Pencurian data
- Serangan terhadap target tanpa izin
- Aktivitas ilegal lainnya

### Rekomendasi operasional

- Jalankan di VM terisolasi atau lab khusus
- Jangan ekspos port `8080` dan `8888` ke jaringan luar
- Gunakan SSH tunnel jika perlu akses remote
- Monitor aktivitas AI agent
- Batasi `alwaysAllow` pada MCP client jika agent mendukung eksekusi otomatis
- Simpan bukti/hasil scan dengan aman
- Patuhi rules of engagement dan kebijakan organisasi

## Struktur Direktori

Struktur default:

```text
/opt/gh0st-pi/
├── llama/
│   └── .llama-app/
│       └── llama
├── models/
│   ├── Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
│   ├── Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf
│   ├── Qwen3-8B-Q4_K_M.gguf
│   └── Qwen3-4B-Q4_K_M.gguf
├── uv/
│   └── bin/
│       ├── uv
│       └── uvx
├── tools/
│   └── hexstrike-ai/
│       ├── hexstrike_server.py
│       ├── hexstrike_mcp.py
│       ├── requirements.txt
│       └── hexstrike-env/
└── workspace/
```

Service runit:

```text
/etc/sv/llama/
└── run
```

Symlink service:

```text
/etc/runit/runsvdir/default/llama -> /etc/sv/llama
```

Global symlink:

```text
/usr/local/bin/llama
/usr/local/bin/uv
/usr/local/bin/uvx
```

## Kredit

Projek ini berdiri di atas banyak upstream , antara lain:

- T4n OS
- Void Linux
- runit
- XBPS
- llama.cpp
- llama.app installer
- Pi coding agent
- pi-llama-cpp
- REA / morluto
- HexStrike AI
- Astral uv
- Hugging Face
- Unsloth model GGUF
- Seluruh maintainer paket dan tool keamanan yang digunakan secara terpisah

## Lisensi

[MIT](LICENSE) - Proyek Lainnya, mengikuti Lisensi Masing-Masing