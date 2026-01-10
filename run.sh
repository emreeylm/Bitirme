#!/bin/bash
# Projeyi çalıştırmak için script

set -e

echo "🚀 MARL Trafik Kontrol Projesi Başlatılıyor..."
echo ""

# SUMO_HOME ayarla
export SUMO_HOME=/opt/homebrew/opt/sumo/share/sumo
export PYTHONPATH=$PYTHONPATH:$SUMO_HOME/tools

# Virtual environment aktif et
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment aktif"
else
    echo "⚠️  Virtual environment bulunamadı. Oluşturuluyor..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip --quiet
fi

# Bağımlılıkları kontrol et
echo "📦 Bağımlılıklar kontrol ediliyor..."
python3 -c "import torch; import numpy; import gymnasium; import matplotlib; import yaml" 2>/dev/null || {
    echo "⚠️  Bazı bağımlılıklar eksik. Yükleniyor..."
    pip install -r requirements.txt --quiet || {
        echo "❌ Bağımlılık yükleme hatası!"
        echo "Manuel olarak çalıştırın: pip install -r requirements.txt"
        exit 1
    }
}

echo "✅ Bağımlılıklar hazır"
echo ""

# Test modu
if [ "$1" == "test" ]; then
    echo "🧪 Test modu..."
    python3 test_imports.py
    echo ""
    echo "🔗 SUMO bağlantı testi (network izni gerekebilir)..."
    python3 test_run.py || echo "⚠️  SUMO testi başarısız (network izni gerekebilir)"
    exit 0
fi

# Eğitim modu
if [ "$1" == "train" ]; then
    ALGORITHM=${2:-dqn}
    echo "🎓 Eğitim başlatılıyor: $ALGORITHM"
    python3 src/train.py --algorithm $ALGORITHM --config configs/default.yaml
    exit 0
fi

# Yardım
echo "Kullanım:"
echo "  ./run.sh test          - Testleri çalıştır"
echo "  ./run.sh train [algo]  - Eğitimi başlat (dqn/maddpg/qmix)"
echo ""
echo "Örnek:"
echo "  ./run.sh test"
echo "  ./run.sh train dqn"
