from pony.orm.core import db_session
from pony import orm
from pony.orm import Database,Required,Set,select,commit
import ui_global
import json
import os
import sqlite3
from sqlite3.dbapi2 import Error
from datetime import datetime
from PIL import Image


nom_id=-1
seen_birds_ids = set()
birds_ids = -1


def init_on_start(hashMap,_files=None,_data=None):
    ui_global.init()
    return hashMap


def menu_input(hashMap,_files=None,_data=None):
    if hashMap.get("listener")=="menu":
        if hashMap.get("menu")=="Список птиц":
            hashMap.put("ShowScreen","Список птиц")
        if hashMap.get("menu1")=="Птицы которых я видел":
            hashMap.put("ShowScreen","Добавить птиц которых я видел")

    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("FinishProcess","")
    return hashMap


def menu_on_start(hashMap,_files=None,_data=None):
    return hashMap


def birds_on_start(hashMap, _files=None, _data=None):
    hashMap.put("mm_local", "")
    hashMap.put("mm_compression", "70")
    hashMap.put("mm_size", "65")

    list = {"customcards": {

        "layout": {
            "type": "LinearLayout",
            "orientation": "vertical",
            "height": "match_parent",
            "width": "match_parent",
            "weight": "0",
            "Elements": [
                {
                    "type": "LinearLayout",
                    "orientation": "horizontal",
                    "height": "wrap_content",
                    "width": "match_parent",
                    "weight": "0",
                    "Elements": [
                        {
                            "type": "Picture",
                            "show_by_condition": "",
                            "Value": "@pic",
                            "NoRefresh": False,
                            "document_type": "",
                            "mask": "",
                            "Variable": "",
                            "TextSize": "16",
                            "TextColor": "#DB7093",
                            "TextBold": True,
                            "TextItalic": False,
                            "BackgroundColor": "",
                            "width": "100",
                            "height": "100",
                            "weight": 0
                        },
                        {
                            "type": "LinearLayout",
                            "orientation": "vertical",
                            "height": "wrap_content",
                            "width": "match_parent",
                            "weight": "1",
                            "Elements": [
                                {
                                    "type": "TextView",
                                    "show_by_condition": "",
                                    "Value": "@name",
                                    "NoRefresh": False,
                                    "document_type": "",
                                    "TextBold": True,
                                    "TextSize": "24",
                                    "mask": "",
                                    "Variable": ""
                                },
                                {
                                    "type": "TextView",
                                    "show_by_condition": "",
                                    "Value": "@color",
                                    "NoRefresh": False,
                                    "document_type": "",
                                    "mask": "",
                                    "Variable": ""
                                },
                            ]
                        }
                    ]
                }
            ]
        }
    }
    }

    query = select(c for c in ui_global.SW_Birds)
    list["customcards"]["cardsdata"] = []

    for record in query:
        pic = ""
        if 'photo' in record.pictures:
            p = record.pictures['photo']
            if len(p) > 0:
                for jf in _files:  # находим путь к файлу по идентификатору
                    if jf['id'] == p[0]:
                        if os.path.exists(jf['path']):
                            pic = "~" + jf['path']
                        break

        list["customcards"]["cardsdata"].append(
            {"name": record.name, "key": record.id, "color": str(record.color),
             "pictures": json.dumps(record.pictures), "pic": pic})

    hashMap.put("list", json.dumps(list))

    return hashMap


def open_nom(hashMap, nom_id, key):
    jlist = json.loads(hashMap.get("list"))
    goodsarray = jlist["customcards"]['cardsdata']

    jrecord = next(item for item in goodsarray if str(item["key"]) == key)

    nom_id = jrecord['key']
    hashMap.put("name", jrecord['name'])
    hashMap.put("color", jrecord['color'])
    hashMap.put("nom_id", str(nom_id))

    jg = json.loads(jrecord['pictures'])
    if 'photo' in jg:
        hashMap.put("photoGallery", json.dumps(jg['photo']))
    else:
        hashMap.put("photoGallery", json.dumps([]))

    hashMap.put("ShowScreen", "Карточка птицы")

    return hashMap, nom_id


def birds_input(hashMap, _files=None, _data=None):
    global nom_id

    if hashMap.get("listener") == "btn_add":
        hashMap.put("name", "")
        hashMap.put("color", "")
        hashMap.put("photoGallery", json.dumps([]))  # пустой список под галерею

        hashMap.put("ShowScreen", "СозданиеНовойПтицы")

    elif hashMap.get("listener") == "CardsClick":
        hashMap, nom_id = open_nom(hashMap, nom_id, hashMap.get("selected_card_key"))
        # hashMap.put("toast", str(nom_id))

    elif hashMap.get("listener") == "vision":
        # hashMap.put("toast",hashMap.get("nom_id"))
        nom = ui_global.SW_Birds.get(id=int(hashMap.get("nom_id")))
        if nom == None:
            hashMap.put("toast", "Товар не найден")
        else:
            hashMap, nom_id = open_nom(hashMap, nom_id, str(nom.id))
            hashMap.put("speak", nom.name)
    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("FinishProcess","")

    return hashMap


def birds_record_on_start(hashMap, _files=None, _data=None):
    hashMap.put("mm_local", "")
    hashMap.put("mm_compression", "70")
    hashMap.put("mm_size", "65")

    hashMap.put("fill_name", json.dumps({"hint": "Название птицы", "default_text": hashMap.get("name")}))
    hashMap.put("fill_color", json.dumps({"hint": "Цвет", "default_text": hashMap.get("color")}))

    return hashMap


def get_if_exist(hashMap, field):
    if hashMap.containsKey(field):
        res = hashMap.get(field)
    else:
        res = ""
    return res


def getint_if_exist(hashMap, field):
    if not hashMap.containsKey(field):
        res = 0  # Значение по умолчанию, если поле отсутствует
    else:
        try:
            value = hashMap.get(field)
            if value is not None:
                res = int(value)
            else:
                res = 0
        except ValueError:
            res = 0  # Обработка ошибки, если значение не является целым числом
    return res


def getboolean_if_exist(hashMap, field):
    if not hashMap.containsKey(field):
        res = 0
    else:
        if hashMap.get(field) == "true":
            res = 1
        else:
            res = 0

    return res


def getfloat_if_exist(hashMap, field):
    if not hashMap.containsKey(field):
        res = 0
    else:
        try:
            res = float(hashMap.get(field))

        except:
            return 0
    return res


def save_nom(hashMap):
    global nom_id
    if not hashMap.containsKey("name"):
        hashMap.put("toast", "Не указано название птицы")
        return hashMap, False
    else:
        if len(hashMap.get("name")) == 0:
            hashMap.put("toast", "Не указано название птицы")
            return hashMap, False

    if nom_id < 0:

        with db_session:
            r = ui_global.SW_Birds(name=get_if_exist(hashMap, "name"),
                                   color=get_if_exist(hashMap, "color"),
                                   number_of_sightings=getint_if_exist(hashMap, "number_of_sightings"),
                                   )
            nom_id = r.id
            commit()


    else:
        with db_session:

            r = ui_global.SW_Birds[nom_id]
            r.name = get_if_exist(hashMap, "name")
            r.color = get_if_exist(hashMap, "color")
            r.number_of_sightings = getint_if_exist(hashMap, "number_of_sightings")
            j = {}
            j['photo'] = json.loads(hashMap.get("photoGallery"))
            r.pictures = j

            commit()
    return hashMap, True


def birds_record_input(hashMap, _files=None, _data=None):
    global nom_id

    if hashMap.get("listener") == "btn_save":
        hashMap, success = save_nom(hashMap)
        if success:
            hashMap.put("ShowScreen", "Список птиц")

    elif hashMap.get("listener") == "CardsClick":
        hashMap.put("toast", str(hashMap.get("selected_card_key")))

    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("ShowScreen", "Список птиц")

    elif hashMap.get("listener") == 'menu_del':
        with db_session:
            r = ui_global.SW_Birds[nom_id]
            r.delete()
        hashMap.put("ShowScreen", "Список птиц")
        hashMap.put("toast", "Удалено...")

    elif hashMap.get("listener") == "photo":

        # Можно вообще этого не делать-оставлять как есть. Это для примера.
        image_file = str(
            hashMap.get("photo_path"))  # "переменная"+"_path" - сюда помещается путь к полученной фотографии

        image = Image.open(image_file)
        im = image.resize((500, 500))
        im.save(image_file)

        jphotoarr = json.loads(hashMap.get("photoGallery"))
        hashMap.put("photoGallery", json.dumps(jphotoarr))

    elif hashMap.get(
            "listener") == "gallery_change":
        if hashMap.containsKey("photoGallery"):
            jphotoarr = json.loads(hashMap.get("photoGallery"))
            hashMap.put("photoGallery", json.dumps(jphotoarr))

    return hashMap


def card_bird_on_start(hashMap, _files=None, _data=None):
    hashMap.put("mm_local", "")
    hashMap.put("mm_compression", "70")
    hashMap.put("mm_size", "65")

    hashMap.put("fill_name", hashMap.get("name"))
    hashMap.put("fill_color", hashMap.get("color"))
    hashMap.put("fill_id", hashMap.get("created_at"))

    return hashMap


def card_bird_on_input(hashMap, _files=None, _data=None):
    global seen_birds_ids
    global nom_id

    nom_id = int(hashMap.get("nom_id"))

    if hashMap.get("listener") == "seen":
        if nom_id >= 0:
            with db_session:
                r = ui_global.SW_Birds[nom_id]
                r.number_of_sightings += 1
                commit()
                hashMap.put("number_of_sightings", str(r.number_of_sightings))
                global seen_birds_ids
                seen_birds_ids.add(nom_id)
                hashMap.put("toast", str(seen_birds_ids))

        else:
            hashMap.put("toast", "Выберите птицу для увеличения числа наблюдений")

    elif hashMap.get("listener") == "btn_edit":
        if nom_id >= 0:
            bird = ui_global.SW_Birds.get(id=nom_id)
            hashMap.put("name", bird.name)
            hashMap.put("color", bird.color)
            hashMap.put("number_of_sightings", str(bird.number_of_sightings))
            # hashMap.put("photoGallery", json.dumps(bird.pictures['photo']))  # Assuming 'photo' key exists in 'pictures'

            hashMap.put("ShowScreen", "СозданиеНовойПтицы")

    elif hashMap.get("listener") == 'menu_del':
        with db_session:
            r = ui_global.SW_Birds[nom_id]
            r.delete()
        hashMap.put("ShowScreen", "Список птиц")
        hashMap.put("toast", "Удалено...")

    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("ShowScreen", "Список птиц")

    return hashMap


def add_seen_birds_on_start(hashMap, _files=None, _data=None):
    global nom_id
    global seen_birds_ids

    hashMap.put("mm_local", "")
    hashMap.put("mm_compression", "70")
    hashMap.put("mm_size", "65")

    list = {"customcards": {

        "layout": {
            "type": "LinearLayout",
            "orientation": "vertical",
            "height": "match_parent",
            "width": "match_parent",
            "weight": "0",
            "Elements": [
                {
                    "type": "LinearLayout",
                    "orientation": "horizontal",
                    "height": "wrap_content",
                    "width": "match_parent",
                    "weight": "0",
                    "Elements": [
                        {
                            "type": "Picture",
                            "show_by_condition": "",
                            "Value": "@pic",
                            "NoRefresh": False,
                            "document_type": "",
                            "mask": "",
                            "Variable": "",
                            "TextSize": "16",
                            "TextColor": "#DB7093",
                            "TextBold": True,
                            "TextItalic": False,
                            "BackgroundColor": "",
                            "width": "100",
                            "height": "100",
                            "weight": 0
                        },
                        {
                            "type": "LinearLayout",
                            "orientation": "vertical",
                            "height": "wrap_content",
                            "width": "match_parent",
                            "weight": "1",
                            "Elements": [
                                {
                                    "type": "TextView",
                                    "show_by_condition": "",
                                    "Value": "@name",
                                    "NoRefresh": False,
                                    "document_type": "",
                                    "TextBold": True,
                                    "TextSize": "24",
                                    "mask": "",
                                    "Variable": ""
                                },
                                {
                                    "type": "TextView",
                                    "show_by_condition": "",
                                    "Value": "@color",
                                    "NoRefresh": False,
                                    "document_type": "",
                                    "mask": "",
                                    "Variable": ""
                                },
                                {
                                    "type": "TextView",
                                    "show_by_condition": "",
                                    "Value": "@created_at",
                                    "NoRefresh": False,
                                    "document_type": "",
                                    "mask": "",
                                    "Variable": ""
                                },
                                {
                                    "type": "TextView",
                                    "show_by_condition": "",
                                    "Value": "@number_of_sightings",
                                    "NoRefresh": False,
                                    "document_type": "",
                                    "mask": "",
                                    "Variable": ""
                                },

                            ]
                        }
                    ]
                }
            ]
        }

    }
    }
    query_seen_birds = select(c for c in ui_global.SW_SeenBirds)
    list["customcards"]["cardsdata"] = []
    for record in query_seen_birds:
        pic = ""
        if 'photo' in record.pictures:
            p = record.pictures['photo']
            if len(p) > 0:
                for jf in _files:  # находим путь к файлу по идентификатору
                    if jf['id'] == p[0]:
                        if os.path.exists(jf['path']):
                            pic = "~" + jf['path']
                        break

        list["customcards"]["cardsdata"].append(
            {"name": record.name, "key": record.id, "color": str(record.color),
             "number_of_sightings": record.number_of_sightings, "created_at": str(record.created_at),
             "pictures": json.dumps(record.pictures), "pic": pic})
    hashMap.put("list", json.dumps(list))

    return hashMap


def seen_birds_input(hashMap, _files=None, _data=None):
    global nom_id

    hashMap.put("name", "")
    hashMap.put("color", "")
    hashMap.put("number_of_sightings", "")
    hashMap.put("photoGallery", json.dumps([]))  # пустой список под галерею
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hashMap.put("created_at", created_at)
    if hashMap.get("listener") == "btn_add_seen":

        query = select(c for c in ui_global.SW_Birds if c.id in seen_birds_ids)

        for record in query:
            with db_session:
                r = ui_global.SW_SeenBirds.get(id=record.id)
                if r:
                    r.set(
                        name=record.name,
                        color=record.color,
                        number_of_sightings=record.number_of_sightings,
                        pictures=record.pictures,
                        created_at=created_at,
                    )
                else:
                    r = ui_global.SW_SeenBirds(
                        id=record.id,
                        name=record.name,
                        color=record.color,
                        number_of_sightings=record.number_of_sightings,
                        pictures=record.pictures,
                        created_at=created_at,
                    )
                commit()

    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("FinishProcess","")

    elif hashMap.get("listener") == 'CardsClick':
        hashMap, nom_id = open_nom(hashMap, nom_id, hashMap.get("selected_card_key"))
        with db_session:
            r = ui_global.SW_SeenBirds[nom_id]
            r.delete()
        hashMap.put("toast", "Удалено...")

    return hashMap

