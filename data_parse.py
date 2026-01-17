import json
import os
import xml.etree.ElementTree as ET


class Translation:
    def __init__(self, path):
        with open(path) as f:
            self.data = json.load(f)

    def get_translation(self, key):
        return self.data.get(key) or key

    def reverse_lookup(self, translation):
        for key in self.data:
            if self.data[key] == translation:
                return key
        return None


class ObjectData:
    def __init__(self, path):
        self.tree = ET.parse(path)

    def get_category_xml(self, category):
        for tree_child in self.tree.getroot():
            if tree_child.tag == "Category" and tree_child.attrib["ID"] == category:
                return tree_child
        raise BaseException("Category " + category + " not found in object data")

    def get_object_xml(self, category, key):
        cat_xml = self.get_category_xml(category)
        for cat_child in cat_xml:
            if cat_child.tag == "GameObject" and cat_child.attrib["ID"] == key:
                return cat_child
        raise BaseException(
            "Object " + key + " not found in category " + category + " in object data"
        )


class DataExtractor:
    def __init__(self, extracted_folder):
        self.extracted_folder = extracted_folder
        self.english_translation = Translation(
            os.path.join(self.extracted_folder, "english.json")
        )
        self.object_data = ObjectData(
            os.path.join(self.extracted_folder, "gameobjectdata.xml")
        )

    def extract_single_pony(self, pony_object_data_xml):
        result = {
            "name": self.english_translation.get_translation(
                pony_object_data_xml.find("Name").attrib["Unlocal"]
            ),
            "description": self.english_translation.get_translation(
                pony_object_data_xml.find("Description").attrib["Unlocal"]
            ),
            "on_arrive_xp": int(pony_object_data_xml.find("OnArrive").attrib["EarnXP"]),
        }
        star_rewards = pony_object_data_xml.find("StarRewards")
        ai = pony_object_data_xml.find("AI")
        is_already_max_level = ai.attrib["Max_Level"] == "1"
        result["start_max_level"] = is_already_max_level
        if star_rewards != None and not is_already_max_level:
            star_rewards_id = star_rewards.find("ID")
            star_rewards_amount = star_rewards.find("Amount")
            result["rewards"] = []
            for i in range(5):
                id = star_rewards_id.findall("Item")[i].attrib["Value"]
                amount = int(star_rewards_amount.findall("Item")[i].attrib["Value"])
                result["rewards"].append({"id": id, "amount": amount})
            result["no_star_reward"] = False
        else:
            result["no_star_reward"] = True

        return result

    def get_pony_data(self, pony_id):
        return self.extract_single_pony(
            self.object_data.get_object_xml("Pony", pony_id)
        )

    def get_pony_id_from_name(self, name):
        for pony_element in self.object_data.get_category_xml("Pony"):
            pony_data = self.extract_single_pony(pony_element)
            if pony_data["name"] == name:
                return pony_element.attrib["ID"]
        return None

    def generate_pony_json(self, output_path):
        to_write = {}
        for pony_element in self.object_data.get_category_xml("Pony"):
            to_write[pony_element.attrib["ID"]] = self.extract_single_pony(pony_element)
        with open(output_path, "w") as f:
            json.dump(to_write, f, indent=2)


if __name__ == "__main__":
    EXTRACTED_FOLDER = "base_built/"
    OUTPUT_FOLDER = "./wikiout"

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    extractor = DataExtractor(EXTRACTED_FOLDER)
    print(
        extractor.extract_single_pony(
            extractor.object_data.get_object_xml("Pony", "Pony_Twilight_Sparkle")
        )
    )
    extractor.generate_pony_json(os.path.join(OUTPUT_FOLDER, "pony.json"))
