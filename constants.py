from environs import Env

env = Env()
env.read_env()

TOKEN = env.str(name="TOKEN")

DIDOX_URL = "https://gnk-api.didox.uz/api/v1/utils/info/"
