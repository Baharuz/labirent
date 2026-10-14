# Kullanım kılavuzu

## Başlatma

README'deki kurulum komutlarını proje kökünde çalıştırın. `src/main.py` giriş noktasıdır. Menüde manuel, bilgisayar, çok oyunculu, ayarlar ve çıkış bulunur.

## Manuel mod

WASD veya yön tuşlarıyla hareket edin. Sağ panel hamle, deneme ve çarpışma sayılarını gösterir. Peynir bulunduğunda sonuç görünür ve hareket durur. T aynı haritayı sıfır sayaçla başlatır; R yeni harita oluşturur; ESC menüye döner.

## Bilgisayar modu

Fare kendi hareket denemeleriyle keşfeder. Space veya Duraklat düğmesi durdurur/devam ettirir; +/- hızı 1-30 adım/sn arasında değiştirir. Ayarlar ekranı keşif izini açıp kapatır. Bu bir DFS keşif gösterimidir; Q değerleri deneysel kayıttır. T aynı haritayı yeniden, sıfır keşif hafızasıyla başlatır.

## Çok oyunculu mod

Aynı LAN/Wi-Fi'da bir bilgisayar oda kurar. Oda sahibinin `ipconfig` çıktısındaki aktif bağlantının IPv4 adresini diğer bilgisayarda adres alanına yazın. Başlangıçta yazan 127.0.0.1'i Backspace ile silin. Odaya katılın. Harita ve hazır mesajları eşitlendikten sonra yarış başlayacaktır.

Gri fare oda sahibi (P1), mavi fare katılan kullanıcıdır (P2). Herkes kendi klavyesindeki WASD/yön tuşlarını kullanır. İlk peynire ulaşan kazanır; iki oyuncunun hamleleri ayrı gösterilir. Kazanan belli olduktan sonra oda sahibi Yeni yarış/R ile yeni harita gönderir. Katılan oyuncu bekler. Bağlantı koparsa ESC ile menüye dönüp yeniden oda kurun.

## Sorun giderme

- `No module named pygame`: kurulumu aynı sanal ortamın Python'u ile yapın.
- Bağlantı reddedildi: önce oda kurulduğunu ve doğru IPv4 adresini kontrol edin.
- Bağlantı zaman aşımı: aynı ağda olduğunuzu, özel ağ güvenlik duvarı iznini ve misafir Wi-Fi izolasyonunu kontrol edin.
- Port kullanımda: başka bir oda sahibi penceresi varsa kapatın. Aynı bilgisayarda ikinci pencere Odaya katıl modunda olmalı.
- Yanlış/bozuk ağ verisi: bağlantı güvenli biçimde kapatılır; menüden yeni oda açın.
- Fiziksel cihaz testi: teslim öncesinde iki ayrı bilgisayarla bir tam yarış ve yeni tur deneyin.

## Teslim

`docs/Labirent_Dokumantasyon.pdf` mail eki olarak kullanılabilir. Depo bağlantısı: https://github.com/Baharuz/labirent . Mail otomatik gönderilmemiştir.
