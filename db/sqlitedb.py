import sqlite3
from loguru import logger


def create_conn():
    conn = sqlite3.connect('sqlite3.db')
    return conn


def create_data():
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')  # 开启外键（默认是禁用的）

    try:
        cursor.execute(
            """
            create table if not exists search_history(
                `id` varchar(3),
                `search` TEXT,
                `video_id` varchar(19),
                `datetime` varchar(19),
                primary key (`id`,video_id)
            )
            """
        )

        cursor.execute(
            """
            create table if not exists video_info(
                `video_id` varchar(19),
                `search_id` varchar(3),
                `title` TEXT,
                `author_name` varchar(32),
                `video_publish_time` varchar(19),
                `duration` int,
                `collect_count` int,
                `comment_count` int,
                `digg_count` int,
                `share_count` int,
                primary key (`video_id`,search_id),
                FOREIGN KEY (search_id) REFERENCES search_history(id) ON DELETE CASCADE -- 外键+使用级联删除
            )
            """
        )
        cursor.execute(
            """
            create table if not exists users(
                `uid` varchar(16),
                `video_id` varchar(19),
                `user_name` varchar(32),          
                `homepage_link` varchar(128),
                `has_letter` int,  -- 是否私信过
                primary key (`uid`, video_id),
                FOREIGN KEY (video_id) REFERENCES video_info(video_id) ON DELETE CASCADE 
            )
            """
        )
        cursor.execute(
            """
            create table if not exists comments(
                `uid` varchar(16),
                `ip_address` varchar(32),
                `comment_time` varchar(19),
                `comment_text` TEXT,
                primary key (`uid`, comment_time),
                FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
            )  
            """
        )
        conn.commit()
    except Exception as e:
        logger.error(f"create table Exception: {repr(e)}")
    finally:
        cursor.close()
        conn.close()


def insert_data(sql):
    conn = create_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('PRAGMA foreign_keys=ON;')
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        logger.error(f"insert Exception: {repr(e)}, sql: {sql}")
    finally:
        cursor.close()
        conn.close()


def select_data(sql):
    conn = create_conn()
    cursor = conn.cursor()
    try:
        result = cursor.execute(sql)
        return result.fetchall()
    except Exception as e:
        logger.error(f"select Exception: {repr(e)}, sql: {sql}")
    finally:
        cursor.close()
        conn.close()


def update_date(sql):
    conn = create_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('PRAGMA foreign_keys=ON;')
        cursor.execute(sql)
        conn.commit()
        logger.info("update success")
    except Exception as e:
        logger.error(f"update Exception: {repr(e)}, sql: {sql}")
    finally:
        cursor.close()
        conn.close()


def truncate_table(table_name):
    """清空表"""
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name};")
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = '{table_name}';")
    cursor.close()
    conn.close()


if __name__ == '__main__':
    print(sqlite3.sqlite_version)
    create_data()

    """
    
    级联删除的时候会有问题，在删除某个搜索历史的数据时，会把其他的搜索历史下的数据给删了1111111111111111111111111111111111111111
    例如：同一个用户在不同视频下的评论，会都删了
    """

    # sql = """
    #     INSERT INTO qimai_data(`index`,`name`)
    #     VALUES (?,?)
    # """
    # insert_data(sql, item)
    # result = select_data('select * from qimai_data')
    # print(result)

