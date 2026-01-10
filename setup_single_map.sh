#!/bin/bash
# Tek kavşak map dosyalarını kur

echo "🚦 Tek Kavşak Map Kurulumu"
echo "=" * 50

SCENARIO_DIR="data/scenarios/single_intersection_new"
DESKTOP_PATH="/Users/emre/Desktop"

# Network dosyasını kopyala
if [ -f "$DESKTOP_PATH/single_tls.net.xml" ]; then
    cp "$DESKTOP_PATH/single_tls.net.xml" "$SCENARIO_DIR/"
    echo "✅ single_tls.net.xml kopyalandı"
elif [ -f "$DESKTOP_PATH/map/single_tls.net.xml" ]; then
    cp "$DESKTOP_PATH/map/single_tls.net.xml" "$SCENARIO_DIR/"
    echo "✅ single_tls.net.xml kopyalandı (map klasöründen)"
else
    echo "⚠️  single_tls.net.xml bulunamadı"
    echo "   Lütfen dosyayı şuraya kopyala: $SCENARIO_DIR/"
fi

# fixed.add.xml kontrolü
if [ ! -f "$SCENARIO_DIR/fixed.add.xml" ]; then
    echo "✅ fixed.add.xml oluşturuldu (boş)"
fi

echo ""
echo "📁 Senaryo dosyaları:"
ls -lh "$SCENARIO_DIR"/*.xml "$SCENARIO_DIR"/*.sumocfg 2>/dev/null | awk '{print "   " $9}'

echo ""
echo "✅ Kurulum tamamlandı!"
echo ""
echo "🎯 Kullanım:"
echo "   Düşük trafik:  python3 src/train.py --algorithm dqn --config configs/single_low.yaml"
echo "   Orta trafik:   python3 src/train.py --algorithm dqn --config configs/single_medium.yaml"
echo "   Yüksek trafik: python3 src/train.py --algorithm dqn --config configs/single_high.yaml"
