#!/bin/bash
# Tek kavşak eğitimi başlat

cd /Users/emre/Desktop/developers/Bitirme

export SUMO_HOME=/opt/homebrew/opt/sumo/share/sumo
export PYTHONPATH=$PYTHONPATH:$SUMO_HOME/tools
source venv/bin/activate

echo "🚦 Tek Kavşak Eğitimi"
echo "=" * 50
echo ""
echo "Seçenekler:"
echo "  1. Düşük trafik (200 araç/saat)"
echo "  2. Orta trafik (500 araç/saat)"
echo "  3. Yüksek trafik (1000 araç/saat)"
echo ""

if [ -z "$1" ]; then
    echo "Kullanım: ./train_single.sh [low|medium|high]"
    echo ""
    echo "Örnek: ./train_single.sh low"
    exit 1
fi

case $1 in
    low)
        echo "🎯 Düşük trafik ile eğitim başlatılıyor..."
        python3 src/train.py --algorithm dqn --config configs/single_low.yaml
        ;;
    medium)
        echo "🎯 Orta trafik ile eğitim başlatılıyor..."
        python3 src/train.py --algorithm dqn --config configs/single_medium.yaml
        ;;
    high)
        echo "🎯 Yüksek trafik ile eğitim başlatılıyor..."
        python3 src/train.py --algorithm dqn --config configs/single_high.yaml
        ;;
    *)
        echo "❌ Geçersiz seçenek: $1"
        echo "Kullanım: ./train_single.sh [low|medium|high]"
        exit 1
        ;;
esac
