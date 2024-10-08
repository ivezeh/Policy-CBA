from django.shortcuts import render
from django.views.generic import FormView
from django.contrib import messages
from .forms import InvestmentAnalysisForm
from .services import InvestmentAnalyzer, SentimentAnalyzer

class InvestmentAnalysisView(FormView):
    template_name = 'policy_analyzer/analysis.html'
    form_class = InvestmentAnalysisForm
    success_url = '#results'  # Anchor to results section

    def form_valid(self, form):
        analysis = form.save()
        
        # Perform investment analysis
        investment_analysis = InvestmentAnalyzer.analyze_investment(
            analysis.sector,
            analysis.investment_amount,
            analysis.estimated_return,
            analysis.description
        )
        
        # Analyze market sentiment if feedback is provided
        sentiment_analysis = None
        if analysis.public_feedback:
            sentiment_analysis = SentimentAnalyzer.analyze_market_sentiment(
                analysis.public_feedback
            )
        
        context = self.get_context_data(form=form)
        context.update({
            'analysis': analysis,
            'investment_analysis': investment_analysis,
            'sentiment_analysis': sentiment_analysis,
            'show_results': True
        })
        
        return render(self.request, self.template_name, context)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)