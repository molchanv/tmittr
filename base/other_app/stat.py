# Изменение статистики пользователя
# пример: если у пользователя статистика 1 0 0, где 1 - "в процессе",
# то при передаче такой статистики в stat_success отнимется единица от "в процессе"
# и прибавится к "выполненно"

def stat_in_process(stat):
    list = stat.split(',')
    list[0] = str(int(list[0]) + 1)
    return ','.join(list)

def stat_success(stat):
    list = stat.split(',')
    list[1] = str(int(list[1]) + 1)
    list[0] = str(int(list[0]) - 1)
    return ','.join(list)

def stat_fail(stat):
    list = stat.split(',')
    list[2] = str(int(list[2]) + 1)
    list[0] = str(int(list[0]) - 1)
    return ','.join(list)
