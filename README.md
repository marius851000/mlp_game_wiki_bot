## MLP-game-wiki bot
A bot for the [My Little Pony mobile game Wiki](https://mlp-game-wiki.no) that can do some stuff, such as import data from the game into the character infobox (the only thing it can do for now).

I can resume if it failed to do some processing. It uses an very simple append-only set. See ``AppendOnlyPersistence`` in ``main.py`` for more details.

I uses the pywikibot framework, as well as mwparserfromhell.

You need to edit and rename ``user-config.template.py`` and ``user-password.template.py``, then run ``pwb login`` before being able run ``main.py``.

You might need to edit the path to the data folder, as extracted by luna-kit.

### Things it can do:
- edit character’s template to match data in regard to (note: it will not overwrite differing data):
  - id
  - description
  - arrival bonus
  - level up reward (it will delete them if missing from the file definition)
- List missing character pages (first, do a full run of ``main.py`` (it will edit the page, but also generate the ``present_pony_id.py`` file) and then run ``find_absent_id.py``)
(and that’s all)
