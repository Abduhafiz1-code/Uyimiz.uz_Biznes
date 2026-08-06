"""Seed the CRM with the demo data drawn on frame 07 of the Uyimiz design board.

    python manage.py seed_demo

Creates the agent Nodira Aliyeva (+998901234567 / uyimiz2026) together with the
clients, properties, deals and showings that make the Panel read exactly like
the design: 17 active clients, 6 deals this month, 18,4 mln commission, 12%
platform share, 9 minute response time and a 4,7 star rating.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from agents.models import TIER_ORDER, TIER_THRESHOLDS, Agent, AgentTier, CertificationStatus
from crm.models import (
    Activity,
    ActivityKind,
    Client,
    ClientStatus,
    Deal,
    DealStage,
    DealType,
    LeadSource,
    Property,
    PropertyBadge,
    PropertyStatus,
    Showing,
    ShowingStatus,
)

DEMO_PHONE = '+998901234567'
DEMO_PASSWORD = 'uyimiz2026'


def tier_for(total_deals):
    """Jami bitim soniga mos darajani qaytaradi."""
    tier = TIER_ORDER[0]
    for candidate in TIER_ORDER:
        if total_deals >= TIER_THRESHOLDS[candidate]:
            tier = candidate
    return tier


class Command(BaseCommand):
    help = "Uyimiz Agent CRM uchun demo ma'lumotlarni yaratadi"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help="Avvalgi demo yozuvlarni o'chirib, qaytadan yaratadi",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()

        agent, created = Agent.objects.get_or_create(
            phone=DEMO_PHONE,
            defaults={
                'full_name': 'Nodira Aliyeva',
                'email': 'nodira@uyimiz.uz',
                'district': 'Chilonzor',
                'certification': CertificationStatus.TASDIQLANGAN,
                'rating': Decimal('4.7'),
                'tier': AgentTier.TAJRIBALI,
                'platform_share': 12,
                'commission_rate': Decimal('1.50'),
                'avg_response_minutes': 9,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            agent.set_password(DEMO_PASSWORD)
            agent.save()
            self.stdout.write(self.style.SUCCESS(f'Agent yaratildi: {DEMO_PHONE} / {DEMO_PASSWORD}'))

        if options['reset']:
            Activity.objects.filter(agent=agent).delete()
            Showing.objects.filter(agent=agent).delete()
            Deal.objects.filter(agent=agent).delete()
            Client.objects.filter(agent=agent).delete()
            Property.objects.filter(agent=agent).delete()
            self.stdout.write('Eski demo yozuvlar tozalandi')

        if Client.objects.filter(agent=agent).exists():
            self.stdout.write(
                self.style.WARNING("Demo ma'lumot allaqachon bor — qayta yaratish uchun --reset")
            )
            return

        rivals = self._seed_rivals()
        properties = self._seed_properties(agent, now)
        clients = self._seed_clients(agent, now)
        self._seed_deals(agent, clients, properties, now)
        self._seed_showings(agent, clients, properties, now)
        self._seed_activity(agent, now)

        self.stdout.write(
            self.style.SUCCESS(
                f'Tayyor: {len(clients)} mijoz, {len(properties)} obyekt, '
                f'{Deal.objects.filter(agent=agent).count()} bitim, {len(rivals)} raqib agent'
            )
        )

    # ---- agents ------------------------------------------------------------

    def _seed_rivals(self):
        """Other agents so the Reyting leaderboard has something to rank against."""
        rows = [
            ('Jasur Toshpulatov', '+998901112233', 'Yunusobod', '4.9', AgentTier.TOP, 44, 6),
            ('Malika Rasulova', '+998902223344', 'Mirobod', '4.8', AgentTier.TOP, 41, 12),
            ('Sardor Nazarov', '+998903334455', 'Sergeli', '4.4', AgentTier.TAJRIBALI, 22, 8),
            ('Kamron Ismoilov', '+998904445566', 'Olmazor', '4.1', AgentTier.TAJRIBALI, 17, 4),
            ('Aziza Yo\'ldosheva', '+998905556677', 'Yakkasaroy', '3.9', AgentTier.FAOL, 9, 3),
        ]
        made = []
        for name, phone, district, rating, tier, deals, response in rows:
            rival, created = Agent.objects.get_or_create(
                phone=phone,
                defaults={
                    'full_name': name,
                    'district': district,
                    'rating': Decimal(rating),
                    'tier': tier,
                    'certification': CertificationStatus.TASDIQLANGAN,
                    # Raqib agentlar bu CRM ichida bitim yopmaydi — hammasi tarix.
                    'historical_deals': deals,
                    'total_deals': deals,
                    'avg_response_minutes': response,
                },
            )
            if created:
                rival.set_password(DEMO_PASSWORD)
                rival.save()
            made.append(rival)
        return made

    # ---- properties --------------------------------------------------------

    def _seed_properties(self, agent, now):
        rows = [
            # listing_id, title, district, address, type, price, cur, rooms, area,
            # floor, floors, year, status, badge, photos, views, days_ago
            ('40218', '3 xonali kvartira', 'Chilonzor', "Chilonzor 11-kvartal", DealType.SOTIB_OLISH,
             54000, 'USD', 3, '72.0', 3, 5, 1998, PropertyStatus.FAOL, PropertyBadge.ODDIY, 12, 341, 2),
            ('40219', '3 xonali kvartira', 'Chilonzor', "Chilonzor 19-kvartal", DealType.SOTIB_OLISH,
             61200, 'USD', 3, '78.0', 5, 9, 2012, PropertyStatus.BAND, PropertyBadge.VIP, 16, 892, 6),
            ('40225', '2 xonali kvartira', 'Chilonzor', "Qatortol ko'chasi 14", DealType.SOTIB_OLISH,
             47800, 'USD', 2, '54.0', 2, 4, 1991, PropertyStatus.FAOL, PropertyBadge.ODDIY, 9, 210, 9),
            ('40231', '3 xonali kvartira', 'Chilonzor', 'Novza metro yonida', DealType.SOTIB_OLISH,
             58000, 'USD', 3, '70.0', 7, 9, 2005, PropertyStatus.FAOL, PropertyBadge.PREMIUM, 14, 604, 4),
            ('40244', '2 xonali kvartira', 'Chilonzor', "Chilonzor 6-kvartal", DealType.SOTIB_OLISH,
             39500, 'USD', 2, '46.0', 1, 4, 1987, PropertyStatus.FAOL, PropertyBadge.ODDIY, 7, 128, 1),
            ('40256', '3 xonali yangi bino', 'Yunusobod', "Yunusobod 4-kvartal", DealType.SOTIB_OLISH,
             72000, 'USD', 3, '88.0', 12, 16, 2024, PropertyStatus.FAOL, PropertyBadge.VIP, 20, 1130, 11),
            ('40262', '2 xonali kvartira', 'Mirzo Ulug\'bek', "Buyuk Ipak Yo'li 42", DealType.IJARA,
             4200000, 'UZS', 2, '64.0', 4, 9, 2010, PropertyStatus.FAOL, PropertyBadge.ODDIY, 11, 287, 3),
            ('40270', '1 xonali studiya', 'Chilonzor', "Chilonzor 8-kvartal", DealType.IJARA,
             2800000, 'UZS', 1, '38.0', 6, 9, 2016, PropertyStatus.SOTILGAN, PropertyBadge.ODDIY, 8, 455, 22),
            ('40277', '4 xonali kvartira', 'Yunusobod', "Amir Temur shoh ko'chasi", DealType.SOTIB_OLISH,
             95000, 'USD', 4, '112.0', 8, 12, 2019, PropertyStatus.FAOL, PropertyBadge.PREMIUM, 18, 762, 14),
            ('40283', '2 xonali kvartira', 'Chilonzor', "Chilonzor 22-kvartal", DealType.SOTIB_OLISH,
             51500, 'USD', 2, '58.0', 3, 9, 2008, PropertyStatus.ARXIV, PropertyBadge.ODDIY, 6, 94, 40),
        ]
        owners = [
            ('Dilshod Aliyev', '+998 90 111 41 62'),
            ('Kamola Rustamova', '+998 93 220 18 07'),
            ('Otabek Karimov', '+998 91 333 55 12'),
            ('Zilola Mahmudova', '+998 94 707 22 45'),
        ]
        made = []
        for i, row in enumerate(rows):
            (listing_id, title, district, address, deal_type, price, currency, rooms, area,
             floor, floors, year, status, badge, photos, views, days_ago) = row
            owner_name, owner_phone = owners[i % len(owners)]
            made.append(
                Property.objects.create(
                    agent=agent,
                    listing_id=listing_id,
                    title=title,
                    district=district,
                    address=address,
                    deal_type=deal_type,
                    price=Decimal(price),
                    currency=currency,
                    rooms=rooms,
                    area=Decimal(area),
                    floor=floor,
                    total_floors=floors,
                    built_year=year,
                    status=status,
                    badge=badge,
                    is_verified=status != PropertyStatus.ARXIV,
                    owner_name=owner_name,
                    owner_phone=owner_phone,
                    photo_count=photos,
                    views=views,
                    description=(
                        "Metroga 7 daqiqa piyoda. Uy g'ishtli, oynalar hovliga qaraydi. "
                        'Mebel kelishuv asosida qoladi.'
                    ),
                    created_at=now - timedelta(days=days_ago),
                )
            )
        return made

    # ---- clients -----------------------------------------------------------

    def _seed_clients(self, agent, now):
        # The first four rows are verbatim from the design board's table.
        rows = [
            ('Kamola Rustamova', '+998 93 220 18 07', '3 xona, Chilonzor', DealType.SOTIB_OLISH,
             '$50–60k', 50000, 60000, ClientStatus.QONGIROQ, LeadSource.MOBIL, 0.08, True),
            ('Sardor Tashmatov', '+998 90 455 77 21', 'Ijara, 2 xona', DealType.IJARA,
             "5 mln/oy", 5000000, 5000000, ClientStatus.KORSATUV, LeadSource.WEB, 1, True),
            ('Zilola Mahmudova', '+998 94 707 22 45', 'Yangi bino, 2 xona', DealType.SOTIB_OLISH,
             '$70–80k', 70000, 80000, ClientStatus.SHARTNOMADA, LeadSource.TELEGRAM, 3, True),
            ('Jasur Xolmatov', '+998 91 612 09 34', 'Sotish, Yunusobod', DealType.SOTIB_OLISH,
             '$61k', 61000, 61000, ClientStatus.FOTOGA, LeadSource.WEB, 4, False),
            ('Otabek Karimov', '+998 91 333 55 12', '2 xona, Novza', DealType.SOTIB_OLISH,
             '$45–55k', 45000, 55000, ClientStatus.KORSATUV, LeadSource.MOBIL, 5, True),
            ('Nigora Salimova', '+998 97 145 62 88', 'Ijara, 3 xona', DealType.IJARA,
             '6 mln/oy', 6000000, 6000000, ClientStatus.QONGIROQ, LeadSource.TELEGRAM, 6, False),
            ('Bekzod Yusupov', '+998 90 800 34 19', '4 xona, Yunusobod', DealType.SOTIB_OLISH,
             '$90–100k', 90000, 100000, ClientStatus.SHARTNOMADA, LeadSource.WEB, 8, True),
            ('Dilnoza Rahimova', '+998 93 512 77 40', 'Studiya, kunlik', DealType.KUNLIK,
             '450 ming/kun', 450000, 450000, ClientStatus.KORSATUV, LeadSource.MOBIL, 9, True),
            ('Alisher Nazarov', '+998 94 221 09 55', '3 xona, Chilonzor', DealType.SOTIB_OLISH,
             '$55–65k', 55000, 65000, ClientStatus.QONGIROQ, LeadSource.WEB, 11, False),
            ('Malika Tursunova', '+998 90 340 12 76', '2 xona, Qatortol', DealType.SOTIB_OLISH,
             '$40–50k', 40000, 50000, ClientStatus.FOTOGA, LeadSource.TELEGRAM, 12, True),
            ('Rustam Abdullayev', '+998 91 900 45 32', 'Ijara, 1 xona', DealType.IJARA,
             '3 mln/oy', 3000000, 3000000, ClientStatus.KORSATUV, LeadSource.MOBIL, 14, True),
            ('Gulnora Ismoilova', '+998 97 664 20 18', '3 xona, yangi bino', DealType.SOTIB_OLISH,
             '$75–85k', 75000, 85000, ClientStatus.SHARTNOMADA, LeadSource.WEB, 16, True),
            ('Shohruh Qodirov', '+998 93 118 55 09', '2 xona, Sergeli', DealType.SOTIB_OLISH,
             '$38–46k', 38000, 46000, ClientStatus.QONGIROQ, LeadSource.MOBIL, 18, False),
            ('Feruza Sattorova', '+998 90 277 63 41', 'Ijara, 2 xona', DealType.IJARA,
             '4,5 mln/oy', 4500000, 4500000, ClientStatus.KORSATUV, LeadSource.TELEGRAM, 19, True),
            ('Ulug\'bek Mirzayev', '+998 94 505 88 12', '4 xona, Mirobod', DealType.SOTIB_OLISH,
             '$110k', 110000, 110000, ClientStatus.FOTOGA, LeadSource.WEB, 21, True),
            ('Sevara Jo\'rayeva', '+998 91 432 17 60', '1 xona, Chilonzor', DealType.SOTIB_OLISH,
             '$30–36k', 30000, 36000, ClientStatus.QONGIROQ, LeadSource.MOBIL, 23, False),
            ('Doniyor Ergashev', '+998 90 611 24 85', '3 xona, Novza', DealType.SOTIB_OLISH,
             '$58–68k', 58000, 68000, ClientStatus.KORSATUV, LeadSource.WEB, 25, True),
            # Closed / rejected leads — excluded from the "faol mijozlar" KPI.
            ('Aziz Rahmonov', '+998 93 700 91 22', '2 xona, Chilonzor', DealType.SOTIB_OLISH,
             '$48k', 48000, 48000, ClientStatus.YOPILGAN, LeadSource.WEB, 28, True),
            ('Kamron Sobirov', '+998 97 222 44 90', 'Ijara, studiya', DealType.IJARA,
             '2,8 mln/oy', 2800000, 2800000, ClientStatus.YOPILGAN, LeadSource.TELEGRAM, 31, True),
            ('Laziz Umarov', '+998 91 355 66 07', '3 xona, byudjet past', DealType.SOTIB_OLISH,
             '$25k', 25000, 25000, ClientStatus.RAD, LeadSource.MOBIL, 34, False),
        ]
        made = []
        for row in rows:
            (name, phone, request, deal_type, budget_label, bmin, bmax,
             cstatus, source, days_ago, verified) = row
            created_at = now - timedelta(days=days_ago, hours=3)
            made.append(
                Client.objects.create(
                    agent=agent,
                    name=name,
                    phone=phone,
                    request=request,
                    deal_type=deal_type,
                    district=agent.district,
                    budget_label=budget_label,
                    budget_min=Decimal(bmin),
                    budget_max=Decimal(bmax),
                    status=cstatus,
                    source=source,
                    is_verified=verified,
                    note='Platforma tomonidan hudud va reyting bo\'yicha biriktirildi.',
                    created_at=created_at,
                    last_contact_at=created_at + timedelta(hours=2),
                )
            )
        return made

    # ---- deals -------------------------------------------------------------

    def _seed_deals(self, agent, clients, properties, now):
        by_name = {c.name: c for c in clients}
        by_listing = {p.listing_id: p for p in properties}
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Six deals closed this month — matches the "Bu oydagi bitimlar: 6" KPI.
        # Commissions total 18,4 mln so'm with a 12% platform cut.
        closed = [
            ('Zilola Mahmudova', '40256', 72000, 'USD', 3_600_000),
            ('Bekzod Yusupov', '40277', 95000, 'USD', 4_750_000),
            ('Gulnora Ismoilova', '40231', 58000, 'USD', 2_900_000),
            ('Aziz Rahmonov', '40225', 47800, 'USD', 2_390_000),
            ('Kamron Sobirov', '40270', 2800000, 'UZS', 2_800_000),
            ('Dilnoza Rahimova', '40219', 61200, 'USD', 1_960_000),
        ]
        # Spread the closings evenly over the month so far, so the KPI reads 6
        # even when the command runs on the 1st.
        span = max((now - month_start).total_seconds(), 0)
        for i, (name, listing, amount, currency, commission) in enumerate(closed):
            offset = span * (i + 1) / (len(closed) + 1)
            closed_at = now - timedelta(seconds=offset)
            Deal.objects.create(
                agent=agent,
                client=by_name[name],
                listing=by_listing.get(listing),
                stage=DealStage.YOPILGAN,
                amount=Decimal(amount),
                currency=currency,
                commission=Decimal(commission),
                platform_cut=Decimal(commission) * Decimal('0.12'),
                contract_signed=True,
                note='Shartnoma platformada e-imzo bilan tuzildi.',
                created_at=closed_at - timedelta(days=9),
                closed_at=closed_at,
            )

        # Open pipeline.
        pipeline = [
            ('Sardor Tashmatov', '40262', DealStage.KORSATUV, 4200000, 'UZS', 840_000, 4),
            ('Otabek Karimov', '40244', DealStage.KORSATUV, 39500, 'USD', 1_975_000, 6),
            ('Feruza Sattorova', '40262', DealStage.KORSATUV, 4500000, 'UZS', 900_000, 3),
            ('Malika Tursunova', '40225', DealStage.KELISHUV, 47800, 'USD', 2_390_000, 10),
            ('Doniyor Ergashev', '40231', DealStage.KELISHUV, 58000, 'USD', 2_900_000, 7),
            ('Jasur Xolmatov', '40218', DealStage.SHARTNOMA, 54000, 'USD', 2_700_000, 13),
            ('Ulug\'bek Mirzayev', '40277', DealStage.SHARTNOMA, 95000, 'USD', 4_750_000, 15),
            ('Laziz Umarov', '40283', DealStage.BEKOR, 51500, 'USD', 0, 24),
        ]
        for name, listing, stage, amount, currency, commission, days_ago in pipeline:
            Deal.objects.create(
                agent=agent,
                client=by_name[name],
                listing=by_listing.get(listing),
                stage=stage,
                amount=Decimal(amount),
                currency=currency,
                commission=Decimal(commission),
                platform_cut=Decimal(commission) * Decimal('0.12'),
                contract_signed=stage == DealStage.SHARTNOMA,
                created_at=now - timedelta(days=days_ago),
            )

        # Figmada "Top Makler'ga 8 bitim" yozilgan — ya'ni jami 32 bitim (40 - 8).
        # Shundan 6 tasi shu CRM ichida yopilgan, qolgani — oldingi tarix.
        closed_here = Deal.objects.filter(agent=agent, stage=DealStage.YOPILGAN).count()
        agent.historical_deals = 32 - closed_here
        agent.total_deals = 32
        # Darajani jami bitimdan qayta hisoblaymiz — agent avvaldan mavjud bo'lsa,
        # eski qiymat qolib ketmasin.
        agent.tier = tier_for(agent.total_deals)
        agent.save(update_fields=['historical_deals', 'total_deals', 'tier'])

    # ---- showings ----------------------------------------------------------

    def _seed_showings(self, agent, clients, properties, now):
        by_name = {c.name: c for c in clients}
        by_listing = {p.listing_id: p for p in properties}
        rows = [
            ('Sardor Tashmatov', '40262', 1, 15, "Uy egasi 15:00 da ochiq"),
            ('Otabek Karimov', '40244', 2, 11, 'Mijoz mashinada keladi'),
            ('Feruza Sattorova', '40262', 3, 17, 'Mebel holatini ko\'rmoqchi'),
            ('Doniyor Ergashev', '40231', 5, 12, 'Kadastr hujjatini olib borish'),
            ('Alisher Nazarov', '40218', 6, 14, ''),
        ]
        for name, listing, days_ahead, hour, note in rows:
            Showing.objects.create(
                agent=agent,
                client=by_name[name],
                listing=by_listing[listing],
                scheduled_at=(now + timedelta(days=days_ahead)).replace(
                    hour=hour, minute=0, second=0, microsecond=0
                ),
                status=ShowingStatus.REJALASHTIRILGAN,
                note=note,
            )

    # ---- activity ----------------------------------------------------------

    def _seed_activity(self, agent, now):
        rows = [
            (ActivityKind.MIJOZ, 'Kamola R. avtomatik biriktirildi — Mobil ilova', 2),
            (ActivityKind.KORSATUV, "Sardor T. uchun ko'rsatuv belgilandi — 40262", 5),
            (ActivityKind.SHARTNOMA, 'Zilola M. shartnomasi e-imzo bilan tasdiqlandi', 26),
            (ActivityKind.BITIM, 'Bekzod Y. bitimi yopildi — 4,75 mln komissiya', 50),
            (ActivityKind.REYTING, "Reyting 4,6 dan 4,7 ga ko'tarildi", 74),
            (ActivityKind.QONGIROQ, "Nigora S. ga qo'ng'iroq qilindi — javob yo'q", 96),
        ]
        for kind, text, hours_ago in rows:
            Activity.objects.create(
                agent=agent,
                kind=kind,
                text=text,
                created_at=now - timedelta(hours=hours_ago),
            )
