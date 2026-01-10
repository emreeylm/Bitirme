# 1. Giriş

## 1.1 Trafik Yönetiminin Önemi

Şehir içi trafik yönetimi, modern kentleşmenin en kritik sorunlarından biridir. Artan nüfus ve araç sayısıyla birlikte, trafik tıkanıklıkları hem ekonomik hem de çevresel açıdan ciddi maliyetlere yol açmaktadır. Dünya genelinde şehirler, trafik sinyalizasyon sistemlerini optimize ederek bu sorunları azaltmaya çalışmaktadır. Etkili bir trafik yönetim sistemi:

- **Bekleme sürelerini** minimize ederek sürücülerin zaman kaybını azaltır
- **Yakıt tüketimini** düşürerek ekonomik tasarruf sağlar
- **Karbon emisyonlarını** azaltarak çevresel etkiyi minimize eder
- **Trafik akışını** iyileştirerek şehir içi ulaşım verimliliğini artırır

## 1.2 Mevcut Sistemlerin Eksiklikleri

Günümüzde yaygın olarak kullanılan trafik sinyalizasyon sistemleri genellikle **sabit zamanlı** (fixed-time) veya **kural tabanlı** (rule-based) yaklaşımlara dayanmaktadır:

### Sabit Zamanlı Sistemler
- **Webster Metodu**: Trafik akışı istatistiklerine dayalı önceden belirlenmiş zamanlama
- **SCOOT (Split, Cycle, Offset Optimization Technique)**: Adaptif ancak sınırlı optimizasyon
- **SOTL (Self-Organizing Traffic Lights)**: Basit kurallara dayalı reaktif kontrol

Bu sistemlerin temel eksiklikleri:
- Trafik yoğunluğundaki **dinamik değişimlere** uyum sağlayamama
- **Komşu kavşaklarla koordinasyon** eksikliği
- **Gerçek zamanlı veri** kullanımının sınırlı olması
- **Karmaşık trafik senaryolarında** verimsizlik

### Kural Tabanlı Sistemler
- **Max-Pressure**: Basınç bazlı kontrol algoritması
- **Adaptive Control**: Sensör verilerine dayalı basit adaptasyon

Bu sistemler de:
- **Öğrenme yeteneği** bulunmamaktadır
- **Uzun vadeli optimizasyon** yapamamaktadır
- **Çok ajanlı koordinasyon** için yetersizdir

## 1.3 Yapay Zekânın Rolü

Yapay zeka ve özellikle **Takviyeli Öğrenme (Reinforcement Learning, RL)**, trafik yönetimi için yeni fırsatlar sunmaktadır:

### Tek Ajanlı RL
- **DQN (Deep Q-Network)**: Tek kavşak için derin öğrenme tabanlı optimizasyon
- **A2C/A3C**: Actor-Critic metodları ile politika optimizasyonu
- **PPO**: Proximal Policy Optimization ile kararlı öğrenme

### Çok Ajanlı RL (MARL)
- **MADDPG**: Merkezi eğitim, merkezi olmayan yürütme
- **QMIX**: Değer faktörizasyonu ile koordineli öğrenme
- **CoLight**: Grafik dikkat ağları ile komşu bilgi paylaşımı

RL tabanlı sistemlerin avantajları:
- **Deneyimden öğrenme** yeteneği
- **Uzun vadeli ödül maksimizasyonu**
- **Dinamik ortamlara adaptasyon**
- **Çok ajanlı koordinasyon** potansiyeli

## 1.4 Çalışmanın Motivasyonu ve Amaçları

Bu çalışma, şehir içi trafik yönetiminde **Çok Ajanlı Takviyeli Öğrenme (MARL)** kullanarak trafik ışıklarını optimize etmeyi amaçlamaktadır. Temel motivasyonlar:

1. **Akademik Katkı**: MARL algoritmalarının trafik kontrolüne uygulanması ve karşılaştırılması
2. **Pratik Değer**: Gerçek dünya trafik senaryolarına uygulanabilir çözümler geliştirme
3. **Türkiye Bağlamı**: Türkiye şehir topolojilerine uyarlanabilir bir sistem tasarımı
4. **Açık Kaynak**: Topluma açık, yeniden kullanılabilir bir altyapı sağlama

### Amaçlar

1. **SUMO-TraCI** tabanlı bir trafik simülasyon ortamı geliştirmek
2. **DQN, MADDPG, QMIX** algoritmalarını trafik kontrolüne uyarlamak
3. **Çok kavşaklı senaryolarda** koordineli öğrenme sağlamak
4. **Baseline modellerle** (Webster, SOTL, Max-Pressure) karşılaştırmalı değerlendirme yapmak
5. **Performans metriklerinde** önemli iyileşmeler elde etmek:
   - Ortalama bekleme süresinde **%20+** azalma
   - Duruş sayısında **%15+** azalma
   - Yakıt tüketimi ve emisyonlarda **%10+** azalma

## 1.5 Katkılar (Contributions)

Bu çalışmanın bilimsel ve pratik katkıları:

### Bilimsel Katkılar
1. **MARL Algoritmalarının Karşılaştırması**: DQN, MADDPG ve QMIX'in trafik kontrolü bağlamında sistematik karşılaştırması
2. **Ajan Tasarımı**: Trafik sinyalizasyonu için optimize edilmiş state-action-reward tasarımı
3. **Koordinasyon Mekanizması**: Komşu kavşaklar arası bilgi paylaşımı ve koordinasyon stratejileri
4. **Simülasyon Altyapısı**: Açık kaynak, yeniden kullanılabilir SUMO-TraCI entegrasyonu

### Pratik Katkılar
1. **Açık Kaynak Kod**: Topluma açık, dokümante edilmiş bir MARL trafik kontrol altyapısı
2. **Türkiye Uyumluluğu**: Türkiye şehir topolojilerine uyarlanabilir yapı
3. **Performans İyileştirmeleri**: Ölçülebilir ve anlamlı trafik metriklerinde iyileştirmeler
4. **Gerçek Hayat Entegrasyonu**: Sensör verileri ve kamera görüntüleri ile entegrasyon potansiyeli

## 1.6 Tez Yapısı

Bu tez aşağıdaki bölümlerden oluşmaktadır:

- **Bölüm 2**: Literatür özeti ve ilgili çalışmalar
- **Bölüm 3**: Yöntem - Trafik simülasyon ortamı, ajan tasarımı, öğrenme algoritmaları
- **Bölüm 4**: Deneysel kurulum - Senaryolar, donanım, ölçütler, baseline modeller
- **Bölüm 5**: Sonuçlar ve tartışma - Performans analizi, karşılaştırmalar
- **Bölüm 6**: Sonuç ve gelecek çalışmalar
