# 🚦 Tek Kavşak Senaryoları

## 📁 Dosya Yapısı

```
data/scenarios/single_intersection_new/
├── single_tls.net.xml          # Network dosyası (kullanıcıdan alınacak)
├── traffic_low.rou.xml         # Düşük trafik (200 araç/saat)
├── traffic_medium.rou.xml      # Orta trafik (500 araç/saat)
├── traffic_high.rou.xml        # Yüksek trafik (1000 araç/saat)
├── fixed.add.xml               # Ek ayarlar
├── map_low.sumocfg             # Düşük trafik config
├── map_medium.sumocfg          # Orta trafik config
└── map_high.sumocfg            # Yüksek trafik config
```

## 🎯 Senaryolar

| Senaryo | Araç/Saat | Açıklama |
|---------|-----------|----------|
| **Düşük** | 200 | Hafif trafik, kolay öğrenme |
| **Orta** | 500 | Normal trafik yoğunluğu |
| **Yüksek** | 1000 | Yoğun trafik, zorlu senaryo |

## 🚀 Kullanım

### 1. Network Dosyasını Kopyala

```bash
# single_tls.net.xml dosyasını şuraya kopyala:
cp /path/to/single_tls.net.xml data/scenarios/single_intersection_new/
```

### 2. Düşük Trafik ile Eğitim

```bash
python3 src/train.py --algorithm dqn --config configs/single_low.yaml
```

### 3. Orta Trafik ile Eğitim

```bash
python3 src/train.py --algorithm dqn --config configs/single_medium.yaml
```

### 4. Yüksek Trafik ile Eğitim

```bash
python3 src/train.py --algorithm dqn --config configs/single_high.yaml
```

## 📊 Curriculum Learning

Sırayla eğitmek için:

1. **Düşük trafik** → Model temel öğrenir
2. **Orta trafik** → Model gelişir
3. **Yüksek trafik** → Model zorlu senaryoda çalışır

## ⚠️ Not

`single_tls.net.xml` dosyasını Desktop'tan veya başka bir yerden kopyalaman gerekiyor. Route dosyaları otomatik oluşturuldu.
