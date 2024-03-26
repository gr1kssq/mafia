import sqlite3
import random


def insert_player(player_id: int, username: str) -> None:
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    sql = "INSERT INTO players (player_id, username) VALUES (?, ?)"
    cur.execute(sql, (player_id, username))
    conn.commit()
    conn.close()

def players_amount() -> int:
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    sql = "SELECT * FROM players"
    cur.execute(sql)
    res = cur.fetchall()
    conn.commit()
    conn.close()
    return len(res)

def get_mafia_usernames() -> str:
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    sql = f"SELECT username FROM players where role = 'mafia' "
    cur.execute(sql)
    data = cur.fetchall()
    names = ''
    for row in data:
        name = row[0]
        names += name + '\n'
    conn.close()
    return names

def get_players_roles() -> list:
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    sql = f"SELECT player_id, role FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    conn.close()
    return data

def get_all_alive() -> list:
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    sql = f"SELECT username FROM players WHERE dead = 0"
    cur.execute(sql)
    data = cur.fetchall()
    data = [row[0] for row in data]
    conn.close()
    return data

def set_roles(players: int) -> None:
    game_roles = ['citizen'] * players
    mafias = int(players * 0.3)
    for i in range(mafias):
        game_roles[i] = "mafia"
    random.shuffle(game_roles)

    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    cur.execute("SELECT player_id FROM players")
    player_ids = cur.fetchall()

    for role, player_id in zip(game_roles, player_ids):
        cur.execute("UPDATE players SET role=? WHERE player_id =?", (role, player_id[0]))
    conn.commit()
    conn.close()


def vote(type, username, player_id):
    # type = 'mafia_vote, citizen_vote'
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(
        f"SELECT username FROM players WHERE player_id = {player_id} and dead = 0 and voted = 0")
    can_vote = cur.fetchone()
    if can_vote:  # если список не пустой, значит пользователь существует
        cur.execute(
            f"UPDATE players SET {type} = {type} + 1 WHERE username = '{username}' ")
        cur.execute(
            f"UPDATE players SET voted = 1 WHERE player_id = '{player_id}' ")
        con.commit()
        con.close()
        return True
    con.close()
    return False

def mafia_kill() -> str:
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    cur.execute("SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE dead=0 AND role='mafia' ")
    mafia_alive = cur.fetchone()[0]
    username_killed = "Никого"
    if max_votes == mafia_alive:
        cur.execute("SELECT username FROM players WHERE mafia_vote=?", (max_votes,))
        username_killed = cur.fetchone()[0]
        cur.execute("UPDATE players SET dead=1 WHERE username=?", (username_killed,))
        conn.commit()
    conn.close()
    return username_killed

def citizen_kill() -> str:
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    cur.execute("SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE dead=0 AND citizen_vote=?", (max_votes,))
    votes_count = cur.fetchone()[0]
    username_killed = "Никого"
    if votes_count == 1:
        cur.execute("SELECT username FROM players WHERE citizen_vote=?", (max_votes,))
        username_killed = cur.fetchone()[0]
        cur.execute("UPDATE players SET dead=1 WHERE username=?", (username_killed,))
        conn.commit()
    conn.close()
    return username_killed

def check_winner():
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM players WHERE role='mafia' and dead=0")
    mafia_alive = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE role != 'mafia' and dead=0")
    citizen_alive = cur.fetchone()[0]
    if mafia_alive >= citizen_alive:
        return "Мафия"
    if mafia_alive == 0:
        return "Горожане"

def clear(dead: bool=False):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"UPDATE players SET citizen_vote = 0, mafia_vote = 0, voted = 0"
    if dead:
        sql += ', dead = 0'
    cur.execute(sql)
    con.commit()
    con.close()


def get_users():
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM players")
    data = cur.fetchall()
    conn.commit()
    conn.close()
    return data