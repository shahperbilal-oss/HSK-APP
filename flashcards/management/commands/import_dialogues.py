from django.core.management.base import BaseCommand

from flashcards.models import Dialogue


DIALOGUES = [
    {
        "title": "健身房办卡咨询",
        "category": "gym",
        "level": 2,
        "lines": [
            {"speaker": "A", "cn": "你好，我想了解一下你们的会员卡。", "pinyin": "Nǐhǎo, wǒ xiǎng liǎojiě yíxià nǐmen de huìyuánkǎ.", "en": "Hi, I'd like to ask about your membership cards."},
            {"speaker": "B", "cn": "好的，我们有月卡、季卡和年卡。", "pinyin": "Hǎo de, wǒmen yǒu yuèkǎ, jìkǎ hé niánkǎ.", "en": "Sure, we have monthly, quarterly, and annual cards."},
            {"speaker": "A", "cn": "年卡有什么优惠吗？", "pinyin": "Niánkǎ yǒu shénme yōuhuì ma?", "en": "Are there any discounts for the annual card?"},
            {"speaker": "B", "cn": "现在办年卡可以送两节私教课。", "pinyin": "Xiànzài bàn niánkǎ kěyǐ sòng liǎng jié sījiào kè.", "en": "If you buy an annual card now, you get two personal training sessions."},
            {"speaker": "A", "cn": "听起来不错，我先试一节课。", "pinyin": "Tīng qǐlái búcuò, wǒ xiān shì yì jié kè.", "en": "Sounds good. I'll try one class first."},
        ],
    },
    {
        "title": "课堂小组讨论",
        "category": "class",
        "level": 2,
        "lines": [
            {"speaker": "A", "cn": "我们这次报告的主题是什么？", "pinyin": "Wǒmen zhè cì bàogào de zhǔtí shì shénme?", "en": "What's the topic of our presentation this time?"},
            {"speaker": "B", "cn": "老师让我们介绍一个中国城市。", "pinyin": "Lǎoshī ràng wǒmen jièshào yí gè Zhōngguó chéngshì.", "en": "The teacher asked us to introduce a Chinese city."},
            {"speaker": "A", "cn": "那我们选上海吧，我可以负责历史部分。", "pinyin": "Nà wǒmen xuǎn Shànghǎi ba, wǒ kěyǐ fùzé lìshǐ bùfen.", "en": "Then let's choose Shanghai. I can handle the history part."},
            {"speaker": "B", "cn": "好，我来做交通和美食。", "pinyin": "Hǎo, wǒ lái zuò jiāotōng hé měishí.", "en": "Great, I'll do transportation and food."},
            {"speaker": "A", "cn": "我们明天课后再一起练习。", "pinyin": "Wǒmen míngtiān kèhòu zài yìqǐ liànxí.", "en": "Let's practice together after class tomorrow."},
        ],
    },
    {
        "title": "在家安排周末",
        "category": "home",
        "level": 1,
        "lines": [
            {"speaker": "妈妈", "cn": "这个周末你有什么计划？", "pinyin": "Zhège zhōumò nǐ yǒu shénme jìhuà?", "en": "What plans do you have this weekend?"},
            {"speaker": "我", "cn": "我想先写作业，然后打扫房间。", "pinyin": "Wǒ xiǎng xiān xiě zuòyè, ránhòu dǎsǎo fángjiān.", "en": "I want to do homework first, then clean my room."},
            {"speaker": "妈妈", "cn": "下午我们一起去买菜吧。", "pinyin": "Xiàwǔ wǒmen yìqǐ qù mǎicài ba.", "en": "Let's go grocery shopping together in the afternoon."},
            {"speaker": "我", "cn": "好啊，晚上我也想学做饭。", "pinyin": "Hǎo a, wǎnshang wǒ yě xiǎng xué zuòfàn.", "en": "Sure. I also want to learn cooking tonight."},
            {"speaker": "妈妈", "cn": "没问题，我教你做西红柿鸡蛋。", "pinyin": "Méi wèntí, wǒ jiāo nǐ zuò xīhóngshì jīdàn.", "en": "No problem. I'll teach you tomato eggs."},
        ],
    },
    {
        "title": "和朋友约见面",
        "category": "friends",
        "level": 2,
        "lines": [
            {"speaker": "A", "cn": "周五晚上有空吗？", "pinyin": "Zhōuwǔ wǎnshang yǒu kòng ma?", "en": "Are you free Friday night?"},
            {"speaker": "B", "cn": "有啊，你想做什么？", "pinyin": "Yǒu a, nǐ xiǎng zuò shénme?", "en": "Yes, what do you want to do?"},
            {"speaker": "A", "cn": "我们去新开的咖啡店聊聊天吧。", "pinyin": "Wǒmen qù xīn kāi de kāfēidiàn liáotiān ba.", "en": "Let's go chat at the newly opened cafe."},
            {"speaker": "B", "cn": "好主意，我听说那里的蛋糕很好吃。", "pinyin": "Hǎo zhǔyì, wǒ tīngshuō nàli de dàngāo hěn hǎochī.", "en": "Great idea. I heard the cakes there are very good."},
            {"speaker": "A", "cn": "那我们七点门口见。", "pinyin": "Nà wǒmen qī diǎn ménkǒu jiàn.", "en": "Then let's meet at the entrance at seven."},
        ],
    },
    {
        "title": "进出口业务邮件确认",
        "category": "import_export",
        "level": 4,
        "lines": [
            {"speaker": "客户", "cn": "您好，我们想确认这批货的发货时间。", "pinyin": "Nínhǎo, wǒmen xiǎng quèrèn zhè pī huò de fāhuò shíjiān.", "en": "Hello, we'd like to confirm the shipping time for this batch of goods."},
            {"speaker": "业务员", "cn": "按照合同，货物将在下周三装柜。", "pinyin": "Ànzhào hétóng, huòwù jiāng zài xià zhōu sān zhuāngguì.", "en": "According to the contract, the goods will be loaded next Wednesday."},
            {"speaker": "客户", "cn": "请问提单和装箱单什么时候可以提供？", "pinyin": "Qǐngwèn tídān hé zhuāngxiāngdān shénme shíhou kěyǐ tígōng?", "en": "When can the bill of lading and packing list be provided?"},
            {"speaker": "业务员", "cn": "船开后两个工作日内，我们会发送全套单据扫描件。", "pinyin": "Chuán kāi hòu liǎng gè gōngzuòrì nèi, wǒmen huì fāsòng quántào dānjù sǎomiáojiàn.", "en": "Within two working days after departure, we'll send scanned copies of the full document set."},
            {"speaker": "客户", "cn": "好的，谢谢。请同时确认保险条款。", "pinyin": "Hǎo de, xièxie. Qǐng tóngshí quèrèn bǎoxiǎn tiáokuǎn.", "en": "Okay, thank you. Please also confirm the insurance terms."},
        ],
    },
]


class Command(BaseCommand):
    help = "Import scenario-based dialogues."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for item in DIALOGUES:
            _, is_created = Dialogue.objects.update_or_create(
                title=item["title"],
                category=item["category"],
                defaults={"level": item["level"], "lines": item["lines"]},
            )
            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Dialogue import complete. Created {created}, updated {updated}, total {len(DIALOGUES)}."
            )
        )
