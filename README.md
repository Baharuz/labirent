# Labirent | Fare ve Peynir

Python ve Pygame ile geliştirilmiş labirent oyunu.

## Oyun modları

- **Manuel:** WASD / yön tuşları ile peynire ulaş.
- **RL:** Fare labirenti önceden bilmeden duvarları hareket deneyerek öğrenir. DFS tabanlı geri izleme ile keşfeder; Q-Learning değerleri her denemede güncellenir. Oyuncu haritanın tamamını görür; ajan yalnızca öğrendiği bilgileri kullanır. Canlı panel hamle, çarpışma, keşif, ödül ve Q değerlerini gösterir.
- **Çok oyunculu:** Aynı yerel ağda TCP bağlantısı üzerinden iki oyuncuyla yarış.
- **Ayarlar:** RL hızı ve keşif izi seçenekleri.

## Kurulum

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\main.py
```

## RL yaklaşımı

1. Her yeni labirentte keşif hafızası ve Q tablosu sıfırlanır.
2. Ajan denemediği yönler arasında Q değerine göre seçim yapar; eşitlikte sol, yukarı, sağ, aşağı sırasını kullanır.
3. Duvara çarptığında konum değişmez; duvar kaydedilir ve ceza uygulanır.
4. Yeni hücreleri ziyaret eder, çıkmazlarda geçmiş yolundan geri döner.
5. Peynire ulaşınca ödül alır ve oyun biter.

**Not:** Keşfin tamamlanması DFS tabanlı geri izlemeye dayanır; Q-Learning hareket değerlerini günceller. Çok oyunculu modun iki ayrı bilgisayarda ayrıca denenmesi önerilir.

## Dosyalar

- `src/main.py`: Menü, çizim, oyun döngüsü ve istatistikler
- `src/maze.py`: Rastgele çözülebilir labirent
- `src/rl_agent.py`: Keşif ve Q-Learning
- `src/network.py`: Socket bağlantısı
