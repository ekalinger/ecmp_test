# ECMP TEST
***Схема:***

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;----------&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;------------  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  <-OSPF-> |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  
input ->|  R1  &nbsp;&nbsp;|  <-OSPF-> |   R2     |  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  <-OSPF-> |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;----------&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;------------  
  
R1, R2 - namespaces  
input, OSPF - линки veth(3 штуки)  
пакеты забираются внутри namespace r2 с непосредственно veth  
  
Проверка работы ECMP основана на генерации пакетов с случайными последовательностями TCP портов, IP Source. IP Destination оставляем статичным, но при версии ядра 6.14 и выше можно протестить несколько IP destination  
Для проведения тестов генерируем пакеты и тут же вычисляем хэш и смотрим как он должен распределиться. Далее отправляем пакеты и снифаем уже на veth R2 (output1, output2, output3)  
Если распределения примерно совпадают, то тест проходит  
  
***Условия:*** 
Linux debian или ubuntu  
На текущий момент в ядре линукс старше 5.13 реализован хеширование пакета по чистому IP Source в случае активации ECMP, все версии ниже можно только настроить хеширование по IP Source и IP Destination  
Перел запуском настройки окружени необходимо проверить версию ядра и в зависимости от этого отредкатировать файл environment.sh и закомментировать/расскомментировать сответсвующие строки  
  
***Настройка окружения:***  
1)отредактировать при необходимости файл environment.sh и запустить его  
2)запустить pip3 install requirements.txt  
3)запустить тест pytest --alluredir=allure-results  
4)проверить получение маршрутов OSPF и установление метрик в namespaces r1 (ip netns exec r1 ip route)  
"""  
(venv) root@debian:/home/user/ecmp_test# ip netns exec r1 ip route  
10.0.1.0/24 dev veth-r1-input proto kernel scope link src 10.0.1.1  
10.1.1.0/24 dev veth-r1-l2 proto kernel scope link src 10.1.1.1  
10.2.1.0/24 dev veth-r1-l3 proto kernel scope link src 10.2.1.1  
10.3.1.0/24 dev veth-r1-l4 proto kernel scope link src 10.3.1.1  
172.172.174.1 proto ospf metric 20  
        nexthop via 10.1.1.2 dev veth-r1-l2 weight 1  
        nexthop via 10.2.1.2 dev veth-r1-l3 weight 1  
        nexthop via 10.3.1.2 dev veth-r1-l4 weight 1  
"""  
5)для проверки результата запустить allure serve -h xx.xx.xx.xx -p 10050 allure-results, где хх.хх.хх.хх IP адресс вашего сервера  

***Методики тестов***
Проверка распределения пакетов по Source IP на 3 интерфейса.
Начальные условия - маршруты в 
1)На вход подаём траффик
