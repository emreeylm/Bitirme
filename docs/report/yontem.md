# 3. Yöntem

## 3.1 Trafik Simülasyon Ortamı

### 3.1.1 SUMO (Simulation of Urban MObility)

SUMO, açık kaynak kodlu bir mikro trafik simülasyon aracıdır ve şehir içi trafik akışını gerçekçi bir şekilde modellemek için kullanılmaktadır. Bu çalışmada SUMO'nun sağladığı özellikler:

- **Gerçekçi Araç Dinamiği**: Hızlanma, yavaşlama, takip mesafesi modelleri
- **Çok Modlu Trafik**: Araçlar, yayalar, bisikletler
- **Dinamik Rotalama**: Araçların rotalarını gerçek zamanlı değiştirebilmesi
- **Detaylı Metrikler**: Bekleme süresi, kuyruk uzunluğu, emisyonlar

### 3.1.2 TraCI (Traffic Control Interface)

TraCI, SUMO ile Python arasında gerçek zamanlı iletişim sağlayan bir API'dir. Bu çalışmada TraCI kullanılarak:

- **Durum Gözlemi**: Trafik ışığı fazları, kuyruk uzunlukları, bekleme süreleri
- **Eylem Uygulama**: Trafik ışığı fazlarını değiştirme
- **Gerçek Zamanlı Kontrol**: Her simülasyon adımında ajan-ortam etkileşimi

### 3.1.3 OSM (OpenStreetMap) Kullanarak Yol Ağı Oluşturma

Gerçekçi trafik senaryoları için OpenStreetMap verilerinden yol ağları oluşturulmaktadır:

```python
# SUMO netconvert ile OSM'den ağ oluşturma
netconvert --osm-files map.osm --output-file network.net.xml
```

Bu yaklaşım:
- **Gerçek Şehir Topolojileri**: Türkiye şehirlerinden gerçek yol ağları
- **Ölçeklenebilirlik**: Farklı boyutlarda ağlar (tek kavşak, grid, gerçek şehir)
- **Esneklik**: Farklı trafik senaryoları için kolay modifikasyon

## 3.2 Ajan Tasarımı

### 3.2.1 State (Gözlem) Uzayı

Her trafik ışığı ajanı için state uzayı aşağıdaki bileşenlerden oluşmaktadır:

**Lokal Bilgiler:**
- **Kuyruk Uzunlukları**: Her giriş şeridi için kuyruktaki araç sayısı (normalize edilmiş)
- **Bekleme Süreleri**: Her şerit için birikmiş bekleme süresi (normalize edilmiş)
- **Araç Sayıları**: Her şeritteki toplam araç sayısı (normalize edilmiş)
- **Mevcut Faz**: Trafik ışığının şu anki fazı (one-hot veya normalize edilmiş)
- **Faz Süresi**: Son faz değişikliğinden bu yana geçen süre (normalize edilmiş)

**Komşu Bilgileri (Multi-Agent için):**
- **Komşu Durumları**: Yakındaki kavşakların state vektörleri
- **Komşu Fazları**: Komşu trafik ışıklarının mevcut fazları
- **Araç Akışı**: Komşu kavşaklardan gelen araç akışı bilgisi

**Matematiksel Gösterim:**
```
s_t = [q_1, q_2, ..., q_n, w_1, w_2, ..., w_n, v_1, v_2, ..., v_n, p, t, s_neighbor]
```

Burada:
- `q_i`: i. şeridin kuyruk uzunluğu
- `w_i`: i. şeridin bekleme süresi
- `v_i`: i. şeridin araç sayısı
- `p`: Mevcut faz
- `t`: Faz süresi
- `s_neighbor`: Komşu durumları

### 3.2.2 Action (Eylem) Uzayı

**Tek Ajanlı Senaryo:**
- **Ayrık Eylem Uzayı**: Faz seçimi (0, 1, 2, 3)
- Her faz bir trafik akışı kombinasyonunu temsil eder

**Çok Ajanlı Senaryo:**
- Her ajan için ayrık faz seçimi
- Koordineli eylem: Tüm ajanların eylemleri birlikte uygulanır

**Faz Geçişleri:**
- **Sarı Faz Zorunluluğu**: Yeşil fazdan diğer yeşil faza geçişte sarı faz zorunludur
- **Minimum Yeşil Süre**: Her yeşil faz için minimum süre garantisi
- **Maksimum Yeşil Süre**: Uzun süreli yeşil fazların önlenmesi

### 3.2.3 Reward (Ödül) Fonksiyonu

Reward fonksiyonu, trafik performansını optimize etmek için çoklu metrikleri birleştirir:

**Bileşenler:**
1. **Bekleme Süresi Cezası**: `-α_w * Σ waiting_time`
2. **Kuyruk Uzunluğu Cezası**: `-α_q * Σ queue_length`
3. **Duruş Sayısı Cezası**: `-α_s * Σ stop_count`
4. **Gecikme Cezası**: `-α_d * Σ delay`
5. **Akış Ödülü**: `+α_t * throughput`

**Toplam Reward:**
```
R_t = α_t * throughput - (α_w * W_t + α_q * Q_t + α_s * S_t + α_d * D_t)
```

**Ağırlık Seçimi:**
- `α_w = 0.1`: Bekleme süresi ağırlığı
- `α_q = 0.1`: Kuyruk uzunluğu ağırlığı
- `α_s = 0.05`: Duruş sayısı ağırlığı
- `α_d = 0.1`: Gecikme ağırlığı
- `α_t = 0.05`: Akış ödülü ağırlığı

### 3.2.4 Multi-Agent Communication (Komşu Kavşaklar)

**Komşu Tanımı:**
- Fiziksel yakınlık: Belirli mesafe içindeki kavşaklar
- Trafik akışı bağlantısı: Doğrudan bağlı kavşaklar

**Bilgi Paylaşımı:**
- **State Paylaşımı**: Komşu ajanların state vektörleri
- **Eylem Koordinasyonu**: Eş zamanlı faz değişiklikleri
- **Gradyan Paylaşımı**: Merkezi eğitim sırasında gradyan bilgisi

## 3.3 Öğrenme Algoritmaları

### 3.3.1 Tek Kavşak için DQN

**Mimari:**
- **Q-Network**: 3 katmanlı MLP (128-128-64 nöron)
- **Target Network**: Kararlı öğrenme için ayrı target network
- **Experience Replay**: Geçmiş deneyimlerden öğrenme

**Özellikler:**
- Epsilon-greedy keşif stratejisi
- Gradient clipping ile kararlılık
- Periyodik target network güncellemesi

**Neden DQN?**
- Tek ajanlı senaryolarda kanıtlanmış performans
- Ayrık eylem uzayı için uygun
- Göreceli basitlik ve hızlı yakınsama

### 3.3.2 MARL için MADDPG

**Mimari:**
- **Actor Network**: Her ajan için deterministik politika
- **Critic Network**: Tüm ajanların state-action çiftlerini değerlendiren merkezi critic
- **Target Networks**: Actor ve critic için ayrı target networkler

**Özellikler:**
- Merkezi eğitim, merkezi olmayan yürütme
- Deterministik politika gradyanı
- Soft target network güncellemesi (τ = 0.01)

**Neden MADDPG?**
- Sürekli eylem uzayı desteği (normalize edilmiş faz süreleri)
- Çok ajanlı koordinasyon yeteneği
- Kararlı öğrenme özellikleri

### 3.3.3 Değer Faktorizasyonu için QMIX

**Mimari:**
- **Agent Q-Networks**: Her ajan için bireysel Q-network
- **Mixing Network**: Bireysel Q-değerlerini birleştiren hipernetwork
- **Monotonluk Kısıtı**: Mixing network ağırlıkları pozitif (mutlak değer)

**Özellikler:**
- Değer faktörizasyonu ile ölçeklenebilirlik
- Global state kullanımı
- Monotonluk garantisi ile optimal politika korunması

**Neden QMIX?**
- Ölçeklenebilir çok ajanlı öğrenme
- Koordinasyon garantileri
- Ayrık eylem uzayı için uygun

### 3.3.4 Algoritma Seçim Gerekçesi

| Algoritma | Senaryo | Avantajlar | Dezavantajlar |
|-----------|---------|------------|---------------|
| DQN | Tek kavşak | Basit, hızlı | Çok ajanlı için uygun değil |
| MADDPG | Çok kavşak | Koordinasyon, sürekli eylem | Karmaşık, yavaş |
| QMIX | Çok kavşak | Ölçeklenebilir, garantiler | Global state gereksinimi |

## 3.4 Eğitim Pipeline'ı

### 3.4.1 Episode Tasarımı

**Episode Yapısı:**
- **Başlangıç**: Rastgele trafik yoğunluğu ile başlatma
- **Süre**: 3600 saniye (1 saat) simülasyon
- **Adım Boyutu**: 5 saniye (delta_time)
- **Sonlandırma**: Zaman limiti veya trafik durumu

**Curriculum Learning:**
- **Aşama 1**: Düşük trafik yoğunluğu
- **Aşama 2**: Orta trafik yoğunluğu
- **Aşama 3**: Yüksek trafik yoğunluğu
- **Aşama 4**: Değişken trafik yoğunluğu

### 3.4.2 Hyperparametreler

**DQN:**
- Learning rate: 0.001
- Gamma (discount): 0.99
- Epsilon decay: 0.995
- Batch size: 64
- Buffer size: 10000
- Target update frequency: 100

**MADDPG:**
- Actor learning rate: 0.001
- Critic learning rate: 0.001
- Tau (soft update): 0.01
- Noise scale: 0.1

**QMIX:**
- Learning rate: 0.0005
- Gamma: 0.99
- Tau: 0.005
- Epsilon decay: 0.99

### 3.4.3 Eğitim Süreci

1. **Başlatma**: Ortam ve ajanların başlatılması
2. **Keşif**: Epsilon-greedy ile eylem seçimi
3. **Deneyim Toplama**: State-action-reward-next_state çiftlerinin saklanması
4. **Öğrenme**: Replay buffer'dan batch örnekleme ve network güncellemesi
5. **Değerlendirme**: Periyodik performans değerlendirmesi
6. **Kaydetme**: Checkpoint kaydetme

### 3.4.4 Değerlendirme Metrikleri

- **Ortalama Bekleme Süresi**: Araç başına ortalama bekleme süresi
- **Kuyruk Uzunluğu**: Şerit başına ortalama kuyruk uzunluğu
- **Duruş Sayısı**: Toplam duruş sayısı
- **Yakıt Tüketimi**: Toplam yakıt tüketimi (SUMO emisyon modeli)
- **Karbon Emisyonu**: CO2 emisyonları
- **Akış Oranı**: Saatte geçen araç sayısı
