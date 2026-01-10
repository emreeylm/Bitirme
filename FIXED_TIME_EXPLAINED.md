# 🚦 Fixed-Time Policy (Sabit Zamanlı Politika) Açıklaması

## 📖 Tanım

**Fixed-Time Policy**, trafik ışıklarının **önceden belirlenmiş sabit bir zamanlama** ile çalıştığı klasik trafik kontrol yöntemidir. Trafik durumuna bakmaksızın, her zaman aynı zamanlama döngüsünü takip eder.

## 🔄 Nasıl Çalışır?

### Temel Prensip

1. **Sabit Döngü Süresi**: Her faz için önceden belirlenmiş süreler
2. **Değişmez Zamanlama**: Trafik yoğunluğu ne olursa olsun aynı zamanlama
3. **Önceden Planlanmış**: Trafik mühendisleri tarafından tasarlanır

### Örnek Zamanlama

```
Faz 0 (Yeşil): 42 saniye
Faz 1 (Sarı):  3 saniye
Faz 2 (Yeşil): 42 saniye  
Faz 3 (Sarı):  3 saniye
─────────────────────────
Toplam Döngü:  90 saniye
```

Bu döngü sürekli tekrarlanır.

## 📊 Avantajları

✅ **Basit ve Anlaşılır**: Karmaşık algoritma yok
✅ **Öngörülebilir**: Sürücüler ne zaman yeşil yanacağını bilir
✅ **Düşük Maliyet**: Sensör veya AI gerektirmez
✅ **Kararlı**: Sistem çökmez, her zaman çalışır

## ❌ Dezavantajları

❌ **Adapte Olamaz**: Trafik yoğunluğu değişse bile aynı zamanlama
❌ **Verimsiz**: Boş yollarda bile bekletir
❌ **Yoğun Saatlerde Kötü**: Trafik patlamalarına uyum sağlayamaz
❌ **Manuel Optimizasyon**: Trafik mühendisleri tarafından sık sık ayarlanması gerekir

## 🆚 Karşılaştırma

| Özellik | Fixed-Time | Random | DQN (RL) |
|---------|------------|--------|----------|
| Trafiğe Uyum | ❌ Yok | ❌ Yok | ✅ Var |
| Öğrenme | ❌ Yok | ❌ Yok | ✅ Var |
| Karmaşıklık | ⭐ Düşük | ⭐ Düşük | ⭐⭐⭐ Yüksek |
| Performans | ⭐⭐ Orta | ⭐ Kötü | ⭐⭐⭐ İyi |

## 💻 Kodda Nasıl Uygulanıyor?

```python
# Fixed-Time Policy
if policy == "fixed":
    for tl_id in traffic_lights:
        if phase_timer[tl_id] >= 45:  # 42s yeşil + 3s sarı
            current_phase[tl_id] = (current_phase[tl_id] + 1) % 4
            traci.trafficlight.setPhase(tl_id, current_phase[tl_id])
            phase_timer[tl_id] = 0
        else:
            phase_timer[tl_id] += delta_time
```

**Açıklama:**
- Her 45 saniyede bir faz değişir
- 4 faz döngüsel olarak tekrarlanır (0→1→2→3→0...)
- Trafik durumuna bakılmaz

## 🌍 Gerçek Dünyada

Fixed-Time Policy, dünyada en yaygın kullanılan yöntemdir:

- **Küçük şehirler**: Trafik yoğunluğu düşük ve öngörülebilir
- **Gece saatleri**: Trafik az olduğunda yeterli
- **Basit kavşaklar**: Karmaşık kontrol gerektirmeyen yerler

## 📈 Bizim Projede Kullanımı

Baseline (karşılaştırma) olarak kullanıyoruz:

1. **Fixed-Time** → Klasik yöntem (iyi baseline)
2. **Random** → En kötü senaryo (kötü baseline)
3. **DQN** → Bizim modelimiz (bunları geçmeli)

Eğer DQN, Fixed-Time'dan daha iyi performans gösterirse → **Başarılı!** ✅

## 🎯 Örnek Senaryo

**Sabah Saat 8:00 - Yoğun Trafik**

- **Fixed-Time**: Her zaman 42s yeşil, trafik yoğun olsa da
- **DQN**: Trafiği görür, yoğun yöne daha uzun yeşil verir
- **Sonuç**: DQN daha az bekleme süresi sağlar

**Gece Saat 2:00 - Boş Yollar**

- **Fixed-Time**: Yine 42s bekletir, oysa kimse yok
- **DQN**: Boş yolları görür, hızlı geçiş sağlar
- **Sonuç**: DQN daha verimli

## 📝 Özet

**Fixed-Time Policy** = Trafik durumuna bakmadan sabit zamanlama ile çalışan klasik yöntem. Basit ama adapte olamaz. Bizim için **baseline** olarak kullanıyoruz - DQN'in bunu geçmesi gerekiyor!
