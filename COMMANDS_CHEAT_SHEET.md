# ALFHANA KITCHEN - COMMANDS CHEAT SHEET

> **مسار المشروع:** `C:\Users\Fouad\OneDrive\Desktop\shark2`
> **GitHub:** `https://github.com/Fo2shh/alf_hana` | SSH: `git@github.com:Fo2shh/alf_hana.git`

---

## 📦 TABLE 1: GIT & GITHUB COMMANDS

| المهمة | الأمر (الكود) | الملاحظات |
|--------|---------------|-----------|
| تحميل المشروع لأول مرة (HTTPS) | `git clone https://github.com/Fo2shh/alf_hana.git shark2` | لا تحتاج مفتاح SSH |
| تحميل المشروع لأول مرة (SSH) | `git clone git@github.com:Fo2shh/alf_hana.git shark2` | تحتاج مفتاح SSH |
| رفع مشروع محلي جديد على GitHub | `git init`<br>`git add .`<br>`git commit -m "Initial commit"`<br>`git branch -M main`<br>`git remote add origin https://github.com/Fo2shh/alf_hana.git`<br>`git push -u origin main` | قم بهذا داخل مجلد المشروع |
| جلب آخر التحديثات من GitHub | `git pull` أو `git pull origin main` | قبل ما تبدأ شغل يومي |
| عرض الملفات التي تغيرت | `git status` | قبل الـ commit |
| إضافة كل الملفات للـ commit | `git add .` | "Dot" تعني كل شيء |
| إضافة ملفات محددة فقط | `git add core/views.py requirements.txt` | أكتب الأسماء واحدة تلو الأخرى |
| حفظ التغييرات (Commit) | `git commit -m "رسالة توضح ماذا غيرت"` | مثال: `"Fix: solve Django venv error"` |
| رفع للـ GitHub بعد Commit | `git push` | بعد الـ commit مباشرة |
| إنشاء فرع جديد (Branch) | `git checkout -b feature/map-fix` | للعمل على ميزة جديدة |
| الانتقال لفرع موجود | `git checkout main` | التبديل بين الفروع |
| دمج فرع داخل الفرع الحالي | `git checkout main`<br>`git merge feature/map-fix` | بعد تنفيذ الميزة |
| عرض سجل الحفظات (Log) | `git log --oneline -15` | اضغط `q` للخروج |
| عرض رابط الريموت الحالي | `git remote -v` | للتأكد من الرابط الصحيح |
| تغيير رابط الريموت | `git remote set-url origin https://github.com/Fo2shh/alf_hana.git` | إذا أردت تغيير الرابط |

---

## 🐍 TABLE 2: VIRTUAL ENVIRONMENT (VENV)

| المهمة | الأمر (الكود) | الملاحظات |
|--------|---------------|-----------|
| إنشاء VENV جديد | `python -m venv venv` | اسم المجلد سيكون `venv` |
| حذف الـ VENV بالكامل | `rmdir /s /q venv` | امسح كل شيء داخل الـ venv |
| ترقية pip داخل الـ venv | `venv\Scripts\python.exe -m pip install --upgrade pip` | **الأفضل دائماً** بهذا الشكل |
| تنصيب حزمة واحدة | `venv\Scripts\python.exe -m pip install django` | مثال Django |
| تنصيب حزمة بنسخة محددة | `venv\Scripts\python.exe -m pip install django==5.1.7` | مثال نسخة محددة |
| تنصيب كل المتطلبات من ملف | `venv\Scripts\python.exe -m pip install -r requirements.txt` | من ملف `requirements.txt` |
| **إعادة تنصيب نظيفة (إصلاح تلف)** | `venv\Scripts\python.exe -m pip install --no-cache-dir --force-reinstall -r requirements.txt` | ⭐ يصلح 90% من مشاكل Django التالفة |
| حذف حزمة | `venv\Scripts\python.exe -m pip uninstall -y django` | الـ `-y` تجاوز التأكيد |
| عرض الحزم المثبتة | `venv\Scripts\python.exe -m pip list` | ترى كل ما هو مثبت |
| تصدير الحزم إلى requirements.txt | `venv\Scripts\python.exe -m pip freeze > requirements.txt` | بعد تنصيب حزمة جديدة |
| تفعيل الـ venv (اختياري) | CMD: `venv\Scripts\activate.bat`<br>PowerShell: `venv\Scripts\Activate.ps1` | بعد التفعيل تكتب `python` فقط بدلاً من المسار الكامل |
| إلغاء التفعيل | `deactivate` | بعد التفعيل فقط |
| اختبار إن Django يعمل | `venv\Scripts\python.exe -c "import django; print(django.get_version())"` | تظهر رقم النسخة |

---

## 🔧 TABLE 3: DJANGO MANAGE.PY - الأوامر الأساسية

> **الصيغة العامة:** `venv\Scripts\python.exe manage.py <الأمر>`

| المهمة | الأمر (الجزء الثاني فقط) | الملاحظات |
|--------|--------------------------|-----------|
| تشغيل السيرفر | `runserver` | المنفذ الافتراضي 8000 |
| تشغيل السيرفر على منفذ مختلف | `runserver 8080` أو `runserver 0.0.0.0:8000` | للوصول من LAN آخر |
| إنشاء ملفات الـ migrations | `makemigrations` | بعد تغيير `models.py` |
| إنشاء migrations لـ app محدد | `makemigrations core`<br>`makemigrations orders` | أفضل لتجنب التداخل |
| تطبيق الـ migrations على قاعدة البيانات | `migrate` | ينشئ الجداول في SQLite |
| عرض حالة الـ migrations | `showmigrations` | ترى أيهما نُفذ وأي لم ينفذ |
| ترحيل app محدد فقط | `migrate core` أو `migrate orders` | لتطبيق migrations لـ app واحد |
| التراجع عن كل migrations لـ app | `migrate core zero` | ⚠ يمسح كل بيانات الـ app |
| جمع الملفات الساكنة | `collectstatic --noinput` | CSS, JS, صور داخل `staticfiles/` |
| **مسح القديم + جمع جديد** | `collectstatic --clear --noinput` | ⭐ أفضل لتجنب الملفات القديمة |
| إنشاء مستخدم سوبر (Admin) | `createsuperuser` | يسألك اسم/بريد/كلمة مرور تفاعلياً |
| تغيير كلمة مرور مستخدم | `changepassword admin` | تغيير باسورد الأدمن |
| فحص مشاكل المشروع | `check` | يتأكد إن كل شيء صحيح |
| فحص مشاكل الإنتاج | `check --deploy` | تشخيص أعمق للـ production |
| فتح Django Shell بايثون | `shell` | لتجربة استعلامات قاعدة البيانات يدويًا |
| تشغيل كل الاختبارات | `test` | أو `test core` لـ app واحد |
| تشغيل الاختبارات بتفاصيل أكثر | `test -v 2` | مستوى التفاصيل 2 |
| طباعة SQL لمigration محدد | `sqlmigrate core 0001_initial` | ترى الاستعلامات النهائية |

---

## ⚙️ TABLE 4: سكربتات المشروع المخصصة

| المهمة | الأمر (الكود) | الملاحظات |
|--------|---------------|-----------|
| إنشاء 3 مستخدمين افتراضيين | `venv\Scripts\python.exe create_admin.py` | admin / kitchen / driver1 |
| تحديث أرقام الهواتف في قاعدة البيانات | `venv\Scripts\python.exe update_phones.py` | إذا كان لديك ملف هذا |

---

## 🚀 TABLE 5: التشغيل السريع - أوامر مجمعة

### 5A. الإعداد الكامل لأول مرة (بدون startfresh.bat)
```cmd
cd /d C:\Users\Fouad\OneDrive\Desktop\shark2
python -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
venv\Scripts\python.exe -c "import django; print(django.get_version())"
venv\Scripts\python.exe manage.py makemigrations core orders
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py collectstatic --clear --noinput
venv\Scripts\python.exe create_admin.py
venv\Scripts\python.exe manage.py runserver
```

### 5B. التشغيل اليومي السريع (بدون start.bat)
```cmd
cd /d C:\Users\Fouad\OneDrive\Desktop\shark2
venv\Scripts\python.exe manage.py makemigrations
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py collectstatic --noinput
venv\Scripts\python.exe manage.py runserver
```

### 5C. سير عمل الجيت اليومي (من أجندة لـ GitHub)
```cmd
git status
git add .
git commit -m "Describe your changes here"
git push
```

### 5D. سحب آخر التحديثات من GitHub + تشغيل
```cmd
cd /d C:\Users\Fouad\OneDrive\Desktop\shark2
git pull
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py collectstatic --noinput
venv\Scripts\python.exe manage.py runserver
```

---

## 🧨 TABLE 6: أوامر إصلاح المشاكل (TROUBLESHOOTING)

| المشكلة | الحل (الكود) |
|---------|--------------|
| ❌ `ModuleNotFoundError: No module named 'django'` | `venv\Scripts\python.exe -m pip install -r requirements.txt` |
| ❌ `No module named 'django.utils'` أو أي جزء تالف من Django | **⭐ إصلاح قوي:**<br>`venv\Scripts\python.exe -m pip install --no-cache-dir --force-reinstall -r requirements.txt` |
| ❌ VENV موجود لكن شيء ما خطأ | **⭐ الدمار الشامل للـ venv:**<br>`rmdir /s /q venv`<br>`python -m venv venv`<br>`venv\Scripts\python.exe -m pip install --upgrade pip`<br>`venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt` |
| ❌ `Virtual Environment not found` | `python -m venv venv` ثم أكمل الخطوات |
| ❌ جدول غير موجود: `no such table: core_xxx` | `venv\Scripts\python.exe manage.py makemigrations`<br>`venv\Scripts\python.exe manage.py migrate` |
| ❌ ملفات ثابتة (CSS/JS) لا تظهر | `venv\Scripts\python.exe manage.py collectstatic --clear --noinput` وتأكد `DEBUG=True` في settings |
| ❌ منفذ 8000 مستخدم بالفعل | شغل على منفذ آخر: `venv\Scripts\python.exe manage.py runserver 8080` |
| ❌ إعادة تعيين قاعدة البيانات (تمسح كل البيانات ⚠) | `del /f db.sqlite3` ثم احذف ملفات `000X_*.py` من `core/migrations/` و `orders/migrations/` وابقَ فقط `__init__.py`<br>ثم: `makemigrations core orders` → `migrate` → `create_admin.py` |
| ❌ PowerShell خطأ `ExecutionPolicy` | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` اضغط Y |

---

## 🔐 TABLE 7: بيانات الدخول الافتراضية

| الدور | اسم المستخدم | كلمة المرور | رابط تسجيل الدخول |
|------|-------------|------------|------------------|
| Admin (الأدمن) | `admin` | `admin123` | http://127.0.0.1:8000/admin/ |
| Kitchen (المطبخ) | `kitchen` | `kitchen123` | http://127.0.0.1:8000/ |
| Driver (المندوب) | `driver1` | `driver123` | http://127.0.0.1:8000/driver/ |

> يتم إنشاء هذه المستخدمين تلقائياً عند تشغيل: `venv\Scripts\python.exe create_admin.py`

---

## 💾 TABLE 8: ملفات الباتش (One-Click Run) - ماذا تفعل

| الملف | متى تستخدمه؟ | ماذا يفعل داخلياً؟ |
|-------|-------------|-------------------|
| ⭐ `startfresh.bat` | **أول مرة فقط** أو عند حدوث أخطاء غريبة | إنشاء venv → تنصيب متطلبات → migrations → collectstatic → إنشاء مستخدمين → تشغيل السيرفر |
| ⭐ `start.bat` | كل يوم بعد الإعداد الأول | migrations → collectstatic → تشغيل السيرفر |

---

## 📁 TABLE 9: هيكل الملفات المهمة في المشروع

| المسار | المحتوى |
|--------|---------|
| `manage.py` | ملف تحكم Django الأساسي |
| `requirements.txt` | قائمة الحزم المطلوبة (Django, qrcode...) |
| `create_admin.py` | سكربت إنشاء الـ 3 مستخدمين افتراضياً |
| `db.sqlite3` | ⚠ ملف قاعدة البيانات (يُنشأ تلقائياً بعد migrate) |
| `venv/` | ⚠ مجلد البيئة الافتراضية (يمكن حذفه وإعادة بنائه أي وقت) |
| `staticfiles/` | ⚠ مجلد الملفات الساكنة المجمعة (collectstatic) |
| `alfhana_kitchen/` | إعدادات المشروع الرئيسية (settings.py, urls.py...) |
| `core/` | التطبيق الأساسي: العملاء، المستخدمين، الخريطة، المندوبين |
| `core/migrations/` | ملفات ترحيل قاعدة البيانات (لا تحذف إلا إذا كنت تعرف ماذا تفعل) |
| `orders/` | تطبيق الطلبات: إنشاء، تعديل، طباعة الطلبات |
| `orders/migrations/` | ملفات ترحيل طلبات |
| `alfhana_kitchen/settings.py` | ⚙ إعدادات Django الأساسية |
