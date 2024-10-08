from django import forms
from .models import InvestmentAnalysis

class InvestmentAnalysisForm(forms.ModelForm):
    SECTOR_CHOICES = [
        ('housing', 'Housing'),
        ('education', 'Education'),
        ('healthcare', 'Healthcare')
    ]
    
    sector = forms.ChoiceField(choices=SECTOR_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    investment_amount = forms.DecimalField(
        max_digits=12, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter investment amount'})
    )
    estimated_return = forms.DecimalField(
        max_digits=12, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter estimated return'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe your investment plan'
        })
    )
    public_feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any public sentiment or feedback (optional)'
        })
    )

    class Meta:
        model = InvestmentAnalysis
        fields = ['sector', 'investment_amount', 'estimated_return', 'description', 'public_feedback']