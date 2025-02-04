﻿**Введение**

Arcade_Infinity – это игра-аркада с бесконечными уровнями, где авантюрист путешествует по катакомбам. Сначала Вы ходите с обыкновенным пистолетом, но со временем за полученные у монстров монеты сможете купить оружие помощнее. Но чем больше уровней Вы пройдете, тем сложнее становиться дальше.

Описание файлов (по иерархии):

- master – файл запуска, где находятся главный класс, где происходят все действия в игре, функции для сохранения игры, установка ui спрайтов и так далее;

- sprites – файл классов игровых персонажей и других объектов;

- room – файл классов комнаты и коридора; 

- images – файл, где создаются и хранятся изображения персонажей и других объектов из директории map;

- ui – файл классов кнопок, магазина, товаров магазина и тому подобное;

- others – файл с дополнительными характеристиками и функциями.

Описание директории:

- textures – директория текстурок к игре;

- map – директория комнат к игре;

- ui – директория кнопок к игре;

- saves – директория сохранения к игре.

**Основная часть**

**Карта**

Все комнаты и коридоры сделаны в tiled editor map и находятся в директории map, но для комнат с монстрами, нужна директория с его названием в директории map/ barrels\_and\_spike. Почему так сделано будет объяснено в теме про бочки, шипов и свечек.

Комната 704\*704;

Протяженность коридора различна: длина вертикального - 608, горизонтального - 576. Но с учетом особенностями соединении с комнатами они выравниваются;

Ключевой момент карты: карта представляет собой квадрат 4\*4, в котором комнаты случайно выбирают свои координаты. Следовательно, с учетом коридоров между ними карта получается с длиной около 4500 и такой шириной. Тогда размер 4500\*4500. Координаты относительно квадрата 4\*4 нужны только для комнат и коридоров. Другие классы используют координаты относительно этих же комнат за исключением немногих.

И тогда поднимается вопрос об оптимизации отрисовки. Так как комнаты и коридоры прямоугольные, следовательно, можно найти их пересечение с экраном игры пользователя:

![](Картинки%20для%20readme/Aspose.Words.84858e6b-afc3-41ef-b2aa-0d1364c64585.001.png)![](Картинки%20для%20readme/Aspose.Words.84858e6b-afc3-41ef-b2aa-0d1364c64585.002.png)

Но этого было недостаточно. Любое крохотное пересечение все равно будет рисовать полную комнату, хотя нам нужно только ту часть, где она на экране. Для этого есть другая оптимизация:

![](Картинки%20для%20readme/Aspose.Words.84858e6b-afc3-41ef-b2aa-0d1364c64585.003.png)

![](Картинки%20для%20readme/Aspose.Words.84858e6b-afc3-41ef-b2aa-0d1364c64585.004.png)

Вторая особенность 2D проекта - это попытка сделать его 3D. То есть игрок может проходить сквозь определённую часть стены (в коде эту часть стены называется passing walls). Посмотрите на эти моменты:

![](Картинки%20для%20readme/Aspose.Words.84858e6b-afc3-41ef-b2aa-0d1364c64585.005.png) ![](Картинки%20для%20readme/Aspose.Words.84858e6b-afc3-41ef-b2aa-0d1364c64585.006.png) ![](Картинки%20для%20readme/Aspose.Words.84858e6b-afc3-41ef-b2aa-0d1364c64585.007.png)

Последние два фотографии идеально показывают попытку сделать игру 3D.

**Механика игры**

Инструкция клавиш и мышки:

- Клавиши W, A, S, D – движение игрока;

- Клавиша F - взять оружие;

- Клавиша G – выбросить оружие;

- Клавиша E – выпить бутылку исцеления;

- Клавиша Enter – перейти на следующий уровень;

- Клавиша Escape – пауза;

- Левая кнопка мыши – стрелять из оружия.

**Оружия**

В игре 11 видов и многие отличаются друг от друга не только по внешности, но и по особенности стрельбы, но у некоторых все же есть общие черты(M4A4 и AК47). Авантюрист может брать собой максимум 3 оружия и не может остаться без оружия, то есть у него Вы не сможете выбросить оружие, если оно у вас последнее в инвентаре. И чтобы главный герой не стрелял бесконечно, была добавлена перезарядка оружия. 

И тут есть одна особенность: авантюрист может поменять оружие во время перезарядки, но когда он опять возьмет оружие, требующие перезарядку, вместо полного магазина будет написана 0, и, когда Вы нажмете на выстрел, то он начнет его перезаряжать. Объясняется это тем, что главный герой часто забывает количество патронов в оружие. 

Также есть другая особенность оружий. Все оружия стреляют туда, куда указывает мышка. И у оружия есть разброс, то есть пуля может откланяться от места назначения. Идеальный пример – сравните узи с AK47 или М4А4. Также на разброс пули влияет положение мыши: чем ближе к персонажу, тем сильнее разброс. Из-за разброса может понизиться точность, а в игре, скажу по секрету, очень важна точность попадания по монстру.

Другие особенности оружия и пуль:

- Пули в зависимости от оружия могут иметь разные размеры, скорость полета или наносить урон по области;

- Золотой пистолет(Infinity) имеет бесконечные патроны;

- Установщик мин (Miniplacer) ставит вместо пули мину, которая стоит на месте и через некоторое время, если не наступили на нее монстры, исчезает.


**Монстры**

Как только авантюрист заходит в комнату с монстрами, все монстры сразу нацеливаются на него. После смерти они 'отдают' монеты игроку. Монстров пока 2 вида: гули и зомби. 

Гули не носят оружия (если смотреть на них в игре) и ориентированы на ближний бой. Во время сражения они прямо идут к главному герою, но иногда могут пойти в любую другую сторону с большей скоростью, из-за чего монстры либо приблизятся к вам быстрее, если другая сторона – это именно к вам, либо отдалятся, если другая сторона – это от вас, либо идти к вам с другой стороны. Такое движение заставляет человека долго прицеливаться. Гули большие и всегда идут на игрока, что делает их танками защищая зомби от выстрелов игрока.

Зомби носят пистолеты и ориентированы на дальний бой. Во время сражения они прицеливаются к авантюристу и периодически стреляют по нему. 10 пуль от зомби способны убить игрока, что может заставить главного героя часто двигаться. Зомби маленькие и не всегда идут на игрока, но точны.

Со временем они станут сильнее, например, увеличиться урон, игрок меньше будет получать монет и тому подобное.

**Бочки, шипы и свечи**

Бочки – преграда, которая либо спасает, либо препятствует игроку. После разрушения, они могут оставить (15 % вероятность) бутылку исцеления.

Шипы – преграда, на которую, если человек наступает, получает урон.

Свечи – простая декорация, через которую не может пройти персонаж.

Их объединяет то, что они устанавливаются по-особому: в комнатах, изначально находящиеся в директории map, в первом слое под названием 'Флажки' расположены специальные плитки, на которых будут стоять свечи. А в map/barrels\_and\_spike расположены директории комнат, внутри которых можно увидеть варианты установок бочек и шипов. Это сделано для того, чтобы в будущем сделать вторую программу или на tiled editor map люди в будущем создавали свои комнаты со своими вариантами установок бочек и шипов. Специальные плитки имеют id, которые нужны для инициализации комнат. Какие это id - написано в документации классов бочек, шипов и свечек. Примеры:

![](Картинки%20для%20readme/Aspose.Words.84858e6b-afc3-41ef-b2aa-0d1364c64585.008.png) ![](Картинки%20для%20readme/Aspose.Words.84858e6b-afc3-41ef-b2aa-0d1364c64585.009.png)

**Сохранение**

В директории saves хранятся 3 сохранения игры. После прохождения, например, первого уровня в сохранение перезаписываются ваши данные, а именно: здоровье, баланс (кол-во монет) и инвентарь игрока и следующий уровень. Если вы проигрываете, то данные перезаписывают такие, с какими Вы начинаете игру с самого начала. Если в начале уровня у Вас было полное здоровье, а после прохождения комнаты стало 70, и Вы вышли и зашли обратно, то у Вас будет полное здоровье, а не 70.

**Заключение**

В заключение, каждый из нас напишет свой абзац о проекте.

Данис:

Было сложно. Мы многого хотели сделать, но не успели. Его еще можно продолжить, например, добавить ‘вторую жизнь’, новые оружия, новых монстров, выбор внешности главного героя (не только его) и еще много чего. У этого проекта есть будущее и его можно продолжить.


Руслан:

Я рад, что участвовал в создании этого проекта. Он показал мне, что не стоит планировать больше, чем сумеешь и успеешь сделать. Не так просто было создавать игру без игрового движка, реализовывать ее механики с полного нуля. Но это очень был интересный опыт. Могу сказать, что проекту есть куда стремиться, его можно доработать и сделать еще лучше.
