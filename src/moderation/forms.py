from django import forms
from .models import ProductProposal

class ProposalCreateForm(forms.ModelForm):
    class Meta:
        model = ProductProposal
        fields = ["name", "kind", "photo", "kcal", "proteins", "fats", "carbs", "categories_text", "comment"]

    def clean_name(self):
        return (self.cleaned_data.get("name") or "").strip()

    def clean_kind(self):
        return (self.cleaned_data.get("kind") or "").strip()

class ProposalModerateForm(forms.ModelForm):
    class Meta:
        model = ProductProposal
        fields = ["name", "kind", "kcal", "proteins", "fats", "carbs", "categories_text", "status"]
