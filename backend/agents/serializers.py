from rest_framework import serializers

from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    initials = serializers.CharField(read_only=True)
    tier_percent = serializers.SerializerMethodField()
    tier_remaining = serializers.SerializerMethodField()
    tier_next_label = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = [
            'id',
            'phone',
            'full_name',
            'email',
            'district',
            'initials',
            'rating',
            'tier',
            'certification',
            'platform_share',
            'commission_rate',
            'avg_response_minutes',
            'total_deals',
            'joined_at',
            'tier_percent',
            'tier_remaining',
            'tier_next_label',
        ]
        read_only_fields = ['id', 'phone', 'rating', 'tier', 'total_deals', 'joined_at']

    def _progress(self, obj):
        if not hasattr(obj, '_cached_progress'):
            obj._cached_progress = obj.tier_progress()
        return obj._cached_progress

    def get_tier_percent(self, obj):
        return self._progress(obj)[0]

    def get_tier_remaining(self, obj):
        return self._progress(obj)[1]

    def get_tier_next_label(self, obj):
        return self._progress(obj)[2]


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
