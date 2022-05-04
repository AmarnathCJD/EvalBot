from config import env, AUTH


def init_db():
    if env.get("MONGO_URI"):
        from pymongo import MongoClient
        client = MongoClient(env["MONGO_URI"])
        db = client["bot"]
        return db
    else:
        return None


DB = init_db()


def auth_user(user_id):
    if DB != None:
        DB.users.update_one({"user_id": user_id}, {
            "$set": {"auth": True}}, upsert=True)
    if user_id not in AUTH:
        AUTH.append(user_id)


def unauth_user(user_id):
    if DB != None:
        DB.users.delete_one({"user_id": user_id})
    if user_id in AUTH:
        AUTH.remove(user_id)


def is_auth(user_id):
    if user_id in AUTH or user_id == int(env["OWNER_ID"]):
        return True
    return False


def get_auth_users():
    if DB != None:
        return [user["user_id"] for user in DB.users.find({})]
    else:
        return AUTH


def __load_auth():
    AUTH.clear()
    AUTH.extend(get_auth_users())


__load_auth()
