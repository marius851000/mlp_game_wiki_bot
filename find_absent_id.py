import os

import mwparserfromhell
import pywikibot

from data_parse import DataExtractor

ponies_with_pages = set()
with open("present_pony_id.txt", "r") as f:
    for line in f.readlines():
        this_pony = line.strip()
        ponies_with_pages.add(this_pony)

extractor = DataExtractor("/home/marius/Sync/programming_project/luna-kit/base_built/")
ponies_without_pages = set()
for pony_element in extractor.object_data.get_category_xml("Pony"):
    this_pony = pony_element.attrib["ID"]
    if (
        this_pony
        in [
            "Pony_Blonn_Di",  # multi-person character
            "Pony_Adagio_Dazzle",  # transform
            "Pony_Danu_Ch",  # transform
            "Pony_Maniac_Renew",  # cinematic pony
            "Pony_Token_Test",
            "Pony_Crystal_Luna_Hair_Test",
            "Pony_Windigo",  # obviously not a complete pony
            "Pony_Shadowbolts_f",  # multi-person character
            "Pony_Shadowbolts_s",  # idem
            "Pony_Tirek",  # obviously not a complete pony
            "Pony_Tirek_TOTB",  # idem
            "Pony_Grogartized_Discord",  # transform
            "Pony_KP",  # transform
            "Pony_Derpy",  # obviously not a complete pony
            "Pony_Las_Pegasus_Showponies_Green",  # obviously not a complete pony
            "Pony_Las_Pegasus_Showponies_Blue",  # idem
            "Pony_Sonata_Dusk",  # transform
            "Pony_Aria_Blaze",  # idem
            "Pony_Disguised_Spike",  # obviously not a complete pony
            "Pony_King_Sombra_CE",  # clone of Pony_King_Sombra
            "Pony_Chest",  # Uhm... not a complete... pony?
            "Pony_Celebration_Pinkie_Pie",  # transform
            "Pony_Fondant_Frenzy_Marine_Sandwich",  # transform
            "Pony_Drained_Lord_Tirek",  # transform
            "Pony_Mystery_Pony",  # obviously not a complete pony
            "Pony_Bad_Apple_Hidden",  # variant of bad apple?
        ]
        or this_pony.startswith("Pony_Apple_Infantry_")  # multi-person characters
        or this_pony.endswith("_Changelling_Light")  # transforms
        or this_pony.lower().startswith("pony_supercharged_")  # transforms
        or this_pony.startswith("Pony_Super_Charged_")  # transforms
        or this_pony.startswith("Pony_Quest_")
        or this_pony.startswith("Pony_Crit_")
        or this_pony.endswith("_Seapony")  # transforms
        or this_pony.startswith("Pony_Kirin_")  # tranforms
        or this_pony.startswith("Pony_Nirik_")  # transforms
        or this_pony.startswith("Pony_Minotaurocellus_")
        or this_pony.startswith("Pony_Sea_")  # transforms
    ):
        continue
    if this_pony not in ponies_with_pages:
        print(str(this_pony) + " not present")
        ponies_without_pages.add(this_pony)

print(ponies_without_pages)
