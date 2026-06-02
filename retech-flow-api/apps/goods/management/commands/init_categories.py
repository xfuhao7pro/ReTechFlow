from django.core.management.base import BaseCommand
from django.db import transaction
from apps.goods.models import Category, CategoryAttribute

class Command(BaseCommand):
    help = '一键初始化超级详细的 3C 商品分类和动态属性模板数据 (已移除 input_type)'

    def handle(self, *args, **options):
        # 1. 安全检查
        if Category.objects.exists():
            self.stdout.write(self.style.WARNING('⚠️ 数据库中已存在分类数据，请先运行 python manage.py clear_categories 清空后再试。'))
            return

        self.stdout.write('⏳ 开始初始化 3C 商品分类和海量属性数据...')

        # 通用成色选项（复用度高，提出来）
        CONDITION_OPTIONS = ["全新未拆封", "充新 (仅拆封/试机)", "99新 (无任何磕碰划痕)", "95新 (极轻微使用痕迹)", "9新 (有明显磕碰/划痕)", "伊拉克战损版", "配件"]

        # 核心数据结构：已经去除了繁琐的 input_type，一切皆标签
        INIT_DATA = [
            {
                "name": "智能手机",
                "sort": 1,
                "attributes": [
                    {"name": "品牌", "options": ["苹果 (Apple)", "华为 (Huawei)", "小米 (Xiaomi)", "vivo", "OPPO", "荣耀 (Honor)", "三星 (Samsung)", "魅族 (Meizu)", "一加 (OnePlus)", "真我 (realme)", "iQOO", "红米 (Redmi)", "其他品牌"]},
                    {"name": "成色", "options": CONDITION_OPTIONS},
                    {"name": "存储容量", "options": ["64GB", "128GB", "256GB", "512GB", "1TB", "2TB"]},
                    {"name": "运行内存", "options": ["4GB", "6GB", "8GB", "12GB", "16GB", "24GB"]},
                    {"name": "版本", "options": ["国行原装", "港澳台版", "美版无锁", "美版有锁", "日韩版", "其他外版"]}
                ]
            },
            {
                "name": "笔记本电脑",
                "sort": 2,
                "attributes": [
                    {"name": "品牌", "options": ["苹果 (MacBook)", "联想 (Lenovo/拯救者)", "华硕 (ASUS/ROG)", "戴尔 (DELL/外星人)", "惠普 (HP)", "华为 (Huawei)", "小米/红米", "宏碁 (Acer)", "微星 (MSI)", "神舟 (Hasee)", "其他品牌"]},
                    {"name": "成色", "options": CONDITION_OPTIONS},
                    {"name": "处理器 (CPU)", "options": ["苹果 M 系列", "Intel Core i9", "Intel Core i7", "Intel Core i5", "Intel Core i3", "AMD Ryzen 9", "AMD Ryzen 7", "AMD Ryzen 5", "其他"]},
                    {"name": "显卡 (GPU)", "options": ["核心显卡", "RTX 4090/4080", "RTX 4070/4060", "RTX 30系", "RTX 20系/GTX 16系", "AMD RX系列", "其他独立显卡"]},
                    {"name": "内存 (RAM)", "options": ["8GB", "16GB", "32GB", "64GB及以上"]},
                    {"name": "硬盘类型", "options": ["纯固态硬盘 (SSD)", "固态+机械混搭", "纯机械硬盘 (HDD)"]}
                ]
            },
            {
                "name": "平板电脑",
                "sort": 3,
                "attributes": [
                    {"name": "品牌", "options": ["苹果 (iPad)", "华为 (MatePad)", "小米 (Xiaomi Pad)", "三星 (Galaxy Tab)", "联想", "荣耀", "微软 (Surface)", "其他品牌"]},
                    {"name": "成色", "options": CONDITION_OPTIONS},
                    {"name": "存储容量", "options": ["64GB", "128GB", "256GB", "512GB", "1TB及以上"]},
                    {"name": "网络类型", "options": ["WiFi版", "WiFi+蜂窝网络版 (插卡)", "5G全网通"]}
                ]
            },
            {
                "name": "摄影摄像",
                "sort": 4,
                "attributes": [
                    {"name": "品牌", "options": ["索尼 (SONY)", "佳能 (Canon)", "尼康 (Nikon)", "富士 (Fujifilm)", "松下 (Panasonic)", "大疆 (DJI)", "理光 (Ricoh)", "徕卡 (Leica)", "其他品牌"]},
                    {"name": "成色", "options": CONDITION_OPTIONS},
                    {"name": "器材类型", "options": ["微单/无反相机", "单反相机", "卡片相机", "运动相机/全景", "摄像机", "单卖镜头", "无人机"]},
                    {"name": "画幅尺寸", "options": ["全画幅", "APS-C画幅", "M43画幅", "一英寸", "中画幅"]}
                ]
            },
            {
                "name": "游戏电玩",
                "sort": 5,
                "attributes": [
                    {"name": "品牌", "options": ["任天堂 (Nintendo)", "索尼 (PlayStation)", "微软 (Xbox)", "Valve (Steam Deck)", "华硕 (ROG Ally)", "其他掌机品牌"]},
                    {"name": "成色", "options": CONDITION_OPTIONS},
                    {"name": "设备类型", "options": ["家用主机 (接电视)", "便携掌机", "VR/AR设备", "游戏光盘/卡带", "游戏手柄/外设"]},
                    {"name": "版本", "options": ["国行 (带锁)", "港版", "日版", "其他海外版", "已破解 (破译版)"]}
                ]
            },
            {
                "name": "耳机/音响",
                "sort": 6,
                "attributes": [
                    {"name": "品牌", "options": ["苹果 (AirPods/Beats)", "索尼 (SONY)", "森海塞尔", "Bose", "漫步者", "华为", "小米", "哈曼卡顿", "Marshall", "其他品牌"]},
                    {"name": "成色", "options": CONDITION_OPTIONS},
                    {"name": "佩戴方式", "options": ["真无线入耳式 (TWS)", "头戴式", "颈挂式", "骨传导/气传导", "桌面音箱"]},
                    {"name": "功能特点", "options": ["主动降噪", "HIFI高保真", "防水运动", "普通蓝牙", "纯有线"]}
                ]
            },
            {
                "name": "智能穿戴",
                "sort": 7,
                "attributes": [
                    {"name": "品牌", "options": ["苹果 (Apple Watch)", "华为", "小米", "佳明 (Garmin)", "三星", "荣耀", "OPPO/vivo", "其他品牌"]},
                    {"name": "成色", "options": CONDITION_OPTIONS},
                    {"name": "产品类型", "options": ["智能手表", "运动手环", "智能眼镜", "其他"]}
                ]
            },
            {
                "name": "电脑DIY配件",
                "sort": 8,
                "attributes": [
                    {"name": "品牌", "options": ["英特尔 (Intel)", "AMD", "英伟达 (NVIDIA)", "华硕", "微星", "技嘉", "七彩虹", "金士顿", "西部数据", "海盗船", "其他配件品牌"]},
                    {"name": "成色", "options": ["全新未拆封", "充新上机", "正常使用痕迹", "矿渣/锻炼过", "故障件/尸体"]},
                    {"name": "配件类别", "options": ["CPU处理器", "独立显卡", "主板", "内存条", "固态硬盘 (M.2/SATA)", "机械硬盘", "电源", "机箱/散热", "显示器"]}
                ]
            },
            {
                "name": "其他闲置数码",
                "sort": 99,
                "attributes": [
                    {"name": "成色", "options": CONDITION_OPTIONS},
                    {"name": "能否正常开机", "options": ["功能完全正常", "部分按键/功能失灵", "无法开机 (当配件卖)"]}
                ]
            }
        ]

        try:
            with transaction.atomic():
                for c_data in INIT_DATA:
                    category = Category.objects.create(
                        name=c_data["name"],
                        sort=c_data["sort"]
                    )

                    attrs_to_create = []
                    for attr_data in c_data["attributes"]:
                        attrs_to_create.append(
                            CategoryAttribute(
                                category=category,
                                name=attr_data["name"],
                                # 这里不再写入 input_type 字段
                                options=attr_data["options"]
                            )
                        )

                    CategoryAttribute.objects.bulk_create(attrs_to_create)
                    self.stdout.write(f'✅ 分类 [{category.name}] 及其 {len(attrs_to_create)} 个属性初始化完毕.')

            self.stdout.write(self.style.SUCCESS('\n🎉 所有 3C 商品分类和动态属性模板初始化大功告成！前端可以愉快的用胶囊渲染了！'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 初始化失败，所有写入已回滚。报错信息: {str(e)}'))