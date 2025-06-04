---
id: nvme-perf-tests
title: Тесты производительности nvme дисков
description: Собираем тесты производительности nvme дисков
tags: [hardware, drive, perf, tests, nvme]
---
# Тесты nvme дисков

Собираем тесты производительности nvme дисков

## Методика
Для тестирования диска используем [FIO](https://fio.readthedocs.io/en/latest)
#### Тест 1. Линейная запись
Проверяем сколько байтиков можно влить в устройств за 60 секнуд
```bash
fio -ioengine=libaio -direct=1 -invalidate=1 -name=SeqWr4Md32t60 -bs=4M -iodepth=32 -rw=write -runtime=60 -filename=/dev/nvmeXn1
```
#### Тест 2. Линейное чтение

## Сводная таблица

| Производитель | Модель | FW rev |Размер | Тест 1 | Тест 2 |
| --- | --- | --- | --- | --- | --- |
| INTEL | SSDPF2KE032T1O | 9CV10450 | 3.20  TB | | |