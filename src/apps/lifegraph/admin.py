from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import LifeNode, NodeParticipant


@admin.register(LifeNode)
class LifeNodeAdmin(ModelAdmin):
    list_display = ("id", "owner", "occurred_at", "raw_text_excerpt")
    list_filter = ("privacy", "source_type", "ai_parsed")
    search_fields = ("raw_text", "title", "what", "owner__username")
    ordering = ("-occurred_at", "-id")

    @admin.display(description="原始输入")
    def raw_text_excerpt(self, obj):
        return obj.raw_text[:60]


@admin.register(NodeParticipant)
class NodeParticipantAdmin(ModelAdmin):
    list_display = ("id", "node", "display_name", "user", "status")
    list_filter = ("status", "role")
    search_fields = ("display_name", "user__username", "node__raw_text")
