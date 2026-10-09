<img width="548" height="537" alt="image" src="https://github.com/user-attachments/assets/d8ea4edc-6a58-4828-abdc-315784861fa9" />
Fare kavşakta. Önce sol yolu deneyecek.
<img width="552" height="538" alt="image" src="https://github.com/user-attachments/assets/bd837c0b-d356-4a51-b604-47d8d68a1bb1" />
Sola ilerledi. Yeni hücre keşfetti.
<img width="547" height="536" alt="image" src="https://github.com/user-attachments/assets/246b89ca-1132-49b6-833e-7faa3926fefb" />
Yolun sonuna ulaştı; çevredeki duvarları deniyor.
<img width="548" height="535" alt="image" src="https://github.com/user-attachments/assets/4519b15d-7f26-4f3c-8101-7430222bb8b4" />
Çıkmaz olduğunu öğrendi. Geri dönüyor.
<img width="547" height="532" alt="image" src="https://github.com/user-attachments/assets/a602dd46-235c-4612-9b5a-61450c88ae0a" />
Kavşağa döndü. Sol yol tamamlandı, yukarıyı deneyecek.
<img width="553" height="530" alt="image" src="https://github.com/user-attachments/assets/3921afb9-a9eb-4d05-9435-3353fbc3e177" />
Yeni keşfedilmemiş yoldan ilerliyor.

Hareket seçimi nasıl yapılacak?
Önce dört yönümüz var:
SOL → YUKARI → SAĞ → AŞAĞI
Ancak bu sıralama yalnızca başlangıçta eşit değerli seçenekler için geçerli olacak.
Her adımda şu kuralları uygulayacağız:
1. Daha önce duvar olduğu öğrenilmiş yönleri ele.
2. Henüz denenmemiş yönleri belirle.
3. Birden fazla yön varsa Q değerlerine göre seçim yap; eşitlikte sol-yukarı-sağ-aşağı sırasını kullan.
4. Duvarla karşılaşırsa ceza ver, duvarı kaydet, Q değerini güncelle.
5. Yeni hücreye geçerse ödül ver, ziyaret bilgilerini güncelle.
6. Bütün yönler denendiyse path_stack ile geri dön.
7. Peynir bulunursa +100 ödül ver ve bölümü bitir.
