##Database fields:

- ts DateTime
- userId (UInt32) - я думаю что при условии что в день будет загружаться фал такого размера, то UInt32 можетн не хватить. Есть пустые значения.
- sessionId UInt32 - вообще по первому мнению максимальное значение 4808, но что то пошло не так, вероятно там есть значение больше, по этому unit32.
- page FixedString(50) - обычно их ограничееное количество и для экономии места, можно тоже было в Enum8 перевести.
- auth FixedString(10) - можно тоже в Enum8
- method FixedString(7) - максимальным по колиеству символов, из принятных, статусом является CONNECT, но в выборке присутствуют только 2 GET\PUT, и если бы я обладал большей информациие о выгрузке, то вероянто использовал Enum8
- status UInt16 - Тут аналогично, была бы спецификация веб сервиса, с указанием возможных ответов, опять же Enum8
- level Enum8 -  0 = free \ 1 = paid
- itemInSession UInt16 - Максимально 1005, по этому и не UInt8
- location Nullable(String) - Возможно стоило разделить на 2 поля, по запятой, потому что как я понимаю это округа - можно было сделать не nullable
- userAgent Nullable(String) - можно было сделать не nullable
- lastName Nullable(FixedString(50)) - Тут скорее нужно как то условится о максимальной длинне имени - можно было сделать не nullable
- firstName Nullable(FixedString(50)) -  Тут скорее нужно как то условится о максимальной длинне фамилии - можно было сделать не nullable
- registration DateTime
- gender Enum8 - 0 = Null \ 1 = M \ 2 = F 
- artist Nullable(String) - можно было сделать не nullable
- song  Nullable(String) - можно было сделать не nullable
- length Float32


"можно было сделать не nullable" как я понял nullable поля медленне работают, по этому можно их перевести в не null, по примеру gender