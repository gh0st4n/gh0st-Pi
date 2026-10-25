finalize() {
  if [ -n "$REAL_USER" ] && [ "$REAL_USER" != "root" ]; then
    info "chown -> $REAL_USER : $GH0ST_ROOT (seluruh artefak SSD, incl. venv & cache pip HexStrike)"
    chown -R "$REAL_USER" "$GH0ST_ROOT" 2>/dev/null || true
  fi

  shell=""
  if [ -n "$REAL_HOME" ]; then
    if [ -f "$REAL_HOME/.bashrc" ]; then shell="$REAL_HOME/.bashrc"; fi
    if [ -f "$REAL_HOME/.zshrc" ]; then shell="$REAL_HOME/.zshrc"; fi
    if [ -f "$REAL_HOME/.config/fish/config.fish" ]; then shell="$REAL_HOME/.config/fish/config.fish"; fi
  fi

  info "================ gh0st-pi provisioning selesai ================"
  info "llama bin     : ${LLAMA_BIN:-?}   (symlink: /usr/local/bin/llama)"
  info "llama home    : $LLAMA_HOME  (SSD)"
  info "models dir    : $LLAMA_MODELS  (SSD; knob HDD lihat [H])"
  info "uv bin        : ${UV_BIN:-?}   (DEFAULT OFF; symlink global bila aktif)"
  info "backend       : $GH0ST_BACKEND"
  info "service llama : sudo sv status llama | logs: sudo sv log llama"
  info "endpoint llama: http://127.0.0.1:$PORT (localhost-only)"
  info "HexStrike     : $HEX_DIR (venv: $HEX_ENV)  status=$([ "$HEX_OK" = 1 ] && echo SIAP || echo 'BELUM SIAP (lihat [E])')"
  info "workspace     : $WORKSPACE"

  if [ -n "$FAILED" ]; then
    warn "Model GAGAL unduh (ulangi/manual):$FAILED"
  fi

  if [ -n "$shell" ]; then
    info "Reload shell  : source $shell (atau terminal baru)"
  fi

  cat <<EOF
----------------------- NEXT STEPS (interaktif / manual) -----------------------
[ A ] Offline via Pi (llama.cpp)
1. Shell baru (atau source $shell) -> LLAMA_SERVER_URL ter-set.
2. Jalankan 'pi' lalu '/models' -> provider "Llama.cpp" muncul dgn model
Qwen2.5-Coder-7B/3B + Qwen3-8B/4B (status Loaded/Sleeping/Unloaded).
Set thinking level (off..max); utk CTF/reasoning naikkan high/xhigh.
(Utk server ber-API-key: 'llama serve --api-key <k>' lalu '/login' di Pi.)
3. Ganti model default service: edit DEFAULT_MODEL_FILE -> 'sudo sv restart llama',
ATAU upgrade router/llama-swap ([D]).
4. Ekstensi Pi terpasang (best-effort): pi-llama-cpp, pi-agent-modes, pi-themes,
pi-manage-todo-list, pi-redteam, pi-security-analysis. Bila ada yang gagal
(Pi interaktif / jaringan), ulangi manual sbg user: 'pi install npm:<ext>'.

[ B ] Online providers (DeepSeek / Qwen / GLM-Z.AI / OpenRouter)
- Halaman MODELS Pi sudah memuat 1598 model + pricing; tinggal isi kunci:
di Pi jalankan '/login' -> pilih provider -> paste API key. (Skrip sengaja
tak menaruh kredensial.)
- Strategi: online ctx-besar (DeepSeek V4 / GLM-5.3 ~1M tok) utk coding
hardcore & RE kode raksasa; llama.cpp offline utk sampel malware/privasi
& no-net -> cocok pilar [2] & [3].

[ C ] REA (morluto/rea) -> pilar [2] reverse engineering / bug hunting
1. Pastikan Node >=22 (sudah dicek via node_ok; bila <22 upgrade dulu).
2. 'npx rea-agents setup' -> pilih agent "Pi"/Claude-compatible, review &
APPROVE (REA backup config existing), lalu RESTART Pi.
3. Native/Android opsional: Ghidra+JDK21 (atau Hopper/IDA) & headless JADX
sesuai target; REA start engine saat dibutuhkan. Linux butuh
procps-compatible 'ps' di PATH REA utk cek kepemilikan proses (paket
'procps-ng' sudah di-install di atas).
4. Uji: "inspect <binary/APK>, tunjukkan bukti, jelaskan logika entrypoint".

[ D ] Upgrade offline ke multi-model / swap (OPSIONAL, verifikasi dulu)
- pi-llama-cpp dukung router (--models-preset) & llama-swap. Format
presets.ini / config llama-swap TIDAK dijamin sama antar versi llama.cpp:
CEK docs ggml-org/llama.cpp & mostlygeek/llama-swap versi kamu.
- Setelah yakin, ganti blok exec di /etc/sv/llama/run dr --model menjadi
--models-preset $LLAMA_MODELS/presets.ini (+ --sleep-idle-seconds N agar
model idle dilepas dr RAM => penting di 16GB; ini juga mengaktifkan
indikator 'Sleeping' di Pi), lalu 'sudo sv restart llama'.
- overrides per-model (cost/contextSize/reasoning/capabilities) di
~/.pi/agent/settings.json key "llamaSettings" (jangan timpa config existing).

[ E ] HexStrike AI -> pilar [4]  (MCP server on-demand; BUKAN service runit)
STATUS provisioning: $([ "$HEX_OK" = 1 ] && echo "SIAP (venv + requirements terpasang)" || echo "BELUM SIAP -> kerjakan langkah pemulihan di bawah sebelum pakai")
1. Start server MCP (pilih salah satu; venv di $HEX_ENV):
cd $HEX_DIR && source hexstrike-env/bin/activate && python3 hexstrike_server.py --port $HEX_PORT
ATAU tanpa activate (panggil interpreter venv langsung):
$HEX_ENV/bin/python $HEX_DIR/hexstrike_server.py --port $HEX_PORT
Debug: tambah --debug ; custom port: --port N. Health: curl http://127.0.0.1:$HEX_PORT/health
2. Hubungkan ke agent via MCP (contoh dari README HexStrike):
- Claude Desktop (~/.config/Claude/claude_desktop_config.json):
"mcpServers": { "hexstrike-ai": { "command": "$HEX_ENV/bin/python",
"args": ["$HEX_DIR/hexstrike_mcp.py","--server","http://localhost:$HEX_PORT"],
"timeout": 300, "disabled": false } }
- VS Code (.vscode/settings.json): servers.hexstrike { type:"stdio",
command:"$HEX_ENV/bin/python", args:["$HEX_DIR/hexstrike_mcp.py","--server","http://localhost:$HEX_PORT"] }
- Agent lain yang dukung MCP: Cursor, Roo Code, 5ire, dsb.
CATATAN JUJUR: README HexStrike TIDAK menyebut integrasi ke Pi. Menyambung
HexStrike ke Pi butuh registrasi MCP manual di sisi Pi (bukan dijamin
upstream). Jangan berasumsi 'pi' langsung melihat tool HexStrike.
3. PEMULIHAN bila [E] status BELUM SIAP:
- clone gagal  -> cek jaringan/URL $REPO_HEX ; ulangi 'sudo sh setup.sh'
- venv/pip hilang -> pada Void pastikan python3 lengkap (ensurepip bundled);
verifikasi nama paket di voidlinux.org/packages bila perlu python3-venv/devel.
- 'pip install -r requirements.txt' gagal build C-extension -> biasanya
butuh python3-devel + gcc + libffi(-dev) + header terkait. Verifikasi
NAMA paketnya di voidlinux.org/packages (JANGAN menebak), install, lalu:
$HEX_ENV/bin/pip install -r $HEX_DIR/requirements.txt
4. Tool eksternal HexStrike (nmap/masscan/gobuster/ffuf/sqlmap/nikto/hydra/
john/hashcat/radare2/binwalk/pwntools/...) TIDK dipasang skrip ini
(minim by default + legal scope). Install subset yang kamu pahami &
BERWENANG uji, mis: sudo xbps-install -S nmap masscan gobuster ffuf sqlmap
nikto hydra john hashcat radare2 binwalk   (verifikasi nama per paket).
5. Browser agent (screenshot/DOM) butuh chromium + chromedriver (atau
google-chrome) -> opsional, install manual; TIDK auto (berat, minim).
6. DISCIPLINE (dari README HexStrike & REA): jalankan di lingkungan terisolasi;
HANYA target milikmu / ber-authorization tertulis (pentest berizin, bug
bounty in-scope, CTF, riset). Jangan uji sistem tanpa izin.

[ F ] Ekosistem T4n Labs -> pilar [3]
- Clone repo kerja ke $WORKSPACE ; pakai Pi (online utk refactor besar,
offline llama utk kode sensitif) + automation via mode RPC/JSON Pi
(pi -p / stdin-stdout JSONL) utk pipeline CI lokal & script sederhana.
- uv (bila GH0ST_INSTALL_UV=1) tersedia sbg frontend venv/pip universal utk
tool python ad-hoc; TIDK dipakai llama.app/HexStrike/REA/Pi (jalur default).
- HexStrike (bila [E] SIAP) bisa jadi MCP tool-chain utk otomasi pentest
ber-izin; tetap tunduk disiplin authorized-scope di [E].6.

[ G ] FALLBACK pilar [1] kalau 'llama serve' TIDAK kompatibel API pi-llama-cpp
Gejala: service UP, /health 200, tapi /v1/models tak kembalikan 'data' => Pi
buta model. Solusi: build llama-server dari source (flag-nya kita YAKINI
kompatibel pi-llama-cpp). INI SATU-SATUNYA tempat toolchain C++ dipakai:
sudo xbps-install -S cmake make gcc
git clone --depth 1 https://github.com/ggml-org/llama.cpp /opt/llama/src
cd /opt/llama/src && cmake -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/llama
cmake --build build -j"\$(nproc)" && cmake --install build
# lalu edit /etc/sv/llama/run: exec /opt/llama/bin/llama-server --model ...
# (llama-server LANGSUNG, TANPA subcommand 'serve'), lalu:
sudo sv restart llama
'llama' (installer resmi) tetap dipakai utk CLI manual / pilar lain; hanya
PILAR [1] yg mundur ke llama-server.

[ H ] TATA LETAK PENYIMPANAN (SSD /opt vs HDD ~)  ->  opsional, manual
Skrip ini sudah menaruh SEMUA artefak berat di /opt (SSD), incl. venv &
cache pip HexStrike. Dua hal yang SENGAJA TIDK disentuh karena per-user /
berisiko, tapi bisa kamu pindahkan:
(1) Model GGUF ke HDD bila SSD 256GB sesak (load sekali saat start, bukan
eksekusi berulang => kandidat pertama turun ke HDD; binari/venv TETAP SSD):
# saat install:  sudo env LLAMA_MODELS=/mnt/hdd/gh0st-models sh setup.sh
# ATAU edit /etc/sv/llama/run (baris --model & export LLAMA_MODELS)
#   + rc export LLAMA_MODELS, lalu 'sudo sv restart llama'.
(2) Config+sesi Pi (~/.pi, bisa membesar saat coding/RE intensif) ke SSD
via symlink UNIX (lakukan saat Pi TIDK jalan; BACKUP dulu):
mv ~/.pi /opt/gh0st-pi/pi && ln -s /opt/gh0st-pi/pi ~/.pi
Risiko: kalau /opt unmount/permission salah, Pi rusak -> pastikan mount.
(3) npm cache (dipakai 'npx rea-agents' & 'pi install npm:') ke SSD:
npm config set cache /opt/gh0st-pi/npm-cache
rc user (~/.bashrc dll) TETAP di HDD by-design: shell harus baca dari \$HOME,
dan isinya cuma 'export LLAMA_MODELS/LLAMA_SERVER_URL' (pointer, bukan data).
--------------------------------------------------------------------------------
EOF
}