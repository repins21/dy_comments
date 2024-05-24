
from sqlitedb import insert_data, select_data


def insert(table_name: str, data: dict):
    values = ''

    for k, v in data.items():
        if not values:
            if isinstance(v, int):
                values = f"{v}"
            else:
                values = f"'{v}'"
        else:
            if isinstance(v, int):
                values += f",{v}"
            else:
                values += f",'{v}'"

    sql = f"""
        INSERT INTO {table_name}({','.join(list(data.keys()))})
        VALUES ({values})
    """
    insert_data(sql)


def get_max_search_id():
    sql = f"""
        SELECT MAX(`id`) FROM search_history;
    """
    ret = select_data(sql)

    max_id = ret[0][0]
    if max_id is None:
        max_search_id = '001'
    else:  # id加1
        add_one = str(int(max_id) + 1)
        max_search_id = '0' * (3 - len(add_one)) + add_one

    return max_search_id


if __name__ == '__main__':
    get_max_search_id()
