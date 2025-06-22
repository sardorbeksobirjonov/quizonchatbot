# quiz_game_bot.py
import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from aiogram.filters.state import StateFilter
from collections import defaultdict

API_TOKEN = "7613597359:AAHOICxC1nc5yIjVAyHuXJ7BdBTpM2Ht57U"
ADMIN_ID = 7752032178
ADMIN_PASSWORD = "1234"
JOIN_CHANNELS = [
    ("zeoforge", "https://t.me/zeoforge"),
    ("FayzliTV", "https://t.me/FayzliTV")
]

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# States
data_store = defaultdict(lambda: {
    "score": 0, "correct": 0, "wrong": 0,
    "used_questions": set(), "answered_question": False
})
user_list = set()

class QuizState(StatesGroup):
    playing = State()
    awaiting_password = State()
    awaiting_ad = State()

questions = [
    {"question": "Odam tanasida nechta yurak bor?", "options": ["1", "2", "3", "0"], "answer": "1"},
    {"question": "Eng katta sayyora qaysi?", "options": ["Yer", "Yupiter", "Mars", "Venera"], "answer": "Yupiter"},
    {"question": "Kompyuterning miyasi nima?", "options": ["RAM", "Mouse", "CPU", "Monitor"], "answer": "CPU"},
    {"question": "Eng tez hayvon nima?", "options": ["Qartal", "Cheetah", "Ot", "Kaplumbağa"], "answer": "Cheetah"},
    {"question": "Bir yilda nechta oy 31 kunlik?", "options": ["5", "7", "8", "12"], "answer": "7"},
    {"question": "Oʻzbekiston qachon mustaqil boʻlgan?", "options": ["1990", "1991", "1992", "1993"], "answer": "1991"},
    {"question": "Qaysi meva ichida urugʻ boʻlmaydi?", "options": ["Olma", "Uzum", "Banan", "Gilos"], "answer": "Banan"},
    {"question": "Qaysi rang spektrda yoʻq?", "options": ["Qizil", "Yashil", "Sariq", "Kulrang"], "answer": "Kulrang"},
    {"question": "Qaysi oyda eng kam kun bor?", "options": ["Yanvar", "Fevral", "Mart", "Aprel"], "answer": "Fevral"},
    {"question": "Dinozavrlar qaysi davrda yashagan?", "options": ["Yurassic", "Modern", "Ice Age", "Bronze Age"], "answer": "Yurassic"},
    {"question": "Aral dengizi asosan qaysi ikki davlat oʻrtasida joylashgan?", "options": ["Oʻzbekiston va Qozogʻiston", "Rossiya va Ukraina", "Turkiya va Eron", "Tojikiston va Afgʻoniston"], "answer": "Oʻzbekiston va Qozogʻiston"},
{"question": "Yuzasi 64 sm² bo‘lgan kvadratning bir tomoni nechaga teng?", "options": ["6", "8", "7", "9"], "answer": "8"},
{"question": "Koinotdagi eng yaqin yulduz qanday nomlanadi?", "options": ["Proxima Centauri", "Vega", "Sirius", "Betelgeuse"], "answer": "Proxima Centauri"},
{"question": "Inson organizmidagi eng uzun suyak qaysi?", "options": ["Bilak suyagi", "Boldir suyagi", "Son suyagi", "Yelkama suyagi"], "answer": "Son suyagi"},
{"question": "Qaysi hayvon orqa-orqasiga yura olmaydi?", "options": ["Kaltaqush", "Ot", "Qapla", "Kaptar"], "answer": "Ot"},
{"question": "Kompas ignasi doim qayerga qaraydi?", "options": ["G‘arb", "Sharq", "Shimol", "Janub"], "answer": "Shimol"},
{"question": "Bir tonna nechta kilogrammga teng?", "options": ["100", "1000", "500", "1500"], "answer": "1000"},
{"question": "Ko‘z qorachig‘i yorug‘likka nisbatan nima qiladi?", "options": ["Kengayadi", "Qorayadi", "Qisqaradi", "Uzayadi"], "answer": "Qisqaradi"},
{"question": "Qaysi element suv bilan aloqa qilganda portlashi mumkin?", "options": ["Temir", "Litiy", "Nikel", "Kislorod"], "answer": "Litiy"},
{"question": "Quyosh va Yer orasidagi masofa taxminan nechaga teng?", "options": ["150 ming km", "1,5 million km", "150 million km", "15 million km"], "answer": "150 million km"},
{"question": "Internetga birinchi ulangan davlat qaysi?", "options": ["Rossiya", "Buyuk Britaniya", "AQSh", "Fransiya"], "answer": "AQSh"},
{"question": "Tovuqlar kuniga taxminan nechta tuxum qo‘yadi?", "options": ["0", "1", "3", "5"], "answer": "1"},
{"question": "Qanday modda olovni o‘chira olmaydi?", "options": ["Qum", "Ko‘piksimon modda", "Benzin", "Suv"], "answer": "Benzin"},
{"question": "100 ning 25 foizi nechiga teng?", "options": ["20", "25", "15", "30"], "answer": "25"},
{"question": "Qaysi sayyora Quyosh tizimida eng sovuq hisoblanadi?", "options": ["Mars", "Yupiter", "Neptun", "Merkuriy"], "answer": "Neptun"},
{"question": "Sut kisloroddan og‘irmi yoki yengilmi?", "options": ["Og‘ir", "Yengil", "Teng", "Bu taqqoslab bo‘lmaydi"], "answer": "Og‘ir"},
{"question": "Qaysi qit’ada eng ko‘p davlat mavjud?", "options": ["Afrika", "Osiyo", "Yevropa", "Janubiy Amerika"], "answer": "Afrika"},
{"question": "DNA nima degan so‘zlarning qisqartmasi?", "options": ["Dinamik Nurlanish Agentligi", "Dezoksiribonuklein kislota", "Doimiy Navo Aksariyati", "Davlat Normativ Arxivi"], "answer": "Dezoksiribonuklein kislota"},
{"question": "Toshkent metrosi nechinchi yilda ochilgan?", "options": ["1977", "1975", "1979", "1981"], "answer": "1977"},
{"question": "Eng yengil gaz?", "options": ["Azot", "Vodorod", "Kislorod", "Heliy"], "answer": "Vodorod"},
{"question": "10² ning qiymati nechaga teng?", "options": ["20", "100", "10", "1000"], "answer": "100"},
{"question": "Qaysi hayvon uyqusiz yashay oladi?", "options": ["Fil", "Dengiz delfini", "Baliq", "Sigir"], "answer": "Dengiz delfini"},
{"question": "Kim birinchi marta oyga qadam qo‘ygan?", "options": ["Yuriy Gagarin", "Buzz Aldrin", "Neil Armstrong", "Alan Shepard"], "answer": "Neil Armstrong"},
{"question": "Karbonat angidridning formulasi nima?", "options": ["CO", "CO2", "CH4", "H2O"], "answer": "CO2"},
{"question": "Qaysi qush eng baland uchishi mumkin?", "options": ["Laylak", "Qaldirg‘och", "Oqqush", "Gippogrif"], "answer": "Laylak"},
{"question": "Celsiy bo‘yicha suv necha darajada qaynaydi?", "options": ["90", "100", "110", "80"], "answer": "100"},
{"question": "O‘zbek tilida nechta unli tovush bor?", "options": ["6", "9", "7", "8"], "answer": "6"},
{"question": "Qaysi biri fotosintezda ishtirok etadi?", "options": ["Suv", "Karbonat angidrid", "Quyosh nuri", "Barchasi"], "answer": "Barchasi"},
{"question": "Kompyuterning doimiy xotirasi nima deb ataladi?", "options": ["RAM", "ROM", "CPU", "GPU"], "answer": "ROM"},
{"question": "Odam tanasida qancha juft yurak bor?", "options": ["0", "1", "2", "3"], "answer": "1"},
{"question": "Qaysi hayvon ucholmaydi?", "options": ["Tovus", "Qaldirg‘och", "Pingvin", "Kaptar"], "answer": "Pingvin"},
{"question": "Suvda elektr tokini o‘tkazadigan moddalar nima deb ataladi?", "options": ["Izolyator", "Metall", "Elektrolit", "Semikonduktor"], "answer": "Elektrolit"},
{"question": "Kompyuter operatsion tizimi misoli?", "options": ["Excel", "Windows", "Google", "Photoshop"], "answer": "Windows"},
{"question": "Qaysi hayvonning yuragi tanasida emas boshida joylashgan?", "options": ["Dengiz yulduzi", "Qora mantiya", "Karakatitsa", "Qaldirg‘och"], "answer": "Karakatitsa"},
{"question": "Quyosh nuri spektrdagi nechta asosiy rangdan iborat?", "options": ["3", "5", "7", "9"], "answer": "7"},
{"question": "9 × 6 nechiga teng?", "options": ["54", "63", "45", "56"], "answer": "54"},
{"question": "Fotosintez jarayonida nima hosil bo‘ladi?", "options": ["Kislorod", "Uglerod", "Azot", "Suv"], "answer": "Kislorod"},
{"question": "To‘rtburchakning yuzasi qanday topiladi?", "options": ["Uzunlik × Kenglik", "2 × (a+b)", "πr²", "a²"], "answer": "Uzunlik × Kenglik"},
{"question": "Quyidagi qaysi qurilma axborotni saqlash uchun ishlatiladi?", "options": ["Monitor", "Printer", "Qattiq disk", "Sichqoncha"], "answer": "Qattiq disk"},
{"question": "Limon qaysi vitamin bilan boy?", "options": ["A", "B", "C", "D"], "answer": "C"},
{"question": "Bir hafta nechta kun?", "options": ["5", "6", "7", "8"], "answer": "7"},
{"question": "Qaysi jonivor suvda ham, quruqlikda ham yashaydi?", "options": ["Sichqon", "Qoplon", "Qurbaqa", "Quyon"], "answer": "Qurbaqa"},
{"question": "Eng qisqa oy qaysi?", "options": ["Yanvar", "Fevral", "Mart", "Aprel"], "answer": "Fevral"},
{"question": "O‘simliklar qayerdan oziqlanadi?", "options": ["Havo", "Quyosh", "Yomg‘ir", "Tuproq"], "answer": "Tuproq"},
{"question": "Qaysi biri elektromagnit to‘lqinlar turkumiga kiradi?", "options": ["Ovoz", "Yorug‘lik", "Harorat", "Gaz"], "answer": "Yorug‘lik"},
{"question": "3 × 4 + 5 ning natijasi nechiga teng?", "options": ["17", "12", "9", "21"], "answer": "17"},
{"question": "Suvning kimyoviy formulasi nima?", "options": ["H2O", "CO2", "NaCl", "O2"], "answer": "H2O"},
{"question": "Yer atmosferasida eng ko‘p gaz qaysi?", "options": ["Kislorod", "Azot", "Karbonat angidrid", "Argon"], "answer": "Azot"},
{"question": "Yuzasi eng katta qit’a qaysi?", "options": ["Afrika", "Osiyo", "Amerika", "Antarktida"], "answer": "Osiyo"},
{"question": "5 ning kvadrati nechiga teng?", "options": ["25", "10", "15", "30"], "answer": "25"},
{"question": "Qaysi biri bir hujayrali organizm?", "options": ["Zamburug‘", "Bakteriya", "Odam", "Chumchuq"], "answer": "Bakteriya"},
{"question": "Yil fasllari nimaga qarab o‘zgaradi?", "options": ["Oy fazalari", "Quyosh nuri", "Yerning aylanishiga", "Yer orbitasining qiyaligi"], "answer": "Yer orbitasining qiyaligi"},
{"question": "Bir kilogrammda nechta gramm bor?", "options": ["100", "1000", "10", "500"], "answer": "1000"},
{"question": "Quyidagi sonlarning eng kichigi qaysi? 0.3; 1/2; 0.25", "options": ["0.3", "1/2", "0.25", "Barchasi teng"], "answer": "0.25"},
{"question": "Fazoda og‘irlik mavjudmi?", "options": ["Ha", "Yo‘q", "Ba’zan", "Faqat kunduzi"], "answer": "Yo‘q"},
{"question": "Bir yilda nechta oy bor?", "options": ["10", "11", "12", "13"], "answer": "12"},
{"question": "Yerning tabiiy yo‘ldoshi nima?", "options": ["Quyosh", "Oy", "Mars", "Yulduz"], "answer": "Oy"},
{"question": "Qaysi rang olovda eng issiq?", "options": ["Qizil", "Sariq", "Ko‘k", "Yashil"], "answer": "Ko‘k"},
{"question": "O‘zbekiston poytaxti qaysi?", "options": ["Buxoro", "Toshkent", "Samarqand", "Xiva"], "answer": "Toshkent"},
{"question": "Eng kichik musbat tub son qaysi?", "options": ["1", "2", "3", "5"], "answer": "2"},
{"question": "Kompyuterning miya qismi?", "options": ["Klaviatura", "Protsessor", "Monitor", "Sichqoncha"], "answer": "Protsessor"},
{"question": "Quyosh tizimidagi eng katta sayyora qaysi?", "options": ["Yupiter", "Mars", "Neptun", "Saturn"], "answer": "Yupiter"},
{"question": "Eng uzun daryo qaysi?", "options": ["Nil", "Amazonka", "Volga", "Missisipi"], "answer": "Nil"},
{"question": "Suv qaynash harorati?", "options": ["50°C", "80°C", "100°C", "120°C"], "answer": "100°C"},
{"question": "Inson yuragida nechta bo‘lim bor?", "options": ["2", "3", "4", "5"], "answer": "4"},
{"question": "Shimoliy qutb qaerda joylashgan?", "options": ["Antarktida", "Yevropa", "Arktika", "Avstraliya"], "answer": "Arktika"},
{"question": "Qaysi tilda eng ko‘p inson so‘zlashadi?", "options": ["Ingliz", "Ispan", "Xitoy", "Arab"], "answer": "Xitoy"},
{"question": "Vitamin C nima uchun kerak?", "options": ["Suyaklar", "Immunitet", "Ko‘z", "Teri"], "answer": "Immunitet"},
{"question": "Sharqda quyosh...", "options": ["botadi", "chiqadi", "yo‘qoladi", "muzlaydi"], "answer": "chiqadi"},
{"question": "Kompyuterdagi 'Ctrl+Z' nima qiladi?", "options": ["Qaytaradi", "Kesadi", "Nusxalaydi", "Chop etadi"], "answer": "Qaytaradi"},
{"question": "Bosh harf bilan yoziladi?", "options": ["Shaxs nomlari", "Fe’llar", "Olmoshlar", "Raqamlar"], "answer": "Shaxs nomlari"},
{"question": "Qaysi biri qush emas?", "options": ["Qaldirg‘och", "Tuyaqush", "Ko‘rshapalak", "Tovus"], "answer": "Ko‘rshapalak"},
{"question": "Tirik organizmlarda DNK nima?", "options": ["Suyak", "Genetik kod", "Qon", "Nerv"], "answer": "Genetik kod"},
{"question": "Asosiy ranglar qaysilar?", "options": ["Qizil, Ko‘k, Sariq", "Yashil, Ko‘k, Qora", "Sariq, Yashil, Kulrang", "Ko‘k, Oq, Jigarrang"], "answer": "Qizil, Ko‘k, Sariq"},
{"question": "O'zbek alifbosida nechta harf bor?", "options": ["26", "28", "30", "29"], "answer": "29"},
{"question": "O‘zbekiston mustaqillik kuni qaysi?", "options": ["1-iyun", "9-may", "1-sentabr", "31-dekabr"], "answer": "1-sentabr"},
{"question": "Olimpiada har necha yilda o‘tkaziladi?", "options": ["2", "3", "4", "5"], "answer": "4"},
{"question": "Eng yengil element?", "options": ["Vodorod", "Kislorod", "Uglerod", "Azot"], "answer": "Vodorod"},
{"question": "Qaysi hayvon tuxum qo‘yadi?", "options": ["Sigir", "Echki", "O‘rdak", "Mushuk"], "answer": "O‘rdak"},
{"question": "Ichimlik suvi qanday bo‘lishi kerak?", "options": ["Shirin", "Sho‘r", "Toza", "Gazli"], "answer": "Toza"},
{"question": "Qanday sayyora 'qizil sayyora' deb ataladi?", "options": ["Yupiter", "Saturn", "Mars", "Merkuriy"], "answer": "Mars"},
{"question": "Odam tanasida nechta suyak bor?", "options": ["106", "206", "306", "406"], "answer": "206"},
{"question": "Yilning eng qisqa kuni?", "options": ["1-yanvar", "21-dekabr", "1-mart", "30-iyun"], "answer": "21-dekabr"},
{"question": "Qaysi hayvon eng tez yuguradi?", "options": ["Fil", "Kaplumbağa", "Qoplon", "Quyon"], "answer": "Qoplon"},
{"question": "Qaysi oyda eng kam kun bor?", "options": ["Yanvar", "Fevral", "Mart", "Aprel"], "answer": "Fevral"},
{"question": "Yerning sun’iy yo‘ldoshi qanday nomlanadi?", "options": ["Oy", "Mars", "Sputnik", "Hubble"], "answer": "Oy"},
{"question": "Atom raqami 1 bo‘lgan element?", "options": ["Heliy", "Kislorod", "Vodorod", "Azot"], "answer": "Vodorod"},
{"question": "Dunyodagi eng katta okean qaysi?", "options": ["Atlantika", "Tinch", "Hind", "Shimoliy Muz"], "answer": "Tinch"},
{"question": "Kompyuterning 'miya' qismi qaysi?", "options": ["Protsessor", "Klaviatura", "Monitor", "Sichqoncha"], "answer": "Protsessor"},
{"question": "Dinozavrlar qaysi davrda yashagan?", "options": ["Yura", "Neolit", "Renessans", "Bronza"], "answer": "Yura"},
{"question": "Yevropadagi eng uzun daryo?", "options": ["Dunay", "Volga", "Reyn", "Temza"], "answer": "Volga"},
{"question": "Vitamin D qayerdan olinadi?", "options": ["Non", "Quyosh nuri", "Go‘sht", "Sut"], "answer": "Quyosh nuri"},
{"question": "Shakar qaysi modda?", "options": ["Oqsil", "Yog‘", "Uglevod", "Mineral"], "answer": "Uglevod"},
{"question": "Insonning yuragi necha bo‘limdan iborat?", "options": ["2", "3", "4", "5"], "answer": "4"},
{"question": "Eng katta qush qaysi?", "options": ["Qaldirg‘och", "Qarg‘a", "Tuyaqush", "Tovus"], "answer": "Tuyaqush"},
{"question": "Soat nechta daqiqadan iborat?", "options": ["60", "45", "100", "30"], "answer": "60"},
{"question": "Qaysi qurilma matn chop etadi?", "options": ["Skanner", "Printer", "Monitor", "Modem"], "answer": "Printer"},
{"question": "0 ga ko‘paytirilgan har qanday son nechiga teng?", "options": ["1", "0", "Manfiy", "Sonning o‘zi"], "answer": "0"},
{"question": "Qaysi hayvon faqat suvda yashaydi?", "options": ["Qurbaqa", "Pingvin", "Ayuq", "Dengiz baliqlari"], "answer": "Dengiz baliqlari"},
{"question": "Karbonat angidrid kimyoviy formulasi nima?", "options": ["CO", "CO2", "O2", "H2O"], "answer": "CO2"},
{"question": "Kompyuter qismlaridan biri?", "options": ["Soat", "Kitob", "Protsessor", "Ruchka"], "answer": "Protsessor"},
{"question": "Qaysi biri tabiiy yoqilg‘i emas?", "options": ["Gaz", "Ko‘mir", "Neft", "Elektr"], "answer": "Elektr"},
{"question": "Qaysi a'zo tanada qon haydaydi?", "options": ["O‘pka", "Jigar", "Yurak", "Buyrak"], "answer": "Yurak"},
{"question": "Bo‘sh joy bilan to‘ldiring: Quyosh ___ nurlari orqali issiqlik beradi.", "options": ["Mikro", "Infraqizil", "Ultrabinafsha", "Rentgen"], "answer": "Infraqizil"},
{"question": "Qaysi son tub son emas?", "options": ["17", "19", "21", "23"], "answer": "21"},
{"question": "Agar bitta olma 300 gramm bo‘lsa, 4 ta olmaning og‘irligi nechcha?", "options": ["1 kg", "1.2 kg", "1.4 kg", "1.6 kg"], "answer": "1.2 kg"},
{"question": "Sonli qatorni to‘ldiring: 2, 4, 8, 16, ...", "options": ["18", "24", "32", "30"], "answer": "32"},
{"question": "Insondagi eng mayda suyak qaerda?", "options": ["Tizzada", "Oyoqda", "Quloqda", "Qo‘lda"], "answer": "Quloqda"},
{"question": "Ilon qanday harakatlanadi?", "options": ["Yuguradi", "Sakraydi", "Sirradi", "Emaklaydi"], "answer": "Sirradi"},
{"question": "4 × (3 + 2) natijasi nechchi?", "options": ["14", "16", "20", "24"], "answer": "20"},
{"question": "Kompyuter kiritish qurilmasi qaysi?", "options": ["Monitor", "Sichqoncha", "Printer", "Projektor"], "answer": "Sichqoncha"},
{"question": "Inson tanasining qaysi qismi isitmani nazorat qiladi?", "options": ["Yurak", "O‘pka", "Bosh miya", "Qon"], "answer": "Bosh miya"},
{"question": "Agar 5 litr suvga 2 litr qo‘shilsa, nechchi bo‘ladi?", "options": ["6", "7", "8", "9"], "answer": "7"},
{"question": "Yerning ichki qatlamiga nima deyiladi?", "options": ["Tog‘", "Magna", "Yadro", "Yer po‘sti"], "answer": "Yadro"},
{"question": "Qaysi sayyora eng yaqin joylashgan Quyoshga?", "options": ["Venus", "Merkuriy", "Yer", "Mars"], "answer": "Merkuriy"},
{"question": "Qaysi metall suyuq holatda bo‘ladi xona haroratida?", "options": ["Temir", "Qo‘rg‘oshin", "Simob", "Nikel"], "answer": "Simob"},
{"question": "Insonning normal tana harorati necha daraja?", "options": ["35°C", "36.6°C", "37.5°C", "39°C"], "answer": "36.6°C"},
{"question": "O‘zbek tilida nechta undosh tovush bor?", "options": ["20", "21", "23", "24"], "answer": "23"},
{"question": "Qaysi shahar Movarounnahr markazi bo‘lgan?", "options": ["Toshkent", "Samarqand", "Buxoro", "Xiva"], "answer": "Samarqand"},
{"question": "Qaysi jonzot tuxum qo‘ymaydi?", "options": ["To‘tiqush", "Echki", "Kaplumbağa", "O‘rdak"], "answer": "Echki"},
{"question": "Qaysi asbob elektr kuchini o‘lchaydi?", "options": ["Termometr", "Voltmetr", "Kompas", "Barometr"], "answer": "Voltmetr"},
{"question": "Sonlar orasida eng kichik musbat tub son?", "options": ["1", "2", "3", "0"], "answer": "2"},
{"question": "Ranglar spektri nechtadan iborat?", "options": ["5", "6", "7", "8"], "answer": "7"},
{"question": "Inson qonni qaysi organ orqali tozalaydi?", "options": ["Buyrak", "Yurak", "Jigar", "Ichak"], "answer": "Buyrak"},
{"question": "Kompyuterda faylni saqlash tugmasi?", "options": ["Ctrl + C", "Ctrl + V", "Ctrl + S", "Ctrl + X"], "answer": "Ctrl + S"},
{"question": "Qaysi yulduzga eng yaqin sayyora?", "options": ["Proxima", "Sirius", "Quyosh", "Betelgeuse"], "answer": "Quyosh"},
{"question": "Qaysi son toq?", "options": ["18", "24", "11", "36"], "answer": "11"},
]

async def is_user_joined(user_id):
    for channel, _ in JOIN_CHANNELS:
        try:
            member = await bot.get_chat_member(f"@{channel}", user_id)
            if member.status in ["left"]:
                return False
        except:
            return False
    return True

@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_list.add(user_id)

    if not await is_user_joined(user_id):
        join_buttons = [[InlineKeyboardButton(text="📢 Kanalga qo‘shilish", url=url)] for _, url in JOIN_CHANNELS]
        join_buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_join")])
        markup = InlineKeyboardMarkup(inline_keyboard=join_buttons)
        await message.answer("<b>🎮 Oʻyinni boshlash uchun quyidagi kanallarga a’zo bo‘ling:</b>", reply_markup=markup)
        return

    await message.answer(
        "<b>📜 Qoida:</b>\n"
        "Bu bot orqali savollarga javob berib ball to‘plang va turli sovg‘alarni yutib oling! 🎁\n"
        "✅ To‘g‘ri javob: <b>+5</b> ball\n"
        "❌ Noto‘g‘ri javob: <b>-2</b> ball\n"
        "🔁 Ballar yig‘ilaveradi va har safar natijangiz yangilanadi!\n"
        "SOvga olsh uchun admnga murohat qiling admn: @sardorbeksobirjonov\n"
        "<b>Omad!</b> 🍀"
    )
    menu_buttons = [
        [InlineKeyboardButton(text="🎮 Oʻyinni boshlash", callback_data="start_game")],
        [InlineKeyboardButton(text="📊 Ballim", callback_data="show_my_score"), InlineKeyboardButton(text="🛠 Admin panel", callback_data="admin")]
    ]
    await message.answer("<b>Quyidagilardan birini tanlang:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=menu_buttons))

@dp.callback_query(F.data == "check_join")
async def recheck_channels(callback: CallbackQuery, state: FSMContext):
    if await is_user_joined(callback.from_user.id):
        await start_handler(callback.message, state)
    else:
        await callback.answer("Hali ham kanallarga a’zo emassiz!", show_alert=True)

@dp.callback_query(F.data == "start_game")
async def game_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizState.playing)
    data_store[callback.from_user.id] = {"score": 0, "correct": 0, "wrong": 0, "used_questions": set(), "answered_question": False}
    await send_question(callback, callback.from_user.id)

async def send_question(callback_or_message, user_id):
    used = data_store[user_id]["used_questions"]
    available_questions = [i for i in range(len(questions)) if i not in used]

    if not available_questions:
        return await end_game(callback_or_message, user_id)

    q_index = random.choice(available_questions)
    data_store[user_id]["used_questions"].add(q_index)
    data_store[user_id]["answered_question"] = False
    q = questions[q_index]

    buttons = [InlineKeyboardButton(text=opt, callback_data=f"answer:{opt}:{q['answer']}") for opt in q['options']]
    markup = InlineKeyboardMarkup(inline_keyboard=[
        buttons[:2],
        buttons[2:],
        [InlineKeyboardButton(text="⛔ To‘xtatish", callback_data="stop_game")]
    ])

    await bot.send_message(user_id, f"<b>{q['question']}</b>", reply_markup=markup)

@dp.callback_query(F.data.startswith("answer:"))
async def answer_handler(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id

    if data_store[uid]["answered_question"]:
        await callback.answer("⛔ Siz bu savolga javob berdingiz!", show_alert=True)
        return

    data_store[uid]["answered_question"] = True

    _, user_ans, correct_ans = callback.data.split(":")
    if user_ans == correct_ans:
        data_store[uid]["score"] += 5
        data_store[uid]["correct"] += 1
        await callback.answer("✅ To‘g‘ri! +5 ball")
    else:
        data_store[uid]["score"] -= 2
        data_store[uid]["wrong"] += 1
        await callback.answer("❌ Noto‘g‘ri! -2 ball")

    await callback.message.edit_reply_markup(reply_markup=None)
    await send_question(callback, uid)

@dp.callback_query(F.data == "stop_game")
async def stop_game(callback: CallbackQuery, state: FSMContext):
    await end_game(callback, callback.from_user.id)
    await state.clear()

async def end_game(callback_or_message, uid):
    name = callback_or_message.from_user.full_name if hasattr(callback_or_message, 'from_user') else "User"
    info = data_store[uid]
    await bot.send_message(
        uid,
        f"<b>📥 Oʻyin yakuni:</b>\n"
        f"👤 Ism: {name}\n"
        f"✅ To‘g‘ri javoblar: {info['correct']}\n"
        f"❌ Noto‘g‘ri javoblar: {info['wrong']}\n"
        f"🏅 Umumiy ball: <b>{info['score']}</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🔁 Qayta o‘ynash", callback_data="start_game")]]
        )
    )

@dp.callback_query(F.data == "show_my_score")
async def show_score(callback: CallbackQuery):
    info = data_store[callback.from_user.id]
    await callback.message.answer(f"🏅 Umumiy ballingiz: <b>{info['score']}</b>\n✅ To‘g‘ri: {info['correct']}\n❌ Noto‘g‘ri: {info['wrong']}")

@dp.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔐 Admin parolni kiriting:")
    await state.set_state(QuizState.awaiting_password)

@dp.message(StateFilter(QuizState.awaiting_password))
async def check_password(message: Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="send_ad")],
            [InlineKeyboardButton(text="📋 Foydalanuvchilar", callback_data="user_list")]
        ])
        await message.answer("✅ Parol to‘g‘ri!", reply_markup=markup)
    else:
        await message.answer("❌ Noto‘g‘ri parol!")
        await state.clear()

@dp.callback_query(F.data == "user_list")
async def show_users(callback: CallbackQuery):
    text = "👥 <b>Foydalanuvchilar</b>\n"
    for uid in user_list:
        info = data_store[uid]
        text += f"👤 <a href='tg://user?id={uid}'>ID: {uid}</a> - Ball: <b>{info['score']}</b>\n"
    await callback.message.answer(text)

@dp.callback_query(F.data == "send_ad")
async def ask_ad(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizState.awaiting_ad)
    await callback.message.answer("✉️ Reklama matnini kiriting:")

@dp.message(StateFilter(QuizState.awaiting_ad))
async def send_advert(message: Message, state: FSMContext):
    await state.clear()
    sent = 0
    for uid in user_list:
        try:
            await bot.send_message(uid, f"📢 <b>Reklama</b>:\n{message.text}")
            sent += 1
        except:
            continue
    await message.answer(f"✅ {sent} foydalanuvchiga yuborildi.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
