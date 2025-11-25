## Запросы к API/сайту ЛФЛ

### JSON

1. Статистика игроков клуба в турнире/дивизионе
   * ...
   * для дивизиона возвращает, видимо, голы за всё время ([пример](https://api.lfl.ru/api/clubs/2282/squads?per_page=50&division=922))  
2. Матчи клуба в турнире (сыгранные):
   * ...
   * иногда может возвращать несыгранный матч ([пример](https://page.lfl.ru/matches-calendar/2282?order=desc&currentDate=true))
   * не работает фильтр по дивизиону + дивизион не всегда указан в ответе ([пример](https://api.lfl.ru/api/matches?club=2282&division_id=d1086&season=&per_page=40&currentDate=true&sort=time))
3. Протокол матча
   * ...
   * в ответе не предусмотрены передачи 
4. Таблица турнира
   * [https://api.lfl.ru/api//tournaments/28285/rating?per_page=30](https://api.lfl.ru/api//tournaments/28285/rating?per_page=30) 
5. Матчи игрока (используется player_id, отсортированы по убыванию даты) 
   * [https://api.lfl.ru/api/persons/39335/matches?per_page=30&tournament=29582](https://api.lfl.ru/api/persons/39335/matches?per_page=30&tournament=29582)
   * опционально указывается tournament


### HTML

1. Матчи клуба в турнире (отсортированные по убыванию даты):
   * [https://lfl.ru/tournament29582/tour/match?club_id=10779&sortBy=name_desc](https://lfl.ru/tournament29582/tour/match?club_id=10779&sortBy=name_desc)
2. Статистика игроков клуба в **дивизионе**:
   * [https://lfl.ru/?ajax=1&method=tournament_squads_table&division_id=1086&club_id=2282](https://lfl.ru/?ajax=1&method=tournament_squads_table&division_id=1086&club_id=2282) 
   