from ._config import DB

auth = DB.get_collection("auth")

AUTH = []


def is_auth(user_id):
    return user_id in AUTH


def auth_user(user_id):
    if user_id not in AUTH:
        AUTH.append(user_id)
        auth.insert_one({"id": user_id})
        return True
    else:
        return False


def unauth_user(user_id):
    try:
        AUTH.remove(user_id)
        auth.delete_one({"id": user_id}, comment="unauth")
        return True
    except ValueError:
        return False


def get_auth_users():
    return [user["id"] for user in auth.find({})]


def __load_auth():
    AUTH.clear()
    AUTH.extend(get_auth_users())


__load_auth()

# Quotly Database

quotly = DB.get_collection("quotly")


def set_qrate(chat_id, mode: bool):
    quotly.update_one({"chat_id": chat_id}, {
                      "$set": {"qrate": mode}}, upsert=True)


def get_qrate(chat_id):
    q = quotly.find_one({"chat_id": chat_id})
    if q:
        return q.get('qrate') or False
    return False

def add_quote(chat_id, quote):
    quotly.update_one({"chat_id": chat_id}, {
                      "$push": {"quotes": quote}}, upsert=True)

def get_quotes(chat_id):
    q = quotly.find_one({"chat_id": chat_id})
    if q:
        return q["quotes"]
    return False                      
