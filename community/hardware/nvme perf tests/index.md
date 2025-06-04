---
id: nvme-perf-tests
title: Тесты производительности nvme дисков
description: Собираем тесты производительности nvme дисков
tags: [hardware, drive, perf, tests, nvme]
---
# Тесты nvme дисков

Собираем тесты производительности nvme дисков

## Методика (надо бы заскриптовать)
Для тестирования диска используем [FIO](https://fio.readthedocs.io/en/latest)
#### Тест 1. Линейная запись
Проверяем сколько байтиков можно влить в устройств за 600 секнуд
```bash
fio -ioengine=libaio -direct=1 -invalidate=1 -name=SeqW4Md32t600 -bs=4M -iodepth=32 -rw=write -runtime=600 --output SeqW4Md32t600.json --output-format=json+ -filename=/dev/nvmeXn1
```
в таблицу вставляем вывод 
```bash
jq '.jobs[].write.bw_bytes' SeqW4Md32t600.json
```

#### Тест 2. Линейное чтение
```bash
fio -ioengine=libaio -direct=1 -invalidate=1 -name=SeqR4Md32t600 -bs=4M -iodepth=32 -rw=read -runtime=600 --output SeqR4Md32t600.json --output-format=json+ -filename=/dev/nvmeXn1
```
в таблицу вставляем результат 
```bash
jq '.jobs[].read.bw' SeqR4Md32t600.json 
```
---
По возможности приложите полные файлы тестов в папку fio-results, подпапка с именем производитель_модель

## Сводная таблица

| Производитель | Модель | FW rev |Размер | Тест 1 | Тест 2 |
| --- | --- | --- | --- | --- | --- |
| INTEL | SSDPF2KE032T1O | 9CV10450 | 3.20  TB |3763883354| 6753895 |