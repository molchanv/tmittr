# в функцию передается словарь данных из формы, в котором имеются пары ключ:значение вида {"mon":1}
# функция извлекает все значения из таких пар, соединяет воедино и привязывает к ключу weekdays
def weekdays_nums(dict):
    week = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    nums = []
    dict = dict.copy()

    for weekday in week:
        if weekday in dict:
            # в список nums записывается порядковыый номер дня недели
            nums.append(str(dict[weekday]))
            # из словаря удаляется день недели
            dict.pop(weekday)

    # элементы списка nums собираются воедино
    weekdays = ''.join(nums)
    # в словаре остается одна пара ключ:значение, в которую записывается число вида "134", где
    # каждая цифра - порядковый номер дня недели
    dict['weekdays'] = int(weekdays)
    return dict


# эта функция преобразует число в список с днями недели
def inverse_weekdays_nums(nums):
    week = {
        '1': 'Пн',
        '2': 'Вт',
        '3': 'Ср',
        '4': 'Чт',
        '5': 'Пт',
        '6': 'Сб',
        '7': 'Вс',
    }
    list = []
    for i in str(nums):
        if i in week:
            list.append(week[i])
    return list
