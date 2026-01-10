# 🧠 DQN (Deep Q-Network) Modeli Açıklaması

## 📖 Tanım

**DQN (Deep Q-Network)**, trafik durumunu gözlemleyip **en iyi fazı öğrenerek** seçen bir yapay zeka modelidir. Deneyimlerden öğrenir ve zamanla daha iyi kararlar verir.

## 🔄 Nasıl Çalışır?

### Temel Prensip

1. **Gözlem (Observation)**: Trafik durumunu analiz eder
   - Kuyruk uzunlukları
   - Bekleme süreleri
   - Araç sayıları
   - Mevcut faz bilgisi

2. **Karar Verme**: Sinir ağı ile en iyi fazı seçer
   - Her faz için Q-değeri hesaplar
   - En yüksek Q-değerine sahip fazı seçer

3. **Öğrenme**: Deneyimlerden öğrenir
   - Hangi durumda hangi fazın daha iyi olduğunu öğrenir
   - Reward'lardan geri bildirim alır

### Öğrenme Süreci

```
Episode 1:   Random gibi davranır (keşif)
Episode 100: Bazı kalıpları öğrenmeye başlar
Episode 500: İyi kararlar vermeye başlar
Episode 1000: Optimize edilmiş politika
```

## 💻 Kodda Nasıl Çalışıyor?

### 1. Gözlem (State)

```python
# Trafik durumunu gözlemle
state = [
    queue_lengths,      # Kuyruk uzunlukları
    waiting_times,      # Bekleme süreleri
    vehicle_counts,     # Araç sayıları
    current_phase,      # Mevcut faz
    phase_duration      # Faz süresi
]
```

### 2. Q-Network (Sinir Ağı)

```python
# Her faz için Q-değeri hesapla
q_values = q_network(state)
# Örnek: [2.5, 1.8, 3.2, 1.1]
#         Faz0 Faz1 Faz2 Faz3

# En yüksek Q-değerine sahip fazı seç
action = q_values.argmax()  # Faz 2 seçildi (3.2 en yüksek)
```

### 3. Öğrenme (Training)

```python
# Deneyimleri sakla
replay_buffer.push(state, action, reward, next_state, done)

# Batch'lerden öğren
loss = train(replay_buffer.sample(batch_size))

# Q-değerlerini güncelle
# "Bu durumda Faz 2 seçmek iyi bir karardı" → Öğren!
```

## 🎯 Neden Daha İyi?

### 1. **Adaptif (Uyum Sağlayan)**

| Durum | Random | Fixed-Time | **DQN** |
|-------|--------|------------|---------|
| Yoğun trafik | Rastgele | Sabit süre | **Uzun yeşil verir** ✅ |
| Boş yollar | Rastgele | Sabit süre | **Hızlı geçiş** ✅ |
| Değişken trafik | Rastgele | Sabit süre | **Dinamik uyum** ✅ |

### 2. **Öğrenme Yeteneği**

```
Episode 1:   "Kuzey yönüne yeşil vermek iyi oldu" → Öğren
Episode 10:  "Kuzey yoğunsa uzun yeşil vermek daha iyi" → Öğren
Episode 100: "Sabah saatlerinde kuzey yoğun oluyor" → Öğren
```

### 3. **Optimizasyon**

- **Random**: Hiç optimizasyon yok
- **Fixed-Time**: Manuel optimizasyon (trafik mühendisi yapar)
- **DQN**: **Otomatik optimizasyon** (kendisi öğrenir) ✅

## 📊 Karşılaştırma Tablosu

| Özellik | Random | Fixed-Time | **DQN** |
|---------|--------|------------|---------|
| Trafiğe Uyum | ❌ Yok | ❌ Yok | ✅ **Var** |
| Öğrenme | ❌ Yok | ❌ Yok | ✅ **Var** |
| Optimizasyon | ❌ Yok | ⚠️ Manuel | ✅ **Otomatik** |
| Performans | ⭐ Kötü | ⭐⭐ Orta | ⭐⭐⭐ **İyi** |
| Tutarlılık | ❌ Yok | ✅ Var | ✅ **Var** |
| Adaptasyon | ❌ Yok | ❌ Yok | ✅ **Var** |

## 🎬 Senaryo Örnekleri

### Senaryo 1: Sabah Yoğunluğu

**Durum**: Sabah 8:00, kuzey yönünde 100 araç kuyruk

- **Random**: Rastgele faz → Belki güneye yeşil (100 araç bekler!)
- **Fixed-Time**: 42s sonra kuzeye yeşil (100 araç bekler)
- **DQN**: Kuzeyi görür → Hemen kuzeye yeşil verir ✅

**Sonuç**: DQN en az bekleme süresi sağlar

### Senaryo 2: Gece Boş Yollar

**Durum**: Gece 2:00, hiç araç yok

- **Random**: Rastgele faz → Gereksiz bekletir
- **Fixed-Time**: 42s bekletir (oysa kimse yok)
- **DQN**: Boş yolları görür → Hızlı geçiş sağlar ✅

**Sonuç**: DQN en verimli

### Senaryo 3: Değişken Trafik

**Durum**: Trafik yoğunluğu sürekli değişiyor

- **Random**: Rastgele → Tutarsız
- **Fixed-Time**: Sabit → Değişime uyum sağlayamaz
- **DQN**: Değişikliği algılar → Dinamik uyum ✅

**Sonuç**: DQN en adaptif

## 🧠 Öğrenme Süreci

### Episode 1-100: Keşif Fazı

```
Epsilon: 1.0 (100% rastgele)
→ Model henüz öğrenmemiş, keşif yapıyor
→ Random gibi davranır
```

### Episode 100-500: Öğrenme Fazı

```
Epsilon: 0.5 (50% rastgele, 50% öğrenmiş)
→ Bazı kalıpları öğrenmeye başlar
→ "Kuzey yoğunsa kuzeye yeşil vermek iyi"
```

### Episode 500-1000: Optimizasyon Fazı

```
Epsilon: 0.01 (99% öğrenmiş)
→ İyi kararlar vermeye başlar
→ Fixed-Time'dan daha iyi performans
```

## 📈 Beklenen Performans

```
Random Baseline:     -8000 reward
Fixed-Time Baseline: -6000 reward
DQN (Episode 100):   -7000 reward (henüz öğreniyor)
DQN (Episode 500):   -5000 reward (iyileşiyor)
DQN (Episode 1000):  -3000 reward (çok iyi!) ✅
```

## 🎯 Özet

**DQN Modeli** = Trafik durumunu gözlemleyip, deneyimlerden öğrenerek en iyi fazı seçen yapay zeka modeli.

### Avantajları:
✅ Trafiğe uyum sağlar
✅ Deneyimlerden öğrenir
✅ Otomatik optimizasyon
✅ Zamanla daha iyi olur

### Neden Geçer?
- **Random**: Hiç mantık yok → DQN mantıklı kararlar verir
- **Fixed-Time**: Sabit, uyum sağlayamaz → DQN dinamik uyum sağlar
- **DQN**: Öğrenir ve optimize eder → En iyi performans

## 🔍 Test Etmek İçin

```bash
# DQN eğitimi
python3 src/train.py --algorithm dqn --config configs/single_low.yaml

# Eğitilmiş modeli değerlendir
python3 evaluate.py --checkpoint experiments/checkpoints/single_low/dqn_episode_1000.pt

# Baseline ile karşılaştır
python3 baseline_metrics.py --config single_low --policy random --episodes 10
python3 baseline_metrics.py --config single_low --policy fixed --episodes 10
```

**Beklenen Sonuç:**
```
Random:      -8000 reward (en kötü)
Fixed-Time:  -6000 reward (orta)
DQN:         -3000 reward (en iyi!) ✅
```

DQN'in Random ve Fixed-Time'ı geçmesi beklenir! 🎯
