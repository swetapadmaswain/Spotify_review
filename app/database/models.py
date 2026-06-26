from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from .connection import Base


class DataCollectionRun(Base):
    """Track data collection runs"""
    __tablename__ = 'data_collection_runs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    records_collected = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default='running')
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<DataCollectionRun(id={self.id}, source={self.source}, status={self.status})>"


class RawDataMetadata(Base):
    """Track raw data files and their processing status"""
    __tablename__ = 'raw_data_metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)
    file_path = Column(String(255), nullable=False)
    record_count = Column(Integer, nullable=True)
    collection_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed = Column(Boolean, nullable=False, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<RawDataMetadata(id={self.id}, source={self.source}, processed={self.processed})>"


class ProcessedReview(Base):
    """Store processed review data"""
    __tablename__ = 'processed_reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(255), nullable=True)  # Original ID from source
    source = Column(String(50), nullable=False)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    author = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=True)
    score = Column(Integer, nullable=True)  # For Reddit/social media
    version = Column(String(50), nullable=True)
    url = Column(String(500), nullable=True)
    subreddit = Column(String(100), nullable=True)  # For Reddit
    created_at = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<ProcessedReview(id={self.id}, source={self.source}, author={self.author})>"


class SentimentAnalysis(Base):
    """Store sentiment analysis results for a review"""
    __tablename__ = 'sentiment_analysis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey('processed_reviews.id'), nullable=True)
    sentiment = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=True)
    emotion = Column(String(50), nullable=True)
    intensity = Column(String(20), nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SentimentAnalysis(id={self.id}, review_id={self.review_id}, sentiment={self.sentiment})>"


class TopicAnalysis(Base):
    """Store topic analysis results for a review"""
    __tablename__ = 'topic_analysis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey('processed_reviews.id'), nullable=True)
    primary_topic = Column(String(100), nullable=True)
    secondary_topics = Column(JSON, nullable=True)
    relevance_scores = Column(JSON, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TopicAnalysis(id={self.id}, review_id={self.review_id}, primary_topic={self.primary_topic})>"


class EntityAnalysis(Base):
    """Store entity analysis results for a review"""
    __tablename__ = 'entity_analysis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey('processed_reviews.id'), nullable=True)
    entities = Column(JSON, nullable=True)
    entity_types = Column(JSON, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<EntityAnalysis(id={self.id}, review_id={self.review_id})>"


class RagCache(Base):
    """Cache RAG query results"""
    __tablename__ = 'rag_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<RagCache(id={self.id}, query='{self.query[:20]}...')>"


# ─── Phase 3: Insight Store Models ───────────────────────────────────────────

class PatternInsight(Base):
    """Store detected patterns (temporal, thematic, cross-platform)"""
    __tablename__ = 'pattern_insights'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_type = Column(String(50), nullable=True)   # temporal / thematic / cross_platform
    pattern_description = Column(Text, nullable=True)
    frequency = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)
    time_period = Column(String(20), nullable=True)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PatternInsight(id={self.id}, type={self.pattern_type})>"


class UserSegment(Base):
    """Store user segment definitions and metadata"""
    __tablename__ = 'user_segments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment_name = Column(String(100), nullable=True)
    segment_criteria = Column(JSON, nullable=True)
    user_count = Column(Integer, nullable=True)
    primary_challenges = Column(JSON, nullable=True)   # replaces TEXT[]
    avg_sentiment = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserSegment(id={self.id}, name={self.segment_name})>"


class RootCauseAnalysisResult(Base):
    """Store root cause analysis results for topics"""
    __tablename__ = 'root_cause_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_topic = Column(String(100), nullable=True)
    root_causes = Column(JSON, nullable=True)
    intermediate_factors = Column(JSON, nullable=True)
    surface_symptoms = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<RootCauseAnalysisResult(id={self.id}, topic={self.issue_topic})>"


class UnmetNeed(Base):
    """Store identified unmet user needs with priority scores"""
    __tablename__ = 'unmet_needs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    need_description = Column(Text, nullable=True)
    need_category = Column(String(50), nullable=True)
    request_count = Column(Integer, nullable=True)
    priority_score = Column(Float, nullable=True)
    strategic_impact = Column(String(20), nullable=True)
    identified_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UnmetNeed(id={self.id}, category={self.need_category})>"


# ─── Phase 4: Reporting & Recommendations Models ─────────────────────────────

class Recommendation(Base):
    """Store strategic recommendations generated from insights"""
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # product / algorithm / ux / education
    priority = Column(String(20), nullable=True)   # high / medium / low
    complexity = Column(String(20), nullable=True)
    expected_impact = Column(String(20), nullable=True)
    success_metrics = Column(JSON, nullable=True)
    dependencies = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Recommendation(id={self.id}, title={self.title})>"


class RoadmapItem(Base):
    """Product roadmap items derived from recommendations"""
    __tablename__ = 'roadmap_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), nullable=True)
    estimated_effort = Column(String(20), nullable=True)
    quarter = Column(String(10), nullable=True)
    success_metrics = Column(JSON, nullable=True)
    dependencies = Column(JSON, nullable=True)
    recommendation_id = Column(Integer, ForeignKey('recommendations.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<RoadmapItem(id={self.id}, title={self.title})>"


class GeneratedReport(Base):
    """Persisted comprehensive insight reports"""
    __tablename__ = 'generated_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_type = Column(String(50), nullable=False, default='comprehensive')
    template_type = Column(String(50), nullable=True)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<GeneratedReport(id={self.id}, type={self.report_type})>"
