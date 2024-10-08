from django.db import models

class InvestmentAnalysis(models.Model):
    SECTOR_CHOICES = [
        ('housing', 'Housing & Real Estate'),
        ('education', 'Education'),
        ('healthcare', 'Healthcare')
    ]
    
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES)
    investment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_return = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    public_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sector.capitalize()} Investment Analysis - ${self.investment_amount}"