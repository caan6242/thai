const sampleWords = [
  { thai: "สวัสดี", romanization: "sawatdee", english: "hello", category: "greetings", notes: "Polite greeting and goodbye." },
  { thai: "ขอบคุณ", romanization: "khop khun", english: "thank you", category: "manners", notes: "Add ค่ะ/ครับ for politeness." },
  { thai: "ใช่", romanization: "chai", english: "yes", category: "basics", notes: "Affirming that something is correct." },
  { thai: "ไม่ใช่", romanization: "mai chai", english: "no / not correct", category: "basics", notes: "Use when denying a statement." },
  { thai: "น้ำ", romanization: "nam", english: "water", category: "food", notes: "Also appears in many compound words." },
  { thai: "กาแฟ", romanization: "gaa-fae", english: "coffee", category: "food", notes: "Useful for cafe practice." },
  { thai: "เท่าไหร่", romanization: "tao rai", english: "how much", category: "shopping", notes: "Question word for price or amount." },
  { thai: "ห้องน้ำ", romanization: "hong nam", english: "bathroom", category: "travel", notes: "Literally water room." },
  { thai: "อร่อย", romanization: "a-roi", english: "delicious", category: "food", notes: "Good praise after eating." },
  { thai: "ช้าๆ", romanization: "chaa chaa", english: "slowly", category: "conversation", notes: "Useful phrase: พูดช้าๆได้ไหม" }
];

const listeningClips = [
  { thai: "สวัสดีค่ะ", romanization: "sawatdee kha", english: "hello", level: "Beginner" },
  { thai: "ขอน้ำหนึ่งแก้ว", romanization: "khor nam nueng gaew", english: "one glass of water, please", level: "Beginner" },
  { thai: "ราคาเท่าไหร่", romanization: "raa-khaa tao rai", english: "how much is it?", level: "Beginner" },
  { thai: "พูดช้าๆได้ไหม", romanization: "phuut chaa chaa dai mai", english: "can you speak slowly?", level: "Beginner" },
  { thai: "ฉันกำลังเรียนภาษาไทย", romanization: "chan gamlang rian phasaa thai", english: "I am studying Thai", level: "Beginner" }
];

const scenarios = {
  cafe: [
    { thai: "สวัสดีค่ะ รับอะไรดีคะ", romanization: "sawatdee kha, rap arai dee kha", english: "Hello, what would you like?" },
    { thai: "เอากาแฟร้อนหรือเย็นคะ", romanization: "ao gaa-fae ron rue yen kha", english: "Would you like hot or iced coffee?" },
    { thai: "ทั้งหมดห้าสิบบาทค่ะ", romanization: "thang mot haa sip baat kha", english: "That is 50 baht total." }
  ],
  intro: [
    { thai: "คุณชื่ออะไรคะ", romanization: "khun chue arai kha", english: "What is your name?" },
    { thai: "คุณมาจากประเทศอะไรคะ", romanization: "khun maa jaak prathet arai kha", english: "What country are you from?" },
    { thai: "ยินดีที่ได้รู้จักค่ะ", romanization: "yin dee tee dai ruu jak kha", english: "Nice to meet you." }
  ],
  market: [
    { thai: "อยากซื้ออะไรคะ", romanization: "yaak sue arai kha", english: "What would you like to buy?" },
    { thai: "อันนี้อร่อยมากค่ะ", romanization: "an nee a-roi maak kha", english: "This one is very delicious." },
    { thai: "ลดราคาได้ไหมคะ", romanization: "lot raa-khaa dai mai kha", english: "Can you lower the price?" }
  ],
  directions: [
    { thai: "ไปสถานีรถไฟฟ้ายังไงคะ", romanization: "pai sathanee rot fai faa yang ngai kha", english: "How do I get to the train station?" },
    { thai: "ตรงไปแล้วเลี้ยวซ้ายค่ะ", romanization: "trong pai laew liao saai kha", english: "Go straight, then turn left." },
    { thai: "อยู่ใกล้มากค่ะ", romanization: "yuu glai maak kha", english: "It is very nearby." }
  ]
};

const beginnerLessons = [
  {
    title: "Greetings and Polite Particles",
    goal: "Say hello, thank someone, and sound polite with ค่ะ or ครับ.",
    vocab: [
      { thai: "สวัสดี", romanization: "sawatdee", english: "hello / goodbye" },
      { thai: "ขอบคุณ", romanization: "khop khun", english: "thank you" },
      { thai: "ค่ะ", romanization: "kha", english: "polite particle for many female speakers" },
      { thai: "ครับ", romanization: "khrap", english: "polite particle for many male speakers" }
    ],
    phrases: ["สวัสดีค่ะ", "ขอบคุณครับ", "สวัสดี คุณสบายดีไหม"],
    practice: ["Greet a teacher politely.", "Thank someone using ค่ะ or ครับ.", "Read the phrases slowly, then at normal speed."]
  },
  {
    title: "Introducing Yourself",
    goal: "Give your name and ask for someone else's name.",
    vocab: [
      { thai: "ฉัน", romanization: "chan", english: "I / me" },
      { thai: "ผม", romanization: "phom", english: "I / me, commonly male speaker" },
      { thai: "ชื่อ", romanization: "chue", english: "name / called" },
      { thai: "อะไร", romanization: "arai", english: "what" }
    ],
    phrases: ["ฉันชื่อแอนนา", "คุณชื่ออะไรคะ", "ยินดีที่ได้รู้จัก"],
    practice: ["Write your name in the sentence ฉันชื่อ...", "Ask someone their name.", "Say nice to meet you out loud twice."]
  },
  {
    title: "Yes, No, and Not",
    goal: "Answer simple questions with yes, no, and not correct.",
    vocab: [
      { thai: "ใช่", romanization: "chai", english: "yes / correct" },
      { thai: "ไม่ใช่", romanization: "mai chai", english: "no / not correct" },
      { thai: "ไม่", romanization: "mai", english: "not / no" },
      { thai: "ได้", romanization: "dai", english: "can / able / okay" }
    ],
    phrases: ["ใช่ค่ะ", "ไม่ใช่ครับ", "ไม่เป็นไร"],
    practice: ["Answer yes politely.", "Turn ใช่ into ไม่ใช่.", "Make one no-answer using ไม่."]
  },
  {
    title: "Numbers 1-10",
    goal: "Recognize the first ten numbers for prices and time.",
    vocab: [
      { thai: "หนึ่ง", romanization: "nueng", english: "one" },
      { thai: "สอง", romanization: "song", english: "two" },
      { thai: "สาม", romanization: "saam", english: "three" },
      { thai: "สิบ", romanization: "sip", english: "ten" }
    ],
    phrases: ["หนึ่ง สอง สาม", "ห้าบาท", "สิบบาท"],
    practice: ["Count from one to ten.", "Say 5 baht and 10 baht.", "Listen to each number and repeat."]
  },
  {
    title: "Telling Time",
    goal: "Ask what time it is and understand hour words.",
    vocab: [
      { thai: "เวลา", romanization: "welaa", english: "time" },
      { thai: "กี่โมง", romanization: "gee mong", english: "what time" },
      { thai: "โมง", romanization: "mong", english: "o'clock / hour marker" },
      { thai: "นาที", romanization: "naa-thee", english: "minute" }
    ],
    phrases: ["กี่โมงแล้ว", "สามโมง", "ห้านาที"],
    practice: ["Ask what time it is.", "Say three o'clock.", "Write one time you study Thai."]
  },
  {
    title: "Days of the Week",
    goal: "Name common days and talk about today or tomorrow.",
    vocab: [
      { thai: "วัน", romanization: "wan", english: "day" },
      { thai: "วันนี้", romanization: "wan nee", english: "today" },
      { thai: "พรุ่งนี้", romanization: "phrung nee", english: "tomorrow" },
      { thai: "เมื่อวาน", romanization: "muea waan", english: "yesterday" }
    ],
    phrases: ["วันนี้วันอะไร", "พรุ่งนี้ฉันเรียนภาษาไทย", "เมื่อวานฉันดื่มกาแฟ"],
    practice: ["Ask what day it is.", "Say you study Thai tomorrow.", "Make one sentence with วันนี้."]
  },
  {
    title: "Colors",
    goal: "Describe objects with basic colors.",
    vocab: [
      { thai: "สี", romanization: "see", english: "color" },
      { thai: "สีแดง", romanization: "see daeng", english: "red" },
      { thai: "สีฟ้า", romanization: "see faa", english: "blue / sky blue" },
      { thai: "สีเขียว", romanization: "see khiao", english: "green" }
    ],
    phrases: ["เสื้อสีแดง", "แก้วสีฟ้า", "บ้านสีเขียว"],
    practice: ["Name three colors near you.", "Describe a shirt.", "Tap each color word and say it."]
  },
  {
    title: "Household Items",
    goal: "Name common things at home.",
    vocab: [
      { thai: "บ้าน", romanization: "baan", english: "house / home" },
      { thai: "โต๊ะ", romanization: "to", english: "table" },
      { thai: "เก้าอี้", romanization: "gao-ee", english: "chair" },
      { thai: "เตียง", romanization: "tiang", english: "bed" }
    ],
    phrases: ["นี่คือโต๊ะ", "เก้าอี้อยู่ในบ้าน", "เตียงอยู่ในห้อง"],
    practice: ["Point to a table and say โต๊ะ.", "Make a sentence with บ้าน.", "List three items in your room."]
  },
  {
    title: "Family",
    goal: "Talk about family members simply.",
    vocab: [
      { thai: "ครอบครัว", romanization: "khrop khrua", english: "family" },
      { thai: "แม่", romanization: "mae", english: "mother" },
      { thai: "พ่อ", romanization: "pho", english: "father" },
      { thai: "พี่", romanization: "phee", english: "older sibling" }
    ],
    phrases: ["นี่คือแม่ของฉัน", "พ่ออยู่บ้าน", "ฉันมีพี่หนึ่งคน"],
    practice: ["Say mother and father.", "Make one sentence about family.", "Ask a simple มี question."]
  },
  {
    title: "Food and Drink",
    goal: "Order simple food and drinks.",
    vocab: [
      { thai: "อาหาร", romanization: "aa-haan", english: "food" },
      { thai: "น้ำ", romanization: "nam", english: "water" },
      { thai: "กาแฟ", romanization: "gaa-fae", english: "coffee" },
      { thai: "ข้าว", romanization: "khao", english: "rice / meal" }
    ],
    phrases: ["ขอน้ำหนึ่งแก้ว", "ฉันชอบกาแฟ", "ข้าวอร่อย"],
    practice: ["Order water.", "Say you like coffee.", "Tell someone the rice is delicious."]
  },
  {
    title: "At a Cafe",
    goal: "Choose hot or iced drinks and ask for one item.",
    vocab: [
      { thai: "ร้อน", romanization: "ron", english: "hot" },
      { thai: "เย็น", romanization: "yen", english: "cold / iced" },
      { thai: "แก้ว", romanization: "gaew", english: "glass / cup" },
      { thai: "เอา", romanization: "ao", english: "want / take" }
    ],
    phrases: ["เอากาแฟเย็นค่ะ", "ขอน้ำหนึ่งแก้ว", "กาแฟร้อนหนึ่งแก้วครับ"],
    practice: ["Order iced coffee.", "Ask for one cup of water.", "Switch the order to hot coffee."]
  },
  {
    title: "Shopping and Prices",
    goal: "Ask how much something costs.",
    vocab: [
      { thai: "ราคา", romanization: "raa-khaa", english: "price" },
      { thai: "เท่าไหร่", romanization: "tao rai", english: "how much" },
      { thai: "บาท", romanization: "baat", english: "baht" },
      { thai: "แพง", romanization: "phaeng", english: "expensive" }
    ],
    phrases: ["ราคาเท่าไหร่", "ห้าสิบบาท", "แพงไหม"],
    practice: ["Ask the price.", "Say 50 baht.", "Ask if something is expensive."]
  },
  {
    title: "Directions",
    goal: "Understand basic movement words.",
    vocab: [
      { thai: "ไป", romanization: "pai", english: "go" },
      { thai: "ตรงไป", romanization: "trong pai", english: "go straight" },
      { thai: "ซ้าย", romanization: "saai", english: "left" },
      { thai: "ขวา", romanization: "khwaa", english: "right" }
    ],
    phrases: ["ตรงไปค่ะ", "เลี้ยวซ้าย", "ไปทางขวา"],
    practice: ["Say go straight.", "Give left and right directions.", "Ask how to go somewhere."]
  },
  {
    title: "Places in Town",
    goal: "Ask for common places while traveling.",
    vocab: [
      { thai: "โรงแรม", romanization: "rong raem", english: "hotel" },
      { thai: "สถานี", romanization: "sathanee", english: "station" },
      { thai: "ร้านอาหาร", romanization: "raan aa-haan", english: "restaurant" },
      { thai: "ห้องน้ำ", romanization: "hong nam", english: "bathroom" }
    ],
    phrases: ["ห้องน้ำอยู่ที่ไหน", "ไปโรงแรมยังไง", "ร้านอาหารอยู่ใกล้ไหม"],
    practice: ["Ask where the bathroom is.", "Ask how to get to a hotel.", "Say restaurant slowly."]
  },
  {
    title: "People and Pronouns",
    goal: "Use I, you, and he/she in simple sentences.",
    vocab: [
      { thai: "คุณ", romanization: "khun", english: "you" },
      { thai: "เขา", romanization: "khao", english: "he / she / they" },
      { thai: "เรา", romanization: "rao", english: "we / us" },
      { thai: "คน", romanization: "khon", english: "person" }
    ],
    phrases: ["คุณสบายดีไหม", "เขาชอบกาแฟ", "เราเรียนภาษาไทย"],
    practice: ["Make one sentence with คุณ.", "Change ฉัน to เรา.", "Ask someone if they are well."]
  },
  {
    title: "Feelings",
    goal: "Say how you feel today.",
    vocab: [
      { thai: "สบายดี", romanization: "sabai dee", english: "well / comfortable" },
      { thai: "เหนื่อย", romanization: "nueai", english: "tired" },
      { thai: "หิว", romanization: "hiw", english: "hungry" },
      { thai: "ดีใจ", romanization: "dee jai", english: "happy / glad" }
    ],
    phrases: ["ฉันสบายดี", "วันนี้เหนื่อย", "ฉันหิวมาก"],
    practice: ["Say how you feel.", "Ask คุณสบายดีไหม.", "Make one วันนี้ sentence."]
  },
  {
    title: "Common Verbs",
    goal: "Build basic sentences with everyday actions.",
    vocab: [
      { thai: "กิน", romanization: "gin", english: "eat" },
      { thai: "ดื่ม", romanization: "duem", english: "drink" },
      { thai: "เรียน", romanization: "rian", english: "study / learn" },
      { thai: "พูด", romanization: "phuut", english: "speak" }
    ],
    phrases: ["ฉันกินข้าว", "เขาดื่มน้ำ", "เราเรียนภาษาไทย"],
    practice: ["Say I eat rice.", "Say we study Thai.", "Use พูด in a request."]
  },
  {
    title: "Questions",
    goal: "Recognize common question words.",
    vocab: [
      { thai: "ไหม", romanization: "mai", english: "yes/no question marker" },
      { thai: "ที่ไหน", romanization: "tee nai", english: "where" },
      { thai: "เมื่อไหร่", romanization: "muea rai", english: "when" },
      { thai: "ทำไม", romanization: "tham mai", english: "why" }
    ],
    phrases: ["คุณชอบไหม", "ห้องน้ำอยู่ที่ไหน", "เรียนเมื่อไหร่"],
    practice: ["Make a yes/no question with ไหม.", "Ask where something is.", "Ask when class is."]
  },
  {
    title: "Describing Things",
    goal: "Use simple adjectives after nouns.",
    vocab: [
      { thai: "ใหญ่", romanization: "yai", english: "big" },
      { thai: "เล็ก", romanization: "lek", english: "small" },
      { thai: "ใหม่", romanization: "mai", english: "new" },
      { thai: "เก่า", romanization: "gao", english: "old" }
    ],
    phrases: ["บ้านใหญ่", "แก้วเล็ก", "โต๊ะใหม่"],
    practice: ["Describe your home.", "Say small cup.", "Make an old/new contrast."]
  },
  {
    title: "Weather",
    goal: "Talk about the weather in simple Thai.",
    vocab: [
      { thai: "อากาศ", romanization: "aa-gaat", english: "weather / air" },
      { thai: "ร้อน", romanization: "ron", english: "hot" },
      { thai: "หนาว", romanization: "naao", english: "cold" },
      { thai: "ฝนตก", romanization: "fon tok", english: "rain falls / raining" }
    ],
    phrases: ["วันนี้อากาศร้อน", "ฝนตกไหม", "อากาศหนาว"],
    practice: ["Say today is hot.", "Ask if it is raining.", "Describe today's weather."]
  },
  {
    title: "Months and Dates",
    goal: "Ask about dates and recognize month words.",
    vocab: [
      { thai: "เดือน", romanization: "duean", english: "month" },
      { thai: "วันที่", romanization: "wan tee", english: "date / day number" },
      { thai: "มกราคม", romanization: "makaraa-khom", english: "January" },
      { thai: "เมษายน", romanization: "mesaa-yon", english: "April" }
    ],
    phrases: ["วันนี้วันที่เท่าไหร่", "เดือนเมษายน", "วันที่หนึ่งมกราคม"],
    practice: ["Ask today's date.", "Say April.", "Write your birthday month."]
  },
  {
    title: "School and Homework",
    goal: "Talk about class, homework, and teachers.",
    vocab: [
      { thai: "โรงเรียน", romanization: "rong rian", english: "school" },
      { thai: "ครู", romanization: "khruu", english: "teacher" },
      { thai: "การบ้าน", romanization: "gaan baan", english: "homework" },
      { thai: "หนังสือ", romanization: "nang sue", english: "book" }
    ],
    phrases: ["ฉันทำการบ้าน", "ครูพูดช้าๆ", "หนังสืออยู่บนโต๊ะ"],
    practice: ["Say I do homework.", "Ask the teacher to speak slowly.", "Name one school item."]
  },
  {
    title: "Body and Health",
    goal: "Name basic body and health words.",
    vocab: [
      { thai: "หัว", romanization: "hua", english: "head" },
      { thai: "มือ", romanization: "mue", english: "hand" },
      { thai: "เจ็บ", romanization: "jep", english: "hurt / sore" },
      { thai: "ป่วย", romanization: "puai", english: "sick" }
    ],
    phrases: ["ฉันป่วย", "เจ็บหัว", "มือของฉัน"],
    practice: ["Say I am sick.", "Name head and hand.", "Make one sentence with เจ็บ."]
  },
  {
    title: "Transport",
    goal: "Recognize ways to get around.",
    vocab: [
      { thai: "รถ", romanization: "rot", english: "vehicle / car" },
      { thai: "รถไฟ", romanization: "rot fai", english: "train" },
      { thai: "รถเมล์", romanization: "rot mae", english: "bus" },
      { thai: "แท็กซี่", romanization: "thaek-see", english: "taxi" }
    ],
    phrases: ["ไปโดยรถไฟ", "เรียกแท็กซี่ได้ไหม", "รถเมล์อยู่ที่ไหน"],
    practice: ["Ask where the bus is.", "Say by train.", "Ask if you can call a taxi."]
  },
  {
    title: "Daily Routine",
    goal: "Describe small routines.",
    vocab: [
      { thai: "ตื่น", romanization: "tuen", english: "wake up" },
      { thai: "ทำงาน", romanization: "tham ngaan", english: "work" },
      { thai: "กลับบ้าน", romanization: "glap baan", english: "go home" },
      { thai: "นอน", romanization: "non", english: "sleep" }
    ],
    phrases: ["ฉันตื่นเจ็ดโมง", "เขาทำงานวันนี้", "ฉันกลับบ้านแล้วนอน"],
    practice: ["Say when you wake up.", "Make one work sentence.", "Say go home."]
  },
  {
    title: "Hobbies",
    goal: "Say what you like doing.",
    vocab: [
      { thai: "ชอบ", romanization: "chop", english: "like" },
      { thai: "อ่าน", romanization: "aan", english: "read" },
      { thai: "ดู", romanization: "duu", english: "watch / look" },
      { thai: "เพลง", romanization: "phleng", english: "song / music" }
    ],
    phrases: ["ฉันชอบอ่านหนังสือ", "เขาชอบดูหนัง", "ฉันฟังเพลง"],
    practice: ["Say one thing you like.", "Ask คุณชอบอะไร.", "Make a sentence with เพลง."]
  },
  {
    title: "Review: Survival Thai",
    goal: "Combine useful beginner phrases for travel and class.",
    vocab: [
      { thai: "ช่วย", romanization: "chuai", english: "help" },
      { thai: "อีกครั้ง", romanization: "eek khrang", english: "again" },
      { thai: "เข้าใจ", romanization: "khao jai", english: "understand" },
      { thai: "ไม่เข้าใจ", romanization: "mai khao jai", english: "do not understand" }
    ],
    phrases: ["ช่วยพูดช้าๆได้ไหม", "พูดอีกครั้งได้ไหม", "ฉันไม่เข้าใจ"],
    practice: ["Ask someone to repeat.", "Say I do not understand.", "Use ช่วย in a polite request."]
  }
];

const state = {
  words: JSON.parse(localStorage.getItem("thaiWords") || "[]"),
  correct: Number(localStorage.getItem("thaiCorrect") || "0"),
  sessions: Number(localStorage.getItem("thaiSessions") || "0"),
  quizMode: "thaiToEnglish",
  quizWord: null,
  clip: listeningClips[0],
  scenarioStep: 0,
  lessonIndex: Number(localStorage.getItem("thaiLessonIndex") || "0")
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

function allLookupWords() {
  const merged = [...sampleWords, ...state.words, ...beginnerLessons.flatMap((lesson) => lesson.vocab)];
  const byThai = new Map();
  merged.forEach((word) => {
    if (!word.thai || !word.english) return;
    const current = byThai.get(word.thai);
    if (!current || String(word.thai).length > String(current.thai).length) byThai.set(word.thai, word);
  });
  return [...byThai.values()].sort((a, b) => b.thai.length - a.thai.length);
}

function lookupWord(thai) {
  return allLookupWords().find((word) => word.thai === thai);
}

function thaiLookupText(text) {
  const source = escapeHtml(text);
  let output = "";
  let index = 0;
  const words = allLookupWords();
  while (index < source.length) {
    const match = words.find((word) => source.slice(index).startsWith(escapeHtml(word.thai)));
    if (match) {
      const thai = escapeHtml(match.thai);
      output += `<button class="lookup-word" data-lookup="${thai}" title="${escapeHtml(match.english)}">${thai}</button>`;
      index += thai.length;
    } else {
      output += source[index];
      index += 1;
    }
  }
  return output;
}

function wordCard(word) {
  return `
    <div class="thai-text">${thaiLookupText(word.thai)}</div>
    <div class="romanization">${escapeHtml(word.romanization || "")}</div>
    <div>${escapeHtml(word.english || "")}</div>
  `;
}

function showLookup(thai, anchor) {
  const word = lookupWord(thai);
  if (!word) return;
  const popover = $("#lookupPopover");
  popover.innerHTML = `
    <div class="lookup-heading">
      <div>
        <div class="thai-text">${escapeHtml(word.thai)}</div>
        <div class="romanization">${escapeHtml(word.romanization || "No romanization yet")}</div>
      </div>
      <button class="icon-btn" data-popover-speak="${escapeHtml(word.thai)}" title="Hear word" aria-label="Hear word">▶</button>
    </div>
    <p>${escapeHtml(word.english)}</p>
    ${word.notes ? `<p class="hint">${escapeHtml(word.notes)}</p>` : ""}
    ${word.category ? `<p class="lookup-tag">${escapeHtml(word.category)}</p>` : ""}
  `;
  const rect = anchor.getBoundingClientRect();
  popover.style.left = `${Math.min(rect.left, window.innerWidth - 280)}px`;
  popover.style.top = `${rect.bottom + window.scrollY + 8}px`;
  popover.classList.remove("hidden");
}

function hideLookup() {
  $("#lookupPopover").classList.add("hidden");
}

function save() {
  localStorage.setItem("thaiWords", JSON.stringify(state.words));
  localStorage.setItem("thaiCorrect", String(state.correct));
  localStorage.setItem("thaiSessions", String(state.sessions));
  localStorage.setItem("thaiLessonIndex", String(state.lessonIndex));
  render();
}

function speak(text, rate = 0.72) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "th-TH";
  utterance.rate = rate;
  utterance.pitch = 1;
  window.speechSynthesis.speak(utterance);
}

function normalize(value) {
  return value.toLowerCase().trim().replace(/[.,!?;:]/g, "").replace(/\s+/g, " ");
}

function pickRandom(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function parseRows(text) {
  return text
    .split(/\r?\n/)
    .map((row) => row.trim())
    .filter(Boolean)
    .map((row) => row.split(row.includes("\t") ? "\t" : ",").map((cell) => cell.trim()))
    .filter((cells) => cells.length >= 2)
    .map((cells, index) => {
      const first = cells[0].toLowerCase();
      if (index === 0 && ["thai", "word", "คำ"].includes(first)) return null;
      return {
        thai: cells[0] || "",
        romanization: cells[1] || "",
        english: cells[2] || cells[1] || "",
        category: cells[3] || "imported",
        notes: cells[4] || ""
      };
    })
    .filter((word) => word && word.thai && word.english);
}

function addWords(words) {
  const existing = new Set(state.words.map((word) => `${word.thai}|${word.english}`));
  const fresh = words.filter((word) => !existing.has(`${word.thai}|${word.english}`));
  state.words = [...fresh, ...state.words];
  save();
  setFeedback(`${fresh.length} word${fresh.length === 1 ? "" : "s"} imported.`);
}

function setFeedback(message) {
  $("#focusTitle").textContent = message;
}

function render() {
  $("#wordCount").textContent = state.words.length;
  $("#streakCount").textContent = state.correct;
  $("#practiceCount").textContent = state.sessions;
  renderWordTable();
  renderReviewList();
  renderWordBuilder();
  renderLessons();
  if (!state.quizWord) nextQuizQuestion();
}

function renderWordTable() {
  const tbody = $("#wordTable");
  tbody.innerHTML = state.words.length
    ? state.words
        .map(
          (word, index) => `
            <tr>
              <td><div class="word-table-thai">${thaiLookupText(word.thai)} <button class="mini-speak" data-speak-word="${index}" title="Hear word" aria-label="Hear word">▶</button></div></td>
              <td>${escapeHtml(word.romanization || "-")}</td>
              <td>${escapeHtml(word.english)}</td>
              <td>${escapeHtml(word.category || "-")}</td>
              <td><button data-delete-word="${index}">Remove</button></td>
            </tr>
          `
        )
        .join("")
    : `<tr><td colspan="5">No saved words yet. Load the sample set or import your own list.</td></tr>`;
}

function renderReviewList() {
  const words = state.words.slice(0, 6);
  $("#reviewList").innerHTML = words.length
    ? words
        .map(
          (word) => `
            <div class="review-item">
              ${wordCard(word)}
            </div>
          `
        )
        .join("")
    : `<div class="review-item">Load a sample set or upload your own words to build a review queue.</div>`;
}

function renderWordBuilder() {
  const source = state.words.length ? state.words : sampleWords;
  const word = pickRandom(source);
  $("#wordBuilder").innerHTML = `
    <div class="word-pill">
      <div class="thai-text">${thaiLookupText(word.thai)}</div>
      <div class="romanization">${escapeHtml(word.romanization)}</div>
      <p>${escapeHtml(word.english)}</p>
      <p class="hint">${escapeHtml(word.notes || "Try making one short sentence with this word.")}</p>
    </div>
    <button data-builder-speak="${escapeHtml(word.thai)}">Hear it</button>
  `;
}

function renderLessons() {
  const activeLesson = beginnerLessons[state.lessonIndex] || beginnerLessons[0];
  $("#lessonList").innerHTML = beginnerLessons
    .map(
      (lesson, index) => `
        <button class="lesson-list-item ${index === state.lessonIndex ? "active" : ""}" data-lesson-index="${index}">
          <span>${index + 1}</span>
          <strong>${escapeHtml(lesson.title)}</strong>
        </button>
      `
    )
    .join("");
  $("#lessonNumber").textContent = `Lesson ${state.lessonIndex + 1} of ${beginnerLessons.length}`;
  $("#lessonTitle").textContent = activeLesson.title;
  $("#lessonGoal").innerHTML = thaiLookupText(activeLesson.goal);
  $("#lessonVocab").innerHTML = activeLesson.vocab
    .map(
      (word) => `
        <div class="lesson-vocab-card lookup-card" data-lookup="${escapeHtml(word.thai)}" tabindex="0">
          ${wordCard(word)}
        </div>
      `
    )
    .join("");
  $("#lessonPhrases").innerHTML = activeLesson.phrases
    .map(
      (phrase) => `
        <div class="phrase-card">
          <div class="thai-text">${thaiLookupText(phrase)}</div>
          <button class="icon-btn" data-phrase-speak="${escapeHtml(phrase)}" title="Play phrase" aria-label="Play phrase">▶</button>
        </div>
      `
    )
    .join("");
  $("#lessonPractice").innerHTML = activeLesson.practice.map((item) => `<div class="practice-item">${escapeHtml(item)}</div>`).join("");
}

function nextQuizQuestion() {
  const pool = state.words.length ? state.words : sampleWords;
  state.quizWord = pickRandom(pool);
  const word = state.quizWord;
  $("#quizCategory").textContent = word.category || "practice";
  $("#quizAnswer").value = "";
  $("#quizFeedback").textContent = "";
  if (state.quizMode === "thaiToEnglish") {
    $("#quizPrompt").innerHTML = thaiLookupText(word.thai);
    $("#quizSubprompt").textContent = word.romanization || "Translate this into English.";
  } else if (state.quizMode === "englishToThai") {
    $("#quizPrompt").textContent = word.english;
    $("#quizSubprompt").textContent = "Type the Thai script or romanization.";
  } else {
    $("#quizPrompt").textContent = "Listen first";
    $("#quizSubprompt").textContent = "Type the English meaning.";
    speak(word.thai);
  }
}

function checkQuizAnswer() {
  if (!state.quizWord) return;
  const answer = normalize($("#quizAnswer").value);
  const word = state.quizWord;
  const accepted =
    state.quizMode === "englishToThai"
      ? [word.thai, word.romanization].map(normalize)
      : [word.english].map(normalize);
  const isCorrect = accepted.some((value) => answer === value || (value.length > 4 && answer.includes(value)));
  if (isCorrect) {
    state.correct += 1;
    $("#quizFeedback").textContent = `Correct: ${word.thai} means ${word.english}.`;
  } else {
    $("#quizFeedback").textContent = `Close practice moment: ${word.thai} (${word.romanization}) means ${word.english}.`;
  }
  state.sessions += 1;
  save();
}

function renderConversation(reset = false) {
  if (reset) {
    state.scenarioStep = 0;
    $("#chatLog").innerHTML = "";
  }
  const scenario = scenarios[$("#scenarioSelect").value];
  const line = scenario[state.scenarioStep % scenario.length];
  $("#chatLog").insertAdjacentHTML(
    "beforeend",
    `<div class="chat-message coach">
      <strong>Coach</strong>
      <div class="thai-text">${thaiLookupText(line.thai)}</div>
      <div class="romanization">${escapeHtml(line.romanization)}</div>
      <div>${escapeHtml(line.english)}</div>
    </div>`
  );
  $("#chatLog").scrollTop = $("#chatLog").scrollHeight;
}

function replyToConversation(reply) {
  if (!reply.trim()) return;
  const scenario = scenarios[$("#scenarioSelect").value];
  const line = scenario[state.scenarioStep % scenario.length];
  $("#chatLog").insertAdjacentHTML("beforeend", `<div class="chat-message learner"><strong>You</strong><div>${escapeHtml(reply)}</div></div>`);
  const encouragement = reply.match(/[ก-๙]/)
    ? "Nice, you used Thai script. Try saying it once more slowly."
    : "Good. For an extra rep, try answering with one Thai word from your vocab bank.";
  $("#chatLog").insertAdjacentHTML(
    "beforeend",
    `<div class="chat-message coach"><strong>Coach note</strong><div>${encouragement}</div><div class="hint">Useful answer: ${thaiLookupText(line.thai)}</div></div>`
  );
  state.scenarioStep += 1;
  state.sessions += 1;
  save();
  renderConversation();
}

function lastCoachThai() {
  const messages = [...document.querySelectorAll(".chat-message.coach .thai-text")];
  return messages.length ? messages[messages.length - 1].textContent.replace(/▶/g, "") : "";
}

function renderClip() {
  $("#clipLevel").textContent = state.clip.level;
  $("#clipThai").innerHTML = thaiLookupText(state.clip.thai);
  $("#clipRomanization").textContent = state.clip.romanization;
  $("#clipFeedback").textContent = "";
  const wrong = listeningClips.filter((clip) => clip.english !== state.clip.english).sort(() => Math.random() - 0.5).slice(0, 3);
  const choices = [state.clip, ...wrong].sort(() => Math.random() - 0.5);
  $("#clipChoices").innerHTML = choices
    .map((clip) => `<button data-clip-answer="${clip.english}">${clip.english}</button>`)
    .join("");
}

function analyzeHomework(makePractice = false) {
  const text = $("#homeworkInput").value.trim();
  const words = state.words.length ? state.words : sampleWords;
  const matches = words.filter((word) => text.includes(word.thai) || normalize(text).includes(normalize(word.english))).slice(0, 8);
  const thaiChunks = text.match(/[ก-๙]+/g) || [];
  const output = [];
  if (!text) {
    $("#homeworkOutput").innerHTML = "Paste an exercise first, then I can break it into vocabulary, sentence patterns, and practice prompts.";
    return;
  }
  output.push(`<p><strong>What I notice</strong></p>`);
  output.push(`<ul>`);
  output.push(`<li>${thaiChunks.length ? `Thai text found: ${thaiLookupText(thaiChunks.slice(0, 8).join(", "))}` : "No Thai script found yet."}</li>`);
  output.push(`<li>${matches.length ? `Matched your vocab: ${matches.map((word) => `${thaiLookupText(word.thai)} = ${escapeHtml(word.english)}`).join("; ")}` : "No saved vocab matches yet."}</li>`);
  output.push(`<li>Try reading once for meaning, once for sound, then once out loud at half speed.</li>`);
  output.push(`</ul>`);
  output.push(`<p><strong>Step-by-step</strong></p>`);
  output.push(`<ul>`);
  output.push(`<li>Circle familiar words and mark unknown words.</li>`);
  output.push(`<li>Identify the sentence job: greeting, question, request, description, or answer.</li>`);
  output.push(`<li>Write a literal translation first, then a natural English translation.</li>`);
  output.push(`</ul>`);
  if (makePractice) {
    output.push(`<p><strong>Practice prompts</strong></p>`);
    output.push(`<ul>`);
    matches.slice(0, 4).forEach((word) => output.push(`<li>Use ${word.thai} in a short sentence.</li>`));
    output.push(`<li>Record yourself reading the sentence slowly, then repeat at normal speed.</li>`);
    output.push(`</ul>`);
  }
  $("#homeworkOutput").innerHTML = output.join("");
}

document.addEventListener("click", (event) => {
  const lookupTarget = event.target.closest("[data-lookup]");
  if (lookupTarget) {
    showLookup(lookupTarget.dataset.lookup, lookupTarget);
    if (lookupTarget.matches(".lookup-word")) event.stopPropagation();
    return;
  }

  const target = event.target.closest("button");
  if (!target) return;

  if (target.matches(".nav-tab")) {
    $$(".nav-tab").forEach((tab) => tab.classList.remove("active"));
    $$(".view").forEach((view) => view.classList.remove("active"));
    target.classList.add("active");
    $(`#${target.dataset.view}`).classList.add("active");
  }

  if (target.dataset.jump) {
    $(`.nav-tab[data-view="${target.dataset.jump}"]`).click();
  }

  if (target.id === "loadSample") addWords(sampleWords);
  if (target.dataset.lessonIndex) {
    state.lessonIndex = Number(target.dataset.lessonIndex);
    save();
  }
  if (target.id === "previousLesson") {
    state.lessonIndex = (state.lessonIndex - 1 + beginnerLessons.length) % beginnerLessons.length;
    save();
  }
  if (target.id === "nextLesson") {
    state.lessonIndex = (state.lessonIndex + 1) % beginnerLessons.length;
    save();
  }
  if (target.id === "shuffleQueue") {
    state.words = state.words.sort(() => Math.random() - 0.5);
    save();
  }
  if (target.id === "clearWords" && confirm("Clear all saved words?")) {
    state.words = [];
    save();
  }
  if (target.dataset.deleteWord) {
    state.words.splice(Number(target.dataset.deleteWord), 1);
    save();
  }
  if (target.dataset.speakWord) speak(state.words[Number(target.dataset.speakWord)].thai);
  if (target.dataset.builderSpeak) speak(target.dataset.builderSpeak);
  if (target.dataset.phraseSpeak) speak(target.dataset.phraseSpeak);
  if (target.dataset.popoverSpeak) speak(target.dataset.popoverSpeak);
  if (target.dataset.quizMode) {
    state.quizMode = target.dataset.quizMode;
    $$(".segmented button").forEach((button) => button.classList.toggle("active", button === target));
    nextQuizQuestion();
  }
  if (target.id === "speakQuiz" && state.quizWord) speak(state.quizWord.thai);
  if (target.id === "checkAnswer") checkQuizAnswer();
  if (target.id === "nextQuestion") nextQuizQuestion();
  if (target.id === "conversationSpeak") speak(lastCoachThai());
  if (target.id === "slowSpeak") speak(lastCoachThai(), 0.48);
  if (target.id === "hintButton") {
    const scenario = scenarios[$("#scenarioSelect").value];
    const line = scenario[state.scenarioStep % scenario.length];
    $("#replyInput").value = line.romanization;
    $("#replyInput").focus();
  }
  if (target.id === "newClip") {
    state.clip = pickRandom(listeningClips);
    renderClip();
  }
  if (target.id === "playClip") speak(state.clip.thai);
  if (target.dataset.clipAnswer) {
    const correct = target.dataset.clipAnswer === state.clip.english;
    target.classList.add(correct ? "correct" : "wrong");
    $("#clipFeedback").textContent = correct
      ? `Correct. ${state.clip.thai} means ${state.clip.english}.`
      : `Listen again: ${state.clip.thai} means ${state.clip.english}.`;
    if (correct) state.correct += 1;
    state.sessions += 1;
    save();
  }
  if (target.id === "analyzeHomework") analyzeHomework(false);
  if (target.id === "makePractice") analyzeHomework(true);
  if (target.id === "useVocabInHomework") {
    $("#homeworkInput").value = state.words.slice(0, 6).map((word) => `${word.thai} = ${word.english}`).join("\n");
    analyzeHomework(true);
  }
});

document.addEventListener("pointerover", (event) => {
  const lookupTarget = event.target.closest("[data-lookup]");
  if (lookupTarget) showLookup(lookupTarget.dataset.lookup, lookupTarget);
});

document.addEventListener("pointerdown", (event) => {
  if (!event.target.closest("[data-lookup], #lookupPopover")) hideLookup();
});

$("#wordForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  addWords([
    {
      thai: formData.get("thai"),
      romanization: formData.get("romanization"),
      english: formData.get("english"),
      category: formData.get("category") || "custom",
      notes: formData.get("notes") || ""
    }
  ]);
  event.currentTarget.reset();
});

$("#importPaste").addEventListener("click", () => addWords(parseRows($("#pasteBox").value)));

$("#fileInput").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  addWords(parseRows(await file.text()));
  event.target.value = "";
});

$("#replyForm").addEventListener("submit", (event) => {
  event.preventDefault();
  replyToConversation($("#replyInput").value);
  $("#replyInput").value = "";
});

$("#scenarioSelect").addEventListener("change", () => renderConversation(true));

render();
renderConversation(true);
renderClip();
