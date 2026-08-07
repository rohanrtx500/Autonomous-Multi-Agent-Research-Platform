export interface PaperItem {
  id: string;
  title: string;
  authors: string[];
  published_year?: number;
  abstract: string;
  url: string;
  pdf_url?: string;
  citation_count?: number;
  venue?: string;
}

export interface SourceDocument {
  id: string;
  title: string;
  content: string;
  source_type: 'arxiv' | 'semantic_scholar' | 'web' | 'github' | 'user_doc';
  url?: string;
  score: number;
}

export interface AgentExecutionLog {
  timestamp: string;
  agent_name: string;
  status: string;
  execution_time_ms: number;
  decision_reasoning: string;
  details?: Record<string, any>;
}

export interface EvaluationMetrics {
  faithfulness_score: number;
  relevance_score: number;
  grounding_score: number;
  confidence_score: number;
  hallucination_risk: number;
  reasoning_quality: number;
  is_acceptable: boolean;
  critique_comments: string[];
}

export interface ResearchResponse {
  job_id: string;
  status: string;
  objective: string;
  final_report_markdown?: string;
  evaluation_metrics?: EvaluationMetrics;
  retrieved_papers_count: number;
  retrieved_web_count: number;
  retrieved_github_count: number;
  agent_logs_count: number;
  agent_logs?: AgentExecutionLog[];
  execution_time_seconds: number;
}
