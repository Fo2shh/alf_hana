"""
Alf Hana Kitchen - Data Seed Script (ROOT LEVEL)
=================================================
Populates ONLY the "صواني وطواجن" (Sawanih w Tawagen / Trays & Pans)
category using the OFFICIAL printed-menu exact order provided by the user.

EXPECTED RUN METHODS (both work inside the project root):
  (A)  venv\\Scripts\\python.exe -m seed_menu
          (runs the file as a module using the venv interpreter directly)

  (B)  venv\\Scripts\\python.exe manage.py shell < seed_menu.py
          (pipes this file into the Django management shell)

This script is IDEMPOTENT:
  * It uses get_or_create() -> SAFE to run 1 or 1000 times.
  * Existing (category + name) rows are REUSED and only PRICE/DESCRIPTION
    are gently synced (never clobber manual edits if they already contain
    a longer description).
"""

import os
import sys


def _bootstrap_django():
    """Ensure DJANGO_SETTINGS_MODULE is set and django.setup() has run.

    Works whether the file is executed directly OR is piped into
    `manage.py shell` (in the latter case Django is already configured).
    """
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "alfhana_kitchen.settings",
    )
    try:
        import django  # noqa: WPS433
    except ImportError as exc:  # pragma: no cover - Django missing guard
        raise ImportError(
            "Couldn't import Django. Make sure your venv is active / "
            "packages installed. Run: "
            "venv\\Scripts\\python.exe -m pip install -r requirements.txt"
        ) from exc
    # django.setup() is idempotent. Safe to call even if `manage.py shell`
    # already bootstrapped the environment.
    django.setup()


_bootstrap_django()


# =====================================================================
# IMPORTS (must happen AFTER django.setup())
# =====================================================================
from core.models import Category, MenuItem  # noqa: E402


# =====================================================================
# OFFICIAL PRINTED MENU - صواني وطواجن
# =====================================================================
# * Order of the tuples below = DISPLAY ORDER on the printed menu
#   (bichamel first, down to masqa-3adeya last - EXACT 24 rows).
# * Tuple shape:  (base_name, price_medium_or_None, price_large_or_single)
#     - If price_medium is None  -> the dish has ONE size only, saved
#                                   under `base_name` at price_large.
#     - If price_medium is set   -> the dish has TWO sizes, saved as
#                                   "base_name (وسط)" and "base_name (كبير)".
# =====================================================================
SAWANIH_TAWAGEN_ORDERED = [
    #  1
    ("بشاميل",                         375, 500),
    #  2
    ("نجرسكو",                         325, 450),
    #  3
    ("مكرونة بالصلصة",                 125, 200),
    #  4
    ("مكرونة وايت صوص",                200, 300),
    #  5
    ("مكرونة الفريدو فراخ",            325, 450),
    #  6
    ("مكرونة بالسجق والفلفل",          350, 500),
    #  7
    ("مكرونة و/ص جمبري",               450, 650),
    #  8
    ("مكرونة ريد/ص جمبري",             450, 700),
    #  9
    ("رقاق",                           375, 500),
    # 10
    ("جلاش",                           350, 450),
    # 11
    ("مكرونة بلونيز",                  400, 600),
    # 12
    ("لازانيا",                         550, 850),
    # 13
    ("طاجن تورلي",                     125, 200),
    # 14
    ("طاجن خضار",                      125, 200),
    # 15
    ("طاجن خضار باللحمة",              None, 450),
    # 16
    ("طاجن فريك",                      None, 175),
    # 17
    ("طاجن فريك بالكبد",               None, 275),
    # 18
    ("طاجن لسان عصفور",                None, 125),
    # 19
    ("طاجن عكاوي",                     None, 550),
    # 20
    ("طاجن كوارع",                     400, 750),
    # 21
    ("طاجن ورق عنب كوارع",             450, 800),
    # 22
    ("طاجن لحمة رأس",                  None, 300),
    # 23
    ("مسقعة أو كوسة بشاميل",           375, 475),
    # 24
    ("مسقعة عادية",                    125, 200),
]

CATEGORY_NAME = "صواني وطواجن"
CATEGORY_DESCRIPTION = (
    "طاجنات، مستعات، بشاميل، لازانيا، مضرونات ومستوعات "
    "الطبخ الكبيرة للعائلات"
)
CATEGORY_ORDER = 1


# =====================================================================
# OFFICIAL PRINTED MENU - اللحوم
# =====================================================================
LAHAM_CATEGORY_NAME = "اللحوم"
LAHAM_CATEGORY_DESCRIPTION = "أصناف اللحوم المشوية، المسلوقة، والمشكلات - الأسعار بالكيلو جرام"
LAHAM_CATEGORY_ORDER = 2

LAHAM_ORDERED = [
    (1,  "لحمة فتة",                      850),
    (2,  "لحمة روستو",                    750),
    (3,  "لحمة رولات",                    900),
    (4,  "لحمة مشوية",                    700),
    (5,  "شاورما لحمة",                   750),
    (6,  "كباب حلة",                      800),
    (7,  "بيكاتا لحم بالمشروم",           850),
    (8,  "لحمة مسلوقة ومحمرة",            650),
    (9,  "لحمة بالصوص البني",             850),
    (10, "ورقة لحمة نص ك",                475),
    (11, "ريش ضاني (شوي فرن)",            850),
    (12, "كفتة فرن",                      550),
    (13, "كفتة فحم",                      550),
    (14, "كفتة أرز",                      650),
    (15, "طرب",                           900),
    (16, "كباب",                          850),
    (17, "مشاوي مشكل",                    825),
]


# =====================================================================
# OFFICIAL PRINTED MENU - حسب الوزن
# =====================================================================
WEIGHT_CATEGORY_NAME = "حسب الوزن"
WEIGHT_CATEGORY_DESCRIPTION = "قطع اللحم الكاملة التي يتم بيعها حسب الوزن الفعلي عند الطلب"
WEIGHT_CATEGORY_ORDER = 3

WEIGHT_ORDERED = [
    (1, "فخدة ضاني"),
    (2, "كتف ضاني"),
    (3, "نصف خروف"),
    (4, "كتف عجل"),
    (5, "فخدة عجل"),
    (6, "لحم ضاني بالعظم"),
    (7, "عرق فلتو"),
    (8, "عرق تربيانكو"),
]


# =====================================================================
# OFFICIAL PRINTED MENU - إضافات
# =====================================================================
EXTRAS_CATEGORY_NAME = "إضافات"
EXTRAS_CATEGORY_DESCRIPTION = "إضافات جانبية وأرز وصوصات وسلطات ومخللات"
EXTRAS_CATEGORY_ORDER = 4

EXTRAS_ORDERED = [
    (1, "أرز بسمتي"),
    (2, "أرز بالخلطة"),
    (3, "أرز بالشعرية"),
    (4, "صوصات"),
    (5, "مخللات"),
    (6, "سلطات"),
]


def _upsert(
    category: Category,
    name: str,
    price: int,
    display_order: int,
    desc: str = "",
) -> bool:
    """Create OR update a single MenuItem; return True when newly created.

    `display_order` controls the list order in Django Admin + everywhere
    that respects Meta.ordering = ['category__order', 'order', 'name'].
    The sequence is the EXACT printed-menu order provided by the user:
        1. بشاميل (وسط)
        2. بشاميل (كبير)
        3. نجرسكو (وسط)
        4. نجرسكو (كبير)
        ... etc., then وسط then كبير within each base item, bases in JSON
        list order, single-size items get their own unique slot.
    """
    item, created = MenuItem.objects.get_or_create(
        category=category,
        name=name,
        defaults={
            "price": price,
            "description": desc,
            "is_active": True,
            "order": display_order,
        },
    )
    if created:
        return True

    # ---- existing row: gentle sync (do NOT overwrite manual tweaks) ----
    changed = False
    if int(item.price) != int(price):
        item.price = price
        changed = True
    if int(item.order) != int(display_order):
        item.order = display_order
        changed = True
    if desc and (not item.description or len(item.description) < 5):
        item.description = desc
        changed = True
    if changed:
        item.save(update_fields=["price", "description", "order", "updated_at"])
    return False


def seed_sawanih_tawagen() -> dict:
    """Seed the صواني وطواجن category + 24 menu items in EXACT user order.

    Returns a stats dict for reporting.
    """
    stats = {
        "categories": {"created": 0, "updated": 0, "total": 0},
        "items":      {"created": 0, "updated": 0, "skipped": 0, "total": 0},
    }

    # ------------------------------------------------------------------
    # 1) Ensure category exists with correct priority (order=1)
    # ------------------------------------------------------------------
    cat, created = Category.objects.get_or_create(
        name=CATEGORY_NAME,
        defaults={
            "description": CATEGORY_DESCRIPTION,
            "order": CATEGORY_ORDER,
            "is_active": True,
        },
    )
    if created:
        stats["categories"]["created"] += 1
    else:
        changed_cat = False
        if not cat.description:
            cat.description = CATEGORY_DESCRIPTION
            changed_cat = True
        if cat.order != CATEGORY_ORDER:
            # Keep صواني وطواجن first as per user request.
            cat.order = CATEGORY_ORDER
            changed_cat = True
        if changed_cat:
            cat.save(update_fields=["description", "order", "updated_at"])
            stats["categories"]["updated"] += 1
    stats["categories"]["total"] = 1

    # ------------------------------------------------------------------
    # 2) Insert / sync each item in PRINTED-MENU ORDER
    #    IMPORTANT: Assign an explicit, sequential `order` number so
    #    Django Admin's list view matches the printed menu 1:1
    #       - Media (وسط) comes BEFORE large (كبير) in the pair
    #       - Pairs are in the user JSON list order
    #       - Single-size items take the next unique slot in sequence
    # ------------------------------------------------------------------
    display_order = 0
    for idx, (base, med, lrg) in enumerate(SAWANIH_TAWAGEN_ORDERED, start=1):
        human_index = f"#{idx:>02}"

        if med is None:
            # ---- Single size dish ----
            display_order += 1
            description = (
                f"{human_index} في قائمة صواني وطواجن - حجم واحد فقط"
            )
            is_new = _upsert(cat, base, lrg, display_order, description)
            stats["items"]["created" if is_new else "skipped"] += 1
            stats["items"]["total"] += 1
            continue

        # ---- Paired (وسط / كبير) dish: وسط FIRST, then كبير ----
        display_order += 1
        med_name = f"{base} (وسط)"
        description_med = (
            f"{human_index} في قائمة صواني وطواجن - الحجم المتوسط"
        )
        is_new_med = _upsert(cat, med_name, med, display_order, description_med)
        stats["items"]["created" if is_new_med else "skipped"] += 1
        stats["items"]["total"] += 1

        display_order += 1
        lrg_name = f"{base} (كبير)"
        description_lrg = (
            f"{human_index} في قائمة صواني وطواجن - الحجم الكبير"
        )
        is_new_lrg = _upsert(cat, lrg_name, lrg, display_order, description_lrg)
        stats["items"]["created" if is_new_lrg else "skipped"] += 1
        stats["items"]["total"] += 1

    return stats


def _get_or_create_category(
    name: str,
    description: str,
    order: int,
    stats: dict,
) -> Category:
    """Get or create a Category; update stats dict in-place."""
    cat, created = Category.objects.get_or_create(
        name=name,
        defaults={
            "description": description,
            "order": order,
            "is_active": True,
        },
    )
    if created:
        stats["categories"]["created"] += 1
    else:
        changed_cat = False
        if not cat.description:
            cat.description = description
            changed_cat = True
        if cat.order != order:
            cat.order = order
            changed_cat = True
        if changed_cat:
            cat.save(update_fields=["description", "order", "updated_at"])
            stats["categories"]["updated"] += 1
    stats["categories"]["total"] += 1
    return cat


def seed_laham() -> dict:
    """Seed قسم اللحوم - 17 items with price-per-kg in EXACT user order."""
    stats = {
        "categories": {"created": 0, "updated": 0, "total": 0},
        "items":      {"created": 0, "updated": 0, "skipped": 0, "total": 0},
    }

    cat = _get_or_create_category(
        LAHAM_CATEGORY_NAME, LAHAM_CATEGORY_DESCRIPTION, LAHAM_CATEGORY_ORDER, stats,
    )

    display_order = 0
    for human_idx, name, price in LAHAM_ORDERED:
        display_order += 1
        description = (
            f"#{human_idx:>02} في قائمة اللحوم - السعر بالكيلو جرام"
        )
        is_new = _upsert(cat, name, price, display_order, description)
        stats["items"]["created" if is_new else "skipped"] += 1
        stats["items"]["total"] += 1

    return stats


def seed_weight_based() -> dict:
    """Seed قسم حسب الوزن - 8 items with price=0 and weight note."""
    stats = {
        "categories": {"created": 0, "updated": 0, "total": 0},
        "items":      {"created": 0, "updated": 0, "skipped": 0, "total": 0},
    }

    cat = _get_or_create_category(
        WEIGHT_CATEGORY_NAME, WEIGHT_CATEGORY_DESCRIPTION, WEIGHT_CATEGORY_ORDER, stats,
    )

    display_order = 0
    for human_idx, name in WEIGHT_ORDERED:
        display_order += 1
        price = 0
        description = (
            f"#{human_idx:>02} في قائمة حسب الوزن - السعر يحدد بالوزن الفعلي عند الطلب"
        )
        is_new = _upsert(cat, name, price, display_order, description)
        stats["items"]["created" if is_new else "skipped"] += 1
        stats["items"]["total"] += 1

    return stats


def seed_extras() -> dict:
    """Seed قسم الإضافات - 6 items (أرز، صوصات، مخللات، سلطات) بالترتيب الصحيح."""
    stats = {
        "categories": {"created": 0, "updated": 0, "total": 0},
        "items":      {"created": 0, "updated": 0, "skipped": 0, "total": 0},
    }

    cat = _get_or_create_category(
        EXTRAS_CATEGORY_NAME, EXTRAS_CATEGORY_DESCRIPTION, EXTRAS_CATEGORY_ORDER, stats,
    )

    display_order = 0
    for human_idx, name in EXTRAS_ORDERED:
        display_order += 1
        price = 0
        description = (
            f"#{human_idx:>02} في قائمة الإضافات جانبية مع الأطباق الرئيسية"
        )
        is_new = _upsert(cat, name, price, display_order, description)
        stats["items"]["created" if is_new else "skipped"] += 1
        stats["items"]["total"] += 1

    return stats


def _print_single_report(category_label: str, category_name: str,
                         base_count: int, base_label: str, stats: dict) -> None:
    """Print a single-category seed report."""
    total_items = MenuItem.objects.filter(category__name=category_name).count()
    sep = "=" * 70
    print()
    print(sep)
    print("  ALFHANA KITCHEN - DATA SEED REPORT")
    print("  Category  : " + category_label)
    print(sep)
    print("  Categories:")
    print("    - new     : " + str(stats["categories"]["created"]))
    print("    - updated : " + str(stats["categories"]["updated"]))
    print("  Items in this run:")
    print("    - new     : " + str(stats["items"]["created"]))
    print("    - skipped : " + str(stats["items"]["skipped"]))
    print("    - processed: " + str(stats["items"]["total"]))
    print()
    print("  Total rows in DB for " + category_name + " : " + str(total_items))
    print()
    print(
        "  Seed spec compliance: "
        + str(base_count)
        + " " + base_label + " in EXACT printed-menu order."
    )
    print(sep)


def _aggregate(stats_list: list) -> dict:
    """Sum stats counters across multiple seed runs."""
    agg = {
        "categories": {"created": 0, "updated": 0, "total": 0},
        "items":      {"created": 0, "updated": 0, "skipped": 0, "total": 0},
    }
    for s in stats_list:
        for k1 in agg:
            for k2 in agg[k1]:
                agg[k1][k2] += s[k1][k2]
    return agg


def _print_grand_report(all_stats: list) -> None:
    """Print a grand summary across all seeded categories."""
    agg = _aggregate([s["stats"] for s in all_stats])
    sep = "=" * 70
    print()
    print(sep)
    print("  ALFHANA KITCHEN - GRAND SEED SUMMARY")
    print(sep)
    for entry in all_stats:
        cat_total = MenuItem.objects.filter(
            category__name=entry["category_name"],
        ).count()
        print(
            "  " + entry["label"].ljust(18)
            + " | items in run: " + str(entry["stats"]["items"]["total"]).rjust(3)
            + " | total DB rows: " + str(cat_total),
        )
    print(sep)
    print(
        "  Total categories : " + str(agg["categories"]["total"])
        + "   (new: " + str(agg["categories"]["created"])
        + " / updated: " + str(agg["categories"]["updated"]) + ")"
    )
    print(
        "  Total items run  : " + str(agg["items"]["total"])
        + "   (new: " + str(agg["items"]["created"])
        + " / skipped: " + str(agg["items"]["skipped"]) + ")"
    )
    grand_total = MenuItem.objects.count()
    print("  Grand total MenuItem rows in DB : " + str(grand_total))
    print(sep)


# =====================================================================
# ENTRY POINTS
# =====================================================================

def run() -> None:
    """Public entry point. Idempotent. Seeds all menu sections."""
    sawanih_stats = seed_sawanih_tawagen()
    _print_single_report(
        category_label=CATEGORY_NAME,
        category_name=CATEGORY_NAME,
        base_count=len(SAWANIH_TAWAGEN_ORDERED),
        base_label="base items",
        stats=sawanih_stats,
    )

    laham_stats = seed_laham()
    _print_single_report(
        category_label=LAHAM_CATEGORY_NAME,
        category_name=LAHAM_CATEGORY_NAME,
        base_count=len(LAHAM_ORDERED),
        base_label="items",
        stats=laham_stats,
    )

    weight_stats = seed_weight_based()
    _print_single_report(
        category_label=WEIGHT_CATEGORY_NAME,
        category_name=WEIGHT_CATEGORY_NAME,
        base_count=len(WEIGHT_ORDERED),
        base_label="items",
        stats=weight_stats,
    )

    extras_stats = seed_extras()
    _print_single_report(
        category_label=EXTRAS_CATEGORY_NAME,
        category_name=EXTRAS_CATEGORY_NAME,
        base_count=len(EXTRAS_ORDERED),
        base_label="items",
        stats=extras_stats,
    )

    all_stats = [
        {"label": CATEGORY_NAME,       "category_name": CATEGORY_NAME,       "stats": sawanih_stats},
        {"label": LAHAM_CATEGORY_NAME, "category_name": LAHAM_CATEGORY_NAME, "stats": laham_stats},
        {"label": WEIGHT_CATEGORY_NAME,"category_name": WEIGHT_CATEGORY_NAME,"stats": weight_stats},
        {"label": EXTRAS_CATEGORY_NAME,"category_name": EXTRAS_CATEGORY_NAME,"stats": extras_stats},
    ]
    _print_grand_report(all_stats)


# Always run automatically. This file is explicitly designed as a ONE-SHOT
# seed script (NOT a reusable importable library module), so immediate
# execution is the correct behaviour in every context:
#   * `python -m seed_menu`            -> __name__ == "__main__"
#   * `python seed_menu.py`            -> __name__ == "__main__"
#   * shell  < seed_menu.py (CMD.exe)  -> __name__ == "<console>" or similar
#   * shell -c "exec(open(...))"       -> any __name__  (call run() below)
#   * import seed_menu (accidental)    -> __name__ == "seed_menu"
run()
