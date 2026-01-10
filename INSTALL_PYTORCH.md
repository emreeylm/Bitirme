# PyTorch Kurulumu

PyTorch SSL sertifika sorunları nedeniyle otomatik yüklenemedi. Manuel olarak yüklemek için:

## Yöntem 1: SSL doğrulamasını atlayarak (Önerilen)

```bash
cd /Users/emre/Desktop/developers/Bitirme
source venv/bin/activate

# SSL doğrulamasını geçici olarak devre dışı bırak
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## Yöntem 2: Conda kullanarak (Alternatif)

```bash
conda install pytorch torchvision torchaudio cpuonly -c pytorch
```

## Yöntem 3: Sistem sertifikalarını güncelleme

macOS'ta Python'un sistem sertifikalarını kullanması için:

```bash
# Python sertifika yolunu kontrol et
python3 -c "import ssl; print(ssl.get_default_verify_paths())"

# Homebrew Python kullanıyorsanız:
/Applications/Python\ 3.*/Install\ Certificates.command
```

## Yöntem 4: pip'i güncelleyip tekrar deneyin

```bash
pip install --upgrade pip
pip install torch
```

## Kontrol

PyTorch yüklendikten sonra:

```bash
python3 -c "import torch; print('PyTorch:', torch.__version__)"
```

## Not

PyTorch olmadan da projenin çoğu kısmı çalışır (SUMO environment, visualization, metrics). Sadece RL algoritmaları (DQN, MADDPG, QMIX) PyTorch gerektirir.
