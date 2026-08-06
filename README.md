# Uyimiz Agent — CRM

Dizayn taxtasining **07-freymi** (`Uyimiz Agent — CRM`) asosida qurilgan to'liq stack ilova.
Faqat **agent CRM** qismi — admin panel (11-freym) bu loyihaga kirmaydi.

- **Frontend:** Vue 3 + TypeScript + Vite + Pinia + Vue Router
- **Backend:** Django 6 + Django REST Framework (token autentifikatsiya)

---

## Ishga tushirish

### 1. Backend

```bash
cd backend
python -m venv venv
venv/Scripts/pip install -r requirements.txt
venv/Scripts/python manage.py migrate
venv/Scripts/python manage.py seed_demo
venv/Scripts/python manage.py runserver
```

Backend **8000**-portda ishlaydi (Django standarti). Agar bu port band bo'lsa,
boshqa portda ishga tushiring va frontendga ham shuni ayting:

```bash
venv/Scripts/python manage.py runserver 8001
```

```bash
VITE_API_TARGET=http://127.0.0.1:8001 npm run dev
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Sayt: <http://localhost:5174> · API: <http://localhost:8000/api/>
(Vite `/api` va `/media` so'rovlarini backendga proksilaydi.)

### Demo hisob

```
+998901234567 / uyimiz2026
```

Demo ma'lumotni qaytadan yaratish: `manage.py seed_demo --reset`

---

## Sahifalar

| Sahifa        | Manzil       | Figma holati                                     |
| ------------- | ------------ | ------------------------------------------------ |
| **Panel**     | `/`          | 07-freym bo'yicha — KPI qatori + Yangi mijozlar   |
| **Mijozlar**  | `/mijozlar`  | Figmada yo'q edi — shu uslubda yasaldi            |
| **Obyektlar** | `/obyektlar` | Figmada yo'q edi — shu uslubda yasaldi            |
| **Bitimlar**  | `/bitimlar`  | Figmada yo'q edi — shu uslubda yasaldi            |
| **Reyting**   | `/reyting`   | Figmada yo'q edi — shu uslubda yasaldi            |

Figmada bo'lmagan ekranlar taxtaning o'z tilida qurildi:

- **Mijozlar** — 07-freymning jadval tili (mono sarlavha, pill holat, ava + ism)
  ustiga filtr qatori va o'ng yon panel qo'shildi.
- **Obyektlar** — 02/03-freymlardagi e'lon kartasi (`.lcard`: foto, narx, manzil,
  meta qatori) agent portfeliga moslashtirildi.
- **Bitimlar** — 09-freymdagi oqim diagrammasi voronka ustunlariga aylantirildi.
- **Reyting** — 07-freym chap panelidagi shkala ("Top Makler'ga 8 bitim") to'liq
  sahifaga kengaytirildi.

---

## Mavzu (rang) almashtirgichi

Tepa panelda almashtirgich turadi. Ikkala palitra ham berilgan Figma fayllaridan
**aynan** ko'chirilgan (`src/styles/tokens.css`):

| Mavzu     | Manba fayl                     | Fon       | Asosiy rang |
| --------- | ------------------------------ | --------- | ----------- |
| Qorong'i  | `uyimiz-figma-board_2.html`    | `#0F1216` | `#2FC7B4`   |
| Yorug'    | `uyimiz-figma-board-oq.html`   | `#F7F8FA` | `#189889`   |

Tanlov `localStorage` da saqlanadi va `index.html` da birinchi bo'yoqdan oldin
qo'llanadi — shuning uchun sahifa ochilishida "chaqnash" bo'lmaydi. Sukut bo'yicha
tizim sozlamasi (`prefers-color-scheme`) olinadi.

---

## Animatsiyalar

`src/styles/animations.css` — barchasi `prefers-reduced-motion: reduce` ostida o'chadi.

- Sahifalar orasida `page` o'tishi, kartalar navbat bilan chiqishi (`.stagger`)
- KPI raqamlari 0 dan sanaladi (`CountUp`), trend chizig'i chizilib chiqadi (`Sparkline`)
- Halqa diagramma segmentlari ketma-ket paydo bo'ladi (`DonutChart`)
- Yon panel o'ngdan sirg'aladi, jadval satrlari va voronka kartalari `TransitionGroup` bilan
- Skeleton yuklanish (`shimmer`), toast bildirishnomalar, hover ko'tarilishlari
- Kirish sahifasidagi girih naqshi sekin siljiydi

---

## API

| Metod       | Manzil                       | Vazifa                                  |
| ----------- | ---------------------------- | --------------------------------------- |
| POST        | `/api/auth/login/`           | Token olish                             |
| POST        | `/api/auth/logout/`          | Tokenni bekor qilish                    |
| GET / PATCH | `/api/auth/me/`              | Agent profili                           |
| GET         | `/api/dashboard/`            | KPI, yangi mijozlar, voronka, faollik   |
| GET         | `/api/rating/`               | Reyting, daraja, agentlar jadvali       |
| CRUD        | `/api/clients/`              | Mijozlar                                |
| POST        | `/api/clients/<id>/status/`  | Mijoz holatini o'zgartirish             |
| CRUD        | `/api/properties/`           | Obyektlar                               |
| CRUD        | `/api/deals/`                | Bitimlar (bosqich o'zgarishi bilan)     |
| CRUD        | `/api/showings/`             | Ko'rsatuvlar                            |
| CRUD        | `/api/activities/`           | Faollik tasmasi                         |

Har bir yozuv faqat o'z agentiga ko'rinadi (`AgentScopedViewSet`).

---

## Demo ma'lumot 07-freymga mos keladi

| Ko'rsatkich         | Qiymat     |
| ------------------- | ---------- |
| Faol mijozlar       | 17         |
| Bu oydagi bitimlar  | 6          |
| Komissiya daromadi  | 18,4 mln   |
| Platforma ulushi    | 12%        |
| Javob tezligi       | 9 daqiqa   |
| Reyting             | 4,7 ★      |
| Keyingi daraja      | Top Makler'ga 8 bitim |
