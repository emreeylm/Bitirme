# Hızlı Başlangıç Kılavuzu

## ✅ Durum Kontrolü

Proje yapısı hazır! Şimdi bağımlılıkları yükleyip çalıştıralım.

## 1. Virtual Environment Oluşturma

```bash
cd /Users/emre/Desktop/developers/Bitirme
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# veya
# venv\Scripts\activate  # Windows
```

## 2. Bağımlılıkları Yükleme

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Not:** Eğer PyTorch yükleme sorunu yaşarsanız:
```bash
# CPU versiyonu için
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# veya CUDA için (NVIDIA GPU varsa)
pip install torch torchvision torchaudio
```

## 3. SUMO Kurulumu Kontrolü

SUMO zaten kurulu görünüyor. Kontrol edin:

```bash
which sumo
sumo --version
```

SUMO_HOME'u ayarlayın (`.bashrc` veya `.zshrc` dosyanıza ekleyin):

```bash
export SUMO_HOME=/opt/homebrew/opt/sumo/share/sumo
export PATH=$PATH:$SUMO_HOME/bin
export PYTHONPATH=$PYTHONPATH:$SUMO_HOME/tools
```

## 4. Test Çalıştırma

### Import Testleri

```bash
python3 test_imports.py
```

Bu test tüm modüllerin doğru import edilip edilmediğini kontrol eder.

### SUMO Bağlantı Testi

```bash
python3 test_run.py
```

Bu test SUMO'nun başlatılıp başlatılamadığını kontrol eder.

## 5. Eğitim Başlatma

### DQN ile Tek Kavşak

```bash
python src/train.py --algorithm dqn --config configs/default.yaml
```

### MADDPG ile Çok Kavşak

```bash
python src/train.py --algorithm maddpg --scenario multi_intersection
```

### QMIX ile Eğitim

```bash
python src/train.py --algorithm qmix --scenario grid_network
```

## 6. Senaryo Dosyaları

Basit bir tek kavşak senaryosu hazır:
- `data/scenarios/single_intersection/single_intersection.net.xml`
- `data/scenarios/single_intersection/single_intersection.rou.xml`
- `data/scenarios/single_intersection/single_intersection.sumocfg`

## Sorun Giderme

### TraCI Import Hatası

```bash
export SUMO_HOME=/opt/homebrew/opt/sumo/share/sumo
export PYTHONPATH=$PYTHONPATH:$SUMO_HOME/tools
python3 -c "import traci; print('OK')"
```

### PyTorch Kurulum Sorunu

```bash
# Önce pip'i güncelleyin
pip install --upgrade pip

# Sonra PyTorch'u yükleyin
pip install torch
```

### SUMO Bağlantı Hatası

SUMO'nun çalıştığından emin olun:
```bash
sumo --version
```

Port çakışması varsa farklı bir port kullanın (test_run.py'de).

## Sonraki Adımlar

1. ✅ Bağımlılıkları yükleyin
2. ✅ Test scriptlerini çalıştırın
3. ✅ Senaryo dosyalarını kontrol edin
4. ⏳ Eğitimi başlatın
5. ⏳ Sonuçları analiz edin

## Yardım

Sorun yaşarsanız:
- `test_imports.py` ile import sorunlarını kontrol edin
- `test_run.py` ile SUMO bağlantısını test edin
- Log dosyalarını kontrol edin: `experiments/logs/`
