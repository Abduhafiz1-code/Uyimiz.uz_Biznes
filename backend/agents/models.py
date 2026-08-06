from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class AgentTier(models.TextChoices):
    """Reyting darajasi — the ladder shown on the CRM sidebar (frame 07)."""

    YANGI = 'Yangi', 'Yangi agent'
    FAOL = 'Faol', 'Faol makler'
    TAJRIBALI = 'Tajribali', 'Tajribali makler'
    TOP = 'Top', 'Top Makler'


#: Closed deals required to reach each tier. Used for the sidebar progress bar.
TIER_THRESHOLDS = {
    AgentTier.YANGI: 0,
    AgentTier.FAOL: 5,
    AgentTier.TAJRIBALI: 15,
    AgentTier.TOP: 40,
}

TIER_ORDER = [AgentTier.YANGI, AgentTier.FAOL, AgentTier.TAJRIBALI, AgentTier.TOP]


class CertificationStatus(models.TextChoices):
    KUTILMOQDA = 'Kutilmoqda', 'Kutilmoqda'
    TASDIQLANGAN = 'Tasdiqlangan', 'Tasdiqlangan'
    BEKOR = 'Bekor qilingan', 'Bekor qilingan'


class AgentManager(BaseUserManager):
    def create_user(self, phone, full_name='', password=None, **extra):
        if not phone:
            raise ValueError('Agentda telefon raqami bo\'lishi shart')
        agent = self.model(phone=phone, full_name=full_name, **extra)
        agent.set_password(password)
        agent.save(using=self._db)
        return agent

    def create_superuser(self, phone, full_name='', password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('certification', CertificationStatus.TASDIQLANGAN)
        return self.create_user(phone, full_name, password, **extra)


class Agent(AbstractBaseUser, PermissionsMixin):
    """A certified Uyimiz Agent — the CRM's only account type."""

    phone = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    district = models.CharField(max_length=64, blank=True, help_text='Biriktirilgan hudud')
    avatar_initials = models.CharField(max_length=4, blank=True)

    rating = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('0.0'))
    tier = models.CharField(max_length=16, choices=AgentTier.choices, default=AgentTier.YANGI)
    certification = models.CharField(
        max_length=20, choices=CertificationStatus.choices, default=CertificationStatus.KUTILMOQDA
    )
    #: Platform's cut of the agent's commission (10–15% per the business model).
    platform_share = models.PositiveSmallIntegerField(default=12)
    #: Fixed commission the agent charges the client (1–2%).
    commission_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.50'))
    avg_response_minutes = models.PositiveIntegerField(default=0)
    #: Career deals closed before this CRM started tracking them. The tier ladder
    #: counts a whole career, so this is the baseline `total_deals` builds on.
    historical_deals = models.PositiveIntegerField(default=0)
    #: historical_deals + deals closed inside the CRM. Kept denormalised so the
    #: sidebar and leaderboard do not re-aggregate on every request.
    total_deals = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateField(auto_now_add=True)

    objects = AgentManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        ordering = ['-rating', '-total_deals']

    def __str__(self):
        return self.full_name or self.phone

    @property
    def initials(self):
        if self.avatar_initials:
            return self.avatar_initials
        parts = [p for p in self.full_name.split() if p]
        return ''.join(p[0].upper() for p in parts[:2]) or self.phone[-2:]

    @property
    def next_tier(self):
        """The tier immediately above the current one, or None at the top."""
        try:
            index = TIER_ORDER.index(AgentTier(self.tier))
        except ValueError:
            index = 0
        if index + 1 >= len(TIER_ORDER):
            return None
        return TIER_ORDER[index + 1]

    def tier_progress(self):
        """Progress toward the next tier: (percent, deals_remaining, next_tier_label).

        Mirrors the sidebar widget "4,7 * · Top Makler'ga 8 bitim".
        """
        nxt = self.next_tier
        if nxt is None:
            return 100, 0, None
        floor = TIER_THRESHOLDS[AgentTier(self.tier)]
        ceiling = TIER_THRESHOLDS[nxt]
        span = max(ceiling - floor, 1)
        done = max(self.total_deals - floor, 0)
        percent = min(round(done / span * 100), 100)
        return percent, max(ceiling - self.total_deals, 0), nxt.label
