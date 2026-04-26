from django.core.management.base import BaseCommand

from flashcards.models import GrammarPoint


GRAMMAR_POINTS = [
    {
        "level": 1,
        "title": "是 (shì) for identification",
        "explanation": "Use 是 to link a subject with a noun phrase.",
        "detailed_explanation": "是 is used when you identify what someone or something is. It usually comes between subject and noun, not before adjectives.",
        "examples": [
            {"cn": "我是学生。", "pinyin": "Wǒ shì xuésheng.", "en": "I am a student."},
            {"cn": "他是老师。", "pinyin": "Tā shì lǎoshī.", "en": "He is a teacher."},
            {"cn": "这是我的书。", "pinyin": "Zhè shì wǒ de shū.", "en": "This is my book."},
            {"cn": "她不是医生。", "pinyin": "Tā bú shì yīshēng.", "en": "She is not a doctor."},
            {"cn": "你是中国人吗？", "pinyin": "Nǐ shì Zhōngguórén ma?", "en": "Are you Chinese?"},
        ],
    },
    {
        "level": 1,
        "title": "有 (yǒu) for possession",
        "explanation": "Use 有 to express 'have/has'.",
        "detailed_explanation": "有 states possession or existence of something related to the subject. Negative form is 没有.",
        "examples": [
            {"cn": "我有一本汉语书。", "pinyin": "Wǒ yǒu yì běn Hànyǔ shū.", "en": "I have a Chinese book."},
            {"cn": "她有一个哥哥。", "pinyin": "Tā yǒu yí gè gēge.", "en": "She has an older brother."},
            {"cn": "我们有很多作业。", "pinyin": "Wǒmen yǒu hěn duō zuòyè.", "en": "We have a lot of homework."},
            {"cn": "我没有钱。", "pinyin": "Wǒ méiyǒu qián.", "en": "I don't have money."},
            {"cn": "你有没有时间？", "pinyin": "Nǐ yǒu méi yǒu shíjiān?", "en": "Do you have time?"},
        ],
    },
    {
        "level": 1,
        "title": "呢 (ne) for follow-up questions",
        "explanation": "Use 呢 to ask 'what about...?' or soften ongoing context.",
        "detailed_explanation": "呢 often follows a topic to ask about the same situation for another person or thing.",
        "examples": [
            {"cn": "我是学生，你呢？", "pinyin": "Wǒ shì xuésheng, nǐ ne?", "en": "I am a student, what about you?"},
            {"cn": "我喜欢咖啡，你呢？", "pinyin": "Wǒ xǐhuān kāfēi, nǐ ne?", "en": "I like coffee, and you?"},
            {"cn": "他在家，你弟弟呢？", "pinyin": "Tā zài jiā, nǐ dìdi ne?", "en": "He is at home, what about your younger brother?"},
            {"cn": "我的书在这儿，你的呢？", "pinyin": "Wǒ de shū zài zhèr, nǐ de ne?", "en": "My book is here, where is yours?"},
            {"cn": "今天很冷，明天呢？", "pinyin": "Jīntiān hěn lěng, míngtiān ne?", "en": "It is cold today, what about tomorrow?"},
        ],
    },
    {
        "level": 1,
        "title": "在 (zài) for location",
        "explanation": "Use 在 before place words to indicate location.",
        "detailed_explanation": "在 can act as a verb ('to be at/in') and appears before locations. It is also used to indicate ongoing action (HSK 2+).",
        "examples": [
            {"cn": "我在学校。", "pinyin": "Wǒ zài xuéxiào.", "en": "I am at school."},
            {"cn": "他在家吗？", "pinyin": "Tā zài jiā ma?", "en": "Is he at home?"},
            {"cn": "书在桌子上。", "pinyin": "Shū zài zhuōzi shàng.", "en": "The book is on the table."},
            {"cn": "妈妈在厨房。", "pinyin": "Māma zài chúfáng.", "en": "Mom is in the kitchen."},
            {"cn": "你现在在哪儿？", "pinyin": "Nǐ xiànzài zài nǎr?", "en": "Where are you now?"},
        ],
    },
    {
        "level": 1,
        "title": "会 (huì) for ability",
        "explanation": "Use 会 to express learned ability.",
        "detailed_explanation": "会 indicates knowing how to do something through learning. It can also express future possibility in higher levels.",
        "examples": [
            {"cn": "我会说汉语。", "pinyin": "Wǒ huì shuō Hànyǔ.", "en": "I can speak Chinese."},
            {"cn": "你会写汉字吗？", "pinyin": "Nǐ huì xiě Hànzì ma?", "en": "Can you write Chinese characters?"},
            {"cn": "她会开车。", "pinyin": "Tā huì kāichē.", "en": "She can drive."},
            {"cn": "我不会游泳。", "pinyin": "Wǒ bú huì yóuyǒng.", "en": "I can't swim."},
            {"cn": "我们都会唱这首歌。", "pinyin": "Wǒmen dōu huì chàng zhè shǒu gē.", "en": "We can all sing this song."},
        ],
    },
    {
        "level": 2,
        "title": "正在 / 在 ... 呢 for ongoing action",
        "explanation": "Use 正在 or 在 before a verb to mark ongoing action.",
        "detailed_explanation": "正在 highlights that an action is happening right now. 在 ... 呢 is another common progressive pattern.",
        "examples": [
            {"cn": "我正在吃饭。", "pinyin": "Wǒ zhèngzài chīfàn.", "en": "I am eating right now."},
            {"cn": "他在看书呢。", "pinyin": "Tā zài kàn shū ne.", "en": "He is reading."},
            {"cn": "我们正在上课。", "pinyin": "Wǒmen zhèngzài shàngkè.", "en": "We are in class now."},
            {"cn": "妈妈在做饭呢。", "pinyin": "Māma zài zuòfàn ne.", "en": "Mom is cooking."},
            {"cn": "他们正在打篮球。", "pinyin": "Tāmen zhèngzài dǎ lánqiú.", "en": "They are playing basketball."},
        ],
    },
    {
        "level": 2,
        "title": "了 for completed actions",
        "explanation": "Use 了 after verbs to mark completed actions.",
        "detailed_explanation": "Verb + 了 emphasizes that an action has occurred. Sentence-final 了 can indicate a new situation.",
        "examples": [
            {"cn": "我吃了早饭。", "pinyin": "Wǒ chī le zǎofàn.", "en": "I ate breakfast."},
            {"cn": "他买了新手机。", "pinyin": "Tā mǎi le xīn shǒujī.", "en": "He bought a new phone."},
            {"cn": "我们到了。", "pinyin": "Wǒmen dào le.", "en": "We have arrived."},
            {"cn": "昨天我看了电影。", "pinyin": "Zuótiān wǒ kàn le diànyǐng.", "en": "I watched a movie yesterday."},
            {"cn": "老师来了。", "pinyin": "Lǎoshī lái le.", "en": "The teacher has arrived."},
        ],
    },
    {
        "level": 2,
        "title": "想 (xiǎng) for intention",
        "explanation": "Use 想 + verb to express desire or intention.",
        "detailed_explanation": "想 can mean 'would like to' or 'want to'. It is softer than 要 for expressing plans.",
        "examples": [
            {"cn": "我想去北京。", "pinyin": "Wǒ xiǎng qù Běijīng.", "en": "I want to go to Beijing."},
            {"cn": "你想吃什么？", "pinyin": "Nǐ xiǎng chī shénme?", "en": "What do you want to eat?"},
            {"cn": "他想学中文。", "pinyin": "Tā xiǎng xué Zhōngwén.", "en": "He wants to learn Chinese."},
            {"cn": "我们想早点儿回家。", "pinyin": "Wǒmen xiǎng zǎodiǎnr huí jiā.", "en": "We want to go home earlier."},
            {"cn": "我不想迟到。", "pinyin": "Wǒ bù xiǎng chídào.", "en": "I don't want to be late."},
        ],
    },
    {
        "level": 2,
        "title": "因为...所以... (cause and result)",
        "explanation": "Use 因为...所以... to connect reason and result.",
        "detailed_explanation": "因为 introduces the cause and 所以 introduces the result. In natural speech, either part may be omitted if context is clear.",
        "examples": [
            {"cn": "因为下雨，所以我没去。", "pinyin": "Yīnwèi xiàyǔ, suǒyǐ wǒ méi qù.", "en": "Because it rained, I didn't go."},
            {"cn": "因为他生病了，所以今天没上班。", "pinyin": "Yīnwèi tā shēngbìng le, suǒyǐ jīntiān méi shàngbān.", "en": "Because he is sick, he didn't work today."},
            {"cn": "因为太晚了，所以我们回家吧。", "pinyin": "Yīnwèi tài wǎn le, suǒyǐ wǒmen huíjiā ba.", "en": "Because it is too late, let's go home."},
            {"cn": "因为这个菜很好吃，所以我常来。", "pinyin": "Yīnwèi zhège cài hěn hǎochī, suǒyǐ wǒ cháng lái.", "en": "Because the dishes are tasty, I come often."},
            {"cn": "因为考试快到了，所以他每天学习。", "pinyin": "Yīnwèi kǎoshì kuài dào le, suǒyǐ tā měitiān xuéxí.", "en": "Because exams are near, he studies every day."},
        ],
    },
    {
        "level": 2,
        "title": "虽然...但是... (concession)",
        "explanation": "Use 虽然...但是... for 'although...still...'.",
        "detailed_explanation": "Although clause with 虽然 is followed by a contrast clause with 但是/可是.",
        "examples": [
            {"cn": "虽然很累，但是我还要工作。", "pinyin": "Suīrán hěn lèi, dànshì wǒ hái yào gōngzuò.", "en": "Although I am tired, I still need to work."},
            {"cn": "虽然下雨了，但是我们还是去了。", "pinyin": "Suīrán xiàyǔ le, dànshì wǒmen háishì qù le.", "en": "Although it rained, we still went."},
            {"cn": "虽然他年轻，但是很有经验。", "pinyin": "Suīrán tā niánqīng, dànshì hěn yǒu jīngyàn.", "en": "Although he is young, he is experienced."},
            {"cn": "虽然不贵，但是质量很好。", "pinyin": "Suīrán bú guì, dànshì zhìliàng hěn hǎo.", "en": "Although it isn't expensive, quality is good."},
            {"cn": "虽然我不会做饭，但是我会学。", "pinyin": "Suīrán wǒ bú huì zuòfàn, dànshì wǒ huì xué.", "en": "Although I can't cook, I will learn."},
        ],
    },
    {
        "level": 3,
        "title": "把 sentence pattern",
        "explanation": "Use 把 + object + verb + complement to highlight disposal/result.",
        "detailed_explanation": "The 把 structure moves the object before the verb and focuses on what happens to it. Usually requires a result/direction/completion element.",
        "examples": [
            {"cn": "请把门关上。", "pinyin": "Qǐng bǎ mén guān shàng.", "en": "Please close the door."},
            {"cn": "我把作业写完了。", "pinyin": "Wǒ bǎ zuòyè xiě wán le.", "en": "I finished writing the homework."},
            {"cn": "他把手机放在桌子上了。", "pinyin": "Tā bǎ shǒujī fàng zài zhuōzi shàng le.", "en": "He put the phone on the table."},
            {"cn": "别把咖啡喝完。", "pinyin": "Bié bǎ kāfēi hē wán.", "en": "Don't finish all the coffee."},
            {"cn": "我已经把票买好了。", "pinyin": "Wǒ yǐjīng bǎ piào mǎi hǎo le.", "en": "I already bought the tickets."},
        ],
    },
    {
        "level": 3,
        "title": "被 sentence pattern (passive voice)",
        "explanation": "Use 被 to express passive meaning.",
        "detailed_explanation": "In passive sentences, the receiver of the action becomes the subject. The performer can be omitted if unknown or unimportant.",
        "examples": [
            {"cn": "我的手机被他拿走了。", "pinyin": "Wǒ de shǒujī bèi tā názǒu le.", "en": "My phone was taken away by him."},
            {"cn": "门被风吹开了。", "pinyin": "Mén bèi fēng chuī kāi le.", "en": "The door was blown open by the wind."},
            {"cn": "作业被老师改完了。", "pinyin": "Zuòyè bèi lǎoshī gǎi wán le.", "en": "The homework was corrected by the teacher."},
            {"cn": "我被这件事感动了。", "pinyin": "Wǒ bèi zhè jiàn shì gǎndòng le.", "en": "I was moved by this matter."},
            {"cn": "他被老板批评了。", "pinyin": "Tā bèi lǎobǎn pīpíng le.", "en": "He was criticized by the boss."},
        ],
    },
    {
        "level": 3,
        "title": "越来越... (increasing change)",
        "explanation": "Use 越来越 + adjective/verb to describe gradual increase.",
        "detailed_explanation": "This pattern means 'more and more'. It is commonly used with adjectives and certain psychological/state verbs.",
        "examples": [
            {"cn": "天气越来越热了。", "pinyin": "Tiānqì yuèláiyuè rè le.", "en": "The weather is getting hotter and hotter."},
            {"cn": "他的中文说得越来越好了。", "pinyin": "Tā de Zhōngwén shuō de yuèláiyuè hǎo le.", "en": "His Chinese is getting better and better."},
            {"cn": "我越来越喜欢这个城市。", "pinyin": "Wǒ yuèláiyuè xǐhuān zhège chéngshì.", "en": "I like this city more and more."},
            {"cn": "路上车越来越多。", "pinyin": "Lù shàng chē yuèláiyuè duō.", "en": "There are more and more cars on the road."},
            {"cn": "孩子越来越懂事了。", "pinyin": "Háizi yuèláiyuè dǒngshì le.", "en": "The child is becoming more and more sensible."},
        ],
    },
    {
        "level": 3,
        "title": "一边...一边... (simultaneous actions)",
        "explanation": "Use 一边...一边... for doing two actions at the same time.",
        "detailed_explanation": "The same subject performs both actions simultaneously. Both verbs usually describe continuous activities.",
        "examples": [
            {"cn": "我一边听音乐，一边做作业。", "pinyin": "Wǒ yìbiān tīng yīnyuè, yìbiān zuò zuòyè.", "en": "I do homework while listening to music."},
            {"cn": "他一边走路，一边打电话。", "pinyin": "Tā yìbiān zǒulù, yìbiān dǎ diànhuà.", "en": "He talks on the phone while walking."},
            {"cn": "我们一边吃饭，一边聊天。", "pinyin": "Wǒmen yìbiān chīfàn, yìbiān liáotiān.", "en": "We chat while eating."},
            {"cn": "她一边看书，一边做笔记。", "pinyin": "Tā yìbiān kànshū, yìbiān zuò bǐjì.", "en": "She takes notes while reading."},
            {"cn": "孩子一边唱歌，一边跳舞。", "pinyin": "Háizi yìbiān chànggē, yìbiān tiàowǔ.", "en": "The child sings and dances at the same time."},
        ],
    },
    {
        "level": 3,
        "title": "只要...就... (sufficient condition)",
        "explanation": "Use 只要...就... for 'as long as... then...'.",
        "detailed_explanation": "只要 introduces a sufficient condition and 就 introduces the predictable outcome.",
        "examples": [
            {"cn": "只要你努力，就会成功。", "pinyin": "Zhǐyào nǐ nǔlì, jiù huì chénggōng.", "en": "As long as you work hard, you will succeed."},
            {"cn": "只要不下雨，我们就去爬山。", "pinyin": "Zhǐyào bú xiàyǔ, wǒmen jiù qù páshān.", "en": "As long as it doesn't rain, we'll go hiking."},
            {"cn": "只要有时间，我就来帮你。", "pinyin": "Zhǐyào yǒu shíjiān, wǒ jiù lái bāng nǐ.", "en": "As long as I have time, I'll help you."},
            {"cn": "只要你喜欢，就买吧。", "pinyin": "Zhǐyào nǐ xǐhuān, jiù mǎi ba.", "en": "As long as you like it, buy it."},
            {"cn": "只要按时吃药，就会好。", "pinyin": "Zhǐyào ànshí chīyào, jiù huì hǎo.", "en": "As long as you take medicine on time, you'll get better."},
        ],
    },
    {
        "level": 4,
        "title": "既...又... (two qualities/actions)",
        "explanation": "Use 既...又... to express two parallel qualities.",
        "detailed_explanation": "既 and 又 pair naturally to emphasize both properties or actions are true together.",
        "examples": [
            {"cn": "这家餐厅既便宜又好吃。", "pinyin": "Zhè jiā cāntīng jì piányi yòu hǎochī.", "en": "This restaurant is both cheap and tasty."},
            {"cn": "他既聪明又努力。", "pinyin": "Tā jì cōngming yòu nǔlì.", "en": "He is both smart and hardworking."},
            {"cn": "这个工作既有意思又有挑战。", "pinyin": "Zhège gōngzuò jì yǒuyìsi yòu yǒu tiǎozhàn.", "en": "This job is both interesting and challenging."},
            {"cn": "她既会唱歌又会跳舞。", "pinyin": "Tā jì huì chànggē yòu huì tiàowǔ.", "en": "She can both sing and dance."},
            {"cn": "这本书既实用又容易懂。", "pinyin": "Zhè běn shū jì shíyòng yòu róngyì dǒng.", "en": "This book is both practical and easy to understand."},
        ],
    },
    {
        "level": 4,
        "title": "即使...也... (hypothetical concession)",
        "explanation": "Use 即使...也... for 'even if... still...'.",
        "detailed_explanation": "即使 introduces a hypothetical unfavorable condition; 也 marks that the result still holds.",
        "examples": [
            {"cn": "即使下雨，我们也要去。", "pinyin": "Jíshǐ xiàyǔ, wǒmen yě yào qù.", "en": "Even if it rains, we will still go."},
            {"cn": "即使很忙，他也每天锻炼。", "pinyin": "Jíshǐ hěn máng, tā yě měitiān duànliàn.", "en": "Even if busy, he still exercises every day."},
            {"cn": "即使你不同意，我也会试试。", "pinyin": "Jíshǐ nǐ bù tóngyì, wǒ yě huì shìshi.", "en": "Even if you disagree, I will still try."},
            {"cn": "即使失败了，也不要放弃。", "pinyin": "Jíshǐ shībài le, yě búyào fàngqì.", "en": "Even if you fail, don't give up."},
            {"cn": "即使价格高，大家也愿意买。", "pinyin": "Jíshǐ jiàgé gāo, dàjiā yě yuànyì mǎi.", "en": "Even if the price is high, people are still willing to buy."},
        ],
    },
    {
        "level": 4,
        "title": "先...然后...最后... (sequencing)",
        "explanation": "Use sequence markers to describe ordered steps clearly.",
        "detailed_explanation": "先 introduces the first step, 然后 introduces next step(s), and 最后 marks the final stage.",
        "examples": [
            {"cn": "先洗手，然后吃饭，最后洗碗。", "pinyin": "Xiān xǐshǒu, ránhòu chīfàn, zuìhòu xǐwǎn.", "en": "First wash hands, then eat, and finally wash dishes."},
            {"cn": "先坐地铁，然后换公交，最后走五分钟。", "pinyin": "Xiān zuò dìtiě, ránhòu huàn gōngjiāo, zuìhòu zǒu wǔ fēnzhōng.", "en": "First take the subway, then transfer to a bus, and finally walk five minutes."},
            {"cn": "先看说明，然后安装，最后测试。", "pinyin": "Xiān kàn shuōmíng, ránhòu ānzhuāng, zuìhòu cèshì.", "en": "First read the instructions, then install, and finally test."},
            {"cn": "我们先讨论问题，然后做决定。", "pinyin": "Wǒmen xiān tǎolùn wèntí, ránhòu zuò juédìng.", "en": "We first discuss the issue, then make a decision."},
            {"cn": "先别着急，最后一定能解决。", "pinyin": "Xiān bié zháojí, zuìhòu yídìng néng jiějué.", "en": "Don't rush at first; it will be solved in the end."},
        ],
    },
    {
        "level": 4,
        "title": "对...来说 (from the perspective of)",
        "explanation": "Use 对...来说 to state viewpoint or relevance.",
        "detailed_explanation": "This pattern sets a subject's perspective. Commonly followed by adjectives or evaluation statements.",
        "examples": [
            {"cn": "对我来说，学习中文很有意思。", "pinyin": "Duì wǒ láishuō, xuéxí Zhōngwén hěn yǒuyìsi.", "en": "For me, learning Chinese is very interesting."},
            {"cn": "对孩子来说，睡眠很重要。", "pinyin": "Duì háizi láishuō, shuìmián hěn zhòngyào.", "en": "For children, sleep is very important."},
            {"cn": "对公司来说，这个决定风险很大。", "pinyin": "Duì gōngsī láishuō, zhège juédìng fēngxiǎn hěn dà.", "en": "For the company, this decision is risky."},
            {"cn": "对外国人来说，声调比较难。", "pinyin": "Duì wàiguórén láishuō, shēngdiào bǐjiào nán.", "en": "For foreigners, tones are relatively difficult."},
            {"cn": "对你来说，这可能是个机会。", "pinyin": "Duì nǐ láishuō, zhè kěnéng shì gè jīhuì.", "en": "For you, this may be an opportunity."},
        ],
    },
    {
        "level": 4,
        "title": "不仅...而且... (not only... but also...)",
        "explanation": "Use 不仅...而且... to add stronger second information.",
        "detailed_explanation": "This pair links two related facts, with the second often being stronger or more surprising.",
        "examples": [
            {"cn": "他不仅会说中文，而且说得很流利。", "pinyin": "Tā bùjǐn huì shuō Zhōngwén, érqiě shuō de hěn liúlì.", "en": "He not only speaks Chinese, but also speaks it fluently."},
            {"cn": "这本书不仅便宜，而且内容很好。", "pinyin": "Zhè běn shū bùjǐn piányi, érqiě nèiróng hěn hǎo.", "en": "This book is not only cheap, but also has great content."},
            {"cn": "她不仅帮助我，而且鼓励我。", "pinyin": "Tā bùjǐn bāngzhù wǒ, érqiě gǔlì wǒ.", "en": "She not only helped me, but also encouraged me."},
            {"cn": "这个地方不仅安静，而且交通方便。", "pinyin": "Zhège dìfang bùjǐn ānjìng, érqiě jiāotōng fāngbiàn.", "en": "This place is not only quiet, but also convenient for transport."},
            {"cn": "他不仅来得早，而且准备得很充分。", "pinyin": "Tā bùjǐn lái de zǎo, érqiě zhǔnbèi de hěn chōngfèn.", "en": "He not only arrived early, but also prepared thoroughly."},
        ],
    },
]


class Command(BaseCommand):
    help = "Import enhanced HSK grammar points with detailed explanations and 5 examples each."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for item in GRAMMAR_POINTS:
            first_example = item["examples"][0]
            _, is_created = GrammarPoint.objects.update_or_create(
                level=item["level"],
                title=item["title"],
                defaults={
                    "explanation": item["explanation"],
                    "detailed_explanation": item["detailed_explanation"],
                    "example_cn": first_example["cn"],
                    "example_pinyin": first_example["pinyin"],
                    "example_en": first_example["en"],
                    "examples": item["examples"],
                },
            )
            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Grammar import complete. Created {created}, updated {updated}, total {len(GRAMMAR_POINTS)}."
            )
        )
