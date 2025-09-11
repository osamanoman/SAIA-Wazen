"""
Knowledge Service for Text-Based Customer Support

This service provides text-based knowledge retrieval capabilities for customer support AI assistants.
It integrates with the existing company-based filtering system and provides intelligent search functionality.
"""

import logging
from typing import List, Dict, Any, Optional
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from product.models import KnowledgeCategory, KnowledgeArticle, KnowledgeSearchLog
from saia.utils import sanitize_search_query

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Service for retrieving text-based knowledge content for customer support"""
    
    def __init__(self, user=None):
        self.user = user
        self.company = user.company if user and hasattr(user, 'company') else None
    
    def search_knowledge(self, query: str, limit: int = 10, article_type: str = None) -> List[Dict[str, Any]]:
        """
        Enhanced intelligent search with intent recognition and multi-strategy approach

        Args:
            query: Search query string
            limit: Maximum number of results to return
            article_type: Filter by article type (optional)

        Returns:
            List of matching articles with relevance ranking
        """
        # Input validation and sanitization
        sanitized_query = sanitize_search_query(query)
        if not sanitized_query:
            logger.warning(f"Invalid or unsafe query provided: {query}")
            return []

        if not self.company:
            logger.warning(f"Knowledge search attempted without company context for user: {self.user}")
            return []

        # Validate limit parameter
        limit = max(1, min(limit, 50))  # Ensure limit is between 1 and 50

        # ENHANCED: Multi-strategy intelligent search
        results = self._intelligent_search(sanitized_query, limit, article_type)

        # Log the search for analytics
        self._log_search(query, len(results))

        return results

    def _intelligent_search(self, query: str, limit: int, article_type: str = None) -> List[Dict[str, Any]]:
        """
        Multi-strategy intelligent search with intent recognition
        """
        # Strategy 1: Intent-based search
        intent_results = self._search_by_intent(query, limit, article_type)
        if intent_results:
            return intent_results

        # Strategy 2: Enhanced keyword search
        keyword_results = self._search_by_keywords(query, limit, article_type)
        if keyword_results:
            return keyword_results

        # Strategy 3: Fallback broad search
        return self._search_fallback(query, limit, article_type)
        
    def _search_by_intent(self, query: str, limit: int, article_type: str = None) -> List[Dict[str, Any]]:
        """
        Search based on user intent recognition
        """
        # Intent mapping: user questions → knowledge base topics
        intent_map = {
            # Login/Access issues (Arabic)
            'تسجيل الدخول': ['تسجيل الدخول', 'login', 'مشاكل', 'دخول'],
            'لا استطيع': ['مشاكل', 'troubleshooting', 'تسجيل الدخول', 'login'],
            'نسيت كلمة المرور': ['كلمة المرور', 'password', 'نسيت', 'forgot'],

            # Insurance renewal (Arabic)
            'انتهى': ['تجديد', 'renewal', 'انتهاء', 'expiry'],
            'تأميني': ['تأمين', 'insurance', 'وثيقة', 'policy'],
            'اجدد': ['تجديد', 'renewal', 'renew'],
            'تجديد': ['تجديد', 'renewal', 'renew', 'تأمين'],

            # Account management (Arabic)
            'حساب': ['حساب', 'account', 'إدارة', 'management'],
            'ملف': ['ملف', 'profile', 'حساب', 'account'],

            # Support (Arabic)
            'مساعدة': ['دعم', 'support', 'مساعدة', 'help'],
            'مشكلة': ['مشاكل', 'problems', 'دعم', 'support'],
            'دعم': ['دعم', 'support', 'مساعدة', 'help'],

            # English equivalents
            'login': ['login', 'تسجيل الدخول', 'access', 'sign in'],
            'password': ['password', 'كلمة المرور', 'forgot', 'reset'],
            'renewal': ['renewal', 'تجديد', 'renew', 'expiry'],
            'expired': ['expired', 'انتهى', 'expiry', 'renewal'],
            'account': ['account', 'حساب', 'profile', 'management'],
            'help': ['help', 'مساعدة', 'support', 'دعم'],
            'support': ['support', 'دعم', 'help', 'مساعدة'],
        }

        # Extract intent from query
        query_lower = query.lower()
        search_terms = []

        for intent_key, related_terms in intent_map.items():
            if intent_key in query_lower:
                search_terms.extend(related_terms)
                break

        if not search_terms:
            return []

        # Search using extracted terms
        return self._execute_search_with_terms(search_terms, limit, article_type)

    def _search_by_keywords(self, query: str, limit: int, article_type: str = None) -> List[Dict[str, Any]]:
        """
        Enhanced keyword-based search with Arabic support
        """
        # Extract key terms from query
        key_terms = self._extract_key_terms(query)

        if not key_terms:
            return []

        return self._execute_search_with_terms(key_terms, limit, article_type)

    def _extract_key_terms(self, query: str) -> List[str]:
        """
        Extract meaningful keywords from user query
        """
        # Remove common Arabic stop words and question words
        stop_words = {
            'في', 'من', 'إلى', 'على', 'عن', 'مع', 'لا', 'ما', 'هذا', 'هذه', 'ذلك', 'تلك',
            'لماذا', 'كيف', 'متى', 'أين', 'ماذا', 'هل', 'لكن', 'أو', 'و', 'أن', 'إن',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'why', 'how', 'when', 'where', 'what', 'can', 'cannot', 'could', 'should', 'would'
        }

        # Split query into words and filter
        words = query.lower().split()
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]

        return key_terms
    
    def _execute_search_with_terms(self, search_terms: List[str], limit: int, article_type: str = None) -> List[Dict[str, Any]]:
        """
        Execute search using multiple terms with intelligent ranking
        """
        try:
            from django.db.models import Q

            # Build base queryset
            queryset = KnowledgeArticle.objects.filter(
                company=self.company,
                is_active=True
            )

            if article_type:
                queryset = queryset.filter(article_type=article_type)

            # Strategy 1: Exact title matches (highest priority)
            exact_matches = []
            for term in search_terms:
                exact_title_matches = queryset.filter(title__icontains=term)
                for article in exact_title_matches:
                    if article not in exact_matches:
                        exact_matches.append(article)

            # Strategy 2: FAQ articles with keyword matches (high priority)
            faq_matches = []
            faq_queryset = queryset.filter(category__name='FAQ')
            for term in search_terms:
                faq_keyword_matches = faq_queryset.filter(
                    Q(title__icontains=term) |
                    Q(content__icontains=term) |
                    Q(keywords__icontains=term)
                )
                for article in faq_keyword_matches:
                    if article not in exact_matches and article not in faq_matches:
                        faq_matches.append(article)

            # Strategy 3: General content matches (lower priority)
            search_q = Q()
            for term in search_terms:
                search_q |= (
                    Q(title__icontains=term) |
                    Q(content__icontains=term) |
                    Q(keywords__icontains=term)
                )

            general_matches = []
            general_results = queryset.filter(search_q).distinct()
            for article in general_results:
                if article not in exact_matches and article not in faq_matches:
                    general_matches.append(article)

            # Combine results with priority ranking
            prioritized_results = exact_matches + faq_matches + general_matches

            # Limit results
            final_results = prioritized_results[:limit]

            return self._format_results(final_results)

        except Exception as e:
            logger.error(f"Search execution failed: {e}")
            return []

    def _search_fallback(self, query: str, limit: int, article_type: str = None) -> List[Dict[str, Any]]:
        """
        Fallback broad search when specific searches fail
        """
        try:
            # Build base queryset
            queryset = KnowledgeArticle.objects.filter(
                company=self.company,
                is_active=True
            )

            if article_type:
                queryset = queryset.filter(article_type=article_type)

            # Broad search across all text fields
            from django.db.models import Q
            broad_search = (
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(keywords__icontains=query) |
                Q(category__name__icontains=query)
            )

            results = queryset.filter(broad_search)[:limit]

            return self._format_results(results)

        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []

    def _format_results(self, results) -> List[Dict[str, Any]]:
        """
        Format search results into standardized dictionary format
        """
        articles = []
        for article in results:
            articles.append({
                'id': article.id,
                'title': article.title,
                'content': article.content,
                'article_type': article.article_type,
                'category': article.category.name,
                'keywords': article.get_keywords_list(),
                'relevance_score': 1.0,  # Default score for non-ranked results
                'created_at': article.created_at,
                'updated_at': article.updated_at
            })
        return articles

    def search_knowledge_simple(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Simple keyword-based search for fallback when full-text search is not available
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching articles
        """
        if not self.company:
            return []
        
        try:
            # Split query into keywords
            keywords = [word.strip().lower() for word in query.split() if len(word.strip()) > 2]
            
            if not keywords:
                return []
            
            # Build Q objects for OR search across title, content, and keywords
            q_objects = Q()
            for keyword in keywords:
                q_objects |= (
                    Q(title__icontains=keyword) |
                    Q(content__icontains=keyword) |
                    Q(keywords__icontains=keyword)
                )
            
            # Execute search
            results = KnowledgeArticle.objects.filter(
                company=self.company,
                is_active=True
            ).filter(q_objects).order_by('display_order', 'title')[:limit]
            
            # Convert to list of dictionaries
            articles = []
            for article in results:
                articles.append({
                    'id': article.id,
                    'title': article.title,
                    'content': article.content,
                    'article_type': article.article_type,
                    'category': article.category.name,
                    'keywords': article.get_keywords_list(),
                    'relevance_score': 1.0,  # Simple search doesn't provide ranking
                    'created_at': article.created_at,
                    'updated_at': article.updated_at
                })
            
            # Log the search
            self._log_search(query, len(articles))
            
            return articles
            
        except Exception as e:
            logger.error(f"Simple knowledge search failed for company {self.company.name}: {e}")
            return []
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all knowledge categories for the company"""
        if not self.company:
            return []
        
        try:
            categories = KnowledgeCategory.objects.filter(
                company=self.company,
                is_active=True
            ).order_by('display_order', 'name')
            
            return [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'description': cat.description,
                    'article_count': cat.articles.filter(is_active=True).count()
                }
                for cat in categories
            ]
            
        except Exception as e:
            logger.error(f"Failed to get categories for company {self.company.name}: {e}")
            return []
    
    def get_articles_by_category(self, category_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all articles in a specific category"""
        if not self.company:
            return []
        
        try:
            articles = KnowledgeArticle.objects.filter(
                company=self.company,
                category__name__iexact=category_name,
                is_active=True
            ).order_by('display_order', 'title')[:limit]
            
            return [
                {
                    'id': article.id,
                    'title': article.title,
                    'content': article.content,
                    'article_type': article.article_type,
                    'category': article.category.name,
                    'keywords': article.get_keywords_list(),
                    'created_at': article.created_at,
                    'updated_at': article.updated_at
                }
                for article in articles
            ]
            
        except Exception as e:
            logger.error(f"Failed to get articles by category for company {self.company.name}: {e}")
            return []
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific article by ID"""
        if not self.company:
            return None
        
        try:
            article = KnowledgeArticle.objects.get(
                id=article_id,
                company=self.company,
                is_active=True
            )
            
            return {
                'id': article.id,
                'title': article.title,
                'content': article.content,
                'article_type': article.article_type,
                'category': article.category.name,
                'keywords': article.get_keywords_list(),
                'created_at': article.created_at,
                'updated_at': article.updated_at
            }
            
        except KnowledgeArticle.DoesNotExist:
            logger.warning(f"Article {article_id} not found for company {self.company.name}")
            return None
        except Exception as e:
            logger.error(f"Failed to get article {article_id} for company {self.company.name}: {e}")
            return None
    
    def _log_search(self, query: str, results_count: int):
        """Log search query for analytics"""
        if not self.company:
            return
        
        try:
            KnowledgeSearchLog.objects.create(
                company=self.company,
                query=query,
                results_count=results_count
            )
        except Exception as e:
            logger.error(f"Failed to log search query: {e}")
    
    def get_search_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get search analytics for the company"""
        if not self.company:
            return {}
        
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            since_date = timezone.now() - timedelta(days=days)
            
            logs = KnowledgeSearchLog.objects.filter(
                company=self.company,
                created_at__gte=since_date
            )
            
            total_searches = logs.count()
            successful_searches = logs.filter(results_count__gt=0).count()
            
            # Most common queries
            common_queries = logs.values('query').annotate(
                count=models.Count('query')
            ).order_by('-count')[:10]
            
            return {
                'total_searches': total_searches,
                'successful_searches': successful_searches,
                'success_rate': (successful_searches / total_searches * 100) if total_searches > 0 else 0,
                'common_queries': list(common_queries)
            }
            
        except Exception as e:
            logger.error(f"Failed to get search analytics for company {self.company.name}: {e}")
            return {}
