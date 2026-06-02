from django.core.management.base import BaseCommand
from apps.goods.models import Category, CategoryAttribute

class Command(BaseCommand):
    help = '【危险】一键清空所有商品分类和动态属性'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⚠️ 警告：此操作将清空 Category 和 CategoryAttribute 表中的所有数据！'))
        self.stdout.write(self.style.WARNING('⚠️ 如果你的商品(Goods)外键设置了 CASCADE，关联的商品也会被一并删除！'))

        # 防呆设计：二次确认
        confirm = input('你确定要继续吗？输入 "yes" 继续，其他任意键取消: ')

        if confirm.lower() != 'yes':
            self.stdout.write(self.style.SUCCESS('已取消操作，数据安全。'))
            return

        try:
            # 1. 先删子表（属性表）
            attr_count, _ = CategoryAttribute.objects.all().delete()
            # 2. 再删主表（分类表）
            cat_count, _ = Category.objects.all().delete()

            self.stdout.write(self.style.SUCCESS(f'✅ 清空完毕！共删除了 {cat_count} 个分类，{attr_count} 个属性。'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 清空失败，可能是因为外键保护限制(PROTECT)。报错信息: {str(e)}'))