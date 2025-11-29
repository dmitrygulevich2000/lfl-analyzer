## Запросы к API/сайту ЛФЛ

### JSON

#### Турниры
1. Турниры/дивизионы, в которых участвует команда 
   * [https://api.lfl.ru/api/V2/tournaments?clubId=2282&per_page=10&season=82](https://api.lfl.ru/api/V2/tournaments?clubId=2282&per_page=10&season=82)
   * ещё можно передать active=true/false
   * в ответе есть турниры из которых состоит дивизион
2. Турниры, из которых состоит дивизион
   * [https://api.lfl.ru/api/divisions/730/tournaments](https://api.lfl.ru/api/divisions/730/tournaments) 
3. Турниры, в которых участвует игрок
   * [https://api.lfl.ru/api/persons/13992/tournaments?season=82](https://api.lfl.ru/api/persons/13992/tournaments?season=82)
4. Таблица турнира/дивизиона (только для tournament_type="Круговой турнир")
   * [https://api.lfl.ru/api/tournaments/28285/rating?per_page=30](https://api.lfl.ru/api/tournaments/28285/rating?per_page=30)
   * для дивизиона будет всё вперемешку

#### Статистика игроков клуба
1. Вся статистика в турнире/дивизионе:
   * [https://api.lfl.ru/api/clubs/2282/squads?page=1&per_page=50&division=730](https://api.lfl.ru/api/clubs/2282/squads?page=1&per_page=50&division=730)
   * для дивизиона возвращает, видимо, голы за всё время
2. Голы и передачи в турнире/дивизионе
   * [https://api.lfl.ru/api/divisions/1086/goalAndAssist/2282?page=1&per_page=30](https://api.lfl.ru/api/divisions/1086/goalAndAssist/2282?page=1&per_page=30)
   * нет бага для дивизиона
   * работает помедленнее, чем squads
3. Статистика вратарей в турнире/дивизионе
   * [https://api.lfl.ru/api/divisions/730/goalkeepers/2282?page=1&per_page=30](https://api.lfl.ru/api/divisions/730/goalkeepers/2282?page=1&per_page=30)

#### Матчи
1. Матчи клуба в турнире (сыгранные):
   * ...
   * иногда может возвращать несыгранный матч ([пример](https://page.lfl.ru/matches-calendar/2282?order=desc&currentDate=true))
   * нет фильтра по дивизиону + дивизион не всегда указан в ответе ([пример](https://api.lfl.ru/api/matches?club=2282&division_id=d1086&season=&per_page=40&currentDate=true&sort=time))
2. Протокол матча
   * ...
   * в ответе не предусмотрены передачи
3. Матчи игрока (используется player_id, отсортированы по убыванию даты) 
   * [https://api.lfl.ru/api/persons/39335/matches?per_page=30&tournament=29582&season=82](https://api.lfl.ru/api/persons/39335/matches?per_page=30&tournament=29582&season=82)

### HTML

1. Матчи клуба в турнире (отсортированные по убыванию даты):
   * [https://lfl.ru/tournament29582/tour/match?club_id=10779&sortBy=name_desc](https://lfl.ru/tournament29582/tour/match?club_id=10779&sortBy=name_desc)
2. Статистика игроков клуба в **дивизионе**:
   * [https://lfl.ru/?ajax=1&method=tournament_squads_table&division_id=1086&club_id=2282](https://lfl.ru/?ajax=1&method=tournament_squads_table&division_id=1086&club_id=2282) 
   