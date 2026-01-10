# 🚀 Tek Kavşak Eğitimi Başlatma

## ✅ Hazırlık Tamamlandı

- ✅ Network dosyası: `single_tls.net.xml` (kopyalandı)
- ✅ Route dosyaları: Düşük/Orta/Yüksek trafik hazır
- ✅ Config dosyaları: Tüm senaryolar için hazır
- ✅ Environment: Test edildi ve çalışıyor

## 🎯 Eğitimi Başlatma

### Yöntem 1: Script ile (Kolay)

```bash
cd /Users/emre/Desktop/developers/Bitirme

# Düşük trafik
./train_single.sh low

# Orta trafik
./train_single.sh medium

# Yüksek trafik
./train_single.sh high
```

### Yöntem 2: Manuel

```bash
cd /Users/emre/Desktop/developers/Bitirme
export SUMO_HOME=/opt/homebrew/opt/sumo/share/sumo
export PYTHONPATH=$PYTHONPATH:$SUMO_HOME/tools
source venv/bin/activate

# Düşük trafik ile başla
python3 src/train.py --algorithm dqn --config configs/single_low.yaml
```

## 📊 Senaryolar

| Senaryo | Araç/Saat | Episode | Süre |
|---------|-----------|---------|------|
| **Düşük** | 200 | 1000 | ~30-40 dk |
| **Orta** | 500 | 1000 | ~30-40 dk |
| **Yüksek** | 1000 | 1000 | ~30-40 dk |

## 💡 Önerilen Sıra

1. **Düşük trafik** ile başla (kolay öğrenme)
2. Checkpoint'i kaydet
3. **Orta trafik** ile devam et
4. **Yüksek trafik** ile bitir

## 📁 Checkpoint'ler

- Düşük: `experiments/checkpoints/single_low/`
- Orta: `experiments/checkpoints/single_medium/`
- Yüksek: `experiments/checkpoints/single_high/`

## ⏸️ Durdurma

`Ctrl+C` ile güvenle durdurabilirsin. Checkpoint'ler otomatik kaydedilir.

## 📈 İlerlemeyi İzleme

Her 10 episode'da bir ilerleme yazdırılır:
```
Episode 10/1000 | Reward: -123.45 | Loss: 0.0123 | Epsilon: 0.950
```
