# Proje Yapısı

```
Bitirme/
├── src/                          # Kaynak kodlar
│   ├── __init__.py
│   ├── train.py                  # Ana eğitim scripti
│   ├── environment/              # SUMO-TraCI ortamı
│   │   ├── __init__.py
│   │   ├── sumo_env.py           # Gymnasium benzeri SUMO ortamı
│   │   └── traffic_agent.py     # Ajan state-action-reward tanımları
│   ├── algorithms/               # RL algoritmaları
│   │   ├── __init__.py
│   │   ├── dqn.py                # DQN implementasyonu
│   │   ├── maddpg.py             # MADDPG implementasyonu
│   │   └── qmix.py               # QMIX implementasyonu
│   └── utils/                    # Yardımcı fonksiyonlar
│       ├── __init__.py
│       ├── visualization.py      # Grafik çizim fonksiyonları
│       └── metrics.py            # Metrik hesaplama fonksiyonları
│
├── configs/                      # Yapılandırma dosyaları
│   └── default.yaml              # Varsayılan konfigürasyon
│
├── experiments/                  # Deney sonuçları
│   ├── logs/                     # Eğitim logları
│   ├── results/                  # Sonuç grafikleri
│   └── checkpoints/              # Model checkpoint'leri
│
├── docs/                         # Dokümantasyon
│   ├── report/                   # Bitirme projesi raporu
│   │   ├── README.md
│   │   ├── giris.md              # Giriş bölümü ✅
│   │   ├── yontem.md             # Yöntem bölümü ✅
│   │   ├── literatur.md          # Literatür (hazırlanacak)
│   │   ├── deney.md              # Deneyler (hazırlanacak)
│   │   └── sonuc.md              # Sonuç (hazırlanacak)
│   └── api/                      # API dokümantasyonu
│
├── tests/                        # Test dosyaları
│   └── test_environment.py
│
├── data/                         # Veri dosyaları
│   ├── scenarios/                # Trafik senaryoları
│   └── osm/                      # OpenStreetMap dosyaları
│
├── scripts/                      # Yardımcı scriptler
│
├── README.md                     # Proje README ✅
├── requirements.txt              # Python bağımlılıkları ✅
├── setup.py                      # Paket kurulum dosyası ✅
├── .gitignore                    # Git ignore dosyası ✅
└── PROJECT_STRUCTURE.md          # Bu dosya
```

## Dosya Açıklamaları

### Kaynak Kodlar (`src/`)

- **`train.py`**: Ana eğitim scripti. DQN, MADDPG, QMIX algoritmalarını çalıştırır.
- **`environment/sumo_env.py`**: SUMO-TraCI entegrasyonu ile Gymnasium benzeri ortam.
- **`environment/traffic_agent.py`**: Ajan state, action, reward tanımları.
- **`algorithms/`**: RL algoritmalarının implementasyonları.

### Yapılandırma (`configs/`)

- **`default.yaml`**: Varsayılan hiperparametreler ve ortam ayarları.

### Dokümantasyon (`docs/`)

- **`report/`**: Bitirme projesi raporunun bölümleri (Markdown formatında).
- **`api/`**: Kod dokümantasyonu (gelecekte eklenecek).

### Veri (`data/`)

- SUMO network, route ve configuration dosyaları.
- OpenStreetMap'ten oluşturulmuş yol ağları.

## Kullanım

### 1. Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# SUMO'yu kur (macOS)
brew install sumo

# SUMO_HOME ortam değişkenini ayarla
export SUMO_HOME=/usr/local/opt/sumo
```

### 2. Eğitim

```bash
# DQN ile tek kavşak eğitimi
python src/train.py --algorithm dqn --config configs/default.yaml

# MADDPG ile çok kavşak eğitimi
python src/train.py --algorithm maddpg --scenario multi_intersection

# QMIX ile eğitim
python src/train.py --algorithm qmix --scenario grid_network
```

### 3. Değerlendirme

```bash
# Eğitilmiş modeli değerlendir
python src/evaluate.py --checkpoint experiments/checkpoints/dqn_episode_1000.pt
```

## Sonraki Adımlar

1. ✅ Proje yapısı oluşturuldu
2. ✅ Temel kod iskeleti hazırlandı
3. ✅ Giriş ve Yöntem bölümleri yazıldı
4. ⏳ SUMO senaryoları oluşturulacak
5. ⏳ Literatür bölümü yazılacak
6. ⏳ Deneyler yapılacak ve sonuçlar analiz edilecek
7. ⏳ Rapor tamamlanacak
