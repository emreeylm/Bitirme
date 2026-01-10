# Şehir İçi Trafik Akışının Çok Ajanlı Takviyeli Öğrenme ile Optimizasyonu

## 📋 Proje Özeti

Bu proje, şehir içi kavşaklarda trafik ışıklarını optimize etmek için **Çok Ajanlı Takviyeli Öğrenme (MARL)** tabanlı bir akıllı trafik yönetim sistemi geliştirmeyi amaçlamaktadır.

### Problem
Günümüzde kullanılan sabit zamanlı veya kural tabanlı sinyalizasyon sistemleri trafik yoğunluğundaki değişimlere uyum sağlayamadığı için verimsiz kalmaktadır. Bu durum:
- Bekleme sürelerinin artmasına
- Yakıt tüketimi ve karbon salınımının yükselmesine
- Kavşaklarda yoğun tıkanıklıklara

sebep olmaktadır.

### Çözüm
Her kavşağı bir "ajan" olarak modelleyip, bu ajanların hem kendi kavşak durumlarını hem de komşu kavşaklardan gelen bilgileri kullanarak koordineli öğrenme yapmasını sağlayan bir sistem.

## 🛠️ Teknolojiler

- **SUMO** — Mikro trafik simülasyonu
- **TraCI** — SUMO ↔️ Python gerçek zamanlı entegrasyonu
- **PyTorch** — Sinir ağları
- **DQN, MADDPG, QMIX** — RL ve MARL algoritmaları
- **OpenAI Gym benzeri çevre** — Eğitim için standart yapı

## 🎯 Beklenen Çıktılar

- Ortalama bekleme süresinde **%20+** iyileşme
- Duruş sayısında **%15+** azalma
- Yakıt tüketimi ve emisyonlarda **%10+** azalma
- Açık kaynak kodlu bir MARL trafik kontrol altyapısı

## 📁 Proje Yapısı

```
Bitirme/
├── src/                    # Kaynak kodlar
│   ├── environment/        # SUMO-TraCI ortamı
│   ├── agents/            # RL ajanları
│   ├── algorithms/        # DQN, MADDPG, QMIX
│   └── utils/             # Yardımcı fonksiyonlar
├── configs/               # Yapılandırma dosyaları
├── experiments/           # Deney sonuçları ve loglar
├── docs/                  # Dokümantasyon ve rapor
├── tests/                 # Test dosyaları
├── data/                  # Trafik senaryoları ve OSM dosyaları
└── scripts/               # Yardımcı scriptler
```

## 🚀 Kurulum

```bash
# Gereksinimleri yükle
pip install -r requirements.txt

# SUMO'yu sisteminize kurun (https://sumo.dlr.de/docs/Installing/index.html)
# macOS için:
brew install sumo

# TraCI Python bağlantısını kontrol edin
python -c "import traci; print('SUMO TraCI bağlantısı başarılı!')"
```

## 📊 Kullanım

```bash
# Tek kavşak için DQN eğitimi
python src/train.py --algorithm dqn --scenario single_intersection

# Çok kavşak için MADDPG eğitimi
python src/train.py --algorithm maddpg --scenario multi_intersection

# QMIX ile eğitim
python src/train.py --algorithm qmix --scenario grid_network
```

## 📝 Dokümantasyon

Detaylı dokümantasyon için `docs/` klasörüne bakın:
- `docs/report/` - Bitirme projesi raporu
- `docs/api/` - API dokümantasyonu

## 📄 Lisans

Bu proje akademik araştırma amaçlı geliştirilmiştir.

## 👤 Yazar

Bitirme Projesi - Trafik Yönetimi için MARL
