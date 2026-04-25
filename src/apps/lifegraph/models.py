from django.conf import settings
from django.db import models


class LifeNode(models.Model):
    class Privacy(models.TextChoices):
        PRIVATE = "private", "仅自己"
        FRIENDS = "friends", "指定好友"
        PUBLIC = "public", "公开"

    class SourceType(models.TextChoices):
        TEXT = "text", "文本"
        VOICE = "voice", "语音"
        IMAGE = "image", "图片"
        VIDEO = "video", "视频"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="所有者",
        on_delete=models.CASCADE,
        related_name="life_nodes",
    )
    raw_text = models.TextField("原始输入")
    title = models.CharField("标题", max_length=255, blank=True, default="")
    what = models.TextField("事件内容", blank=True, default="")
    where_text = models.CharField("地点", max_length=255, blank=True, default="")
    where_lat = models.DecimalField("纬度", max_digits=9, decimal_places=6, null=True, blank=True)
    where_lng = models.DecimalField("经度", max_digits=9, decimal_places=6, null=True, blank=True)
    occurred_at = models.DateTimeField("发生时间", db_index=True)
    privacy = models.CharField(
        "隐私",
        max_length=20,
        choices=Privacy.choices,
        default=Privacy.PRIVATE,
        db_index=True,
    )
    source_type = models.CharField(
        "来源类型",
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.TEXT,
        db_index=True,
    )
    ai_parsed = models.BooleanField("AI 已解析", default=False)
    parsed_payload = models.JSONField("解析结果", blank=True, default=dict)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["-occurred_at", "-id"]
        indexes = [
            models.Index(fields=["owner", "-occurred_at", "-id"], name="idx_lifenode_owner_time"),
        ]
        verbose_name = "LifeNode"
        verbose_name_plural = "LifeNodes"

    def __str__(self) -> str:
        return self.title or self.raw_text[:40] or f"LifeNode {self.pk}"


class NodeParticipant(models.Model):
    class Role(models.TextChoices):
        PARTICIPANT = "participant", "参与者"

    class Status(models.TextChoices):
        SELF = "self", "自己"
        PENDING = "pending", "待确认"
        CONFIRMED = "confirmed", "已确认"
        REJECTED = "rejected", "已拒绝"

    node = models.ForeignKey(
        LifeNode,
        verbose_name="节点",
        on_delete=models.CASCADE,
        related_name="participants",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="用户",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="life_participations",
    )
    display_name = models.CharField("显示名称", max_length=150)
    role = models.CharField(
        "角色",
        max_length=30,
        choices=Role.choices,
        default=Role.PARTICIPANT,
    )
    status = models.CharField(
        "状态",
        max_length=20,
        choices=Status.choices,
        default=Status.SELF,
        db_index=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["node", "user"],
                name="unique_lifenode_user_participant",
                condition=models.Q(user__isnull=False),
            ),
        ]
        verbose_name = "NodeParticipant"
        verbose_name_plural = "NodeParticipants"

    def __str__(self) -> str:
        return self.display_name
