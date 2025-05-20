import pymysql
from datetime import datetime


def connect_to_db():
    """Подключение к базе данных"""
    try:
        conn = pymysql.connect(
            host="fatima6p.beget.tech",
            user="fatima6p_orange",
            password="password",
            database="fatima6p_orange",
            charset='utf8mb4',
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor  # Для возврата результатов в виде словаря
        )
        print("Подключение к БД установлено!")
        return conn
    except pymysql.Error as err:
        print(f"Ошибка подключения к БД: {err}")
        return None


def get_orders_customer(customer_id=None):
    """Получение списка заказов и фильтрация по заказчику"""
    conn = connect_to_db()
    if not conn:
        return []

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT 
                    o.id AS order_id,
                    o.create_date AS order_date,
                    o.number_of_products AS total_products,
                    os.name AS status_name,
                    CONCAT(c.surname, ' ', c.name, ' ', c.patronymic) AS customer_name,
                    c.company_name AS company,
                    o.id_manager,
                    o.price_with_profit,
                    CONCAT(m.surname, ' ', m.name, ' ', m.patronymic) AS manager_name
                FROM orders o
                JOIN customer c ON o.id_customer = c.id
                JOIN order_status os ON o.status_id = os.id
                LEFT JOIN worker m ON o.id_manager = m.id  -- Добавляем менеджера
                WHERE 1=1
                """

            params = []
            if customer_id is not None:
                query += " AND o.id_customer = %s"
                params.append(customer_id)

            query += " ORDER BY o.create_date DESC"

            cursor.execute(query, params or None)
            orders = cursor.fetchall()

            # Форматирование даты
            for order in orders:
                if isinstance(order['order_date'], str):
                    try:
                        dt = datetime.strptime(order['order_date'], "%Y-%m-%d %H:%M:%S")
                        order['order_date'] = dt.strftime("%d.%m.%Y в %H:%M")
                    except Exception as e:
                        print(f"Ошибка форматирования даты: {e}")
                        order['order_date'] = "Некорректная дата"
                elif isinstance(order['order_date'], datetime):
                    order['order_date'] = order['order_date'].strftime("%d.%m.%Y в %H:%M")
                else:
                    order['order_date'] = "Дата не указана"

            return orders

    except pymysql.Error as err:
        print(f"Ошибка выполнения запроса: {err}")
        return []
    finally:
        if conn:
            conn.close()


def get_orders_without_manager(customer_filter=None):
    """Получение списка заказов без назначенного менеджера"""
    conn = connect_to_db()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT 
                o.id AS order_id,
                o.create_date AS order_date,
                o.number_of_products AS total_products,
                o.real_price,
                o.price_with_profit,
                os.name AS status_name,
                os.id AS status_id,  # Добавляем статус ID
                CONCAT(c.surname, ' ', c.name, ' ', c.patronymic) AS customer_name,
                c.company_name AS company,
                c.phone AS customer_phone
            FROM orders o
            JOIN customer c ON o.id_customer = c.id
            JOIN order_status os ON o.status_id = os.id
            WHERE o.id_manager IS NULL  -- Основное условие: заказы без менеджера
            AND os.id != 2  # Исключаем заказы со статусом id = 2
            """
            params = []

            # Фильтр по заказчику
            if customer_filter:
                query += " AND CONCAT(c.surname, ' ', c.name, ' ', c.patronymic) LIKE %s"
                params.append(f"%{customer_filter}%")

            query += " ORDER BY o.create_date DESC"
            cursor.execute(query, params)
            orders = cursor.fetchall()

            # Форматирование даты
            for order in orders:
                if isinstance(order['order_date'], str):
                    try:
                        dt = datetime.strptime(order['order_date'], "%Y-%m-%d %H:%M:%S")
                        order['order_date'] = dt.strftime("%d.%m.%Y в %H:%M")
                    except Exception as e:
                        print(f"Ошибка форматирования даты: {e}")
                        order['order_date'] = "Некорректная дата"
                elif isinstance(order['order_date'], datetime):
                    order['order_date'] = order['order_date'].strftime("%d.%m.%Y в %H:%M")
                else:
                    order['order_date'] = "Дата не указана"

            print(f"Найдено заказов без менеджера: {len(orders)}")
            return orders

    except pymysql.Error as err:
        print(f"Ошибка выполнения запроса: {err}")
        return []
    finally:
        if conn:
            conn.close()


def assign_manager_to_order(order_id, manager_id):
    """Назначение менеджера на заказ"""
    conn = connect_to_db()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE orders 
                SET id_manager = %s 
                WHERE id = %s AND id_manager IS NULL
            """, (manager_id, order_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Ошибка назначения менеджера: {e}")
        return False
    finally:
        if conn: conn.close()


def get_orders(manager_id=None):
    """Получение списка заказов с информацией о заказчике и статусе"""
    conn = connect_to_db()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT 
                o.id AS order_id,
                o.create_date AS order_date,
                o.number_of_products AS total_products,
                o.real_price,
                o.price_with_profit,
                os.id AS status_id,  # Добавляем status_id
                os.name AS status_name,
                CONCAT(c.surname, ' ', c.name, ' ', c.patronymic) AS customer_name,
                c.company_name AS company,
                c.phone AS customer_phone,
                c.email AS customer_email,
                tc.name_type_customer AS customer_type
            FROM orders o
            JOIN customer c ON o.id_customer = c.id
            JOIN order_status os ON o.status_id = os.id
            LEFT JOIN type_customer tc ON c.id_type_customer = tc.id
            WHERE 1=1
            """
            params = []

            if manager_id is not None:
                query += " AND o.id_manager = %s"
                params.append(manager_id)

            query += " ORDER BY o.create_date DESC"

            cursor.execute(query, params or None)
            orders = cursor.fetchall()

            # Форматирование даты
            for order in orders:
                if isinstance(order['order_date'], str):
                    try:
                        # Преобразуем строку в datetime объект
                        dt = datetime.strptime(order['order_date'], "%Y-%m-%d %H:%M:%S")
                        # Форматируем в нужный вид
                        order['order_date'] = dt.strftime("%d.%m.%Y в %H:%M")
                    except Exception as e:
                        print(f"Ошибка форматирования даты: {e}")
                        order['order_date'] = "Некорректная дата"
                elif isinstance(order['order_date'], datetime):  # Если дата пришла как datetime объект
                    order['order_date'] = order['order_date'].strftime("%d.%m.%Y в %H:%M")
                else:
                    order['order_date'] = "Дата не указана"

            return orders

    except pymysql.Error as err:
        print(f"Ошибка выполнения запроса (get_orders): {err}")
        return []
    finally:
        if conn:
            conn.close()


def update_order_status(order_id, new_status_id):
    """Обновление статуса заказа в бд"""
    conn = connect_to_db()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            query = "UPDATE orders SET status_id = %s WHERE id = %s"
            cursor.execute(query, (new_status_id, order_id))
            conn.commit()
            return cursor.rowcount > 0
    except pymysql.Error as err:
        print(f"Ошибка обновления статуса: {err}")
        return False
    finally:
        if conn:
            conn.close()


def get_orders_status(manager_id=None, status_filter=None):
    """Получение списка заказов с фильтрацией по менеджеру и статусу"""
    conn = connect_to_db()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT 
                o.id AS order_id,
                o.create_date AS order_date,
                o.number_of_products AS total_products,
                o.real_price,
                o.price_with_profit,
                os.name AS status_name,
                os.id AS status_id,
                CONCAT(c.surname, ' ', c.name, ' ', c.patronymic) AS customer_name,
                c.company_name AS company,
                c.phone AS customer_phone,
                c.email AS customer_email
            FROM orders o
            JOIN customer c ON o.id_customer = c.id
            JOIN order_status os ON o.status_id = os.id
            WHERE 1=1
            """
            params = []

            # Фильтр по менеджеру
            if manager_id:
                query += " AND o.id_manager = %s"
                params.append(manager_id)

            # Фильтр по статусу
            if status_filter:
                query += " AND os.name LIKE %s"
                params.append(f"%{status_filter}%")

            query += " ORDER BY o.create_date DESC"
            cursor.execute(query, params)
            orders = cursor.fetchall()

            # Форматирование даты
            for order in orders:
                if isinstance(order['order_date'], str):
                    try:
                        dt = datetime.strptime(order['order_date'], "%Y-%m-%d %H:%M:%S")
                        order['order_date'] = dt.strftime("%d.%m.%Y в %H:%M")
                    except Exception as e:
                        print(f"Ошибка форматирования даты: {e}")
                        order['order_date'] = "Некорректная дата"
                elif isinstance(order['order_date'], datetime):
                    order['order_date'] = order['order_date'].strftime("%d.%m.%Y в %H:%M")
                else:
                    order['order_date'] = "Дата не указана"

            print(f"Найдено заказов: {len(orders)}")
            return orders

    except pymysql.Error as err:
        print(f"Ошибка выполнения запроса (get_orders_status): {err}")
        return []
    finally:
        if conn:
            conn.close()


def get_order_products(order_id):
    """Получает продукты заказа"""
    conn = connect_to_db()
    if not conn: return []

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT p.id, pt.name as product_type, 
                   p.length, p.width, p.quantity
            FROM product p
            JOIN product_type pt ON p.product_type_id = pt.id
            WHERE p.id_order = %s
            """
            cursor.execute(query, (order_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка получения продуктов: {e}")
        return []
    finally:
        conn.close()


def get_product_materials(product_id):
    """Получает материалы для продукта"""
    conn = connect_to_db()
    if not conn: return []

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT m.name as material_name, 
                   mc.name as category_name,
                   pm.wigth, pm.lenght
            FROM product_material pm
            JOIN material m ON pm.id_material = m.id
            JOIN material_category mc ON m.id_category = mc.id
            WHERE pm.id_product = %s
            """
            cursor.execute(query, (product_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка получения материалов: {e}")
        return []
    finally:
        conn.close()
