
# Vocabulary APP

Bu uygulama, YDS-İngilizce için şahsi kullanım amacıyla geliştirilmiştir. Python ve SQL kurulu olmayan Windows sistemlerde, setup dosyası aracılığı ile kurularak herhangi bir ekstra araca gereksinim olmadan kullanılabilir.

## Kullanımı

Uygulama, çeşitli kelime ezberleme tekniklerinden oluşmaktadır. Farklı setlerde, aynı Türkçe kelimeye karşılık farklı İngilizce ifadeler bulunabilmektedir ya da bir İngilizce kelimenin anlamı en yaygın anlamıyla değil, farklı anlamları ile çevrilmiş olabilir. Kelimelerin çevirileri yapay zeka tarafından, kelime seti bağlamına göre otomatik bir şekilde tercüme edilmiştir.

Bu nedenle, ilk olarak Flashcard pratikleri ile kelime setlerini tanıyıp daha sonra diğer testlerin yapılması önerilir.
En verimli öğrenme yöntemi ise, yazarak pratik yapma ile gerçekleşmektedir. 

## Çeviriler 

Copilot yapay zekası tarafından otomatik kod tamamlama özelliğinin farklı bir kullanımı ile çeviriler yapılmıştır. Bir okuma metni veya bilimsel makale okuma sürecinde, karşımıza çıkacak çok sayıda bilmediğim kelimenin tek tek anlamlarının araştırılması uzun vakitler alabilir. dict_to_database klasöründe, JSON dosyası içerisinde kelimelerin çevirilmesi otomatik olarak Copilot ile gerçekleştirilir. Ayrıca Copilot kullanımı ile veri setinin bağlamı yakalanarak kelimenin en yaygın haliyle anlamı yerine o an üzerinde okuma yaptığımız metnin bağlamındaki anlamı yakalanabilmektedir. 
JSON dosyası üzerinde istediğiniz kelime ve veri setleri eklentilerini yaptıktan sonra, dict_to_database.py dosyasını çalıştırarak yeni bir database oluşturabilirsiniz. Bu database dosyasını, VocabularyAPP.py dosyası ile aynı dizindeki database ile değiştirerek kendi veri setleriniz üzerinde çalışabilirsiniz.

NOT: Uygulama herhangi bir ticari veya estetik kaygı taşımadan, tamamen sınava yönelik pratik çalışma amacıyla geliştirilmiştir. Benzer hizmeti ücretli abonelik sistemleri ile veren uygulamalar yerine kendi uygulamamı kullanmak ve basit de olsa bir proje deneyimim olması açısından bu uygulamayı geliştirmiş bulunmaktayım.  
 
