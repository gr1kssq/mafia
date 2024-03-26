from telebot import TeleBot
import db
from time import sleep
from random import choice

players = []
TOKEN = '6633582746:AAF1rTnqX8UQpiwwiCa_xVRPWHRCwwl34tM'
bot = TeleBot(TOKEN)
game = False
night = False

def autoplay_citizen(message):
    players_roles = db.get_players_roles()
    for player_id, _ in players_roles:
        usernames = db.get_all_alive()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames:
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote('citizen_vote', vote_username, player_id)
            bot.send_message(
                message.chat.id, f'{name} проголосовал против {vote_username}')
            sleep(0.5)

def autoplay_mafia():
    players_roles = db.get_players_roles()
    for player_id, role in players_roles:
        usernames = db.get_all_alive()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames and role == 'mafia':
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote('mafia_vote', vote_username, player_id)

def game_loop(message):
    global night, game
    bot.send_message(message.chat.id, 'Вэлкам ту зе гейм, ю иметь 2 минута чтобы привет привет')
    sleep(5)
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id, msg)
        if not night:
            bot.send_message(message.chat.id, 'Город спит, мафия вейк ап ту реалити, наступает ночь')
        else:
            bot.send_message(message.chat.id, 'Город просыпается, наступает день')
        winner = db.check_winner()
        if winner:
            game = False
            bot.send_message(message.chat.id, f"Игра окончена, победители: {winner}")
            return

        db.clear(dead=False)
        night = not night
        alive = db.get_all_alive
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, f'В игре:\n{alive}')
        sleep(10)
        autoplay_mafia() if night else autoplay_citizen(message)

def get_killed(night: bool) -> str:
    if not night:
        username_killed = db.citizen_kill()
        return f"Горожане выгнали: {username_killed}"
    username_killed = db.mafia_kill()
    return f"Мафия убила: {username_killed}"

@bot.message_handler(func=lambda m: m.text.lower() == 'готов играть' and m.chat.type == 'private')
def send_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} играет')
    bot.send_message(message.from_user.id, 'Вы добавлены в игру')
    db.insert_player(message.from_user.id,
                     username=message.from_user.first_name)

@bot.message_handler(commands=['play'])
def game_start(message):
    global game
    if not game:
        bot.send_message(message.chat.id, 'Если хотите играть напишите "готов играть" в лс')

@bot.message_handler(commands=["game"])
def game_on(message):
    global game
    players = db.players_amount()
    if players >= 5 and not game:
        db.set_roles(players)
        player_roles = db.get_players_roles()
        mafia_usernames = db.get_mafia_usernames()
        for player_id, role in player_roles:
            bot.send_message(player_id, role)
            if role == "mafia":
                bot.send_message(player_id, f"Все члены мафии:\n{mafia_usernames}")
        db.clear(dead=True)
        game = True
        bot.send_message(message.chat.id, "Игра началась!")
        game_loop(message)
        return
    bot.send_message(message.chat.id, "недостаточно людей!")
    for i in range(5 - players):
        bot_name = f"robot{i}"
        db.insert_player(i, bot_name)
        bot.send_message(message.chat.id, f"{bot_name} добавлен!")
        sleep(0.2)
    game_start(message)

@bot.message_handler(commands=['kick'])
def kick(message):
    username = " ".join(message.text.split(" ")[1:])
    usernames = db.get_all_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого пользователя нет')
            return
        voted = db.vote('citizen_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учтен')
            return
        bot.send_message(message.chat.id, 'У вас больше нет права голосовать')
        return
    bot.send_message(message.chat.id, 'Чичас ночь, вы не можете никого выгнать')

@bot.message_handler(commands=['kill'])
def kill(message):
    username = " ".join(message.text.split(" ")[1:])
    usernames = db.get_mafia_usernames()
    mafia_usernames = db.get_mafia_usernames()
    if night and message.from_user.firstname in mafia_usernames:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого пользователя нет')
            return
        voted = db.vote('mafia_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учтен')
            return
        bot.send_message(message.chat.id, 'У вас больше нет права голосовать')
        return
    bot.send_message(message.chat.id, 'Cейчас нельзя убивать')


bot.infinity_polling(none_stop=True)