# Test raporu

Doğrulama ortamı: Linux, Python 3.12.14, Pygame 2.6.1. Grafik testleri SDL dummy sürücüsüyle, ağ testleri gerçek TCP loopback bağlantısıyla çalıştırıldı.

Komut: `python -m unittest discover -s tests -v`

Sonuç: **15 test başarılı, 0 başarısız**. Ek pencere açılış kontrolü: `python src/main.py --smoke-test` (SDL dummy ile) başarılı. Menü ve bilgisayar ekranları PNG olarak çizdirilip görsel olarak incelendi. İki ayrı fiziksel bilgisayar / gerçek Wi-Fi testi bu ortamda yapılmadı.

## İstenen üç ana test senaryosu

| No | Senaryo ve adımlar | Beklenen | Gerçekleşen |
|---|---|---|---|
| TC-01 | Manuel oyuncu bir duvara çarpsın, sonra iki geçişle hedefe ulaşsın; kazanma sonrası tekrar hareket etsin. | 2 hamle, 3 deneme, 1 çarpışma; kazanma sonrası değişmesin. | Otomatik test geçti. |
| TC-02 | Bilgisayar 100 seed ile üretilmiş labirenti keşfetsin. | Her haritada hedefi bulsun; sayaçlar tutarlı olsun. | 100/100 hedef bulundu; test geçti. |
| TC-03 | Gerçek TCP bağlantısında iki oyuncu eşitlensin; istemci hedefe ulaşsın, yeni tur başlasın, bağlantı kesilsin. | Aynı harita/kazanan/sayaçlar; yeni turda sıfırlama; kopmada hareket durması. | Loopback üzerinde geçti. İki fiziksel cihaz testi bekliyor. |

## Ek kapsam

1. Manuel hareket, duvar, kazanma ve sayaçlar.
2. Geçersiz yön reddi.
3. Üretilen 100 labirentin hedefe bağlantısı (BFS doğrulaması).
4. Bilgisayarın 100 labirentte keşfi ve sayaçları.
5. Seed tekrarlanabilirliği ve boyut doğrulaması.
6. Başlangıcın hedef olduğu sınır durum.
7. Harita/hazır protokolü ve iki tarafta aynı harita.
8. Gerçek TCP yarış, istemci galibiyeti, yeniden yarış, eski tur mesajı, kopma.
9. Oda sahibinin duvar çarpışmasının iki tarafta sayılması.
10. Geçersiz hareket mesajında çökmeyen bağlantı kapatma.
11. Geçersiz durum/duvar içindeki konumun reddi.
12. 64 KiB sınırını aşan mesajın reddi.
13. İptal edilmiş bağlantının sonradan etkinleşememesi.
14. Bekleyen oda kapatılınca portun serbest kalması.
15. Menü/ayarlar/ağ menüsü/oyun çizimi, klavye, kazanma, aynı haritayı sıfırlama ve duraklatma.

## Teslim öncesi fiziksel kontrol

İki bilgisayarı aynı ağa bağlayın. P1 ve P2 ile ayrı ayrı kazanmayı, yeni yarışı, ESC ile ayrılmayı, güvenlik duvarı iznini ve bağlantı kopmasını deneyin. Bu kontrolün sonucu henüz başarılı olarak işaretlenmemiştir.
