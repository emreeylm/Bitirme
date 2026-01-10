# Bitirme Projesi Raporu

Bu klasör bitirme projesi raporunun bölümlerini içermektedir.

## Yapı

- `giris.md` - Giriş bölümü (tamamlandı)
- `yontem.md` - Yöntem bölümü (tamamlandı)
- `literatur.md` - Literatür özeti (hazırlanacak)
- `deney.md` - Deneysel kurulum ve sonuçlar (hazırlanacak)
- `sonuc.md` - Sonuç ve gelecek çalışmalar (hazırlanacak)

## Kullanım

Bu Markdown dosyaları LaTeX'e dönüştürülebilir veya doğrudan PDF olarak derlenebilir.

### Pandoc ile LaTeX'e dönüştürme:

```bash
pandoc giris.md -o giris.tex
```

### PDF oluşturma:

```bash
pandoc giris.md -o giris.pdf --pdf-engine=xelatex
```

## Notlar

- Tüm bölümler Türkçe yazılmıştır
- Akademik yazım kurallarına uyulmalıdır
- Referanslar için BibTeX kullanılabilir
