import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alfhana_kitchen.settings")
django.setup()
from core.models import MenuItem

EXPECTED_NAMES = [
    "بشاميل (وسط)",                "بشاميل (كبير)",
    "نجرسكو (وسط)",                "نجرسكو (كبير)",
    "مكرونة بالصلصة (وسط)",        "مكرونة بالصلصة (كبير)",
    "مكرونة وايت صوص (وسط)",       "مكرونة وايت صوص (كبير)",
    "مكرونة الفريدو فراخ (وسط)",   "مكرونة الفريدو فراخ (كبير)",
    "مكرونة بالسجق والفلفل (وسط)", "مكرونة بالسجق والفلفل (كبير)",
    "مكرونة و/ص جمبري (وسط)",      "مكرونة و/ص جمبري (كبير)",
    "مكرونة ريد/ص جمبري (وسط)",    "مكرونة ريد/ص جمبري (كبير)",
    "رقاق (وسط)",                  "رقاق (كبير)",
    "جلاش (وسط)",                  "جلاش (كبير)",
    "مكرونة بلونيز (وسط)",         "مكرونة بلونيز (كبير)",
    "لازانيا (وسط)",               "لازانيا (كبير)",
    "طاجن تورلي (وسط)",            "طاجن تورلي (كبير)",
    "طاجن خضار (وسط)",             "طاجن خضار (كبير)",
    "طاجن خضار باللحمة",
    "طاجن فريك",
    "طاجن فريك بالكبد",
    "طاجن لسان عصفور",
    "طاجن عكاوي",
    "طاجن كوارع (وسط)",            "طاجن كوارع (كبير)",
    "طاجن ورق عنب كوارع (وسط)",    "طاجن ورق عنب كوارع (كبير)",
    "طاجن لحمة رأس",
    "مسقعة أو كوسة بشاميل (وسط)",  "مسقعة أو كوسة بشاميل (كبير)",
    "مسقعة عادية (وسط)",           "مسقعة عادية (كبير)",
]

qs = MenuItem.objects.filter(category__name="صواني وطواجن").order_by("order").values_list("order", "name", "price")
print("=" * 100)
print("  صواني وطواجن - التحقق النهائي من الترتيب (فرز حسب MenuItem.order)")
print("=" * 100)
print(f"  المتوقع: {len(EXPECTED_NAMES)} سطر")
print(f"  فعلي  : {qs.count()} سطر")
print()

all_ok = (qs.count() == len(EXPECTED_NAMES))
for i, exp in enumerate(EXPECTED_NAMES):
    try:
        row = qs[i]
    except Exception:
        print(f"  ❌ [{i+1:>2}] المتوقع {exp!r}  |  غير موجود في قاعدة البيانات")
        all_ok = False
        continue
    order_db, name_db, price_db = row
    match = (name_db == exp)
    if not match:
        all_ok = False
    mark = "✅" if match else "❌"
    print(f"  {mark} order={int(order_db):>2}   {name_db:<36}   expected={exp:<36}  price={price_db}")

print()
print("=" * 100)
if all_ok:
    print("  ✅ ORDER 100% MATCH - الآن الترتيب في Django Admin يطابق قائمة المنيو حرفياً!")
else:
    print("  ❌ MISMATCH - يراجع")
