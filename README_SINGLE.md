# 🚦 Tek Kavşak Eğitim Rehberi

## ✅ Hazırlanan Dosyalar

### Senaryo Dosyaları
- ✅ `traffic_low.rou.xml` - Düşük trafik (200 araç/saat)
- ✅ `traffic_medium.rou.xml` - Orta trafik (500 araç/saat)
- ✅ `traffic_high.rou.xml` - Yüksek trafik (1000 araç/saat)
- ✅ `map_low.sumocfg` - Düşük trafik config
- ✅ `map_medium.sumocfg` - Orta trafik config
- ✅ `map_high.sumocfg` - Yüksek trafik config
- ✅ `fixed.add.xml` - Ek ayarlar

### Konfigürasyon Dosyaları
- ✅ `configs/single_low.yaml` - Düşük trafik eğitim
- ✅ `configs/single_medium.yaml` - Orta trafik eğitim
- ✅ `configs/single_high.yaml` - Yüksek trafik eğitim

## ⚠️ Eksik Dosya

**`single_tls.net.xml`** dosyasını Desktop'tan kopyalaman gerekiyor:

```bash
# Dosyayı bul
find ~/Desktop -name "single_tls.net.xml"

# Kopyala
cp /path/to/single_tls.net.xml data/scenarios/single_intersection_new/
```

Veya otomatik kurulum:

```bash
./setup_single_map.sh
```

## 🚀 Eğitim Başlatma

### 1. Düşük Trafik (Başlangıç)

```bash
export SUMO_HOME=/opt/homebrew/opt/sumo/share/sumo
export PYTHONPATH=$PYTHONPATH:$SUMO_HOME/tools
source venv/bin/activate

python3 src/train.py --algorithm dqn --config configs/single_low.yaml
```

### 2. Orta Trafik

```bash
python3 src/train.py --algorithm dqn --config configs/single_medium.yaml
```

### 3. Yüksek Trafik

```bash
python3 src/train.py --algorithm dqn --config configs/single_high.yaml
```

## 📊 Curriculum Learning Stratejisi

1. **Düşük trafik** ile başla (kolay öğrenme)
2. Checkpoint'i kaydet
3. **Orta trafik** ile devam et (checkpoint'ten başlat)
4. **Yüksek trafik** ile bitir (zorlu senaryo)

## 📁 Checkpoint'ler

- Düşük: `experiments/checkpoints/single_low/`
- Orta: `experiments/checkpoints/single_medium/`
- Yüksek: `experiments/checkpoints/single_high/`

## 🔄 Eski Map'ler

Eski map'ler yedeklendi:
- `data/scenarios/bursa_old/` (12 kavşak)
- `data/scenarios/single_intersection_old/` (eski tek kavşak)

İhtiyaç olursa geri getirebilirsin.
