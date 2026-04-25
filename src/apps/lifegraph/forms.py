from django import forms

from .models import LifeNode


class LifeNodeQuickCreateForm(forms.ModelForm):
    class Meta:
        model = LifeNode
        fields = ["raw_text", "occurred_at"]
        widgets = {
            "raw_text": forms.Textarea(attrs={"rows": 3, "placeholder": "记录一件刚发生或曾经发生的事"}),
            "occurred_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
