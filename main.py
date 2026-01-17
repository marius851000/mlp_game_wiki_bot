import os
import time
from typing import Any

import mwparserfromhell
import pywikibot
from mwparserfromhell.nodes import Template

from data_parse import DataExtractor


# used to not re-process already processed page, even when interrupted (please note that it is best effort, and pretty bad actually. But it should work)
class AppendOnlyPersistence:
    def __init__(self, path):
        self.present = set()
        if os.path.isfile(path):
            with open(path, "r") as f:
                for line in f.readlines():
                    self.present.add(line.strip())
        self.out = open(path, "a")

    def is_present(self, key):
        return key in self.present

    def add(self, key):
        if key not in self.present:
            self.present.add(key)
            self.out.write(key + "\n")


def recouncile(
    page_name: str, template: Template, expected_value: dict[str, Any], order: list[str]
):
    has_modified = False
    message = ""
    for key in expected_value:
        if "delete" in expected_value[key] and expected_value[key]["delete"]:
            if template.has(key) and template.get(key).value.strip() != "":
                template.remove(key)
                print("Removed " + key + " in " + page_name)
                message += "removed " + key + "\n"
                has_modified = True
        else:
            value = expected_value[key]["value"]
            if not template.has(key):
                before_which_element = None
                take_next = False
                for order_element_key in order:
                    if order_element_key == key:
                        take_next = True
                    if take_next and template.has(order_element_key):
                        before_which_element = order_element_key
                        break
                _ = template.add(key, value, before=before_which_element)
                this_message = (
                    "Modified " + key + " in " + page_name + " to " + str(value)
                )
                print(this_message)
                message += "set " + key + " to " + str(value) + "\n"
                has_modified = True
            else:
                pass
                # TODO:
                # print("TODO: recouncile existing values")
    return (has_modified, message)


IDEAL_CHARACTER_ORDER = [
    "id",
    "name2",
    "image",
    "album",
    "albumdescription",
    "store",
    "storewidth",
    "description",
    "town",
    "cost",
    "gems",
    "playable",
    "level",
    "bonus",
    "residence",
    "update",
    "reward 1",
    "reward 2",
    "reward 3",
    "reward 4",
    "reward 5",
    "milestone",
    "community",
    "boss",
]


class GameDataBot:
    def __init__(self, data_path):
        self.site = pywikibot.Site()
        self.extractor = DataExtractor(data_path)
        self.processed = AppendOnlyPersistence("./processed.txt")
        self.present_pony_id = AppendOnlyPersistence("./present_pony_id.txt")

    def process_page(self, page_name):
        page = pywikibot.Page(self.site, page_name)
        wikicode = mwparserfromhell.parse(page.text)
        was_modified = False
        message = "Update pony infobox data: "
        for template in wikicode.filter_templates():
            if template.name.contains("Infobox character") or template.name.contains(
                "Infobox_character"
            ):
                pony_id = None
                if not template.has("id"):
                    pony_id = self.extractor.get_pony_id_from_name(page_name)
                    if pony_id is None:
                        if page_name in [
                            "Nightmare Parabola",
                            "Nightmare Tree Hugger",
                            "Nightmare Big Mac",
                        ]:
                            continue
                        raise BaseException(
                            "A template in "
                            + page_name
                            + " does not have a character id and can’t auto-find it"
                        )
                        continue
                else:
                    pony_id = template.get("id").value.strip()
                self.present_pony_id.add(pony_id)
                if pony_id in ["Pony_Cinematic_Mane-iac"]:
                    continue
                pony_data = self.extractor.get_pony_data(pony_id)
                expected_values = {
                    "id": {
                        "value": pony_id,
                    },
                    "description": {
                        "value": pony_data["description"],
                    },
                    "bonus": {"value": pony_data["on_arrive_xp"]},
                }
                if not pony_data["no_star_reward"]:
                    mapping_rewards = {
                        "wheel_starmastery": "wheel",
                        "Token_Lottery": "lucky coin",
                        "Lucky Coin": "lucky coin",
                        "Gems": "gem",
                        "PopCurrency1": "pin",
                        "PopCurrency2": "button",
                        "PopCurrency3": "twine",
                        "PopCurrency4": "ribbon",
                        "PopCurrency5": "bow",
                    }
                    for i in range(5):
                        reward_data = pony_data["rewards"][i]
                        print(reward_data, page_name)
                        if not reward_data["id"].startswith(
                            "ProfileAvatar_"
                        ) and not reward_data["id"].startswith("PlayerCardCutieMark_"):
                            if reward_data["amount"] == 1:
                                expected_values["reward " + str(i + 1)] = {
                                    "value": mapping_rewards[reward_data["id"]]
                                }
                else:
                    for i in range(5):
                        expected_values["reward " + str(i + 1)] = {"delete": True}
                print(expected_values)
                (was_just_modified, modification_message) = recouncile(
                    page_name, template, expected_values, IDEAL_CHARACTER_ORDER
                )

                if was_just_modified:
                    was_modified = True
                    message += "\n" + modification_message.strip()

        if was_modified:
            page.text = str(wikicode)
            page.save(message)

    def get_page_name_in_category(self, category_name):
        category = pywikibot.Category(self.site, "Characters")
        result = set()
        for page in list(category.articles()):
            result.add(page.title())
        return result

    def process_pages(self, pages):
        for page_title in pages:
            if not self.processed.is_present(page_title):
                self.process_page(page_title)
                self.processed.add(page_title)
                time.sleep(1)


if __name__ == "__main__":
    bot = GameDataBot("/home/marius/Sync/programming_project/luna-kit/base_built/")
    # bot.process_page("Bow Tie")
    print(bot.process_pages(bot.get_page_name_in_category("Characters")))
