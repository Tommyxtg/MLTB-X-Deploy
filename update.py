from pymongo import MongoClient
from pkg_resources import working_set
from os import getenv, path as ospath
from dotenv import load_dotenv, dotenv_values
from subprocess import run as srun, call as scall
from logging import getLogger, basicConfig, INFO, FileHandler, StreamHandler

if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

basicConfig(format="[%(asctime)s] [%(levelname)s] - %(message)s",
            datefmt="%d-%b-%y %I:%M:%S %p",
            handlers=[FileHandler('log.txt'), StreamHandler()],
            level=INFO)

LOGGER = getLogger(__name__)

load_dotenv("config.env", override=True)

BOT_TOKEN = getenv("BOT_TOKEN", "")
if len(BOT_TOKEN) == 0:
    LOGGER.error("BOT_TOKEN is not set in config.env")
    exit(1)

bot_id = BOT_TOKEN.split(":")[0]

DATABASE_URL = getenv("DATABASE_URL", "")
if len(DATABASE_URL) == 0:
    DATABASE_URL = None
    LOGGER.warning("DATABASE_URL is not set in config.env, using local files for configuration and data storage")

if DATABASE_URL is not None:
    coon = MongoClient(DATABASE_URL)
    db = coon.mltb
    old_config = db.settings.deployConfig.find_one({"_id": bot_id})
    config_dict = db.settings.config.find_one({"_id": bot_id})
    if old_config is not None:
        del old_config["_id"]
    if (old_config is not None and old_config == dict(dotenv_values("config.env"))) or old_config is None:
        getenv("UPSTREAM_REPO") = config_dict.get("UPSTREAM_REPO")
        getenv("UPSTREAM_BRANCH") = config_dict.get("UPSTREAM_BRANCH")
        getenv("UPGRADE_PACKAGES") = config_dict.get("UPGRADE_PACKAGES")
    conn.close()

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "")
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = None
    LOGGER.warning("UPSTREAM_REPO is not set in config.env")

UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "")
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = "master"
    LOGGER.warning("UPSTREAM_BRANCH is not set in config.env")


UPGRADE_PACKAGES = getenv("UPGRADE_PACKAGES", "False")
if UPGRADE_PACKAGES == "true":
    packages = [dist.project_name for dist in working_set]
    scall("pip install " + ' '.join(packages), shell=True)

if UPSTREAM_REPO is not None:
    if ospath.exists('.git'):
        srun(["rm", "-rf", ".git"])

    update = srun([f"git init -q \
                     && git config --global user.email doc.adhikari@gmail.com \
                     && git config --global user.name weebzone \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)

    repo = UPSTREAM_REPO.split("/")
    UPSTREAM_REPO = f"https://github.com/{repo[-2]}/{repo[-1]}"
    if update.returncode == 0:
        LOGGER.info("Successfully updated with latest commits !!")
    else:
        LOGGER.error("Something went Wrong ! Retry or Ask Support !")
    LOGGER.info(f"UPSTREAM_REPO : {UPSTREAM_REPO} | UPSTREAM_BRANCH : {UPSTREAM_BRANCH}")
