import os
import requests
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .huggingface_nlp import analyze_feedback

class LegislativeImpactAnalyzer:
    API_KEY = os.getenv('OPENSTATES_API_KEY', 'bb9c450e-a796-46f8-8221-fa926611fd27')
    BASE_URL = "https://v3.openstates.org/bills"
    
    @classmethod
    def analyze_legislative_impact(cls, sector, investment_description, investment_amount):
        relevant_bills = cls._fetch_relevant_bills(sector, investment_description)
        return cls._calculate_impact(relevant_bills, investment_amount)
    
    @classmethod
    def _fetch_relevant_bills(cls, sector, description):
        params = {
            'jurisdiction': 'California',
            'q': sector,
            'per_page': 20,
            'sort': 'updated_desc'
        }
        headers = {'X-API-Key': cls.API_KEY}
        
        try:
            response = requests.get(cls.BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            bills = response.json().get('results', [])
            
            if not bills or not description:
                return bills
            
            return cls._rank_bills_by_relevance(bills, description)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching bills: {e}")
            return []
    
    @staticmethod
    def _rank_bills_by_relevance(bills, description):
        bill_texts = [f"{b.get('title', '')} {b.get('impact_clause', '')}" for b in bills]
        all_texts = bill_texts + [description]
        
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        description_vector = tfidf_matrix[-1]
        similarity_scores = cosine_similarity(description_vector, tfidf_matrix[:-1])
        
        scored_bills = list(zip(bills, similarity_scores[0]))
        return sorted(scored_bills, key=lambda x: x[1], reverse=True)
    
    @staticmethod
    def _assess_bill_impact(bill):
        latest_action = bill.get('latest_action_description', '').lower()
        impact_magnitude = 0.1  # default impact
        probability = 0.3  # default probability
        
        # Determine probability based on latest action
        if 'chaptered by secretary of state' in latest_action:
            probability = 1.0
            impact_magnitude = 0.2
        elif 'approved by the governor' in latest_action:
            probability = 1.0
            impact_magnitude = 0.2
        elif 'vetoed by governor' in latest_action:
            probability = 0  # Bill was rejected
            impact_magnitude = 0
        elif 'died pursuant to' in latest_action:
            probability = 0  # Bill is dead
            impact_magnitude = 0
        elif 'from committee' in latest_action:
            probability = 0.5
        elif 'introduced' in latest_action:
            probability = 0.3
        
        # Determine if it's a potential risk or opportunity
        is_risk = False
        lower_title = bill.get('title', '').lower()
        risk_keywords = ['tax', 'fee', 'penalty', 'restrict', 'prohibit', 'limit']
        opportunity_keywords = ['tax credit', 'incentive', 'grant', 'streamline', 'simplify']
        
        # Check for risk keywords first, then opportunity keywords
        if any(keyword in lower_title for keyword in risk_keywords):
            is_risk = True
            # Check if it's actually an opportunity (e.g., "tax credit")
            if any(keyword in lower_title for keyword in opportunity_keywords):
                is_risk = False
        
        return {
            'impact_magnitude': impact_magnitude * (-1 if is_risk else 1),
            'probability': probability,
            'is_risk': is_risk
        }

    @classmethod
    def _calculate_impact(cls, relevant_bills, investment_amount):
        total_impact = 0
        risk_factors = []
        opportunities = []
        
        for bill, relevance_score in relevant_bills:
            impact_assessment = cls._assess_bill_impact(bill)
            
            # Only consider bills that aren't dead or vetoed
            if impact_assessment['probability'] > 0:
                impact = impact_assessment['impact_magnitude'] * impact_assessment['probability'] * relevance_score
                
                impact_details = {
                    'bill_title': bill.get('title', 'Untitled'),
                    'bill_id': bill.get('identifier', 'No ID'),
                    'status': bill.get('latest_action_description', 'Status unknown'),
                    'last_updated': bill.get('latest_action_date', 'Date unknown'),
                    'potential_impact': f"{impact_assessment['impact_magnitude']*100:+.1f}%",
                    'probability': f"{impact_assessment['probability']*100:.0f}%",
                    'relevance': f"{relevance_score:.2f}",
                    'subjects': bill.get('subject', ['Not specified']),
                    'url': bill.get('openstates_url', '#')
                }
                
                if impact_assessment['is_risk']:
                    risk_factors.append(impact_details)
                    total_impact += impact  # impact is already negative for risks
                else:
                    opportunities.append(impact_details)
                    total_impact += impact
        
        adjusted_roi = investment_amount * (1 + total_impact)
        
        return {
            'adjusted_roi': adjusted_roi,
            'potential_impact_percentage': total_impact * 100,
            'risk_factors': risk_factors,
            'opportunities': opportunities
        } 


class InvestmentAnalyzer:
    @staticmethod
    def analyze_investment(sector, investment_amount, estimated_return, description):
        try:
            investment_amount = float(investment_amount)
            estimated_return = float(estimated_return)
            roi = (estimated_return - investment_amount) / investment_amount
            
            legislative_impact = LegislativeImpactAnalyzer.analyze_legislative_impact(
                sector, description, investment_amount
            )
            
            return {
                'base_roi': roi,
                'base_roi_percentage': roi * 100,
                'adjusted_roi': legislative_impact['adjusted_roi'],
                'adjusted_roi_percentage': (legislative_impact['adjusted_roi'] - investment_amount) / investment_amount * 100,
                'legislative_impact': legislative_impact['potential_impact_percentage'],
                'risk_factors': legislative_impact['risk_factors'],
                'opportunities': legislative_impact['opportunities']
            }
        except ValueError as e:
            return {
                'error': f"Error in calculation: {str(e)}",
                'base_roi': 0,
                'adjusted_roi': 0,
                'legislative_impact': 0,
                'risk_factors': [],
                'opportunities': []
            }

class SentimentAnalyzer:
    @staticmethod
    def analyze_market_sentiment(feedback):
        result = analyze_feedback(feedback)
        return {
            'sentiment': result[0],
            'confidence': result[1],
            'market_implications': SentimentAnalyzer._interpret_sentiment(result[0])
        }
    
    @staticmethod
    def _interpret_sentiment(sentiment):
        if sentiment == 'Positive':
            return "Favorable market reception likely"
        elif sentiment == 'Negative':
            return "Potential market resistance"
        else:
            return "Mixed market reception possible"