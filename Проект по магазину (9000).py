import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px

df_products = pd.read_csv('/Users/dimagetmanskij/Downloads/product.csv')
df_users = pd.read_csv('/Users/dimagetmanskij/Downloads/users.csv')


n_products = len(df_products) #Количество товаров
n_users = len(df_users)  #Количество клиентов
n_orders = 9000  #Количество новых заказов

np.random.seed(42)  #Фиксируем случайность чисел, чтобы были одинаковые данные при каждом запуске программы

#Создание датафрейма таблицы с заказами
df_orders = pd.DataFrame({
    'order_number': range(1, n_orders + 1),  #Присваивание уникального номера заказа от 100 до 300
    'product_id': np.random.randint(1, n_products + 1, n_orders), #Присваивание рандомного id товара от 1 до 48 не вкл и по количеству новых заказов (200)
    'person_id': np.random.randint(1, n_users + 1, n_orders),  #Присваивание рандомного id покупателя от 1 до 40 (41 не в счёт) и в конце сгенерировать наши 200 шт
    'quantity': np.random.randint(1, 6, n_orders),  # минимальное значение(1), максимальное значение(6, не включая), сколько раз сгенерировать (9000)
    'status': np.random.choice(
    ['delivered', 'pending', 'cancelled'],
    n_orders,
    p=[0.7, 0.2, 0.1])
})

df_orders = df_orders.merge(
    df_products[['id', 'price']],
    left_on='product_id',
    right_on='id',
    how='left')
df_orders['total'] = df_orders['quantity'] * df_orders['price']
df_orders = df_orders.drop('id', axis=1) #Добавление столбца total (общая сумма заказа)

def generate_random_dates(n_orders, start_date = '2025-01-01', end_date = '2026-01-01'):
#Добавление столбца 'время заказа' в таблицу с заказами

    start = pd.to_datetime(start_date)  #Превращение значений в даты
    end = pd.to_datetime(end_date)  #Превращение значений в даты
    days_range = (end - start).days  #Подсчёт кол-ва дней между датами
    random_dates = np.random.randint(0, days_range + 1, n_orders)  #Выбирает случайное число дней от 0 до 365 на кол-во сгенерированных заказов
    return start + pd.to_timedelta(random_dates, unit='D') #Прибавление случайного кол-ва дней в дате start

df_orders['date_order'] = generate_random_dates(n_orders) #Вызов функции с новым столбцом с датой заказа на кол-во заказов

print(df_orders.isnull().sum())  #Проверка, что все строки заполнены
print(df_products.isnull().sum()) #Проверка, что все строки заполнены
print(df_users.isnull().sum()) #Проверка, что все строки заполнены

print(f'Первые 5 строк таблицы с товарами: \n{df_products.head()}')
print('=' * 150)
print(f'Первые 5 строк таблицы с клиентами: \n{df_users.head()}')
print('=' * 150)
print(f'Первые 5 строк таблицы с заказами: \n{df_orders.head()}')


#Подсчет различных KPI метрик
total_price = df_orders.query("status == 'delivered' ")['total'].sum() #Общая выручка у магазина
total_quantity_1 = df_orders.query("status != 'cancelled' ")['quantity'].sum() #Способ посчитать кол-во покупок товаров без учета отмененных заказов

avg_price = total_price / len(df_orders) if total_quantity_1 > 0 else 0 # Подсчёт AOV

cost_price = 2969857658 #Себестоимость
margin = total_price - cost_price #Маржа

try:
    marginality = margin/total_price * 100 #Маржинальность
except ZeroDivisionError:
    marginality = 0
    print('Внимание: недостаточно общей выручки для расчёта маржинальности')


unique_users = df_users['id'].nunique() #Количество уникальных клиентов

ARPU = total_price / unique_users  if unique_users > 0 else 0 # ARPU

#Подсчёт конверсии на целевое действие
joined = df_users.merge(df_orders, left_on='id', right_on='person_id', how='left')
target_users = joined.query("status == 'delivered' ")['id'].nunique()  #Количество покупателей
try:
    conversion = target_users / unique_users * 100
except ZeroDivisionError:
    conversion = 0
    print('Внимание: нет пользователей для расчёта конверсии')

#Подсчет топ-5 товаров по прибыли
top_5 = df_products.merge(df_orders, left_on = 'id', right_on = 'product_id', how = 'inner')
top_5 = top_5.groupby('title')['total'].sum().sort_values(ascending = False).head(5)

total_product = df_products['id'].count() #Общее кол-во товаров в магазине

total_orders = df_orders['order_number'].count() #Общее кол-во заказов за год

avg_quantity_orders = total_quantity_1 / total_orders  if total_orders > 0 else 0#Среднее кол-во товаров в заказе

median_price = df_orders.query("status == 'delivered'")['total'].median() #Подсчёт медианной стоимости заказов

print('=' * 150)
print('KPI метрики по анализу магазина:')
print(f'1. 💰Общая выручка: {total_price} руб.')
print(f'2. 💵Средний чек: {avg_price:.2f} руб.')
print(f'3. 🛒Общее количество купленных товаров за год: {total_quantity_1} шт.')
print(f'4. 🛒Общее количество заказов за год: {total_orders}')
print(f'5. ✔️Маржа : {margin:.2f} руб.')
print(f'6. ✔️Маржинальность: {marginality:.2f}%')
print(f'7. 👤Количество уникальных пользователей: {unique_users} пользователей')
print(f'8. 👤Сколько денег приносит в среднем один покупатель (ARPU): {ARPU:.2f} руб.')
print(f'9. 📦Общее количество товаров в магазине: {total_product}')
print(f'10. 📈ТОП-5 самых доходных товаров: \n{top_5}')
print(f'11. 🎯Конверсия целевой аудитории, которая купила товар: {conversion:.1f}%')
print(f'12. 🎯Целевых пользователей: {target_users}')
print(f'13. 📦Среднее количество товаров в заказе: {avg_quantity_orders:.1f}')
print(f'14. 💰Медианная стоимость заказа: {median_price} руб.')
print()
print('=' * 150)
print('Рекомендации по бизнесу исходя из метрик:')
print("""1. 🚨Сделать бонусную программу для топ-5 клиентов по доходности 
2. 🚨Проанализировать с чем связан спад продаж с октября прошлого года
3. ⚠️Сделать А/В тесты по рекламным интеграциям по привлечению новых клиентов и проверить как на это изменится кол-во:
а) новых клиентов
б) целевых пользователей
в) изменению конверсии 
4. ⚠️Увеличить продукцию магазина до 60 товаров и следить за новинками и их продаваемостью
5. Следить за остатками в магазине основных товаров, которые имеют топ-5 по популярности 
6. Проверить на каких этапах воронки конверсии люди отказываются от товаров и также проверить логистику ожидаемых товаров и постараться уменьшить pending до 15%
""")




"""Вторая часть проекта"""

#Добавим в прошлую таблицу с 9000 заказами заказов за первый месяц года
count_orders = len(df_orders)
max_order_num = df_orders['order_number'].max()
max_date_order = df_orders['date_order'].max()


new_count_orders = 730  #Количество заказов за январь

np.random.seed(777) #Сохранение данных без совпадения с прошлым

new_orders = pd.DataFrame({
    'order_number': range(max_order_num + 1, max_order_num + new_count_orders + 1),
    'product_id': np.random.randint(1, n_products + 1, new_count_orders),
    'person_id': np.random.randint(1, n_users + 1, new_count_orders),
    'quantity': np.random.randint(1, 4, new_count_orders),
    'status': np.random.choice(
        ['delivered', 'pending', 'cancelled'], new_count_orders,
        p=[0.8, 0.1, 0.1]
    )
})

#Добавляем цены и считаем сумму (как в основном коде)
new_orders = new_orders.merge(
    df_products[['id', 'price']],
    left_on='product_id',
    right_on='id',
    how='left'
)
new_orders['total'] = new_orders['quantity'] * new_orders['price']
new_orders = new_orders.drop('id', axis=1)

#Добавляем даты (продолжение по последней дате)
def add_new_dates(n_orders, start_date, end_date_delta_days=60):
    """Генерирует даты после последней существующей даты"""
    start = pd.to_datetime(start_date) + pd.Timedelta(days=1)
    end = start + pd.Timedelta(days=end_date_delta_days)
    days_range = (end - start).days
    random_days = np.random.randint(0, days_range + 1, n_orders)
    return start + pd.to_timedelta(random_days, unit='D')

new_orders['date_order'] = add_new_dates(
    new_count_orders,
    start_date=max_date_order,
    end_date_delta_days=31  # новый период до 31 дней после последнего заказа(месяц)
)


print('=' * 100)
print(new_orders.head())
# print(f'Было заказов за прошлый год - {len(df_orders)}')
# print(f'Добавилось ещё заказов - {len(new_orders)}')
# print(f'Количество дубликатов {new_orders.duplicated().sum()}')
# print(f'Проверка на пустые значения в таблице {new_orders.isnull().sum().sum()}')



#Начинаем подсчёт KPI-метрик магазина по новым заказам по январю
unique_users_january = new_orders['person_id'].nunique()  #Подсчет уникальных пользователей

df_new_orders_merge = df_users.merge(new_orders, left_on='id', right_on='person_id', how='left')
target_users = df_new_orders_merge.query("status == 'delivered'")['id'].nunique()  #Подсчет целевых действий клиентов
try:
    conversion_january = target_users / unique_users_january * 100 #Подсчёт конверсии с проверкой
except ZeroDivisionError:
    conversion_january = 0
    print('Недостаточно уникальных клиентов для подсчета конверсии за месяц')

orders_delivered = new_orders.query("status == 'delivered'")['order_number'].nunique()  #Количество доставленных заказов
orders_pending = new_orders.query("status == 'pending'")['order_number'].nunique()  #Количество заказов в ожидании
orders_cancelled = new_orders.query("status == 'cancelled'")['order_number'].nunique()  #Количество отмененных заказов

total_revenue_january = new_orders.query("status == 'delivered'")['total'].sum()  #Общая выручка за Январь

ARPU = total_revenue_january / unique_users_january
median_price_january = new_orders.query("status == 'delivered'")['total'].median()
avg_price_january = total_revenue_january / len(new_orders) if len(new_orders) > 0 else 0

total_quantity_january = new_orders.query("status != 'cancelled'")['quantity'].sum()  #Общее кол-во купленных товаров

avg_quantity_orders_january = total_quantity_january / len(new_orders) if len(new_orders) > 0 else 0   #Среднее кол-во товаров в заказе

print('📊 KPI метрики за январь 2026')
print('=' * 100)
print(f'🎯Общее кол-во заказов за январь - {len(new_orders)} ')
print(f'💰Общая выручка за январь составляет {total_revenue_january} рублей')
print(f'🚀Количество доставленных заказов - {orders_delivered}')
print(f'⏸️Количество заказов в ожидании - {orders_pending}')
print(f'❌Количество отмененных заказов - {orders_cancelled}')
print(f'👥Общее количество пользователей за месяц - {new_orders['person_id'].nunique()}')
print(f'👥Количество целевых клиентов за январь - {target_users}')
print(f'👑Конверсия за январь составляет - {conversion_january:.1f}%')
print(f'💳ARPU в январе составляет - {ARPU:.1f} рублей')
print(f'💵Медианная стоимость заказа составляет - {median_price_january:.1f} рублей ')
print(f'🏷️AOV составляет - {avg_price_january:.1f} рублей')
print(f'🎁Общее количество купленных товаров за Январь - {total_quantity_january}')
print(f'💵Среднее количество товаров в заказе - {avg_quantity_orders_january:.1f}')
print()
print('=' * 45 +'💡Выводы :' +'=' * 45)
print('=' * 100)
print('1. ➡️Общее количество заказов относительно не изменилось по среднему кол-ву за прошлые месяца в прошлом году')
print('2. 🔥Количество покупателей не изменилось, нет новых клиентов, но и не повысился отток клиентов')
print('3. 📈Улучшилась логистика по заказам, которые находятся в ожидании, в прошлом году в среднем ожидающих заказов было ~147 шт'
      '\n В Январе видим, что ситуация улучшилась почти в 2 раза (84)')
print('4. 🚨Есть глобальный просед по общей выручке заказов, в прошлом году самый неудачный месяц принес 398млн. рублей'
      '\n Здесь же видим, что убыток в виде более 100 млн.рублей')
print('5. 🚨Сильный просед по выручке складывается по двум основным причинам:'
      '\n   1) Январь - месяц долгих новогодних праздников, что могло в том числе повлиять, хотя если сравнивать с прошлым годом,'
      '\n то такого сильного падения не было (более 600 млн.рублей)'
      '\n   2) Что более всего вероятным является по падению, сильное падение общего количество купленной продукции за месяц'
      '\n        а) в прошлом году в среднем за месяц ~2000 товаров'
      '\n        б) Январь - 1380 шт '
      '\n   3) Также наблюдаем спад по среднему количеству товаров в заказе (2.7 > 1.9)' )
print('6. ⚠️В заключении : '
      '\n Количество заказов относительно без изменений, улучшилась логистика заказов по количеству ожидаемых заказов'
      '\n Ухудшилась общая выручка, средний чек, среднее количество товаров в заказе')
print()
print('=' * 100)
print('=' * 42 +'🎯Рекомендации :' +'=' * 42)
print('\n1. ⚠️Проверить склад на количество всей продукции, так как это может быть одной из причин недостатка количества товаров заказах'
      '\n2. 🚨Проверить исправность сайта на добавление в корзину товаров, особенно более 3 товаров, так как более 3 товаров в заказе не было ни у одного клиента'
      '\n3. 🚨Запустить рекомендательную систему в магазине(если ещё не запущена), то есть разработать рекомендации для клиентов,'
      '\n для увеличения плотности корзины клиента'
      '\n4. ⚠️Разработать скидку для клиентов, например, берете 3 товара = 4 и последующие товары идут со скидкой в 20%, '
      '\nчто сильно может заинтересовать клиентов на количество'
      '\n5. 📦Увеличить продукцию магазина, увеличение товарности магазина в 60 товаров (сейчас 47)')

merge_full_by_csv = (
    new_orders
    .merge(df_users, left_on='person_id', right_on='id', how='inner')
    .merge(df_products, left_on='product_id', right_on='id', how='inner')
)  #Делаем денормализация для создания дашбордов

merge_full_by_csv.to_csv('junuary.csv', index=False)

#Общая таблица со всеми заказами за прошлый год + январь
df_all_orders = pd.concat([df_orders, new_orders], ignore_index=True)
print(f'Общее количество заказов в системе: {len(df_all_orders)}')



#Строим один обычный график в самом Python через библиотеку plt
new_orders['date_order'] = pd.to_datetime(new_orders['date_order'], errors='coerce')
show = new_orders.groupby(new_orders['date_order'].dt.date)['total'].sum()
show.plot(kind='bar')
plt.title('Динамика выручки в Январе', fontsize=18)
plt.xlabel('Дата', fontsize=11)
plt.ylabel('Выручка', fontsize=11)
plt.xticks(rotation=45, ha='right', fontsize=8)
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.show()

#Интерактивный график - топ-5 категорий по выручке за январь
merge_full_by_csv['total_delivered'] = merge_full_by_csv.apply(
    lambda row: row['total'] if row['status'] == 'delivered' else 0, axis=1)
top_5 = merge_full_by_csv.groupby('category')['total_delivered'].sum().reset_index()
fig = px.bar(
    top_5,
    x='category',
    y='total_delivered',
    title='Динамика выручки в январе',
    labels={'total_delivered': 'Выручка (руб.)', 'category': 'Категория'},
    color='category'
)
fig.write_html("revenue_dynamic.html")  #График сохранен в систему компьютера и может быть показать в браузере или в самом PyCharm


fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 7))

new_orders.groupby(new_orders['date_order'])['total'].sum().plot(ax=axes[0], kind='line')
axes[0].set_title('Динамика выручки')

top_5.groupby('category')['total_delivered'].sum().reset_index().plot(ax=axes[1], kind='bar')
axes[1].set_title('Топ по категориям')

plt.savefig('my_dashboard.png')
print("График сохранён как my_dashboard.png")










# #Создаем А/B тест с критериями для него
# AB_TEST = {
#     'discount': 0.10,  # процент скидки для топ-5 товаров (10%)
#     'test_duration': 30, # прописываем, что тест у нас будет длиться по времени 30 дней
#     'sample_ratio': 0.5,   #Для выборки берем одинаковое кол-во людей в А и В категории
#     'alpha': 0.05,     #Это p-value, которое означает на какой риск мы можем пойти в тесте, если продажи в В тесте выросли на 10% и p-value < 0.05, то значит скидка сработала и шанс совпадения результата минимален
#     'min_detectable_effect': 0.05 #Какой минимальный эффект хотим получить от теста, то есть здесь задаем значение от 5% минимум нам нужно улучшение конверсии
# }


# def generate_ab_test_data(df_products, df_orders, df_users, discount = 0.10, n_new_orders = 1000):
#     #Определяем топ-5 товаров по выручке
#     top_5 = df_orders.groupby('product_id')['total'].sum().nlargest(5).index.tolist()
#
#     #Делим пользователей на 2 две группы
#     users = df_users['id'].tolist()
#     np.random.shuffle(users)
#     split = len(users) // 2
#     group_a = users[:split]
#     group_b = users[split:]
#
#     #Создаем новые заказы
#     last_order_num = df_orders['order_number'].max() #Находим максмальный номер заказа (9000) для того, чтобы продолжить с этого момента новое кол-во заказов
#
#     test_orders = pd.DataFrame({
#         'order_number': range(last_order_num +1, last_order_num + n_new_orders +1),
#         'product_id': np.random.choice(df_products['id'].to_list(), n_new_orders),
#         'person_id': np.random.choice(users, n_new_orders),
#         'quantity': np.random.randint(1, 6, n_new_orders),
#         'status': np.random.choice(['delivered', 'pending', 'cancelled'],
#     n_new_orders,
#     p=[0.7, 0.2, 0.1])
#     })
#
#     #Добавляем метку группы
#     test_orders['ab_group'] = test_orders['person_id'].apply(
#         lambda x: 'B (скидка)' if x in group_b else 'A (контроль)'
#     )
#
#     #Применяем скидку для группы B на топ-5 товаров
#     test_orders = test_orders.merge(df_products[['id', 'price']], left_on='product_id', right_on='id', how='left')
#     test_orders['price_adjusted'] = test_orders['price']
#     mask = (test_orders['ab_group'] == 'B (скидка)') & (test_orders['product_id'].isin(top_5))
#     test_orders.loc[mask, 'price_adjusted'] = test_orders['price'] * (1 - discount)
#
#     test_orders['total'] = test_orders['quantity'] * test_orders['price_adjusted']
#     test_orders = test_orders.drop('id', axis=1)
#
#     # 6. Добавляем даты тестового периода
#     test_start = pd.Timestamp('2026-01-01')
#     test_end = pd.Timestamp('2026-02-01')
#     test_days = (test_end - test_start).days
#     test_orders['date_order'] = test_start + pd.to_timedelta(
#         np.random.randint(0, test_days + 1, n_new_orders), unit='D'
#     )
#
#     return test_orders, group_a, group_b, top_5
#
# class ABTest:
#     def __init__(self, test_orders, group_a_label='A (контроль)', group_b_label='B (скидка)'):
#         self.df = test_orders
#         self.group_a_label = group_a_label
#         self.group_b_label = group_b_label
#         self.group_a = self.df[self.df['ab_group'] == group_a_label]
#         self.group_b = self.df[self.df['ab_group'] == group_b_label]
#
#     def calculate_metrics(self):
#         """Считаем метрики для каждой группы"""
#
#         def group_stats(group_data):
#             delivered = group_data[group_data['status'] == 'delivered']
#             total_orders = len(group_data)
#             delivered_orders = len(delivered)
#             conversion = (delivered_orders / total_orders * 100) if total_orders > 0 else 0
#
#             return {
#                 'total_orders': total_orders,
#                 'delivered': delivered_orders,
#                 'pending': len(group_data[group_data['status'] == 'pending']),
#                 'cancelled': len(group_data[group_data['status'] == 'cancelled']),
#                 'conversion': conversion,
#                 'revenue': delivered['total'].sum(),
#                 'avg_order': delivered['total'].mean() if len(delivered) > 0 else 0
#             }
#
#         return {
#             'A': group_stats(self.group_a),
#             'B': group_stats(self.group_b)
#         }
#
#     def run_statistical_tests(self):
#         """Проверяем, не случайна ли разница между группами"""
#
#         # Создаём таблицу сопряжённости
#         # Сравниваем: в группе А сколько доставленных/недоставленных
#         #            в группе Б сколько доставленных/недоставленных
#         contingency = pd.crosstab(
#             self.df['ab_group'],
#             self.df['status'] == 'delivered'
#         )
#
#         print("\n📊 Таблица сопряжённости:")
#         print(contingency)
#
#         # Хи-квадрат тест: проверяет, есть ли связь между группой и успехом
#         chi2, p_value, dof, expected = chi2_contingency(contingency)
#
#         # Рассчитываем конверсию для каждой группы
#         metrics = self.calculate_metrics()
#         conv_a = metrics['A']['conversion']
#         conv_b = metrics['B']['conversion']
#
#         # Рассчитываем Lift (улучшение в процентах)
#         lift = ((conv_b - conv_a) / conv_a * 100) if conv_a > 0 else 0
#
#         results = {
#             'chi2': chi2,
#             'p_value': p_value,
#             'dof': dof,
#             'conv_a': conv_a,
#             'conv_b': conv_b,
#             'lift': lift,
#             'is_significant': p_value < 0.05  # True если результат значим
#         }
#
#         return results
#
#     def print_report(self):
#         """Выводим понятный отчёт"""
#
#         metrics = self.calculate_metrics()
#         stats = self.run_statistical_tests()
#
#         print("\n" + "=" * 70)
#         print("📊 РЕЗУЛЬТАТЫ A/B ТЕСТА: СКИДКА 10% НА ТОП-5 ТОВАРОВ")
#         print("=" * 70)
#
#         # Выводим метрики по группам
#         print("\n📈 ГРУППА A (КОНТРОЛЬ) — обычные цены:")
#         print(f"   Заказов: {metrics['A']['total_orders']}")
#         print(f"   Доставлено: {metrics['A']['delivered']}")
#         print(f"   В ожидании: {metrics['A']['pending']}")
#         print(f"   Отменено: {metrics['A']['cancelled']}")
#         print(f"   Конверсия: {metrics['A']['conversion']:.2f}%")
#         print(f"   Выручка: {metrics['A']['revenue']:,.0f} ₽")
#
#         print("\n💰 ГРУППА B (ТЕСТ) — скидка 10% на топ-5 товаров:")
#         print(f"   Заказов: {metrics['B']['total_orders']}")
#         print(f"   Доставлено: {metrics['B']['delivered']}")
#         print(f"   В ожидании: {metrics['B']['pending']}")
#         print(f"   Отменено: {metrics['B']['cancelled']}")
#         print(f"   Конверсия: {metrics['B']['conversion']:.2f}%")
#         print(f"   Выручка: {metrics['B']['revenue']:,.0f} ₽")
#
#         # Статистическая значимость
#         print("\n" + "-" * 50)
#         print("🎯 СТАТИСТИЧЕСКАЯ ЗНАЧИМОСТЬ:")
#         print(f"   p-value: {stats['p_value']:.6f}")
#
#         if stats['is_significant']:
#             print(f"   ✅ РЕЗУЛЬТАТ СТАТИСТИЧЕСКИ ЗНАЧИМ (p < 0.05)")
#             print(f"   Разница между группами НЕ случайна")
#         else:
#             print(f"   ❌ РЕЗУЛЬТАТ НЕ ЗНАЧИМ (p >= 0.05)")
#             print(f"   Разница может быть случайной")
#
#         # Lift и рекомендация
#         print(f"\n📈 LIFT (улучшение конверсии): {stats['lift']:.2f}%")
#
#         print("\n" + "-" * 50)
#         print("💡 РЕКОМЕНДАЦИЯ:")
#
#         if stats['is_significant'] and stats['lift'] > 5:
#             print(f"   ✅ Скидка СРАБОТАЛА! Конверсия выросла на {stats['lift']:.1f}%")
#             print(f"   → ВНЕДРЯЕМ скидку 10% для всех клиентов на топ-5 товаров")
#         elif stats['is_significant'] and stats['lift'] > 0:
#             print(f"   ⚠️ Скидка дала небольшой эффект ({stats['lift']:.1f}%)")
#             print(f"   → Рекомендуется увеличить скидку до 15% и повторить тест")
#         elif stats['is_significant'] and stats['lift'] <= 0:
#             print(f"   ❌ Скидка НЕ СРАБОТАЛА (эффект {stats['lift']:.1f}%)")
#             print(f"   → Не внедряем, ищем другие способы")
#         else:
#             print(f"   ⚠️ НЕДОСТАТОЧНО ДАННЫХ для уверенного вывода")
#             print(f"   → Увеличьте размер выборки (нужно больше заказов в тесте)")
#
#         return stats
#
#
# # 4. ЗАПУСК ВСЕГО A/B ТЕСТА
# # Запускаем генерацию тестовых данных
# test_orders, group_a, group_b, top_5 = generate_ab_test_data(
#     df_products=df_products,
#     df_orders=df_orders,
#     df_users=df_users,
#     discount=0.10,
#     n_new_orders=1000
# )
#
# # Создаём объект A/B теста
# ab_test = ABTest(test_orders)
#
# # Выводим отчёт
# results = ab_test.print_report()

print(df.head())



