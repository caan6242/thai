import csv
import html
import io
import json
import sqlite3
from datetime import date, datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components


DB_PATH = "thai_study.db"
DEFAULT_MODEL = "gpt-5.2"
TRANSCRIBE_MODEL = "gpt-4o-mini-transcribe"

SAMPLE_WORDS = [
    ("สวัสดี", "sawatdee", "hello / goodbye", "greetings", "Polite everyday greeting."),
    ("ขอบคุณ", "khop khun", "thank you", "manners", "Add ค่ะ/ครับ for politeness."),
    ("ใช่", "chai", "yes / correct", "basics", "Affirming something is correct."),
    ("ไม่ใช่", "mai chai", "no / not correct", "basics", "Denying a statement."),
    ("น้ำ", "nam", "water", "food", "Also appears in many compound words."),
    ("กาแฟ", "gaa-fae", "coffee", "food", "Useful for cafe practice."),
    ("เท่าไหร่", "tao rai", "how much", "shopping", "Question word for price or amount."),
    ("ห้องน้ำ", "hong nam", "bathroom", "travel", "Literally water room."),
    ("อร่อย", "a-roi", "delicious", "food", "Good praise after eating."),
    ("ช้าๆ", "chaa chaa", "slowly", "conversation", "Useful phrase: พูดช้าๆได้ไหม"),
]

LESSONS = [
    {
        "title": "Greetings and Politeness",
        "goal": "Greet people and add the polite ending that makes beginner Thai sound warm.",
        "teach": "Thai often uses a polite particle at the end of short phrases. Many female speakers use ค่ะ, many male speakers use ครับ. You can use สวัสดี for hello and goodbye.",
        "pattern": "Phrase + ค่ะ/ครับ",
        "vocab": [
            ("สวัสดี", "sawatdee", "hello / goodbye"),
            ("ขอบคุณ", "khop khun", "thank you"),
            ("ค่ะ", "kha", "polite particle"),
            ("ครับ", "khrap", "polite particle"),
        ],
        "examples": [
            ("สวัสดีค่ะ", "sawatdee kha", "Hello."),
            ("ขอบคุณครับ", "khop khun khrap", "Thank you."),
            ("สวัสดี คุณสบายดีไหม", "sawatdee, khun sabai dee mai", "Hello, how are you?"),
        ],
        "drills": ["Say hello politely twice.", "Thank someone using ค่ะ or ครับ.", "Change the particle and listen again."],
    },
    {
        "title": "Introductions",
        "goal": "Say your name and ask someone else's name.",
        "teach": "The word ชื่อ means name or to be called. Thai often drops 'am/is/are', so ฉันชื่อ Anna literally works as 'I named Anna'.",
        "pattern": "ฉัน/ผม + ชื่อ + name",
        "vocab": [("ฉัน", "chan", "I"), ("ผม", "phom", "I"), ("ชื่อ", "chue", "name"), ("อะไร", "arai", "what")],
        "examples": [
            ("ฉันชื่อแอนนา", "chan chue Anna", "My name is Anna."),
            ("คุณชื่ออะไรคะ", "khun chue arai kha", "What is your name?"),
            ("ยินดีที่ได้รู้จัก", "yin dee tee dai ruu jak", "Nice to meet you."),
        ],
        "drills": ["Put your own name into ฉันชื่อ...", "Ask คุณชื่ออะไรคะ.", "Reply with only your name, then a full sentence."],
    },
    {
        "title": "Yes, No, and Not",
        "goal": "Answer simple questions without overthinking grammar.",
        "teach": "ใช่ means yes/correct. ไม่ goes before a verb or adjective to make it negative. ไม่ใช่ is 'not correct' or 'no' when denying a statement.",
        "pattern": "ไม่ + verb/adjective",
        "vocab": [("ใช่", "chai", "yes / correct"), ("ไม่", "mai", "not"), ("ไม่ใช่", "mai chai", "no / not correct"), ("ได้", "dai", "can / okay")],
        "examples": [("ใช่ค่ะ", "chai kha", "Yes."), ("ไม่ใช่ครับ", "mai chai khrap", "No / not correct."), ("ไม่ได้", "mai dai", "Cannot / not okay.")],
        "drills": ["Turn ใช่ into ไม่ใช่.", "Say cannot.", "Answer yes politely."],
    },
    {
        "title": "Numbers 1-10",
        "goal": "Recognize numbers for prices, quantities, and time.",
        "teach": "Thai numbers combine regularly after ten. Start by making 1-10 automatic, then prices become much easier.",
        "pattern": "number + classifier/thing",
        "vocab": [("หนึ่ง", "nueng", "one"), ("สอง", "song", "two"), ("สาม", "saam", "three"), ("สิบ", "sip", "ten")],
        "examples": [("หนึ่ง สอง สาม", "nueng song saam", "One, two, three."), ("ห้าบาท", "haa baat", "Five baht."), ("สิบบาท", "sip baat", "Ten baht.")],
        "drills": ["Count from 1 to 10.", "Say 5 baht.", "Say 10 baht and listen twice."],
    },
    {
        "title": "Telling Time",
        "goal": "Ask what time it is and understand simple hour answers.",
        "teach": "Thai time has several systems. For a beginner, start with the practical daytime pattern: number + โมง. Use กี่โมงแล้ว to ask 'What time is it now?' Use นาที for minutes. Everyday speech also uses ตอนเช้า morning, ตอนบ่าย afternoon, ตอนเย็น evening, and ตอนกลางคืน night to make time clearer.",
        "pattern": "กี่โมงแล้ว / number + โมง + minutes + นาที",
        "vocab": [
            ("เวลา", "welaa", "time"),
            ("กี่โมง", "gee mong", "what time"),
            ("โมง", "mong", "o'clock / hour marker"),
            ("นาที", "naa-thee", "minute"),
            ("ครึ่ง", "khrueng", "half"),
            ("เช้า", "chao", "morning"),
            ("บ่าย", "baai", "afternoon"),
            ("เย็น", "yen", "evening"),
            ("กลางคืน", "glaang kheun", "night"),
        ],
        "examples": [
            ("กี่โมงแล้ว", "gee mong laew", "What time is it?"),
            ("หนึ่งโมง", "nueng mong", "One o'clock."),
            ("สองโมงครึ่ง", "song mong khrueng", "Half past two."),
            ("สามโมงสิบห้านาที", "saam mong sip haa naa-thee", "3:15."),
            ("เจ็ดโมงเช้า", "jet mong chao", "7:00 in the morning."),
            ("บ่ายสองโมง", "baai song mong", "2:00 in the afternoon."),
            ("หกโมงเย็น", "hok mong yen", "6:00 in the evening."),
            ("สามทุ่ม", "saam thum", "9:00 at night."),
        ],
        "detail_sections": [
            ("The simple clock", ["1:00 = หนึ่งโมง", "2:00 = สองโมง", "3:00 = สามโมง", "Add นาที for minutes: สามโมงห้านาที = 3:05."]),
            ("Half past", ["ครึ่ง means half.", "สองโมงครึ่ง = 2:30.", "หกโมงครึ่ง = 6:30."]),
            ("Useful time-of-day words", ["ตอนเช้า = morning", "ตอนบ่าย = afternoon", "ตอนเย็น = evening", "ตอนกลางคืน = night"]),
            ("Night-time shortcut", ["Thai often uses ทุ่ม for evening/night hours.", "หนึ่งทุ่ม = 7 PM, สองทุ่ม = 8 PM, สามทุ่ม = 9 PM."]),
        ],
        "drills": ["Ask what time it is.", "Say 7:00 in the morning.", "Say 2:30.", "Say 6:15.", "Say 9 PM using ทุ่ม."],
    },
    {
        "title": "Days of the Week",
        "goal": "Talk about today, tomorrow, and yesterday.",
        "teach": "วัน means day. Thai weekdays are named with วัน + a day name. You will hear these constantly for class schedules, appointments, and homework. Start by memorizing the full set, then practice today/tomorrow/yesterday sentences.",
        "pattern": "วัน + weekday / วันนี้เป็นวัน...",
        "vocab": [
            ("วัน", "wan", "day"),
            ("วันจันทร์", "wan jan", "Monday"),
            ("วันอังคาร", "wan ang-khaan", "Tuesday"),
            ("วันพุธ", "wan phut", "Wednesday"),
            ("วันพฤหัสบดี", "wan pha-rue-hat-sa-bor-dee", "Thursday"),
            ("วันศุกร์", "wan suk", "Friday"),
            ("วันเสาร์", "wan sao", "Saturday"),
            ("วันอาทิตย์", "wan aa-thit", "Sunday"),
            ("วันนี้", "wan nee", "today"),
            ("พรุ่งนี้", "phrung nee", "tomorrow"),
            ("เมื่อวาน", "muea waan", "yesterday"),
        ],
        "examples": [
            ("วันนี้วันอะไร", "wan nee wan arai", "What day is today?"),
            ("วันนี้เป็นวันจันทร์", "wan nee pen wan jan", "Today is Monday."),
            ("พรุ่งนี้เป็นวันศุกร์", "phrung nee pen wan suk", "Tomorrow is Friday."),
            ("เมื่อวานเป็นวันอาทิตย์", "muea waan pen wan aa-thit", "Yesterday was Sunday."),
            ("ฉันเรียนภาษาไทยวันพุธ", "chan rian phasaa thai wan phut", "I study Thai on Wednesday."),
        ],
        "detail_sections": [
            ("All weekdays", ["วันจันทร์ = Monday", "วันอังคาร = Tuesday", "วันพุธ = Wednesday", "วันพฤหัสบดี = Thursday", "วันศุกร์ = Friday", "วันเสาร์ = Saturday", "วันอาทิตย์ = Sunday"]),
            ("Schedule pattern", ["ฉันเรียน...วันพุธ = I study...on Wednesday.", "ทำงานวันจันทร์ = work on Monday.", "ไม่มีเรียนวันเสาร์ = no class on Saturday."]),
            ("Today/tomorrow/yesterday", ["วันนี้ = today", "พรุ่งนี้ = tomorrow", "เมื่อวาน = yesterday", "Use เป็น when saying 'is/was a day': วันนี้เป็นวันจันทร์."]),
        ],
        "drills": ["Read all seven days out loud.", "Say today is Monday.", "Say you study Thai on Wednesday.", "Say no class on Saturday.", "Ask what day today is."],
    },
    {
        "title": "Colors",
        "goal": "Describe objects with color words.",
        "teach": "สี means color. Many color names start with สี. Thai adjectives usually come after nouns: shirt red, cup blue.",
        "pattern": "noun + สี + color",
        "vocab": [("สี", "see", "color"), ("สีแดง", "see daeng", "red"), ("สีฟ้า", "see faa", "sky blue"), ("สีเขียว", "see khiao", "green")],
        "examples": [("เสื้อสีแดง", "suea see daeng", "Red shirt."), ("แก้วสีฟ้า", "gaew see faa", "Blue cup."), ("บ้านสีเขียว", "baan see khiao", "Green house.")],
        "drills": ["Name three colors near you.", "Describe your shirt.", "Tap each example and repeat."],
    },
    {
        "title": "Household Items",
        "goal": "Name useful things around the home.",
        "teach": "นี่คือ means this is. อยู่ means is located. Use these to make tiny but useful home sentences.",
        "pattern": "นี่คือ + noun / noun + อยู่ + place",
        "vocab": [("บ้าน", "baan", "home / house"), ("โต๊ะ", "to", "table"), ("เก้าอี้", "gao-ee", "chair"), ("เตียง", "tiang", "bed")],
        "examples": [("นี่คือโต๊ะ", "nee khue to", "This is a table."), ("เก้าอี้อยู่ในบ้าน", "gao-ee yuu nai baan", "The chair is in the house."), ("เตียงอยู่ในห้อง", "tiang yuu nai hong", "The bed is in the room.")],
        "drills": ["Point to a table and say โต๊ะ.", "Make a sentence with บ้าน.", "List three things in your room."],
    },
    {
        "title": "Food and Drink",
        "goal": "Order and talk about simple food.",
        "teach": "ขอ is a polite way to ask for something. Thai often uses classifiers, like แก้ว for a glass/cup.",
        "pattern": "ขอ + item + number + classifier",
        "vocab": [("อาหาร", "aa-haan", "food"), ("น้ำ", "nam", "water"), ("กาแฟ", "gaa-fae", "coffee"), ("ข้าว", "khao", "rice / meal")],
        "examples": [("ขอน้ำหนึ่งแก้ว", "khor nam nueng gaew", "One glass of water, please."), ("ฉันชอบกาแฟ", "chan chop gaa-fae", "I like coffee."), ("ข้าวอร่อย", "khao a-roi", "The rice is delicious.")],
        "drills": ["Order water.", "Say you like coffee.", "Tell someone the food is delicious."],
    },
    {
        "title": "Shopping and Prices",
        "goal": "Ask how much things cost.",
        "teach": "ราคา means price. เท่าไหร่ asks how much/how many. Put them together for a survival phrase.",
        "pattern": "ราคา + เท่าไหร่",
        "vocab": [("ราคา", "raa-khaa", "price"), ("เท่าไหร่", "tao rai", "how much"), ("บาท", "baat", "baht"), ("แพง", "phaeng", "expensive")],
        "examples": [("ราคาเท่าไหร่", "raa-khaa tao rai", "How much is it?"), ("ห้าสิบบาท", "haa sip baat", "Fifty baht."), ("แพงไหม", "phaeng mai", "Is it expensive?")],
        "drills": ["Ask the price.", "Say 50 baht.", "Ask if it is expensive."],
    },
    {
        "title": "Directions",
        "goal": "Understand simple movement directions.",
        "teach": "ไป means go. ตรงไป means go straight. เลี้ยว means turn. Direction words usually come after เลี้ยว.",
        "pattern": "ตรงไป / เลี้ยว + ซ้าย/ขวา",
        "vocab": [("ไป", "pai", "go"), ("ตรงไป", "trong pai", "go straight"), ("ซ้าย", "saai", "left"), ("ขวา", "khwaa", "right")],
        "examples": [("ตรงไปค่ะ", "trong pai kha", "Go straight."), ("เลี้ยวซ้าย", "liao saai", "Turn left."), ("ไปทางขวา", "pai thaang khwaa", "Go to the right.")],
        "drills": ["Say go straight.", "Give left and right directions.", "Ask how to go somewhere."],
    },
    {
        "title": "Questions",
        "goal": "Recognize common question words.",
        "teach": "ไหม turns many statements into yes/no questions. Other question words usually sit where the answer would go.",
        "pattern": "statement + ไหม",
        "vocab": [("ไหม", "mai", "question marker"), ("ที่ไหน", "tee nai", "where"), ("เมื่อไหร่", "muea rai", "when"), ("ทำไม", "tham mai", "why")],
        "examples": [("คุณชอบไหม", "khun chop mai", "Do you like it?"), ("ห้องน้ำอยู่ที่ไหน", "hong nam yuu tee nai", "Where is the bathroom?"), ("เรียนเมื่อไหร่", "rian muea rai", "When do you study?")],
        "drills": ["Make a yes/no question.", "Ask where something is.", "Ask when class is."],
    },
]

LESSON_EXPANSIONS = {
    "Greetings and Politeness": {
        "vocab": [
            ("สบายดีไหม", "sabai dee mai", "how are you?"),
            ("ไม่เป็นไร", "mai pen rai", "it's okay / no problem"),
            ("ขอโทษ", "khor thot", "sorry / excuse me"),
            ("ลาก่อน", "laa gon", "goodbye"),
        ],
        "examples": [
            ("คุณสบายดีไหมคะ", "khun sabai dee mai kha", "How are you?"),
            ("ไม่เป็นไรครับ", "mai pen rai khrap", "It's okay."),
            ("ขอโทษค่ะ", "khor thot kha", "Sorry / excuse me."),
        ],
        "detail_sections": [
            ("Polite endings", ["ค่ะ and ครับ do not translate neatly; they soften the sentence.", "Use คะ for many polite questions from female speakers.", "Short answers can still sound polite: ใช่ค่ะ, ไม่ครับ."]),
            ("Greeting vs goodbye", ["สวัสดี can mean hello or goodbye.", "ลาก่อน is goodbye, but it can sound more final than สวัสดี.", "ขอบคุณ + polite particle is the safest thank-you form."]),
            ("Beginner trap", ["Do not translate every English word.", "Thai often says a short phrase plus a polite ending.", "สวัสดีค่ะ is complete by itself."]),
        ],
        "drills": ["Ask how someone is.", "Say excuse me politely.", "Reply no problem.", "Make hello sound polite.", "Make thank you sound polite."],
    },
    "Introductions": {
        "vocab": [
            ("คุณ", "khun", "you"),
            ("มาจาก", "maa jaak", "come from"),
            ("ประเทศ", "prathet", "country"),
            ("ยินดี", "yin dee", "pleased / glad"),
            ("รู้จัก", "ruu jak", "know / meet"),
        ],
        "examples": [
            ("ฉันมาจากสวีเดน", "chan maa jaak sa-wee-den", "I come from Sweden."),
            ("คุณมาจากประเทศอะไร", "khun maa jaak prathet arai", "What country are you from?"),
            ("ยินดีที่ได้รู้จักครับ", "yin dee tee dai ruu jak khrap", "Nice to meet you."),
        ],
        "detail_sections": [
            ("Name pattern", ["ฉันชื่อ... = My name is...", "ผมชื่อ... is another common 'my name is...' pattern.", "Thai does not need a separate word for 'am' here."]),
            ("Asking back", ["คุณชื่ออะไร = What is your name?", "คุณมาจากประเทศอะไร = What country are you from?", "Add คะ/ครับ if you want it polite."]),
            ("Pronoun comfort", ["ฉัน is broadly useful for beginners.", "ผม is common for male speakers.", "คุณ is polite and safe for 'you'."]),
        ],
        "drills": ["Say your name.", "Ask for someone's name.", "Say where you are from.", "Ask what country someone is from.", "Say nice to meet you."],
    },
    "Yes, No, and Not": {
        "vocab": [
            ("ชอบ", "chop", "like"),
            ("เข้าใจ", "khao jai", "understand"),
            ("ไม่เข้าใจ", "mai khao jai", "do not understand"),
            ("มี", "mee", "have / there is"),
            ("ไม่มี", "mai mee", "do not have / there is no"),
        ],
        "examples": [
            ("ฉันไม่เข้าใจ", "chan mai khao jai", "I do not understand."),
            ("ไม่มีค่ะ", "mai mee kha", "There is none / I do not have it."),
            ("คุณชอบไหม", "khun chop mai", "Do you like it?"),
        ],
        "detail_sections": [
            ("Where ไม่ goes", ["Put ไม่ before the word you negate.", "ชอบ = like, ไม่ชอบ = do not like.", "เข้าใจ = understand, ไม่เข้าใจ = do not understand."]),
            ("ใช่ vs ได้", ["ใช่ answers whether something is correct.", "ได้ often means can/okay/allowed.", "ไม่ใช่ means no/not correct; ไม่ได้ means cannot/not okay."]),
            ("Useful classroom phrase", ["ฉันไม่เข้าใจ is one of the most useful beginner sentences.", "พูดช้าๆได้ไหม = Can you speak slowly?", "พูดอีกครั้งได้ไหม = Can you say it again?"]),
        ],
        "drills": ["Say I do not understand.", "Say I do not like coffee.", "Answer yes politely.", "Answer no/not correct.", "Say cannot."],
    },
    "Numbers 1-10": {
        "vocab": [
            ("สี่", "see", "four"),
            ("ห้า", "haa", "five"),
            ("หก", "hok", "six"),
            ("เจ็ด", "jet", "seven"),
            ("แปด", "bpaet", "eight"),
            ("เก้า", "gao", "nine"),
            ("ศูนย์", "suun", "zero"),
        ],
        "examples": [
            ("ศูนย์ หนึ่ง สอง สาม", "suun nueng song saam", "Zero, one, two, three."),
            ("เจ็ดบาท", "jet baat", "Seven baht."),
            ("เก้าสิบบาท", "gao sip baat", "Ninety baht."),
        ],
        "detail_sections": [
            ("Full set", ["ศูนย์ = 0", "หนึ่ง = 1", "สอง = 2", "สาม = 3", "สี่ = 4", "ห้า = 5", "หก = 6", "เจ็ด = 7", "แปด = 8", "เก้า = 9", "สิบ = 10"]),
            ("Prices", ["number + บาท = price in baht.", "ห้าบาท = 5 baht.", "สิบบาท = 10 baht."]),
            ("Building tens", ["สองสิบ is understandable but ยี่สิบ is the normal word for 20.", "สามสิบ = 30, สี่สิบ = 40, ห้าสิบ = 50.", "For now, recognize สิบ as the ten marker."]),
        ],
        "drills": ["Count 0 to 10.", "Say 7 baht.", "Say 90 baht.", "Listen to 1-10 twice.", "Write your phone number using Thai numbers."],
    },
    "Colors": {
        "vocab": [
            ("สีดำ", "see dam", "black"),
            ("สีขาว", "see khaao", "white"),
            ("สีเหลือง", "see lueang", "yellow"),
            ("สีชมพู", "see chom-phuu", "pink"),
            ("สีม่วง", "see muang", "purple"),
            ("สีน้ำเงิน", "see nam ngoen", "dark blue"),
        ],
        "examples": [
            ("รถสีดำ", "rot see dam", "Black car."),
            ("กระเป๋าสีขาว", "gra-pao see khaao", "White bag."),
            ("ดอกไม้สีเหลือง", "dok mai see lueang", "Yellow flower."),
        ],
        "detail_sections": [
            ("Adjective order", ["Thai color words come after the noun.", "เสื้อสีแดง literally means shirt color red.", "Do not put สีแดง before the noun when describing it."]),
            ("สีฟ้า vs สีน้ำเงิน", ["สีฟ้า is sky blue/light blue.", "สีน้ำเงิน is dark blue/navy.", "Both can translate as blue, but they feel different."]),
            ("Useful classroom task", ["Look around your room and label five objects.", "Say noun + color: โต๊ะสีขาว, เก้าอี้สีดำ.", "Repeat with no English in between."]),
        ],
        "drills": ["Describe your shirt.", "Say black, white, yellow.", "Name two blue things.", "Make three noun + color phrases.", "Ask what color something is: สีอะไร."],
    },
    "Household Items": {
        "vocab": [
            ("ห้อง", "hong", "room"),
            ("ห้องนอน", "hong non", "bedroom"),
            ("ห้องครัว", "hong khrua", "kitchen"),
            ("ประตู", "bpra-tuu", "door"),
            ("หน้าต่าง", "naa-taang", "window"),
            ("ตู้เย็น", "tuu yen", "refrigerator"),
        ],
        "examples": [
            ("ประตูอยู่ทางซ้าย", "bpra-tuu yuu thaang saai", "The door is on the left."),
            ("ตู้เย็นอยู่ในห้องครัว", "tuu yen yuu nai hong khrua", "The fridge is in the kitchen."),
            ("นี่คือห้องนอนของฉัน", "nee khue hong non khong chan", "This is my bedroom."),
        ],
        "detail_sections": [
            ("นี่คือ", ["นี่คือ means this is.", "Use it to identify objects: นี่คือโต๊ะ.", "It is a very useful beginner presentation phrase."]),
            ("อยู่", ["อยู่ tells where something is located.", "โต๊ะอยู่ในห้อง = The table is in the room.", "Add left/right: อยู่ทางซ้าย, อยู่ทางขวา."]),
            ("Rooms", ["ห้อง means room.", "ห้องนอน = bedroom, ห้องครัว = kitchen, ห้องน้ำ = bathroom.", "Many room words are compounds."]),
        ],
        "drills": ["Name five things in your room.", "Say where your bed is.", "Use นี่คือ with three objects.", "Use อยู่ with one room.", "Ask where the bathroom is."],
    },
    "Food and Drink": {
        "vocab": [
            ("ชา", "chaa", "tea"),
            ("นม", "nom", "milk"),
            ("ไก่", "gai", "chicken"),
            ("หมู", "muu", "pork"),
            ("ผัก", "phak", "vegetables"),
            ("เผ็ด", "phet", "spicy"),
        ],
        "examples": [
            ("ขอชาเย็นหนึ่งแก้ว", "khor chaa yen nueng gaew", "One iced tea, please."),
            ("ไม่เผ็ดได้ไหม", "mai phet dai mai", "Can it be not spicy?"),
            ("ฉันไม่กินหมู", "chan mai gin muu", "I do not eat pork."),
        ],
        "detail_sections": [
            ("Ordering with ขอ", ["ขอ makes a polite request.", "ขอน้ำ = water please.", "Add amount/classifier: ขอน้ำหนึ่งแก้ว."]),
            ("Classifiers", ["แก้ว is used for a glass/cup.", "จาน can be used for a plate/dish.", "Beginner shortcut: memorize common full phrases first."]),
            ("Preferences", ["ชอบ = like.", "ไม่ชอบ = do not like.", "ไม่กิน... = I do not eat..."]),
        ],
        "drills": ["Order iced tea.", "Say not spicy, please.", "Say I do not eat pork.", "Say I like coffee.", "Ask for one glass of water."],
    },
    "Shopping and Prices": {
        "vocab": [
            ("ถูก", "thuuk", "cheap"),
            ("ลดราคา", "lot raa-khaa", "discount / lower the price"),
            ("ซื้อ", "sue", "buy"),
            ("ขาย", "khaai", "sell"),
            ("อันนี้", "an nee", "this one"),
            ("เงิน", "ngoen", "money"),
        ],
        "examples": [
            ("อันนี้ราคาเท่าไหร่", "an nee raa-khaa tao rai", "How much is this one?"),
            ("ลดราคาได้ไหม", "lot raa-khaa dai mai", "Can you lower the price?"),
            ("ถูกมากค่ะ", "thuuk maak kha", "Very cheap."),
        ],
        "detail_sections": [
            ("Asking about this one", ["อันนี้ means this one.", "อันนี้ราคาเท่าไหร่ is more specific than ราคาเท่าไหร่.", "Use it while pointing at an item."]),
            ("แพง vs ถูก", ["แพง = expensive.", "ถูก = cheap.", "มาก = very, so แพงมาก = very expensive."]),
            ("Bargaining phrase", ["ลดราคาได้ไหม = Can you reduce the price?", "Use politely and gently.", "Add คะ/ครับ to soften it."]),
        ],
        "drills": ["Ask how much this one is.", "Say very expensive.", "Say very cheap.", "Ask for a discount.", "Say I want to buy this one."],
    },
    "Directions": {
        "vocab": [
            ("ทาง", "thaang", "way / direction"),
            ("ข้างหน้า", "khaang naa", "in front / ahead"),
            ("ข้างหลัง", "khaang lang", "behind"),
            ("ใกล้", "glai", "near"),
            ("ไกล", "glai", "far"),
            ("ที่นี่", "tee nee", "here"),
        ],
        "examples": [
            ("ห้องน้ำอยู่ข้างหน้า", "hong nam yuu khaang naa", "The bathroom is ahead."),
            ("ร้านอาหารอยู่ใกล้ไหม", "raan aa-haan yuu glai mai", "Is the restaurant nearby?"),
            ("ไปทางซ้ายแล้วตรงไป", "pai thaang saai laew trong pai", "Go left, then go straight."),
        ],
        "detail_sections": [
            ("Movement words", ["ไป = go.", "ตรงไป = go straight.", "เลี้ยว = turn.", "Use เลี้ยวซ้าย / เลี้ยวขวา."]),
            ("Location words", ["อยู่ tells where something is.", "ใกล้ = near, ไกล = far.", "ที่นี่ = here, ที่นั่น = there."]),
            ("Direction chain", ["Thai directions can chain actions.", "ตรงไปแล้วเลี้ยวซ้าย = go straight then turn left.", "แล้ว means then/already."]),
        ],
        "drills": ["Say turn left.", "Say turn right.", "Ask if it is near.", "Say the bathroom is ahead.", "Give two-step directions."],
    },
    "Questions": {
        "vocab": [
            ("ใคร", "khrai", "who"),
            ("กี่", "gee", "how many"),
            ("อย่างไร", "yaang rai", "how, formal"),
            ("ใช่ไหม", "chai mai", "right? / isn't it?"),
            ("หรือเปล่า", "rue bplao", "or not?"),
        ],
        "examples": [
            ("นี่คือใคร", "nee khue khrai", "Who is this?"),
            ("มีกี่คน", "mee gee khon", "How many people are there?"),
            ("คุณเรียนภาษาไทยใช่ไหม", "khun rian phasaa thai chai mai", "You study Thai, right?"),
        ],
        "detail_sections": [
            ("ไหม questions", ["Put ไหม at the end of a statement.", "คุณชอบกาแฟ = You like coffee.", "คุณชอบกาแฟไหม = Do you like coffee?"]),
            ("Question words stay in place", ["ที่ไหน appears where the place answer would go.", "ห้องน้ำอยู่ที่ไหน = Bathroom is where?", "เมื่อไหร่ appears where the time answer would go."]),
            ("Checking questions", ["ใช่ไหม checks if something is true.", "หรือเปล่า asks 'or not?'", "Both are very common in speech."]),
        ],
        "drills": ["Make a ไหม question.", "Ask where the bathroom is.", "Ask when class is.", "Ask who this is.", "Ask how many people."],
    },
}

for lesson in LESSONS:
    expansion = LESSON_EXPANSIONS.get(lesson["title"], {})
    for key in ("vocab", "examples", "drills"):
        existing = lesson.get(key, [])
        seen = {item[0] if isinstance(item, tuple) else item for item in existing}
        additions = [item for item in expansion.get(key, []) if (item[0] if isinstance(item, tuple) else item) not in seen]
        lesson[key] = existing + additions
    if expansion.get("detail_sections"):
        lesson["detail_sections"] = lesson.get("detail_sections", []) + expansion["detail_sections"]

CONVERSATION_SCENARIOS = {
    "Cafe order": [
        ("สวัสดีค่ะ รับอะไรดีคะ", "sawatdee kha, rap arai dee kha", "Hello, what would you like?"),
        ("เอากาแฟร้อนหรือเย็นคะ", "ao gaa-fae ron rue yen kha", "Would you like hot or iced coffee?"),
        ("ทั้งหมดห้าสิบบาทค่ะ", "thang mot haa sip baat kha", "That is 50 baht total."),
    ],
    "Introductions": [
        ("คุณชื่ออะไรคะ", "khun chue arai kha", "What is your name?"),
        ("คุณมาจากประเทศอะไรคะ", "khun maa jaak prathet arai kha", "What country are you from?"),
        ("ยินดีที่ได้รู้จักค่ะ", "yin dee tee dai ruu jak kha", "Nice to meet you."),
    ],
    "Directions": [
        ("ไปสถานีรถไฟฟ้ายังไงคะ", "pai sathanee rot fai faa yang ngai kha", "How do I get to the train station?"),
        ("ตรงไปแล้วเลี้ยวซ้ายค่ะ", "trong pai laew liao saai kha", "Go straight, then turn left."),
        ("อยู่ใกล้มากค่ะ", "yuu glai maak kha", "It is very nearby."),
    ],
}


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thai TEXT NOT NULL,
                romanization TEXT,
                english TEXT NOT NULL,
                category TEXT,
                notes TEXT,
                ease REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 0,
                repetitions INTEGER DEFAULT 0,
                due_on TEXT DEFAULT CURRENT_DATE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(thai, english)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                grade TEXT NOT NULL,
                reviewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(card_id) REFERENCES cards(id)
            )
            """
        )


def add_card(thai, romanization, english, category="", notes=""):
    with connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO cards (thai, romanization, english, category, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (thai.strip(), romanization.strip(), english.strip(), category.strip(), notes.strip()),
        )


def load_cards(only_due=False):
    query = "SELECT id, thai, romanization, english, category, notes, ease, interval_days, repetitions, due_on FROM cards"
    params = []
    if only_due:
        query += " WHERE due_on <= ?"
        params.append(date.today().isoformat())
    query += " ORDER BY due_on ASC, id DESC"
    with connect() as conn:
        return conn.execute(query, params).fetchall()


def review_card(card, grade):
    card_id, _, _, _, _, _, ease, interval_days, repetitions, _ = card
    if grade == "again":
        repetitions = 0
        interval_days = 1
        ease = max(1.3, ease - 0.25)
    elif grade == "good":
        repetitions += 1
        interval_days = 1 if repetitions == 1 else max(2, round(interval_days * ease))
    else:
        repetitions += 1
        ease += 0.15
        interval_days = 3 if repetitions == 1 else max(4, round(interval_days * ease * 1.35))

    due_on = (date.today() + timedelta(days=interval_days)).isoformat()
    with connect() as conn:
        conn.execute(
            """
            UPDATE cards
            SET ease = ?, interval_days = ?, repetitions = ?, due_on = ?
            WHERE id = ?
            """,
            (ease, interval_days, repetitions, due_on, card_id),
        )
        conn.execute("INSERT INTO reviews (card_id, grade) VALUES (?, ?)", (card_id, grade))


def parse_vocab_upload(file):
    text = file.getvalue().decode("utf-8-sig")
    dialect = csv.excel_tab if "\t" in text.splitlines()[0] else csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect=dialect))
    if rows and rows[0] and rows[0][0].lower() in {"thai", "word", "คำ"}:
        rows = rows[1:]
    for row in rows:
        if len(row) >= 2 and row[0].strip():
            thai = row[0]
            romanization = row[1] if len(row) > 1 else ""
            english = row[2] if len(row) > 2 else row[1]
            category = row[3] if len(row) > 3 else "uploaded"
            notes = row[4] if len(row) > 4 else ""
            add_card(thai, romanization, english, category, notes)


def get_api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return st.session_state.get("api_key", "")


def has_secret_api_key():
    try:
        return "OPENAI_API_KEY" in st.secrets
    except Exception:
        return False


def install_theme():
    st.markdown(
        """
        <style>
        :root {
          --thai-ink: #18211f;
          --thai-muted: #5d6965;
          --thai-line: #dbe4df;
          --thai-accent: #0f8b8d;
          --thai-gold: #d99b2b;
          --thai-rose: #c85563;
          --thai-deep: #102724;
          --thai-panel: #fffdf7;
          --thai-panel-2: #eef7f4;
        }
        .stApp {
          background: #dfeee9;
          color: var(--thai-ink);
        }
        .block-container {
          background: #f7fbf6;
          border-left: 1px solid rgba(16, 39, 36, 0.08);
          border-right: 1px solid rgba(16, 39, 36, 0.08);
          min-height: 100vh;
        }
        [data-testid="stSidebar"] {
          background: var(--thai-deep);
          border-right: 1px solid rgba(255, 255, 255, 0.12);
        }
        [data-testid="stSidebar"] * {
          color: #f3fbf8 !important;
        }
        [data-testid="stSidebar"] input {
          background: #ffffff !important;
          color: #18211f !important;
        }
        h1, h2, h3 {
          color: var(--thai-ink);
        }
        div[data-testid="stTabs"] button[role="tab"] {
          background: #e3f1ed;
          border-radius: 8px 8px 0 0;
          color: var(--thai-deep);
          margin-right: 0.25rem;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
          background: var(--thai-deep);
          color: #ffffff;
        }
        div[data-testid="stMetric"] {
          background: var(--thai-panel);
          border: 1px solid rgba(16, 39, 36, 0.14);
          border-radius: 8px;
          padding: 0.8rem;
          box-shadow: 0 12px 28px rgba(16, 39, 36, 0.08);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
          background: var(--thai-panel) !important;
          border-color: rgba(16, 39, 36, 0.16) !important;
          box-shadow: 0 14px 34px rgba(16, 39, 36, 0.10);
        }
        .thai-lesson-hero {
          padding: 1.1rem 1.25rem;
          border: 1px solid rgba(16, 39, 36, 0.16);
          border-radius: 8px;
          background:
            linear-gradient(135deg, rgba(15, 139, 141, 0.22), transparent 58%),
            linear-gradient(35deg, rgba(217, 155, 43, 0.20), transparent 48%),
            #fffdf7;
          box-shadow: 0 18px 42px rgba(16, 39, 36, 0.12);
          margin-bottom: 1rem;
        }
        .thai-lesson-hero p {
          color: var(--thai-muted);
          font-size: 1.02rem;
          line-height: 1.6;
        }
        .thai-text {
          font-size: 1.55rem;
          font-weight: 800;
          line-height: 1.35;
        }
        .lookup {
          display: inline-block;
          border-bottom: 2px solid rgba(15, 139, 141, 0.75);
          background: #fff0bf;
          border-radius: 5px;
          padding: 0 0.13rem;
          cursor: help;
          position: relative;
        }
        .lookup:hover {
          background: #bfe6df;
        }
        .lookup:hover::after {
          content: attr(data-tip);
          position: absolute;
          z-index: 50;
          left: 0;
          top: 1.9rem;
          min-width: 210px;
          max-width: 320px;
          padding: 0.7rem;
          border: 1px solid rgba(15, 139, 141, 0.3);
          border-radius: 8px;
          background: #102724;
          color: #ffffff;
          font-size: 0.92rem;
          font-weight: 500;
          line-height: 1.4;
          box-shadow: 0 16px 42px rgba(24, 33, 31, 0.18);
        }
        .pattern-card, .detail-card {
          border: 1px solid rgba(16, 39, 36, 0.15);
          border-radius: 8px;
          background: #fffdf7;
          padding: 0.85rem;
          margin: 0.55rem 0;
          box-shadow: 0 10px 24px rgba(16, 39, 36, 0.07);
        }
        .detail-card {
          background: #eef7f4;
        }
        .detail-card strong {
          color: var(--thai-accent);
        }
        .romanization {
          color: var(--thai-rose);
          font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def glossary_words():
    words = {}
    for thai, romanization, english_text, *_ in SAMPLE_WORDS:
        words[thai] = (romanization, english_text)
    try:
        for _, thai, romanization, english_text, *_ in load_cards():
            if thai and english_text:
                words[thai] = (romanization or "", english_text)
    except Exception:
        pass
    for lesson in LESSONS:
        for thai, romanization, english_text in lesson["vocab"]:
            words[thai] = (romanization, english_text)
        for thai, romanization, english_text in lesson["examples"]:
            words.setdefault(thai, (romanization, english_text))
    extra = [
        ("คุณ", "khun", "you"),
        ("สบายดี", "sabai dee", "well / comfortable"),
        ("รับ", "rap", "receive / take"),
        ("อะไร", "arai", "what"),
        ("ดี", "dee", "good"),
        ("คะ", "kha", "polite question particle"),
        ("ร้อน", "ron", "hot"),
        ("เย็น", "yen", "cold / evening"),
        ("หรือ", "rue", "or"),
        ("ทั้งหมด", "thang mot", "total / all"),
        ("ห้าสิบ", "haa sip", "fifty"),
        ("มาจาก", "maa jaak", "come from"),
        ("ประเทศ", "prathet", "country"),
        ("ยินดี", "yin dee", "pleased / glad"),
        ("รู้จัก", "ruu jak", "know / meet"),
        ("สถานี", "sathanee", "station"),
        ("รถไฟฟ้า", "rot fai faa", "skytrain / electric train"),
        ("ยังไง", "yang ngai", "how"),
        ("แล้ว", "laew", "already / then"),
        ("เลี้ยว", "liao", "turn"),
        ("อยู่", "yuu", "is located / stay"),
        ("ใกล้", "glai", "near"),
        ("มาก", "maak", "very"),
        ("ภาษาไทย", "phasaa thai", "Thai language"),
        ("เรียน", "rian", "study / learn"),
        ("ไม่มี", "mai mee", "do not have / there is no"),
    ]
    for thai, romanization, english_text in extra:
        words.setdefault(thai, (romanization, english_text))
    return sorted(words.items(), key=lambda item: len(item[0]), reverse=True)


def thai_lookup_html(text):
    escaped = html.escape(text)
    output = ""
    index = 0
    words = glossary_words()
    while index < len(escaped):
        match = None
        for thai, (romanization, english_text) in words:
            escaped_thai = html.escape(thai)
            if escaped.startswith(escaped_thai, index):
                match = (escaped_thai, romanization, english_text)
                break
        if match:
            thai, romanization, english_text = match
            tip = html.escape(f"{romanization} = {english_text}", quote=True)
            output += f'<span class="lookup" data-tip="{tip}" title="{tip}">{thai}</span>'
            index += len(thai)
        else:
            output += escaped[index]
            index += 1
    return output


def thai_markdown(text, size_class="thai-text"):
    st.markdown(f'<div class="{size_class}">{thai_lookup_html(text)}</div>', unsafe_allow_html=True)


def openai_client():
    from openai import OpenAI

    return OpenAI(api_key=get_api_key())


def speak_button(text, label="Play audio", rate=0.72, key=None):
    safe_text = json.dumps(text)
    safe_label = html.escape(label)
    safe_id = html.escape(key or f"tts-{abs(hash((text, label, rate)))}")
    components.html(
        f"""
        <button id="{safe_id}" style="
            border: 1px solid #dbe4df;
            border-radius: 8px;
            background: #ffffff;
            color: #18211f;
            padding: 0.55rem 0.75rem;
            cursor: pointer;
            font: 14px system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">{safe_label}</button>
        <script>
        const btn = document.getElementById({json.dumps(safe_id)});
        btn.onclick = () => {{
          const utterance = new SpeechSynthesisUtterance({safe_text});
          utterance.lang = "th-TH";
          utterance.rate = {rate};
          window.speechSynthesis.cancel();
          window.speechSynthesis.speak(utterance);
        }};
        </script>
        """,
        height=44,
    )


def known_vocab_context(limit=80):
    return "\n".join(f"- {thai}: {english}" for _, thai, _, english, *_ in load_cards()[:limit])


def ai_homework_help(text, model):
    vocab_context = known_vocab_context()
    prompt = f"""
You are a patient Thai tutor for a beginner.
Help with the homework without simply doing everything unexplained.

Student homework:
{text}

Known vocabulary:
{vocab_context or "No saved vocabulary yet."}

Return:
1. A beginner-friendly explanation.
2. Important vocabulary with romanization and English.
3. Grammar or sentence pattern notes.
4. A corrected answer if the student included an attempt.
5. Three small practice prompts.
Keep the tone encouraging and concrete.
"""
    response = openai_client().responses.create(model=model, input=prompt)
    return response.output_text


def ai_conversation_reply(history, learner_reply, scenario, model):
    transcript = "\n".join(f"{turn['role']}: {turn['thai']} / {turn.get('english', '')}" for turn in history[-8:])
    prompt = f"""
You are a very patient Thai conversation tutor.
Scenario: {scenario}

Recent conversation:
{transcript}

Learner just replied:
{learner_reply}

Respond with exactly this format:
Thai: <one short natural Thai line>
Romanization: <beginner-friendly romanization>
English: <natural English meaning>
Coach: <one gentle correction or encouragement, under 25 words>

Keep the Thai beginner-friendly and continue the scenario slowly.
"""
    response = openai_client().responses.create(model=model, input=prompt)
    return response.output_text


def transcribe_audio(uploaded_file):
    audio_bytes = uploaded_file.getvalue()
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = uploaded_file.name
    result = openai_client().audio.transcriptions.create(
        model=TRANSCRIBE_MODEL,
        file=audio_file,
        language="th",
        prompt="Thai language learning audio. Preserve Thai script when possible.",
    )
    return result.text


def explain_transcript(transcript, model):
    prompt = f"""
You are a Thai listening coach for a beginner.
Analyze this Thai transcript:

{transcript}

Give:
1. Natural English meaning.
2. Word-by-word Thai vocabulary with romanization.
3. What to listen for next time.
4. A short quiz with answer key.
"""
    response = openai_client().responses.create(model=model, input=prompt)
    return response.output_text


def render_vocab_tab():
    st.subheader("Vocabulary and spaced repetition")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("Upload CSV/TSV rows: `thai, romanization, english, category, notes`.")
        upload = st.file_uploader("Upload vocab list", type=["csv", "tsv", "txt"])
        if upload and st.button("Import uploaded vocab"):
            parse_vocab_upload(upload)
            st.success("Vocabulary imported.")
            st.rerun()

        if st.button("Load sample vocab"):
            for row in SAMPLE_WORDS:
                add_card(*row)
            st.success("Sample words added.")
            st.rerun()

    with col2:
        with st.form("add_card"):
            thai = st.text_input("Thai")
            romanization = st.text_input("Romanization")
            english = st.text_input("English")
            category = st.text_input("Category", value="custom")
            notes = st.text_area("Notes")
            if st.form_submit_button("Add card") and thai and english:
                add_card(thai, romanization, english, category, notes)
                st.success("Card added.")
                st.rerun()

    due_cards = load_cards(only_due=True)
    all_cards = load_cards()
    st.metric("Total cards", len(all_cards))
    st.metric("Due today", len(due_cards))

    st.divider()
    st.subheader("Review")
    if not due_cards:
        st.info("Nothing due right now. Add cards or come back tomorrow.")
    else:
        card = due_cards[0]
        _, thai, romanization, english, category, notes, *_ = card
        with st.container(border=True):
            thai_markdown(thai)
            st.caption(f"{romanization or 'No romanization'} · {category or 'uncategorized'}")
            with st.expander("Show answer"):
                st.markdown(thai_lookup_html(english), unsafe_allow_html=True)
                if notes:
                    st.markdown(thai_lookup_html(notes), unsafe_allow_html=True)
            cols = st.columns(3)
            if cols[0].button("Again"):
                review_card(card, "again")
                st.rerun()
            if cols[1].button("Good"):
                review_card(card, "good")
                st.rerun()
            if cols[2].button("Easy"):
                review_card(card, "easy")
                st.rerun()

    with st.expander("All cards"):
        st.dataframe(
            [
                {
                    "Thai": thai,
                    "Romanization": romanization,
                    "English": english,
                    "Category": category,
                    "Due": due_on,
                    "Interval": interval,
                }
                for _, thai, romanization, english, category, _, _, interval, _, due_on in all_cards
            ],
            use_container_width=True,
        )


def render_homework_tab(model):
    st.subheader("AI homework help")
    if not get_api_key():
        st.warning("Add your OpenAI API key in the sidebar or in `.streamlit/secrets.toml` to use AI help.")

    homework = st.text_area("Paste your Thai homework, instructions, or your attempted answer", height=220)
    if st.button("Explain my homework", type="primary", disabled=not bool(get_api_key())):
        with st.spinner("Thinking like a patient tutor..."):
            st.markdown(thai_lookup_html(ai_homework_help(homework, model)), unsafe_allow_html=True)


def render_audio_tab(model):
    st.subheader("Uploaded audio processing")
    if not get_api_key():
        st.warning("Add your OpenAI API key in the sidebar or in `.streamlit/secrets.toml` to transcribe audio.")

    audio = st.file_uploader("Upload Thai audio", type=["mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav", "webm"])
    if audio:
        st.audio(audio)

    if st.button("Transcribe and quiz me", type="primary", disabled=not bool(audio and get_api_key())):
        with st.spinner("Transcribing Thai audio..."):
            transcript = transcribe_audio(audio)
        st.markdown("### Transcript")
        st.markdown(thai_lookup_html(transcript), unsafe_allow_html=True)
        with st.spinner("Building listening notes..."):
            st.markdown(thai_lookup_html(explain_transcript(transcript, model)), unsafe_allow_html=True)


def render_conversation_tab(model):
    st.subheader("Slow conversation practice")
    st.write("Pick a situation, listen to the coach, reply in Thai, romanization, or English, then keep going slowly.")

    scenario_name = st.selectbox("Scenario", list(CONVERSATION_SCENARIOS.keys()))
    if "conversation_scenario" not in st.session_state or st.session_state.conversation_scenario != scenario_name:
        st.session_state.conversation_scenario = scenario_name
        st.session_state.conversation_step = 0
        st.session_state.conversation_history = []

    scenario = CONVERSATION_SCENARIOS[scenario_name]

    def add_scripted_coach_line():
        line = scenario[st.session_state.conversation_step % len(scenario)]
        st.session_state.conversation_history.append(
            {"role": "Coach", "thai": line[0], "romanization": line[1], "english": line[2], "coach": ""}
        )
        st.session_state.conversation_step += 1

    if not st.session_state.conversation_history:
        add_scripted_coach_line()

    top_cols = st.columns(3)
    if top_cols[0].button("Restart conversation"):
        st.session_state.conversation_step = 0
        st.session_state.conversation_history = []
        add_scripted_coach_line()
        st.rerun()
    if top_cols[1].button("Coach says another line"):
        add_scripted_coach_line()
        st.rerun()
    if top_cols[2].button("Add sample vocab to SRS"):
        for line in scenario:
            add_card(line[0], line[1], line[2], "conversation", f"From {scenario_name}.")
        st.success("Conversation lines added to spaced repetition.")

    for index, turn in enumerate(st.session_state.conversation_history):
        with st.chat_message("assistant" if turn["role"] == "Coach" else "user"):
            thai_markdown(turn["thai"])
            if turn.get("romanization"):
                st.markdown(f'<div class="romanization">{html.escape(turn["romanization"])}</div>', unsafe_allow_html=True)
            if turn.get("english"):
                st.write(turn["english"])
            if turn.get("coach"):
                st.info(turn["coach"])
            cols = st.columns([1, 1, 5])
            with cols[0]:
                speak_button(turn["thai"], "Normal", 0.72, key=f"normal-{index}")
            with cols[1]:
                speak_button(turn["thai"], "Slow", 0.48, key=f"slow-{index}")

    learner_reply = st.chat_input("Reply here")
    if learner_reply:
        st.session_state.conversation_history.append({"role": "You", "thai": learner_reply, "romanization": "", "english": "", "coach": ""})
        if get_api_key():
            with st.spinner("Coach is thinking patiently..."):
                ai_text = ai_conversation_reply(
                    st.session_state.conversation_history,
                    learner_reply,
                    scenario_name,
                    model,
                )
            parsed = {"role": "Coach", "thai": ai_text, "romanization": "", "english": "", "coach": ""}
            for line in ai_text.splitlines():
                if line.startswith("Thai:"):
                    parsed["thai"] = line.replace("Thai:", "", 1).strip()
                elif line.startswith("Romanization:"):
                    parsed["romanization"] = line.replace("Romanization:", "", 1).strip()
                elif line.startswith("English:"):
                    parsed["english"] = line.replace("English:", "", 1).strip()
                elif line.startswith("Coach:"):
                    parsed["coach"] = line.replace("Coach:", "", 1).strip()
            st.session_state.conversation_history.append(parsed)
        else:
            add_scripted_coach_line()
        st.rerun()


def render_lessons_tab():
    st.subheader("Beginner lessons")
    lesson_titles = [lesson["title"] for lesson in LESSONS]
    choice = st.selectbox("Choose a lesson", lesson_titles)
    lesson = next(item for item in LESSONS if item["title"] == choice)

    st.markdown(
        f"""
        <div class="thai-lesson-hero">
          <h2>{html.escape(lesson["title"])}</h2>
          <p>{html.escape(lesson["goal"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Teaching note")
    st.markdown(thai_lookup_html(lesson["teach"]), unsafe_allow_html=True)
    st.markdown("### Pattern")
    st.markdown(f'<div class="pattern-card">{thai_lookup_html(lesson["pattern"])}</div>', unsafe_allow_html=True)

    st.markdown("### Core vocabulary")
    vocab_cols = st.columns(2)
    for index, (thai, romanization, english_text) in enumerate(lesson["vocab"]):
        with vocab_cols[index % 2]:
            with st.container(border=True):
                thai_markdown(thai)
                st.markdown(f'<div class="romanization">{html.escape(romanization)}</div>', unsafe_allow_html=True)
                st.write(english_text)

    st.markdown("### Example phrases")
    for index, (thai, romanization, english_text) in enumerate(lesson["examples"]):
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                thai_markdown(thai)
                st.markdown(f'<div class="romanization">{html.escape(romanization)}</div>', unsafe_allow_html=True)
                st.write(english_text)
            with right:
                speak_button(thai, "Play", 0.72, key=f"lesson-{choice}-{index}")

    if lesson.get("detail_sections"):
        st.markdown("### Details")
        for title, bullets in lesson["detail_sections"]:
            bullet_html = "".join(f"<li>{thai_lookup_html(item)}</li>" for item in bullets)
            st.markdown(
                f'<div class="detail-card"><strong>{html.escape(title)}</strong><ul>{bullet_html}</ul></div>',
                unsafe_allow_html=True,
            )

    st.markdown("### Practice drills")
    for drill in lesson["drills"]:
        st.checkbox(drill, key=f"drill-{choice}-{drill}")

    if st.button("Add this lesson's words to SRS"):
        for thai, romanization, english_text in lesson["vocab"]:
            add_card(thai, romanization, english_text, lesson["title"], lesson["pattern"])
        st.success("Lesson vocabulary added to spaced repetition.")


def main():
    st.set_page_config(page_title="Thai Study Studio", page_icon="ท", layout="wide")
    install_theme()
    init_db()

    st.title("Thai Study Studio")
    st.caption("AI homework help, audio transcription, and spaced repetition for beginner Thai.")

    with st.sidebar:
        st.header("Settings")
        if not has_secret_api_key():
            st.text_input("OpenAI API key", type="password", key="api_key")
        model = st.text_input("Text model", value=DEFAULT_MODEL)
        st.caption(f"Audio transcription model: `{TRANSCRIBE_MODEL}`")

    tabs = st.tabs(["Vocab + SRS", "Lessons", "Conversation", "AI homework", "Audio upload"])
    with tabs[0]:
        render_vocab_tab()
    with tabs[1]:
        render_lessons_tab()
    with tabs[2]:
        render_conversation_tab(model)
    with tabs[3]:
        render_homework_tab(model)
    with tabs[4]:
        render_audio_tab(model)

    st.caption(f"Local date: {datetime.now().date().isoformat()}")


if __name__ == "__main__":
    main()
