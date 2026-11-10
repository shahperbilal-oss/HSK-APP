"""Canonical HSK 1-4 grammar points.

This module is the single source of truth for the grammar section. Each point
carries a short explanation, a longer note on how it behaves, and five real
example sentences - no filler. ``import_grammar`` writes this list into the
database and can prune anything that is no longer listed here.

Keys per point:
    level                 HSK level, 1-4
    title                 unique within a level; shown as the heading
    explanation           one line, shown in the list view
    detailed_explanation  a paragraph on usage, including common mistakes
    examples              exactly five {cn, pinyin, en} sentences
"""

HSK1 = [
    {
        "level": 1,
        "title": "是 (shì) for identification",
        "explanation": "Links a subject to a noun: 'A is B'.",
        "detailed_explanation": (
            "是 connects two nouns or noun phrases to say what something is. "
            "Do not use it before an adjective - Chinese says 我很忙 (I am busy), "
            "never 我是忙. Negate with 不是."
        ),
        "examples": [
            {"cn": "我是学生。", "pinyin": "Wǒ shì xuésheng.", "en": "I am a student."},
            {"cn": "他是我的老师。", "pinyin": "Tā shì wǒ de lǎoshī.", "en": "He is my teacher."},
            {"cn": "这是我的书。", "pinyin": "Zhè shì wǒ de shū.", "en": "This is my book."},
            {"cn": "她不是医生。", "pinyin": "Tā bú shì yīshēng.", "en": "She is not a doctor."},
            {"cn": "你是中国人吗？", "pinyin": "Nǐ shì Zhōngguórén ma?", "en": "Are you Chinese?"},
        ],
    },
    {
        "level": 1,
        "title": "有 (yǒu) for possession and existence",
        "explanation": "Expresses 'to have' or 'there is/are'.",
        "detailed_explanation": (
            "有 states that someone owns something, or that something exists in a "
            "place. Its negative is 没有, never 不有."
        ),
        "examples": [
            {"cn": "我有一本汉语书。", "pinyin": "Wǒ yǒu yì běn Hànyǔ shū.", "en": "I have a Chinese book."},
            {"cn": "她有两个哥哥。", "pinyin": "Tā yǒu liǎng gè gēge.", "en": "She has two older brothers."},
            {"cn": "桌子上有一杯水。", "pinyin": "Zhuōzi shàng yǒu yì bēi shuǐ.", "en": "There is a glass of water on the table."},
            {"cn": "我没有钱。", "pinyin": "Wǒ méiyǒu qián.", "en": "I don't have money."},
            {"cn": "你有没有时间？", "pinyin": "Nǐ yǒu méi yǒu shíjiān?", "en": "Do you have time?"},
        ],
    },
    {
        "level": 1,
        "title": "不 (bù) for negation",
        "explanation": "Negates verbs and adjectives in the present or future.",
        "detailed_explanation": (
            "不 goes directly before the verb or adjective. It covers habits, "
            "opinions and future plans. For a past action that did not happen, use "
            "没 instead. Before a fourth-tone syllable 不 is pronounced bú."
        ),
        "examples": [
            {"cn": "我不喝咖啡。", "pinyin": "Wǒ bù hē kāfēi.", "en": "I don't drink coffee."},
            {"cn": "今天不冷。", "pinyin": "Jīntiān bù lěng.", "en": "It isn't cold today."},
            {"cn": "他不去学校。", "pinyin": "Tā bú qù xuéxiào.", "en": "He isn't going to school."},
            {"cn": "这个菜不好吃。", "pinyin": "Zhège cài bù hǎochī.", "en": "This dish doesn't taste good."},
            {"cn": "我不想睡觉。", "pinyin": "Wǒ bù xiǎng shuìjiào.", "en": "I don't want to sleep."},
        ],
    },
    {
        "level": 1,
        "title": "吗 (ma) for yes/no questions",
        "explanation": "Turns a statement into a yes/no question.",
        "detailed_explanation": (
            "Add 吗 to the end of a normal statement and the word order stays the "
            "same. Do not use 吗 together with a question word such as 什么 or 谁."
        ),
        "examples": [
            {"cn": "你是老师吗？", "pinyin": "Nǐ shì lǎoshī ma?", "en": "Are you a teacher?"},
            {"cn": "你喜欢中国菜吗？", "pinyin": "Nǐ xǐhuan Zhōngguó cài ma?", "en": "Do you like Chinese food?"},
            {"cn": "他在家吗？", "pinyin": "Tā zài jiā ma?", "en": "Is he at home?"},
            {"cn": "今天热吗？", "pinyin": "Jīntiān rè ma?", "en": "Is it hot today?"},
            {"cn": "你会说汉语吗？", "pinyin": "Nǐ huì shuō Hànyǔ ma?", "en": "Can you speak Chinese?"},
        ],
    },
    {
        "level": 1,
        "title": "呢 (ne) for follow-up questions",
        "explanation": "Asks 'and what about...?' without repeating the sentence.",
        "detailed_explanation": (
            "呢 follows a noun or pronoun to bounce the same question back. It also "
            "softens a question about where something is, as in 我的书呢？"
        ),
        "examples": [
            {"cn": "我是学生，你呢？", "pinyin": "Wǒ shì xuésheng, nǐ ne?", "en": "I'm a student, what about you?"},
            {"cn": "我喜欢咖啡，你呢？", "pinyin": "Wǒ xǐhuan kāfēi, nǐ ne?", "en": "I like coffee, and you?"},
            {"cn": "我的手机呢？", "pinyin": "Wǒ de shǒujī ne?", "en": "Where is my phone?"},
            {"cn": "他很好，你的家人呢？", "pinyin": "Tā hěn hǎo, nǐ de jiārén ne?", "en": "He's fine; how about your family?"},
            {"cn": "今天很忙，明天呢？", "pinyin": "Jīntiān hěn máng, míngtiān ne?", "en": "Today is busy; what about tomorrow?"},
        ],
    },
    {
        "level": 1,
        "title": "的 (de) for possession and description",
        "explanation": "Joins a modifier to the noun it describes.",
        "detailed_explanation": (
            "的 marks whatever comes before it as a description of the noun that "
            "follows. With close relationships such as family or friends it is "
            "often dropped: 我妈妈, 我朋友."
        ),
        "examples": [
            {"cn": "这是我的书。", "pinyin": "Zhè shì wǒ de shū.", "en": "This is my book."},
            {"cn": "他是我朋友的哥哥。", "pinyin": "Tā shì wǒ péngyou de gēge.", "en": "He is my friend's older brother."},
            {"cn": "我喜欢红色的衣服。", "pinyin": "Wǒ xǐhuan hóngsè de yīfu.", "en": "I like red clothes."},
            {"cn": "那是老师的车。", "pinyin": "Nà shì lǎoshī de chē.", "en": "That is the teacher's car."},
            {"cn": "这是很好吃的菜。", "pinyin": "Zhè shì hěn hǎochī de cài.", "en": "This is a very tasty dish."},
        ],
    },
    {
        "level": 1,
        "title": "在 (zài) for location",
        "explanation": "Says where someone or something is.",
        "detailed_explanation": (
            "As a verb, 在 means 'to be at' and is followed by a place. As a "
            "preposition it comes before the place and in front of the main verb: "
            "我在家吃饭."
        ),
        "examples": [
            {"cn": "我在家。", "pinyin": "Wǒ zài jiā.", "en": "I am at home."},
            {"cn": "他在学校学习。", "pinyin": "Tā zài xuéxiào xuéxí.", "en": "He studies at school."},
            {"cn": "书在桌子上。", "pinyin": "Shū zài zhuōzi shàng.", "en": "The book is on the table."},
            {"cn": "妈妈在厨房做饭。", "pinyin": "Māma zài chúfáng zuò fàn.", "en": "Mom is cooking in the kitchen."},
            {"cn": "你在哪儿？", "pinyin": "Nǐ zài nǎr?", "en": "Where are you?"},
        ],
    },
    {
        "level": 1,
        "title": "会 (huì) for learned ability",
        "explanation": "Expresses a skill you have learned.",
        "detailed_explanation": (
            "会 is for abilities gained through study or practice, such as languages "
            "or driving. For physical capability or permission in the moment, use 能 "
            "or 可以 instead."
        ),
        "examples": [
            {"cn": "我会说汉语。", "pinyin": "Wǒ huì shuō Hànyǔ.", "en": "I can speak Chinese."},
            {"cn": "她会开车。", "pinyin": "Tā huì kāichē.", "en": "She can drive."},
            {"cn": "我不会做饭。", "pinyin": "Wǒ bú huì zuò fàn.", "en": "I can't cook."},
            {"cn": "你会写汉字吗？", "pinyin": "Nǐ huì xiě Hànzì ma?", "en": "Can you write Chinese characters?"},
            {"cn": "他会打篮球。", "pinyin": "Tā huì dǎ lánqiú.", "en": "He can play basketball."},
        ],
    },
    {
        "level": 1,
        "title": "想 (xiǎng) for wanting to do something",
        "explanation": "Expresses a wish or intention: 'would like to'.",
        "detailed_explanation": (
            "想 comes before a verb to say what you feel like doing. On its own it "
            "also means 'to miss someone'. 要 is stronger and closer to a decision."
        ),
        "examples": [
            {"cn": "我想喝水。", "pinyin": "Wǒ xiǎng hē shuǐ.", "en": "I want to drink water."},
            {"cn": "他想去中国。", "pinyin": "Tā xiǎng qù Zhōngguó.", "en": "He wants to go to China."},
            {"cn": "我不想工作。", "pinyin": "Wǒ bù xiǎng gōngzuò.", "en": "I don't want to work."},
            {"cn": "你想吃什么？", "pinyin": "Nǐ xiǎng chī shénme?", "en": "What would you like to eat?"},
            {"cn": "我很想我的家人。", "pinyin": "Wǒ hěn xiǎng wǒ de jiārén.", "en": "I miss my family very much."},
        ],
    },
    {
        "level": 1,
        "title": "也 (yě) and 都 (dōu)",
        "explanation": "'Also' and 'all' - both go before the verb.",
        "detailed_explanation": (
            "也 and 都 are adverbs, so they sit after the subject and before the "
            "verb, never at the start of the sentence. When both appear, the order "
            "is 也都."
        ),
        "examples": [
            {"cn": "我也是学生。", "pinyin": "Wǒ yě shì xuésheng.", "en": "I am a student too."},
            {"cn": "他也喜欢音乐。", "pinyin": "Tā yě xǐhuan yīnyuè.", "en": "He likes music as well."},
            {"cn": "我们都是中国人。", "pinyin": "Wǒmen dōu shì Zhōngguórén.", "en": "We are all Chinese."},
            {"cn": "他们都很忙。", "pinyin": "Tāmen dōu hěn máng.", "en": "They are all busy."},
            {"cn": "我们也都去。", "pinyin": "Wǒmen yě dōu qù.", "en": "We are all going too."},
        ],
    },
    {
        "level": 1,
        "title": "很 (hěn) with adjectives",
        "explanation": "Adjectives act as the verb; 很 fills the linking slot.",
        "detailed_explanation": (
            "Chinese does not use 是 before adjectives. A bare adjective sounds like "
            "a comparison, so 很 is added as a neutral filler - 我很好 usually means "
            "simply 'I'm fine', not 'I'm very well'."
        ),
        "examples": [
            {"cn": "我很好。", "pinyin": "Wǒ hěn hǎo.", "en": "I am fine."},
            {"cn": "今天很热。", "pinyin": "Jīntiān hěn rè.", "en": "It is hot today."},
            {"cn": "这个菜很好吃。", "pinyin": "Zhège cài hěn hǎochī.", "en": "This dish is delicious."},
            {"cn": "他很忙。", "pinyin": "Tā hěn máng.", "en": "He is busy."},
            {"cn": "我的房间很大。", "pinyin": "Wǒ de fángjiān hěn dà.", "en": "My room is big."},
        ],
    },
    {
        "level": 1,
        "title": "Measure words (一个, 一本, 一杯)",
        "explanation": "A number needs a measure word before the noun.",
        "detailed_explanation": (
            "Chinese counts nouns with a classifier: number + measure word + noun. "
            "个 is the general one; books take 本, flat things 张, cups of liquid 杯. "
            "Use 两 rather than 二 when counting things."
        ),
        "examples": [
            {"cn": "我有一个哥哥。", "pinyin": "Wǒ yǒu yí gè gēge.", "en": "I have one older brother."},
            {"cn": "他买了三本书。", "pinyin": "Tā mǎi le sān běn shū.", "en": "He bought three books."},
            {"cn": "请给我一杯水。", "pinyin": "Qǐng gěi wǒ yì bēi shuǐ.", "en": "Please give me a glass of water."},
            {"cn": "桌子上有两张纸。", "pinyin": "Zhuōzi shàng yǒu liǎng zhāng zhǐ.", "en": "There are two sheets of paper on the table."},
            {"cn": "我们班有二十个学生。", "pinyin": "Wǒmen bān yǒu èrshí gè xuésheng.", "en": "There are twenty students in our class."},
        ],
    },
    {
        "level": 1,
        "title": "Question words (什么, 谁, 哪儿, 几)",
        "explanation": "Ask by replacing the unknown word - the order stays the same.",
        "detailed_explanation": (
            "Chinese does not move question words to the front. Put 什么, 谁, 哪儿 or "
            "几 exactly where the answer would go, and do not add 吗."
        ),
        "examples": [
            {"cn": "你叫什么名字？", "pinyin": "Nǐ jiào shénme míngzi?", "en": "What is your name?"},
            {"cn": "他是谁？", "pinyin": "Tā shì shéi?", "en": "Who is he?"},
            {"cn": "你去哪儿？", "pinyin": "Nǐ qù nǎr?", "en": "Where are you going?"},
            {"cn": "你有几个孩子？", "pinyin": "Nǐ yǒu jǐ gè háizi?", "en": "How many children do you have?"},
            {"cn": "现在几点？", "pinyin": "Xiànzài jǐ diǎn?", "en": "What time is it now?"},
        ],
    },
    {
        "level": 1,
        "title": "Time and place before the verb",
        "explanation": "Chinese word order: subject + time + place + verb.",
        "detailed_explanation": (
            "Unlike English, time and place phrases come before the verb, not after "
            "it. Say 我明天在家看书, never 我看书在家明天. Time can also start the "
            "sentence for emphasis."
        ),
        "examples": [
            {"cn": "我明天去北京。", "pinyin": "Wǒ míngtiān qù Běijīng.", "en": "I am going to Beijing tomorrow."},
            {"cn": "他每天早上跑步。", "pinyin": "Tā měitiān zǎoshang pǎobù.", "en": "He runs every morning."},
            {"cn": "我们在教室上课。", "pinyin": "Wǒmen zài jiàoshì shàngkè.", "en": "We have class in the classroom."},
            {"cn": "明天我不工作。", "pinyin": "Míngtiān wǒ bù gōngzuò.", "en": "I don't work tomorrow."},
            {"cn": "她晚上在家看电视。", "pinyin": "Tā wǎnshang zài jiā kàn diànshì.", "en": "She watches TV at home in the evening."},
        ],
    },
]

HSK2 = [
    {
        "level": 2,
        "title": "了 (le) for completed actions",
        "explanation": "Marks an action as finished.",
        "detailed_explanation": (
            "了 after the verb shows the action was completed. The negative drops 了 "
            "and uses 没(有): 我没去. 了 is not a past tense - it can mark completion "
            "in the future as well."
        ),
        "examples": [
            {"cn": "我吃了早饭。", "pinyin": "Wǒ chī le zǎofàn.", "en": "I ate breakfast."},
            {"cn": "他买了一件衣服。", "pinyin": "Tā mǎi le yí jiàn yīfu.", "en": "He bought a piece of clothing."},
            {"cn": "我昨天看了一部电影。", "pinyin": "Wǒ zuótiān kàn le yí bù diànyǐng.", "en": "I watched a film yesterday."},
            {"cn": "我没去商店。", "pinyin": "Wǒ méi qù shāngdiàn.", "en": "I didn't go to the shop."},
            {"cn": "下课了，我们走吧。", "pinyin": "Xiàkè le, wǒmen zǒu ba.", "en": "Class is over; let's go."},
        ],
    },
    {
        "level": 2,
        "title": "正在 / 在…呢 for ongoing actions",
        "explanation": "Says an action is happening right now.",
        "detailed_explanation": (
            "Put 正在 or 在 before the verb, and optionally 呢 at the end. All three "
            "can combine: 他正在打电话呢. Negate with 没在."
        ),
        "examples": [
            {"cn": "我正在吃饭。", "pinyin": "Wǒ zhèngzài chī fàn.", "en": "I am eating right now."},
            {"cn": "他在看电视呢。", "pinyin": "Tā zài kàn diànshì ne.", "en": "He is watching TV."},
            {"cn": "妈妈正在做饭。", "pinyin": "Māma zhèngzài zuò fàn.", "en": "Mom is cooking."},
            {"cn": "你在做什么呢？", "pinyin": "Nǐ zài zuò shénme ne?", "en": "What are you doing?"},
            {"cn": "他们正在开会。", "pinyin": "Tāmen zhèngzài kāihuì.", "en": "They are in a meeting."},
        ],
    },
    {
        "level": 2,
        "title": "过 (guò) for past experience",
        "explanation": "Says you have done something at least once.",
        "detailed_explanation": (
            "过 after the verb reports experience rather than a specific finished "
            "event. The negative is 没…过, and 过 stays in place: 我没去过日本."
        ),
        "examples": [
            {"cn": "我去过中国。", "pinyin": "Wǒ qù guo Zhōngguó.", "en": "I have been to China."},
            {"cn": "他吃过北京烤鸭。", "pinyin": "Tā chī guo Běijīng kǎoyā.", "en": "He has eaten Beijing duck."},
            {"cn": "我没看过这部电影。", "pinyin": "Wǒ méi kàn guo zhè bù diànyǐng.", "en": "I haven't seen this film."},
            {"cn": "你学过汉语吗？", "pinyin": "Nǐ xué guo Hànyǔ ma?", "en": "Have you ever studied Chinese?"},
            {"cn": "我们见过一次面。", "pinyin": "Wǒmen jiàn guo yí cì miàn.", "en": "We have met once."},
        ],
    },
    {
        "level": 2,
        "title": "要 (yào) for plans and needs",
        "explanation": "'Will', 'want' or 'need to', depending on context.",
        "detailed_explanation": (
            "要 before a verb marks a firm intention or a near-future event. Its "
            "negative depends on meaning: 不想 for 'don't want', 不用 for 'need not'. "
            "不要 is a command meaning 'don't'."
        ),
        "examples": [
            {"cn": "我要去银行。", "pinyin": "Wǒ yào qù yínháng.", "en": "I am going to the bank."},
            {"cn": "他要买一台电脑。", "pinyin": "Tā yào mǎi yì tái diànnǎo.", "en": "He wants to buy a computer."},
            {"cn": "快要下雨了。", "pinyin": "Kuài yào xià yǔ le.", "en": "It is about to rain."},
            {"cn": "你不要走这么快。", "pinyin": "Nǐ bú yào zǒu zhème kuài.", "en": "Don't walk so fast."},
            {"cn": "明天我要早起。", "pinyin": "Míngtiān wǒ yào zǎo qǐ.", "en": "I have to get up early tomorrow."},
        ],
    },
    {
        "level": 2,
        "title": "能 (néng) and 可以 (kěyǐ)",
        "explanation": "Ability in the moment, and permission.",
        "detailed_explanation": (
            "能 covers physical capability or circumstances allowing something; 可以 "
            "leans towards permission. Compare with 会, which is about a learned "
            "skill. A common refusal is 不能."
        ),
        "examples": [
            {"cn": "我今天不能来。", "pinyin": "Wǒ jīntiān bù néng lái.", "en": "I can't come today."},
            {"cn": "你可以用我的电脑。", "pinyin": "Nǐ kěyǐ yòng wǒ de diànnǎo.", "en": "You may use my computer."},
            {"cn": "这里可以吸烟吗？", "pinyin": "Zhèlǐ kěyǐ xīyān ma?", "en": "Is smoking allowed here?"},
            {"cn": "他能跑十公里。", "pinyin": "Tā néng pǎo shí gōnglǐ.", "en": "He can run ten kilometres."},
            {"cn": "我可以问一个问题吗？", "pinyin": "Wǒ kěyǐ wèn yí gè wèntí ma?", "en": "May I ask a question?"},
        ],
    },
    {
        "level": 2,
        "title": "因为…所以… (cause and result)",
        "explanation": "Connects a reason with its result.",
        "detailed_explanation": (
            "Unlike English, Chinese keeps both halves: 因为 introduces the reason "
            "and 所以 the result. Either word may be dropped, but not replaced by a "
            "comma alone in careful writing."
        ),
        "examples": [
            {"cn": "因为下雨，所以我没去。", "pinyin": "Yīnwèi xià yǔ, suǒyǐ wǒ méi qù.", "en": "Because it rained, I didn't go."},
            {"cn": "因为他很忙，所以没来。", "pinyin": "Yīnwèi tā hěn máng, suǒyǐ méi lái.", "en": "He didn't come because he was busy."},
            {"cn": "因为很便宜，所以我买了两个。", "pinyin": "Yīnwèi hěn piányi, suǒyǐ wǒ mǎi le liǎng gè.", "en": "It was cheap, so I bought two."},
            {"cn": "我没吃饭，因为不饿。", "pinyin": "Wǒ méi chī fàn, yīnwèi bú è.", "en": "I didn't eat because I wasn't hungry."},
            {"cn": "因为身体不舒服，所以他请假了。", "pinyin": "Yīnwèi shēntǐ bù shūfu, suǒyǐ tā qǐngjià le.", "en": "He took leave because he felt unwell."},
        ],
    },
    {
        "level": 2,
        "title": "虽然…但是… (concession)",
        "explanation": "'Although... still...' - both halves are kept.",
        "detailed_explanation": (
            "Chinese keeps 但是 (or 可是) in the second clause even though English "
            "drops 'but' after 'although'. 虽然 can come before or after the subject."
        ),
        "examples": [
            {"cn": "虽然很累，但是我很开心。", "pinyin": "Suīrán hěn lèi, dànshì wǒ hěn kāixīn.", "en": "Although I'm tired, I'm happy."},
            {"cn": "虽然下雨，但是他还是来了。", "pinyin": "Suīrán xià yǔ, dànshì tā háishi lái le.", "en": "Although it rained, he still came."},
            {"cn": "这个房子虽然小，但是很干净。", "pinyin": "Zhège fángzi suīrán xiǎo, dànshì hěn gānjìng.", "en": "Although this house is small, it is clean."},
            {"cn": "虽然他很年轻，但是很有经验。", "pinyin": "Suīrán tā hěn niánqīng, dànshì hěn yǒu jīngyàn.", "en": "Although he is young, he is experienced."},
            {"cn": "虽然我学了两年，可是说得还不好。", "pinyin": "Suīrán wǒ xué le liǎng nián, kěshì shuō de hái bù hǎo.", "en": "Although I've studied two years, I still don't speak well."},
        ],
    },
    {
        "level": 2,
        "title": "比 (bǐ) for comparison",
        "explanation": "'A is more ... than B'.",
        "detailed_explanation": (
            "The pattern is A + 比 + B + adjective. Never add 很 or 非常 to the "
            "adjective; use 更 or 还 for 'even more', and put amounts after the "
            "adjective: 大三岁."
        ),
        "examples": [
            {"cn": "他比我高。", "pinyin": "Tā bǐ wǒ gāo.", "en": "He is taller than me."},
            {"cn": "今天比昨天热。", "pinyin": "Jīntiān bǐ zuótiān rè.", "en": "Today is hotter than yesterday."},
            {"cn": "这个比那个便宜。", "pinyin": "Zhège bǐ nàge piányi.", "en": "This one is cheaper than that one."},
            {"cn": "他比我大三岁。", "pinyin": "Tā bǐ wǒ dà sān suì.", "en": "He is three years older than me."},
            {"cn": "坐地铁比开车更快。", "pinyin": "Zuò dìtiě bǐ kāichē gèng kuài.", "en": "Taking the subway is even faster than driving."},
        ],
    },
    {
        "level": 2,
        "title": "得 (de) for degree complements",
        "explanation": "Describes how well an action is performed.",
        "detailed_explanation": (
            "Verb + 得 + adjective comments on the quality of an action. If the verb "
            "takes an object, repeat the verb: 他说汉语说得很好. Negate the adjective, "
            "not the verb: 说得不好."
        ),
        "examples": [
            {"cn": "他跑得很快。", "pinyin": "Tā pǎo de hěn kuài.", "en": "He runs fast."},
            {"cn": "你说得很好。", "pinyin": "Nǐ shuō de hěn hǎo.", "en": "You speak very well."},
            {"cn": "她唱歌唱得很好听。", "pinyin": "Tā chànggē chàng de hěn hǎotīng.", "en": "She sings beautifully."},
            {"cn": "我昨天睡得不好。", "pinyin": "Wǒ zuótiān shuì de bù hǎo.", "en": "I didn't sleep well yesterday."},
            {"cn": "他来得太晚了。", "pinyin": "Tā lái de tài wǎn le.", "en": "He came too late."},
        ],
    },
    {
        "level": 2,
        "title": "就 (jiù) and 才 (cái)",
        "explanation": "'Sooner than expected' versus 'later than expected'.",
        "detailed_explanation": (
            "就 suggests something happened early, quickly or as a matter of course; "
            "才 suggests it took longer or more effort than expected. 才 sentences "
            "normally do not take 了."
        ),
        "examples": [
            {"cn": "他六点就起床了。", "pinyin": "Tā liù diǎn jiù qǐchuáng le.", "en": "He got up as early as six."},
            {"cn": "他十点才起床。", "pinyin": "Tā shí diǎn cái qǐchuáng.", "en": "He didn't get up until ten."},
            {"cn": "我吃完饭就去。", "pinyin": "Wǒ chī wán fàn jiù qù.", "en": "I'll go as soon as I finish eating."},
            {"cn": "我等了一个小时他才来。", "pinyin": "Wǒ děng le yí gè xiǎoshí tā cái lái.", "en": "I waited an hour before he came."},
            {"cn": "这个问题很简单，我一看就懂。", "pinyin": "Zhège wèntí hěn jiǎndān, wǒ yí kàn jiù dǒng.", "en": "This question is easy; I understood at a glance."},
        ],
    },
    {
        "level": 2,
        "title": "有点儿 and 一点儿",
        "explanation": "'A bit' before an adjective versus after it.",
        "detailed_explanation": (
            "有点儿 goes before an adjective and usually carries a complaint: "
            "有点儿贵. 一点儿 follows an adjective in comparisons (便宜一点儿) or "
            "quantifies a noun (一点儿水)."
        ),
        "examples": [
            {"cn": "这件衣服有点儿贵。", "pinyin": "Zhè jiàn yīfu yǒudiǎnr guì.", "en": "This piece of clothing is a bit expensive."},
            {"cn": "便宜一点儿可以吗？", "pinyin": "Piányi yìdiǎnr kěyǐ ma?", "en": "Could you make it a bit cheaper?"},
            {"cn": "我今天有点儿累。", "pinyin": "Wǒ jīntiān yǒudiǎnr lèi.", "en": "I'm a little tired today."},
            {"cn": "请给我一点儿水。", "pinyin": "Qǐng gěi wǒ yìdiǎnr shuǐ.", "en": "Please give me a little water."},
            {"cn": "今天比昨天冷一点儿。", "pinyin": "Jīntiān bǐ zuótiān lěng yìdiǎnr.", "en": "Today is a little colder than yesterday."},
        ],
    },
    {
        "level": 2,
        "title": "从…到… and 离 (lí)",
        "explanation": "Ranges in time or space, and distance between two points.",
        "detailed_explanation": (
            "从…到… frames a span: from a start point to an end point. 离 states how "
            "far one place is from another and is followed by 近 or 远."
        ),
        "examples": [
            {"cn": "我从八点到五点上班。", "pinyin": "Wǒ cóng bā diǎn dào wǔ diǎn shàngbān.", "en": "I work from eight to five."},
            {"cn": "从我家到学校很近。", "pinyin": "Cóng wǒ jiā dào xuéxiào hěn jìn.", "en": "It's close from my home to school."},
            {"cn": "我家离公司很远。", "pinyin": "Wǒ jiā lí gōngsī hěn yuǎn.", "en": "My home is far from the company."},
            {"cn": "银行离这儿不远。", "pinyin": "Yínháng lí zhèr bù yuǎn.", "en": "The bank isn't far from here."},
            {"cn": "从这儿到机场要一个小时。", "pinyin": "Cóng zhèr dào jīchǎng yào yí gè xiǎoshí.", "en": "It takes an hour from here to the airport."},
        ],
    },
    {
        "level": 2,
        "title": "给 (gěi) for the recipient",
        "explanation": "Marks who receives the action.",
        "detailed_explanation": (
            "As a verb 给 means 'to give'. As a preposition it comes before the verb "
            "to mark the person who benefits: 我给你打电话."
        ),
        "examples": [
            {"cn": "我给你打电话。", "pinyin": "Wǒ gěi nǐ dǎ diànhuà.", "en": "I'll call you."},
            {"cn": "他给我买了一本书。", "pinyin": "Tā gěi wǒ mǎi le yì běn shū.", "en": "He bought me a book."},
            {"cn": "请给我一杯茶。", "pinyin": "Qǐng gěi wǒ yì bēi chá.", "en": "Please give me a cup of tea."},
            {"cn": "妈妈给我们做饭。", "pinyin": "Māma gěi wǒmen zuò fàn.", "en": "Mom cooks for us."},
            {"cn": "我给朋友写了一封信。", "pinyin": "Wǒ gěi péngyou xiě le yì fēng xìn.", "en": "I wrote a letter to my friend."},
        ],
    },
    {
        "level": 2,
        "title": "还是 (háishi) and 或者 (huòzhě)",
        "explanation": "'Or' in questions versus 'or' in statements.",
        "detailed_explanation": (
            "Use 还是 to offer a choice in a question, and 或者 to list "
            "alternatives in a statement. Swapping them is a very common mistake."
        ),
        "examples": [
            {"cn": "你喝茶还是喝咖啡？", "pinyin": "Nǐ hē chá háishi hē kāfēi?", "en": "Do you want tea or coffee?"},
            {"cn": "我们坐地铁还是打车？", "pinyin": "Wǒmen zuò dìtiě háishi dǎchē?", "en": "Shall we take the subway or a taxi?"},
            {"cn": "周末我看书或者看电影。", "pinyin": "Zhōumò wǒ kàn shū huòzhě kàn diànyǐng.", "en": "On weekends I read or watch films."},
            {"cn": "你可以给我打电话或者发邮件。", "pinyin": "Nǐ kěyǐ gěi wǒ dǎ diànhuà huòzhě fā yóujiàn.", "en": "You can call me or send an email."},
            {"cn": "今天还是明天都可以。", "pinyin": "Jīntiān háishi míngtiān dōu kěyǐ.", "en": "Either today or tomorrow works."},
        ],
    },
]

HSK3 = [
    {
        "level": 3,
        "title": "把 (bǎ) sentences",
        "explanation": "Moves the object forward to say what happened to it.",
        "detailed_explanation": (
            "The pattern is subject + 把 + object + verb + result. The object must be "
            "specific, and the verb needs something after it - a complement, 了, or a "
            "direction. A bare verb such as 我把书看 is wrong."
        ),
        "examples": [
            {"cn": "我把作业做完了。", "pinyin": "Wǒ bǎ zuòyè zuò wán le.", "en": "I finished the homework."},
            {"cn": "请把门关上。", "pinyin": "Qǐng bǎ mén guān shàng.", "en": "Please close the door."},
            {"cn": "他把杯子打破了。", "pinyin": "Tā bǎ bēizi dǎ pò le.", "en": "He broke the cup."},
            {"cn": "我把手机忘在家里了。", "pinyin": "Wǒ bǎ shǒujī wàng zài jiā lǐ le.", "en": "I left my phone at home."},
            {"cn": "她把房间打扫得很干净。", "pinyin": "Tā bǎ fángjiān dǎsǎo de hěn gānjìng.", "en": "She cleaned the room spotless."},
        ],
    },
    {
        "level": 3,
        "title": "被 (bèi) for the passive",
        "explanation": "Says the subject had something done to it.",
        "detailed_explanation": (
            "Subject + 被 + doer + verb + result. The doer can be left out when it is "
            "unknown. Like 把, the verb needs a result or 了 after it, and 被 often "
            "carries a sense of misfortune."
        ),
        "examples": [
            {"cn": "我的自行车被偷了。", "pinyin": "Wǒ de zìxíngchē bèi tōu le.", "en": "My bicycle was stolen."},
            {"cn": "蛋糕被他吃完了。", "pinyin": "Dàngāo bèi tā chī wán le.", "en": "The cake was eaten up by him."},
            {"cn": "杯子被弟弟打破了。", "pinyin": "Bēizi bèi dìdi dǎ pò le.", "en": "The cup was broken by my younger brother."},
            {"cn": "他被老师批评了。", "pinyin": "Tā bèi lǎoshī pīpíng le.", "en": "He was criticised by the teacher."},
            {"cn": "那本书被借走了。", "pinyin": "Nà běn shū bèi jiè zǒu le.", "en": "That book has been borrowed."},
        ],
    },
    {
        "level": 3,
        "title": "越来越… and 越…越…",
        "explanation": "'More and more' versus 'the more... the more...'.",
        "detailed_explanation": (
            "越来越 + adjective describes a change over time. 越 A 越 B links two "
            "things that rise together, as in 越忙越累. Do not add 很 after 越来越."
        ),
        "examples": [
            {"cn": "天气越来越冷了。", "pinyin": "Tiānqì yuèláiyuè lěng le.", "en": "The weather is getting colder and colder."},
            {"cn": "他的汉语越来越好。", "pinyin": "Tā de Hànyǔ yuèláiyuè hǎo.", "en": "His Chinese is getting better and better."},
            {"cn": "雨越下越大。", "pinyin": "Yǔ yuè xià yuè dà.", "en": "The rain is getting heavier and heavier."},
            {"cn": "我越想越觉得奇怪。", "pinyin": "Wǒ yuè xiǎng yuè juéde qíguài.", "en": "The more I think about it, the stranger it seems."},
            {"cn": "东西越多越难搬。", "pinyin": "Dōngxi yuè duō yuè nán bān.", "en": "The more things there are, the harder they are to move."},
        ],
    },
    {
        "level": 3,
        "title": "一边…一边… (at the same time)",
        "explanation": "Two actions performed simultaneously.",
        "detailed_explanation": (
            "Each 一边 comes before a verb, and the same subject does both actions. "
            "For two long-running situations, 一方面…一方面… is used instead."
        ),
        "examples": [
            {"cn": "他一边吃饭一边看电视。", "pinyin": "Tā yìbiān chī fàn yìbiān kàn diànshì.", "en": "He eats while watching TV."},
            {"cn": "我们一边走一边聊天。", "pinyin": "Wǒmen yìbiān zǒu yìbiān liáotiān.", "en": "We chatted while walking."},
            {"cn": "她一边工作一边学习。", "pinyin": "Tā yìbiān gōngzuò yìbiān xuéxí.", "en": "She works and studies at the same time."},
            {"cn": "别一边开车一边打电话。", "pinyin": "Bié yìbiān kāichē yìbiān dǎ diànhuà.", "en": "Don't phone while driving."},
            {"cn": "孩子一边哭一边跑。", "pinyin": "Háizi yìbiān kū yìbiān pǎo.", "en": "The child ran while crying."},
        ],
    },
    {
        "level": 3,
        "title": "先…然后…再… (sequencing)",
        "explanation": "Puts actions in order: first, then, after that.",
        "detailed_explanation": (
            "先 marks the first step, 然后 or 再 the next, and 最后 the last. 再 is "
            "preferred when the second action depends on finishing the first."
        ),
        "examples": [
            {"cn": "我先洗手，然后吃饭。", "pinyin": "Wǒ xiān xǐ shǒu, ránhòu chī fàn.", "en": "I wash my hands first, then eat."},
            {"cn": "先做作业，再看电视。", "pinyin": "Xiān zuò zuòyè, zài kàn diànshì.", "en": "Do homework first, then watch TV."},
            {"cn": "我们先去超市，然后回家。", "pinyin": "Wǒmen xiān qù chāoshì, ránhòu huí jiā.", "en": "We'll go to the supermarket first, then home."},
            {"cn": "先听老师说，最后再问问题。", "pinyin": "Xiān tīng lǎoshī shuō, zuìhòu zài wèn wèntí.", "en": "Listen to the teacher first, then ask questions at the end."},
            {"cn": "他先介绍自己，然后开始上课。", "pinyin": "Tā xiān jièshào zìjǐ, ránhòu kāishǐ shàngkè.", "en": "He introduced himself first, then started the class."},
        ],
    },
    {
        "level": 3,
        "title": "如果…就… (if, then)",
        "explanation": "States a condition and what follows from it.",
        "detailed_explanation": (
            "如果 (or the more colloquial 要是) opens the condition, and 就 introduces "
            "the result, sitting after the subject. 的话 can close the first clause."
        ),
        "examples": [
            {"cn": "如果明天下雨，我就不去了。", "pinyin": "Rúguǒ míngtiān xià yǔ, wǒ jiù bú qù le.", "en": "If it rains tomorrow, I won't go."},
            {"cn": "如果你有时间，就来我家吧。", "pinyin": "Rúguǒ nǐ yǒu shíjiān, jiù lái wǒ jiā ba.", "en": "If you have time, come to my place."},
            {"cn": "要是太贵，我就不买。", "pinyin": "Yàoshi tài guì, wǒ jiù bù mǎi.", "en": "If it's too expensive, I won't buy it."},
            {"cn": "如果不懂的话，可以问我。", "pinyin": "Rúguǒ bù dǒng de huà, kěyǐ wèn wǒ.", "en": "If you don't understand, you can ask me."},
            {"cn": "如果他来了，我们就开始。", "pinyin": "Rúguǒ tā lái le, wǒmen jiù kāishǐ.", "en": "Once he arrives, we'll start."},
        ],
    },
    {
        "level": 3,
        "title": "只要…就… (sufficient condition)",
        "explanation": "'As long as X, then Y'.",
        "detailed_explanation": (
            "只要 gives the minimum condition needed for the result. Contrast it with "
            "只有…才…, which says the condition is the only way to reach the result."
        ),
        "examples": [
            {"cn": "只要努力，就一定会进步。", "pinyin": "Zhǐyào nǔlì, jiù yídìng huì jìnbù.", "en": "As long as you work hard, you will improve."},
            {"cn": "只要你来，我就很高兴。", "pinyin": "Zhǐyào nǐ lái, wǒ jiù hěn gāoxìng.", "en": "As long as you come, I'll be happy."},
            {"cn": "只要不下雨，我们就去公园。", "pinyin": "Zhǐyào bú xià yǔ, wǒmen jiù qù gōngyuán.", "en": "As long as it doesn't rain, we'll go to the park."},
            {"cn": "只有多练习，才能说得好。", "pinyin": "Zhǐyǒu duō liànxí, cái néng shuō de hǎo.", "en": "Only by practising a lot can you speak well."},
            {"cn": "只要有时间，我就看书。", "pinyin": "Zhǐyào yǒu shíjiān, wǒ jiù kàn shū.", "en": "Whenever I have time, I read."},
        ],
    },
    {
        "level": 3,
        "title": "除了…以外 (except / besides)",
        "explanation": "Excludes or adds, depending on 都 or 还.",
        "detailed_explanation": (
            "With 都 in the second clause the meaning is 'except for'; with 还 or 也 "
            "it means 'besides, in addition to'. 以外 is often shortened or dropped."
        ),
        "examples": [
            {"cn": "除了他以外，我们都去了。", "pinyin": "Chúle tā yǐwài, wǒmen dōu qù le.", "en": "Everyone went except him."},
            {"cn": "除了汉语，他还会说法语。", "pinyin": "Chúle Hànyǔ, tā hái huì shuō Fǎyǔ.", "en": "Besides Chinese, he also speaks French."},
            {"cn": "除了星期天，我每天都上班。", "pinyin": "Chúle xīngqītiān, wǒ měitiān dōu shàngbān.", "en": "I work every day except Sunday."},
            {"cn": "除了看书以外，我也喜欢运动。", "pinyin": "Chúle kàn shū yǐwài, wǒ yě xǐhuan yùndòng.", "en": "Besides reading, I also like sport."},
            {"cn": "除了这个问题，别的都很简单。", "pinyin": "Chúle zhège wèntí, biéde dōu hěn jiǎndān.", "en": "Apart from this question, the rest are easy."},
        ],
    },
    {
        "level": 3,
        "title": "又…又… and 一…就…",
        "explanation": "'Both... and...' and 'as soon as...'.",
        "detailed_explanation": (
            "又 A 又 B stacks two qualities that apply at once. 一 A 就 B says B "
            "follows immediately after A, with both verbs in their normal position."
        ),
        "examples": [
            {"cn": "这个菜又便宜又好吃。", "pinyin": "Zhège cài yòu piányi yòu hǎochī.", "en": "This dish is both cheap and tasty."},
            {"cn": "他又高又瘦。", "pinyin": "Tā yòu gāo yòu shòu.", "en": "He is both tall and thin."},
            {"cn": "我一到家就给你打电话。", "pinyin": "Wǒ yí dào jiā jiù gěi nǐ dǎ diànhuà.", "en": "I'll call you as soon as I get home."},
            {"cn": "他一看就明白了。", "pinyin": "Tā yí kàn jiù míngbai le.", "en": "He understood at first glance."},
            {"cn": "孩子一见到妈妈就笑了。", "pinyin": "Háizi yí jiàn dào māma jiù xiào le.", "en": "The child smiled as soon as he saw his mother."},
        ],
    },
    {
        "level": 3,
        "title": "Resultative complements (完, 好, 懂, 到)",
        "explanation": "A second element states how the action turned out.",
        "detailed_explanation": (
            "Attach the result directly to the verb: 看完 (finish reading), 听懂 "
            "(understand by listening), 找到 (manage to find). The negative uses 没, "
            "as in 没看完."
        ),
        "examples": [
            {"cn": "我看完这本书了。", "pinyin": "Wǒ kàn wán zhè běn shū le.", "en": "I have finished this book."},
            {"cn": "我没听懂他的话。", "pinyin": "Wǒ méi tīng dǒng tā de huà.", "en": "I didn't understand what he said."},
            {"cn": "我找到工作了。", "pinyin": "Wǒ zhǎo dào gōngzuò le.", "en": "I found a job."},
            {"cn": "请把名字写好。", "pinyin": "Qǐng bǎ míngzi xiě hǎo.", "en": "Please write your name properly."},
            {"cn": "作业还没做完。", "pinyin": "Zuòyè hái méi zuò wán.", "en": "The homework isn't finished yet."},
        ],
    },
    {
        "level": 3,
        "title": "Directional complements (进来, 出去, 回来)",
        "explanation": "Shows the direction an action moves in.",
        "detailed_explanation": (
            "来 means motion towards the speaker and 去 away from the speaker. They "
            "combine with 进, 出, 回, 上, 下, and a place word goes between the two "
            "parts, as in 走进教室来."
        ),
        "examples": [
            {"cn": "他走进来了。", "pinyin": "Tā zǒu jìnlái le.", "en": "He walked in."},
            {"cn": "请拿出来给我看看。", "pinyin": "Qǐng ná chūlái gěi wǒ kànkan.", "en": "Please take it out and let me see."},
            {"cn": "我马上回来。", "pinyin": "Wǒ mǎshàng huílái.", "en": "I'll be right back."},
            {"cn": "他跑上楼去了。", "pinyin": "Tā pǎo shàng lóu qù le.", "en": "He ran upstairs."},
            {"cn": "把书放回去吧。", "pinyin": "Bǎ shū fàng huíqù ba.", "en": "Put the book back."},
        ],
    },
    {
        "level": 3,
        "title": "为了 (wèile) for purpose",
        "explanation": "States the goal an action serves.",
        "detailed_explanation": (
            "为了 introduces a purpose and comes at the start of the sentence or "
            "after the subject. To give a reason instead, use 因为 - 为了 always looks "
            "forward to a goal."
        ),
        "examples": [
            {"cn": "为了学好汉语，我每天练习。", "pinyin": "Wèile xué hǎo Hànyǔ, wǒ měitiān liànxí.", "en": "To learn Chinese well, I practise every day."},
            {"cn": "为了身体健康，他开始跑步。", "pinyin": "Wèile shēntǐ jiànkāng, tā kāishǐ pǎobù.", "en": "For his health, he started running."},
            {"cn": "他为了家人努力工作。", "pinyin": "Tā wèile jiārén nǔlì gōngzuò.", "en": "He works hard for his family."},
            {"cn": "为了不迟到，我很早就出门了。", "pinyin": "Wèile bù chídào, wǒ hěn zǎo jiù chūmén le.", "en": "To avoid being late, I left early."},
            {"cn": "为了这次考试，她准备了一个月。", "pinyin": "Wèile zhè cì kǎoshì, tā zhǔnbèi le yí gè yuè.", "en": "She prepared for a month for this exam."},
        ],
    },
    {
        "level": 3,
        "title": "对…感兴趣 and 对…来说",
        "explanation": "'Interested in' and 'as far as ... is concerned'.",
        "detailed_explanation": (
            "对 introduces the thing an attitude points at. 对…感兴趣 means to be "
            "interested in something, while 对…来说 frames a statement from a "
            "particular point of view."
        ),
        "examples": [
            {"cn": "我对中国文化很感兴趣。", "pinyin": "Wǒ duì Zhōngguó wénhuà hěn gǎn xìngqù.", "en": "I'm very interested in Chinese culture."},
            {"cn": "他对音乐不感兴趣。", "pinyin": "Tā duì yīnyuè bù gǎn xìngqù.", "en": "He isn't interested in music."},
            {"cn": "对我来说，这不太难。", "pinyin": "Duì wǒ lái shuō, zhè bú tài nán.", "en": "For me, this isn't too hard."},
            {"cn": "运动对身体很好。", "pinyin": "Yùndòng duì shēntǐ hěn hǎo.", "en": "Exercise is good for the body."},
            {"cn": "对学生来说，时间很重要。", "pinyin": "Duì xuésheng lái shuō, shíjiān hěn zhòngyào.", "en": "For students, time is very important."},
        ],
    },
    {
        "level": 3,
        "title": "着 (zhe) for continuing states",
        "explanation": "Marks a state that stays in place.",
        "detailed_explanation": (
            "着 after a verb describes an ongoing condition rather than an action in "
            "progress, as in 门开着. It also links a background action to a main one, "
            "as in 他站着说话."
        ),
        "examples": [
            {"cn": "门开着。", "pinyin": "Mén kāi zhe.", "en": "The door is open."},
            {"cn": "他站着看书。", "pinyin": "Tā zhàn zhe kàn shū.", "en": "He reads standing up."},
            {"cn": "墙上挂着一张照片。", "pinyin": "Qiáng shàng guà zhe yì zhāng zhàopiàn.", "en": "A photo hangs on the wall."},
            {"cn": "她笑着对我说谢谢。", "pinyin": "Tā xiào zhe duì wǒ shuō xièxie.", "en": "She said thank you with a smile."},
            {"cn": "外面下着大雨。", "pinyin": "Wàimiàn xià zhe dà yǔ.", "en": "It's raining heavily outside."},
        ],
    },
]

HSK4 = [
    {
        "level": 4,
        "title": "不但…而且… / 不仅…而且…",
        "explanation": "'Not only... but also...' - the second point is stronger.",
        "detailed_explanation": (
            "When both clauses share a subject it goes before 不但; when the subjects "
            "differ, each clause keeps its own. 而且 is often reinforced with 还 or 也."
        ),
        "examples": [
            {"cn": "他不但会说汉语，而且说得很好。", "pinyin": "Tā búdàn huì shuō Hànyǔ, érqiě shuō de hěn hǎo.", "en": "He not only speaks Chinese, but speaks it well."},
            {"cn": "这本书不但便宜，而且内容很好。", "pinyin": "Zhè běn shū búdàn piányi, érqiě nèiróng hěn hǎo.", "en": "This book is not only cheap but also has good content."},
            {"cn": "她不仅帮助我，而且鼓励我。", "pinyin": "Tā bùjǐn bāngzhù wǒ, érqiě gǔlì wǒ.", "en": "She not only helped me but also encouraged me."},
            {"cn": "这个地方不仅安静，而且交通方便。", "pinyin": "Zhège dìfang bùjǐn ānjìng, érqiě jiāotōng fāngbiàn.", "en": "This place is not only quiet but also convenient."},
            {"cn": "他不但没生气，反而笑了。", "pinyin": "Tā búdàn méi shēngqì, fǎn'ér xiào le.", "en": "Not only was he not angry, he actually laughed."},
        ],
    },
    {
        "level": 4,
        "title": "即使…也… (even if)",
        "explanation": "Concedes a hypothetical and keeps the result anyway.",
        "detailed_explanation": (
            "即使 introduces a supposed situation and 也 keeps the result unchanged. "
            "Compare 虽然, which concedes a real fact rather than a hypothetical one."
        ),
        "examples": [
            {"cn": "即使下雨，我也会去。", "pinyin": "Jíshǐ xià yǔ, wǒ yě huì qù.", "en": "Even if it rains, I will go."},
            {"cn": "即使很难，我也要试试。", "pinyin": "Jíshǐ hěn nán, wǒ yě yào shìshi.", "en": "Even if it's hard, I want to try."},
            {"cn": "即使他不同意，我们也要做。", "pinyin": "Jíshǐ tā bù tóngyì, wǒmen yě yào zuò.", "en": "Even if he disagrees, we'll do it."},
            {"cn": "即使再忙，也要按时吃饭。", "pinyin": "Jíshǐ zài máng, yě yào ànshí chī fàn.", "en": "However busy you are, you should eat on time."},
            {"cn": "即使失败了，也是一种经验。", "pinyin": "Jíshǐ shībài le, yě shì yì zhǒng jīngyàn.", "en": "Even failure is a kind of experience."},
        ],
    },
    {
        "level": 4,
        "title": "无论 / 不管…都… (no matter)",
        "explanation": "The result holds under every condition.",
        "detailed_explanation": (
            "无论 (written) and 不管 (spoken) must be followed by something open - a "
            "question word, an A 还是 B choice, or 多么. The second clause needs 都 or 也."
        ),
        "examples": [
            {"cn": "无论多难，我都不会放弃。", "pinyin": "Wúlùn duō nán, wǒ dōu bú huì fàngqì.", "en": "No matter how hard it is, I won't give up."},
            {"cn": "不管你去不去，我都要去。", "pinyin": "Bùguǎn nǐ qù bu qù, wǒ dōu yào qù.", "en": "Whether you go or not, I'm going."},
            {"cn": "无论谁来，都要排队。", "pinyin": "Wúlùn shéi lái, dōu yào páiduì.", "en": "No matter who comes, they must queue."},
            {"cn": "不管天气怎么样，他都跑步。", "pinyin": "Bùguǎn tiānqì zěnmeyàng, tā dōu pǎobù.", "en": "Whatever the weather, he runs."},
            {"cn": "无论什么时候，你都可以找我。", "pinyin": "Wúlùn shénme shíhou, nǐ dōu kěyǐ zhǎo wǒ.", "en": "You can come to me at any time."},
        ],
    },
    {
        "level": 4,
        "title": "既然…就… (since, given that)",
        "explanation": "Draws a conclusion from something already true.",
        "detailed_explanation": (
            "既然 states an accepted fact and 就 gives the sensible response to it. "
            "It differs from 因为, which explains a cause rather than urging a "
            "conclusion."
        ),
        "examples": [
            {"cn": "既然你累了，就早点休息吧。", "pinyin": "Jìrán nǐ lèi le, jiù zǎodiǎn xiūxi ba.", "en": "Since you're tired, get some rest."},
            {"cn": "既然决定了，就认真去做。", "pinyin": "Jìrán juédìng le, jiù rènzhēn qù zuò.", "en": "Since it's decided, do it seriously."},
            {"cn": "既然下雨了，我们就别出去了。", "pinyin": "Jìrán xià yǔ le, wǒmen jiù bié chūqù le.", "en": "Since it's raining, let's not go out."},
            {"cn": "既然他不想说，就别问了。", "pinyin": "Jìrán tā bù xiǎng shuō, jiù bié wèn le.", "en": "Since he doesn't want to talk, stop asking."},
            {"cn": "既然来了，就多待几天。", "pinyin": "Jìrán lái le, jiù duō dāi jǐ tiān.", "en": "Since you're here, stay a few more days."},
        ],
    },
    {
        "level": 4,
        "title": "由于…因此… (formal cause and effect)",
        "explanation": "A written-style version of 因为…所以….",
        "detailed_explanation": (
            "由于 appears in reports and formal writing and cannot end a sentence the "
            "way 因为 can. The result clause takes 因此 or 所以."
        ),
        "examples": [
            {"cn": "由于天气不好，航班取消了。", "pinyin": "Yóuyú tiānqì bù hǎo, hángbān qǔxiāo le.", "en": "Due to bad weather, the flight was cancelled."},
            {"cn": "由于工作忙，他很少回家。", "pinyin": "Yóuyú gōngzuò máng, tā hěn shǎo huí jiā.", "en": "Because work is busy, he rarely goes home."},
            {"cn": "由于价格上涨，因此销量下降了。", "pinyin": "Yóuyú jiàgé shàngzhǎng, yīncǐ xiāoliàng xiàjiàng le.", "en": "Because prices rose, sales fell."},
            {"cn": "由于准备充分，考试很顺利。", "pinyin": "Yóuyú zhǔnbèi chōngfèn, kǎoshì hěn shùnlì.", "en": "Thanks to thorough preparation, the exam went smoothly."},
            {"cn": "由于时间有限，我们下次再谈。", "pinyin": "Yóuyú shíjiān yǒuxiàn, wǒmen xià cì zài tán.", "en": "As time is limited, let's talk next time."},
        ],
    },
    {
        "level": 4,
        "title": "既…又… (two qualities at once)",
        "explanation": "Lists two matching qualities in a balanced way.",
        "detailed_explanation": (
            "既 A 又 B is more formal than 又 A 又 B and pairs qualities of the same "
            "kind, both positive or both negative. The two parts must be "
            "grammatically alike."
        ),
        "examples": [
            {"cn": "这个方法既简单又有效。", "pinyin": "Zhège fāngfǎ jì jiǎndān yòu yǒuxiào.", "en": "This method is both simple and effective."},
            {"cn": "他既聪明又努力。", "pinyin": "Tā jì cōngming yòu nǔlì.", "en": "He is both clever and hard-working."},
            {"cn": "这里既安静又方便。", "pinyin": "Zhèlǐ jì ānjìng yòu fāngbiàn.", "en": "It is both quiet and convenient here."},
            {"cn": "这样做既省时间又省钱。", "pinyin": "Zhèyàng zuò jì shěng shíjiān yòu shěng qián.", "en": "Doing it this way saves both time and money."},
            {"cn": "她既是老师又是母亲。", "pinyin": "Tā jì shì lǎoshī yòu shì mǔqīn.", "en": "She is both a teacher and a mother."},
        ],
    },
    {
        "level": 4,
        "title": "之所以…是因为… (result before reason)",
        "explanation": "States the outcome first, then explains why.",
        "detailed_explanation": (
            "This inverts the usual order to put the result in focus. The subject "
            "comes before 之所以, and the explanation follows 是因为."
        ),
        "examples": [
            {"cn": "他之所以成功，是因为很努力。", "pinyin": "Tā zhīsuǒyǐ chénggōng, shì yīnwèi hěn nǔlì.", "en": "The reason he succeeded is that he worked hard."},
            {"cn": "我之所以迟到，是因为堵车。", "pinyin": "Wǒ zhīsuǒyǐ chídào, shì yīnwèi dǔchē.", "en": "I was late because of the traffic."},
            {"cn": "她之所以生气，是因为你没说实话。", "pinyin": "Tā zhīsuǒyǐ shēngqì, shì yīnwèi nǐ méi shuō shíhuà.", "en": "She got angry because you didn't tell the truth."},
            {"cn": "我之所以选择这里，是因为环境好。", "pinyin": "Wǒ zhīsuǒyǐ xuǎnzé zhèlǐ, shì yīnwèi huánjìng hǎo.", "en": "I chose this place because of the environment."},
            {"cn": "价格之所以上涨，是因为需求增加。", "pinyin": "Jiàgé zhīsuǒyǐ shàngzhǎng, shì yīnwèi xūqiú zēngjiā.", "en": "Prices rose because demand increased."},
        ],
    },
    {
        "level": 4,
        "title": "与其…不如… (preferring one option)",
        "explanation": "'Rather than A, better to B'.",
        "detailed_explanation": (
            "与其 introduces the rejected option and 不如 the preferred one. 不如 can "
            "also stand alone to compare two things, as in 我不如他高."
        ),
        "examples": [
            {"cn": "与其等待，不如现在就开始。", "pinyin": "Yǔqí děngdài, bùrú xiànzài jiù kāishǐ.", "en": "Rather than waiting, it's better to start now."},
            {"cn": "与其抱怨，不如想办法。", "pinyin": "Yǔqí bàoyuàn, bùrú xiǎng bànfǎ.", "en": "Rather than complaining, think of a solution."},
            {"cn": "与其坐车，不如走路。", "pinyin": "Yǔqí zuò chē, bùrú zǒulù.", "en": "Rather than taking a bus, it's better to walk."},
            {"cn": "这件事我不如你清楚。", "pinyin": "Zhè jiàn shì wǒ bùrú nǐ qīngchu.", "en": "I don't know this matter as well as you do."},
            {"cn": "与其买新的，不如修一修。", "pinyin": "Yǔqí mǎi xīn de, bùrú xiū yi xiū.", "en": "Rather than buying a new one, better to repair it."},
        ],
    },
    {
        "level": 4,
        "title": "一方面…另一方面… (two sides)",
        "explanation": "Presents two aspects of the same situation.",
        "detailed_explanation": (
            "Used in discussion and writing to balance two considerations. The two "
            "sides may agree with each other or pull in opposite directions."
        ),
        "examples": [
            {"cn": "一方面要工作，另一方面要照顾家人。", "pinyin": "Yì fāngmiàn yào gōngzuò, lìng yì fāngmiàn yào zhàogù jiārén.", "en": "On one hand I must work, on the other I must care for family."},
            {"cn": "这样做一方面省钱，另一方面环保。", "pinyin": "Zhèyàng zuò yì fāngmiàn shěng qián, lìng yì fāngmiàn huánbǎo.", "en": "This saves money on one hand and is eco-friendly on the other."},
            {"cn": "一方面他很想去，另一方面又担心时间。", "pinyin": "Yì fāngmiàn tā hěn xiǎng qù, lìng yì fāngmiàn yòu dānxīn shíjiān.", "en": "On one hand he wants to go, on the other he worries about time."},
            {"cn": "学习一方面靠老师，另一方面靠自己。", "pinyin": "Xuéxí yì fāngmiàn kào lǎoshī, lìng yì fāngmiàn kào zìjǐ.", "en": "Learning depends partly on teachers and partly on yourself."},
            {"cn": "一方面价格便宜，另一方面质量一般。", "pinyin": "Yì fāngmiàn jiàgé piányi, lìng yì fāngmiàn zhìliàng yìbān.", "en": "On one hand it's cheap, on the other the quality is average."},
        ],
    },
    {
        "level": 4,
        "title": "随着… (along with a change)",
        "explanation": "Links one development to another.",
        "detailed_explanation": (
            "随着 is followed by a noun phrase describing change, not a full clause. "
            "The main clause then states what changes alongside it."
        ),
        "examples": [
            {"cn": "随着时间的推移，他慢慢习惯了。", "pinyin": "Suízhe shíjiān de tuīyí, tā mànmàn xíguàn le.", "en": "As time passed, he gradually got used to it."},
            {"cn": "随着科技的发展，生活更方便了。", "pinyin": "Suízhe kējì de fāzhǎn, shēnghuó gèng fāngbiàn le.", "en": "With the development of technology, life has become more convenient."},
            {"cn": "随着年龄的增长，想法也变了。", "pinyin": "Suízhe niánlíng de zēngzhǎng, xiǎngfǎ yě biàn le.", "en": "As I got older, my ideas changed too."},
            {"cn": "随着经济的发展，城市越来越大。", "pinyin": "Suízhe jīngjì de fāzhǎn, chéngshì yuèláiyuè dà.", "en": "As the economy develops, cities keep growing."},
            {"cn": "随着天气变冷，游客少了。", "pinyin": "Suízhe tiānqì biàn lěng, yóukè shǎo le.", "en": "As the weather turned cold, tourists became fewer."},
        ],
    },
    {
        "level": 4,
        "title": "甚至 (shènzhì) for the extreme case",
        "explanation": "Introduces the most surprising item in a list.",
        "detailed_explanation": (
            "甚至 highlights something unexpected and often pairs with 也 or 都. It "
            "usually comes after other, milder examples."
        ),
        "examples": [
            {"cn": "他很忙，甚至没有时间吃饭。", "pinyin": "Tā hěn máng, shènzhì méiyǒu shíjiān chī fàn.", "en": "He is so busy he doesn't even have time to eat."},
            {"cn": "这个字很难，甚至老师也不认识。", "pinyin": "Zhège zì hěn nán, shènzhì lǎoshī yě bú rènshi.", "en": "This character is so rare that even the teacher doesn't know it."},
            {"cn": "他甚至连再见都没说。", "pinyin": "Tā shènzhì lián zàijiàn dōu méi shuō.", "en": "He didn't even say goodbye."},
            {"cn": "天气冷得甚至河都结冰了。", "pinyin": "Tiānqì lěng de shènzhì hé dōu jiébīng le.", "en": "It was so cold that even the river froze."},
            {"cn": "很多人喜欢它，甚至有人每天都来。", "pinyin": "Hěn duō rén xǐhuan tā, shènzhì yǒu rén měitiān dōu lái.", "en": "Many people like it; some even come every day."},
        ],
    },
    {
        "level": 4,
        "title": "连…都/也… (even)",
        "explanation": "Singles out an extreme example for emphasis.",
        "detailed_explanation": (
            "连 puts the surprising element in focus, and 都 or 也 must follow it. "
            "The highlighted item can be the subject or the object."
        ),
        "examples": [
            {"cn": "他连一句话都没说。", "pinyin": "Tā lián yí jù huà dōu méi shuō.", "en": "He didn't say even a single word."},
            {"cn": "这个问题连小孩都会。", "pinyin": "Zhège wèntí lián xiǎohái dōu huì.", "en": "Even a child can answer this question."},
            {"cn": "我连他的名字也不知道。", "pinyin": "Wǒ lián tā de míngzi yě bù zhīdào.", "en": "I don't even know his name."},
            {"cn": "他忙得连饭都忘了吃。", "pinyin": "Tā máng de lián fàn dōu wàng le chī.", "en": "He was so busy he forgot to eat."},
            {"cn": "连老师都觉得这道题很难。", "pinyin": "Lián lǎoshī dōu juéde zhè dào tí hěn nán.", "en": "Even the teacher finds this problem hard."},
        ],
    },
    {
        "level": 4,
        "title": "尽管…还是… (despite)",
        "explanation": "Concedes a real fact, then keeps the outcome.",
        "detailed_explanation": (
            "尽管 is close to 虽然 but more formal, and the second clause typically "
            "takes 还是 or 仍然. Do not confuse it with 尽量, which means 'as far as "
            "possible'."
        ),
        "examples": [
            {"cn": "尽管很忙，他还是来了。", "pinyin": "Jǐnguǎn hěn máng, tā háishi lái le.", "en": "Despite being busy, he still came."},
            {"cn": "尽管困难很多，我们还是完成了。", "pinyin": "Jǐnguǎn kùnnan hěn duō, wǒmen háishi wánchéng le.", "en": "Despite many difficulties, we still finished."},
            {"cn": "尽管下着雨，比赛仍然继续。", "pinyin": "Jǐnguǎn xià zhe yǔ, bǐsài réngrán jìxù.", "en": "Although it was raining, the match continued."},
            {"cn": "尽管他解释了，我还是不明白。", "pinyin": "Jǐnguǎn tā jiěshì le, wǒ háishi bù míngbai.", "en": "Even though he explained, I still don't understand."},
            {"cn": "尽管年纪大了，她还是坚持学习。", "pinyin": "Jǐnguǎn niánjì dà le, tā háishi jiānchí xuéxí.", "en": "Despite her age, she keeps studying."},
        ],
    },
    {
        "level": 4,
        "title": "并且 (bìngqiě) and 而且 (érqiě)",
        "explanation": "Adds a further point in writing.",
        "detailed_explanation": (
            "并且 joins two verbs or clauses of equal weight, usually actions. 而且 "
            "adds a stronger point and pairs with 不但/不仅. Both are more formal "
            "than 还."
        ),
        "examples": [
            {"cn": "他答应了，并且很快就做到了。", "pinyin": "Tā dāying le, bìngqiě hěn kuài jiù zuò dào le.", "en": "He agreed, and quickly did it."},
            {"cn": "公司同意并且支持这个计划。", "pinyin": "Gōngsī tóngyì bìngqiě zhīchí zhège jìhuà.", "en": "The company agreed to and supported this plan."},
            {"cn": "这个方法简单，而且效果很好。", "pinyin": "Zhège fāngfǎ jiǎndān, érqiě xiàoguǒ hěn hǎo.", "en": "This method is simple, and the results are good."},
            {"cn": "他学得很快，并且从不放弃。", "pinyin": "Tā xué de hěn kuài, bìngqiě cóng bú fàngqì.", "en": "He learns fast and never gives up."},
            {"cn": "价格合理，而且服务也不错。", "pinyin": "Jiàgé hélǐ, érqiě fúwù yě búcuò.", "en": "The price is reasonable, and the service is good too."},
        ],
    },
]

ALL_GRAMMAR_POINTS = HSK1 + HSK2 + HSK3 + HSK4
