import json
import re
import sqlite3
import sys

import pandas as pd

from flattracker.config import DB_PATH


def map_bedroom(text: str) -> str:
    mappa = {
        "non-master bedroom": "Non-master Bedroom",
        "master": "Master Bedroom",
        "master bedroom": "Master Bedroom",
        "hall": "Hall",
        "single": "Single",
        "single room": "Single",
        "double": "Double",
    }
    return mappa.get(text.lower(), text)


def process_gender(text: str) -> list[str]:
    if isinstance(text, list):
        return text
    # convert to title case
    text = text.title()
    if "/" in text:
        return text.split("/")
    else:
        return [text]


def map_restrictions(text: str | list) -> list[str]:
    if not isinstance(text, list):
        text = text.split(",")
    text = list(map(str.strip, text))
    mappa = {
        "no smoking": "NO_SMOKING",
        "non smoker": "NO_SMOKING",
        "no drinking": "NO_DRINKING",
        "no alcohol": "NO_DRINKING",
        "non drinker": "NO_DRINKING",
        "no restrictions": "NONE",
        "no restriction": "NONE",
        "no_restrictions": "NONE",
        "no boys": "NO_BOYS",
        "no boys allowed": "NO_BOYS",
        "only vegetarians": "NO_NONVEG",
        "no non-vegetarian food": "NO_NONVEG",
        "no non-vegetarian": "NO_NONVEG",
        "pure veg": "NO_NONVEG",
    }
    out = [mappa.get(x.lower(), x) for x in text]
    if "NONE" in out:
        out = ["NONE"]

    return sorted(out)


def map_furnished(text: str) -> str:
    text = text.replace("-", " ").replace(" ", "")
    mappa = {
        "semifurnished": "SEMI_FURNISHED",
        "fullyfurnished": "FURNISHED",
        "furnished": "FURNISHED",
        "unfurnished": "UNFURNISHED",
        "fullfurnished": "FURNISHED",
    }

    return mappa.get(text.lower(), text)


def process_available_date(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\bapr\b", "april", text)
    text = re.sub(r"(?<=\d)(th|st|rd|nd)", "", text)
    text = text.replace("2025", "").replace(",", "").replace("after", "")
    text = text.title().strip()

    if "Now" in text or "Immediate" in text:
        text = "Immediate"

    if len(text.split(" ")) == 2:
        text = " ".join(sorted(text.split(" ")))
    return text


def process_address(text: str) -> str:
    text = text.title()
    text = text.replace("  ", " ")
    return text


def process_contact_details(text: str) -> str:
    if "ping" in text.lower():
        text = "DM"
    return text


def cleanse(df: pd.DataFrame) -> pd.DataFrame:
    df["Bedroom"] = df["Bedroom"].apply(map_bedroom)
    df["Gender"] = df["Gender"].apply(process_gender)
    df["Address"] = df["Address"].apply(process_address)
    df["Rent"] = df["Rent"].apply(lambda x: 0 if not x else x)
    df["Rent"] = df["Rent"]["astyp"](int)
    df["Deposit"] = df["Deposit"].apply(lambda x: 0 if not x else x)
    df["Deposit"] = df["Deposit"]["astyp"](int)
    df["Restrictions"] = df["Restrictions"].apply(map_restrictions)
    df["Furnished"] = df["Furnished"].apply(map_furnished)
    df["Brokerage"] = df["Brokerage"].apply(lambda x: 0 if not x else x)
    df["Brokerage"] = df["Brokerage"]["astyp"](int)
    df["AvailableDate"] = df["AvailableDate"].apply(process_available_date)
    df["ContactDetail"] = df["ContactDetail"].apply(process_contact_details)
    return df


def count_empty(obj: dict) -> int:
    res = [1 for x in obj.values() if not x]
    return sum(res)


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    master_df = pd.read_sql_query("SELECT * FROM message_data;", conn)
    conn.close()

    dicts = master_df["structured_data"].apply(lambda x: json.loads(x)).to_list()
    df = pd.DataFrame(dicts)
    df = df.fillna("")
    df = cleanse(df)
    cleaned_dicts = df.to_dict(orient="records")
    master_df["structured_data"] = [json.dumps(x) for x in cleaned_dicts]

    # remove rows which have "car rental", "lead" and "external" in their `raw_text` column
    mask = (
        master_df["raw_text"]
        .str.lower()
        .str.contains("lead|car rental|external", regex=True)
    )
    filter_df = master_df[~(mask)]

    # save to database only if "-s" flag is passed
    if len(sys.argv) > 1 and sys.argv[1] == "-s":
        import shutil

        print("SAVING")
        shutil.copy("telegram_data.db", "telegram_data_backup_2.db")
        conn = sqlite3.connect("telegram_data.db")
        conn.execute("DELETE FROM message_data;")
        filter_df.to_sql("message_data", conn, if_exists="append", index=False)
        conn.close()
