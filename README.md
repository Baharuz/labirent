# 🐭 Labirent Oyunu | Manuel Kontrol ve Pekiştirmeli Öğrenme

**Yazılım Sınama – Ödev 4**

Python ve Pygame kullanılarak geliştirilen, farklı oyun modlarına sahip bir labirent uygulamasıdır. Oyunun temel amacı, farenin labirent içerisinde hareket ederek peynire ulaşmasıdır.

Proje kapsamında manuel kontrol, pekiştirmeli öğrenme (Reinforcement Learning – RL), haritalama, yol keşfi ve çok oyunculu iletişim özellikleri ele alınmaktadır.

## 🎮 Oyun Modları

### 1. Manuel Mod

Kullanıcı fareyi klavye üzerinden kontrol ederek peynire ulaşmaya çalışır.

**Özellikler:**
- WASD veya yön tuşlarıyla hareket
- Rastgele oluşturulan, çözülebilir labirentler
- Duvarlardan geçişin engellenmesi
- Hamle sayısının takip edilmesi
- Peynire ulaşıldığında kazanma ekranı
- R tuşuyla yeni bir labirent oluşturulması
- ESC tuşuyla ana menüye dönüş

**Durum:** İlk oynanabilir sürüm geliştirildi.

### 2. Pekiştirmeli Öğrenme (RL) Modu

Bu modda fare kullanıcı müdahalesi olmadan labirenti keşfederek peynire ulaşmaya çalışacaktır.

Fare başlangıçta:
- Peynirin konumunu bilmeyecek.
- Labirentin haritasına sahip olmayacak.
- Duvarları hareket etmeyi deneyerek öğrenecek.
- Geçtiği yolları hafızasında tutacak.
- Çıkmaz sokaklardan geri dönecek.
- Önceki deneyimlerini kullanarak hareket kararlarını güncelleyecek.

**Planlanan yaklaşım:** Q-Learning + Haritalama + DFS tabanlı geri izleme (Backtracking).

**Durum:** Algoritma tasarımı tamamlanma aşamasında, uygulama geliştirilecek.

### 3. Çok Oyunculu Mod

Aynı yerel ağ üzerinde bulunan iki kullanıcının birlikte veya karşılıklı oynayabilmesi hedeflenmektedir.

İletişim için Python Socket programlama kullanılacaktır.

**Durum:** Planlandı.

---

## 🧠 RL Algoritmasının Çalışma Mantığı

### 1. Temel Yaklaşım

RL modunda fare, her yeni labirentte sıfırdan öğrenmeye başlayacaktır.

Oyun motoru gerçek labirenti ve peynirin konumunu bilse de bu bilgiler doğrudan RL ajanına aktarılmayacaktır.

Fare yalnızca bulunduğu konumu, önceki hareketlerini, öğrendiği duvarları ve ziyaret ettiği yolları kullanarak karar verecektir.

Algoritma üç temel mekanizmadan oluşacaktır:

**Haritalama:** Keşfedilen yolların ve duvarların kaydedilmesi.

**DFS tabanlı geri izleme:** Çıkmazlardan geri dönülmesi ve keşfedilmemiş yolların sistematik olarak araştırılması.

**Q-Learning:** Hareketlerin ödül ve cezalara göre değerlendirilmesi ve Q değerlerinin güncellenmesi.

DFS keşif sürecinin tamamlanmasını sağlarken Q-Learning hareket seçiminde öğrenilmiş değerlerden yararlanacaktır.

### 2. Hareket Önceliği

Başlangıçta dört hareket tanımlanacaktır:

**SOL → YUKARI → SAĞ → AŞAĞI**

Bu sıra, başlangıçta Q değerleri eşit olan seçenekler için tercih sırası olarak kullanılacaktır.

Fare daha önce öğrendiği duvarlara tekrar çarpmamaya çalışacaktır. Henüz denenmemiş yönler arasından hareket seçerken Q değerlerini değerlendirecektir.

### 3. Duvarları Deneyerek Öğrenme

Fare bir yöne ilerlemeye çalıştığında:

1. Hedef hücrenin duvar olup olmadığı oyun motoru tarafından kontrol edilir.
2. Duvar varsa fare bulunduğu hücrede kalır.
3. Çarpışma cezası uygulanır.
4. İlgili hücre haritada duvar olarak işaretlenir.
5. Hareketin Q değeri güncellenir.
6. Fare başka bir yön denemeye devam eder.

Böylece fare labirentin tamamını başlangıçta bilmeden keşfeder.

### 4. Kavşak ve Geri İzleme Algoritması

Farenin bir kavşağa ulaştığını düşünelim.

Birden fazla yol bulunduğunda önce keşfedilmemiş bir yön seçilir. Seçilen yol çıkmazla sonuçlanırsa fare önceki konumlarına geri dönerek farklı bir yolu araştırır.

Bu süreç `path_stack` veri yapısıyla yönetilecektir.

#### Adım 1 – Kavşağa ulaşma

Fare kavşaktadır. Başlangıç yön önceliğine göre önce sol yolu deneyecektir.

<img width="548" height="537" alt="Fare kavşakta" src="https://github.com/user-attachments/assets/d8ea4edc-6a58-4828-abdc-315784861fa9" />

#### Adım 2 – Yeni hücre keşfi

Fare sola ilerler ve daha önce ziyaret edilmemiş bir hücre keşfeder.

<img width="552" height="538" alt="Fare sola ilerliyor" src="https://github.com/user-attachments/assets/bd837c0b-d356-4a51-b604-47d8d68a1bb1" />

#### Adım 3 – Yolun sonuna ulaşma

Fare yolun sonuna ulaşır. Çevresindeki yönleri deneyerek duvarları ve geçilebilir yolları belirler.

<img width="547" height="536" alt="Fare çıkmazı keşfediyor" src="https://github.com/user-attachments/assets/246b89ca-1132-49b6-833e-7faa3926fefb" />

#### Adım 4 – Geri dönüş

Fare keşfedilmemiş başka bir yol kalmadığını öğrendiğinde önceki hücresine geri döner.

<img width="548" height="535" alt="Fare geri dönüyor" src="https://github.com/user-attachments/assets/4519b15d-7f26-4f3c-8101-7430222bb8b4" />

#### Adım 5 – Kavşağa yeniden ulaşma

Fare aynı kavşağa döner. Sol yolun tamamen keşfedildiğini hatırladığı için farklı bir yön seçer.

<img width="547" height="532" alt="Fare yeniden kavşakta" src="https://github.com/user-attachments/assets/a602dd46-235c-4612-9b5a-61450c88ae0a" />

#### Adım 6 – Alternatif yolu keşfetme

Fare yukarıdaki keşfedilmemiş yoldan ilerleyerek araştırmasına devam eder.

<img width="553" height="530" alt="Fare yeni yolu keşfediyor" src="https://github.com/user-attachments/assets/3921afb9-a9eb-4d05-9435-3353fbc3e177" />

Bu mekanizma sayesinde fare daha önce araştırdığı çıkmazları gereksiz yere tekrar keşfetmeyecek ve alternatif yolları sistematik olarak deneyecektir.

---

## ⚙️ Hareket Seçim Algoritması

Her karar adımında aşağıdaki işlemler uygulanacaktır:

1. Daha önce duvar olduğu öğrenilen yönler elenir.
2. Henüz denenmemiş yönler belirlenir.
3. Birden fazla uygun yön varsa Q değerlerine göre seçim yapılır.
4. Eşit Q değerlerinde SOL → YUKARI → SAĞ → AŞAĞI önceliği kullanılır.
5. Duvarla karşılaşılırsa ceza uygulanır, duvar kaydedilir ve Q değeri güncellenir.
6. Yeni hücreye geçilirse ödül uygulanır ve ziyaret bilgisi güncellenir.
7. Keşfedilmemiş yön kalmazsa `path_stack` kullanılarak geri dönülür.
8. Peynir bulunursa +100 ödül verilir ve bölüm tamamlanır.

## 🗺️ Haritalama ve Veri Yapıları

| Veri Yapısı | Görevi |
|---|---|
| `known_map` | Keşfedilen duvar ve yolları saklar |
| `position` | Farenin mevcut konumunu tutar |
| `visited` | Ziyaret edilen hücreleri kaydeder |
| `tried_actions` | Her hücrede denenmiş yönleri tutar |
| `path_stack` | Geri dönüş için yol geçmişini saklar |
| `Q_table` | Durum-hareket değerlerini saklar |
| `moves` | Başarılı hareketleri sayar |
| `collisions` | Duvar çarpışmalarını sayar |

Her yeni labirentte keşif haritası, ziyaret kayıtları ve Q tablosu sıfırlanacaktır.

## 🏆 Ödül ve Ceza Sistemi

Başlangıçta aşağıdaki değerler kullanılacaktır:

| Olay | Ödül / Ceza |
|---|---:|
| Peynire ulaşma | +100 |
| Yeni hücre keşfetme | +5 |
| Duvara çarpma | -5 |
| Ziyaret edilmiş hücreye geçme | -1 |
| Her başarılı hareketin temel maliyeti | -0.1 |

Ödül değerleri geliştirme ve test aşamasında yeniden düzenlenebilir.

Geri izleme sırasında eski hücrelerden geçmek bazen zorunlu olduğundan, algoritmanın gerekli geri dönüşleri engellememesine dikkat edilecektir.

## 📐 Q-Learning

Q-Learning, farenin bulunduğu durumda hangi hareketin daha faydalı olduğunu öğrenmek için kullanılacaktır.

Başlangıç için durum, farenin labirentteki koordinatlarıyla temsil edilecektir:

`state = (x, y)`

Hareketler:

`actions = [SOL, YUKARI, SAĞ, AŞAĞI]`

Q değerleri aşağıdaki formülle güncellenecektir:

**Q(s,a) ← Q(s,a) + α [r + γ max Q(s',a') − Q(s,a)]**

Burada:

- `s`: Mevcut durum
- `a`: Seçilen hareket
- `r`: Alınan ödül veya ceza
- `s'`: Sonraki durum
- `α`: Öğrenme hızı
- `γ`: Gelecekteki ödüllerin ağırlığı

Q-Learning ve DFS birlikte kullanılacağından keşif öncelikleri, Q değerleri ve geri dönüş davranışları ayrı ayrı yönetilecektir.

Tek bir labirentte yapılan öğrenmenin sınırlılıkları test edilerek değerlendirilecektir.

---

## 📊 Anlık Öğrenme ve İstatistikler

RL modu çalışırken algoritmanın öğrenme süreci ekranda canlı olarak gösterilecektir.

Planlanan istatistikler:

| İstatistik | Açıklama |
|---|---|
| Hamle sayısı | Başarılı hareket sayısı |
| Duvara çarpma | Başarısız hareket denemeleri |
| Keşfedilen hücre | İlk kez ziyaret edilen hücre sayısı |
| Toplam ödül | Biriken ödül ve cezalar |
| Mevcut konum | Farenin bulunduğu koordinat |
| Seçilen hareket | Son hareket kararı |
| Q değerleri | Bulunulan durumdaki hareket değerleri |
| Öğrenme durumu | Keşif, geri dönüş veya hedef bulundu |

**Canlı güncelleme mantığı:**

Her hareket denemesinden sonra:

1. Hareket sonucu belirlenir.
2. Harita ve ziyaret kayıtları güncellenir.
3. Ödül veya ceza hesaplanır.
4. Q tablosu güncellenir.
5. İstatistik paneli yenilenir.
6. Fare bir sonraki hareketini seçer.

Hareketlerin izlenebilmesi için simülasyon hızı ayarlanabilir olacaktır.

---

## 🧪 Yazılım Sınama

Proje kapsamında en az üç test senaryosu hazırlanacaktır.

### Test 1 – Duvar Çarpışması

**Amaç:** Farenin duvardan geçemediğinin doğrulanması.

**Beklenen sonuç:** Fare bulunduğu hücrede kalır, duvar bilgisi kaydedilir ve çarpışma cezası uygulanır.

### Test 2 – Çıkmaz Sokaktan Geri Dönme

**Amaç:** Geri izleme mekanizmasının doğrulanması.

**Beklenen sonuç:** Fare çıkmazı tespit eder, önceki kavşağa döner ve keşfedilmemiş alternatif yolu dener.

### Test 3 – Peynirin Bulunması

**Amaç:** Hedefe ulaşma ve bölüm sonlandırma işlemlerinin doğrulanması.

**Beklenen sonuç:** Fare peynirin bulunduğu hücreye ulaşır, hedef ödülünü alır ve kazanma ekranı görüntülenir.

Testlerin gerçek sonuçları uygulama tamamlandıktan sonra dokümantasyona eklenecektir.

---

## 🛠️ Kullanılan Teknolojiler

- **Python:** Oyun ve algoritma geliştirme
- **Pygame:** Grafik arayüz, hareket ve kullanıcı etkileşimi
- **Q-Learning:** Pekiştirmeli öğrenme
- **DFS / Backtracking:** Sistematik keşif ve geri izleme
- **Socket:** Planlanan çok oyunculu iletişim
- **Git / GitHub:** Sürüm kontrolü

## 📁 Proje Yapısı

```text
labirent/
├── src/
│   ├── main.py
│   ├── maze.py
│   ├── player.py
│   └── rl_agent.py
├── tests/
├── docs/
├── README.md
├── requirements.txt
└── .gitignore
```

Dosya ve klasör yapısı geliştirme sürecinde güncellenebilir.

## Kurulum ve Çalıştırma

Python kurulu bir bilgisayarda:

```bash
python -m venv .venv
```

Windows ortamında Pygame kurulumu:

```powershell
.\.venv\Scripts\python.exe -m pip install pygame
```

Oyunu başlatma:

```powershell
.\.venv\Scripts\python.exe src\main.py
```

---

**Not:** RL bölümünde açıklanan davranışlar hedeflenen algoritma tasarımını ifade etmektedir. Gerçek uygulama sonuçları ve test verileri geliştirme tamamlandığında eklenecektir.
