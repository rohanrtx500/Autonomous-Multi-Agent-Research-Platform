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

export type ClaimStatus = 'supported' | 'partially_supported' | 'unsupported' | 'unverified';

export interface ClaimVerificationItem {
  claim_id: string;
  claim_text: string;
  section: string;
  citation_indices: number[];
  source_identifiers: string[];
  status: ClaimStatus;
  evidence_snippets: string[];
  confidence_score: number;
  verification_notes: string;
}

export interface CitationVerificationResult {
  total_claims: number;
  supported_claims: number;
  partially_supported_claims: number;
  unsupported_claims: number;
  unverified_claims: number;
  claims_with_citations: number;
  claims_missing_citations: number;
  citation_coverage: number;
  citation_correctness: number;
  unsupported_claim_rate: number;
  grounding_confidence: number;
  verification_status: string;
  claim_details: ClaimVerificationItem[];
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

  // Measurable metrics
  precision_at_k?: number | null;
  recall_at_k?: number | null;
  mrr?: number | null;
  context_relevance?: number | null;
  answer_relevance?: number | null;
  citation_coverage?: number | null;
  citation_correctness?: number | null;
  unsupported_claim_rate?: number | null;
  methodology?: string;
  limitations?: string[];
}

export interface ResearchResponse {
  job_id: string;
  status: string;
  objective: string;
  final_report_markdown?: string;
  evaluation_metrics?: EvaluationMetrics;
  citation_verification?: CitationVerificationResult;
  retrieved_papers_count: number;
  retrieved_web_count: number;
  retrieved_github_count: number;
  retrieved_user_docs_count?: number;
  agent_logs_count: number;
  agent_logs?: AgentExecutionLog[];
  execution_time_seconds: number;
  error_message?: string;
}

export interface PersistentJob {
  job_id: string;
  objective: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress_percent: number;
  current_step: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  execution_time_seconds: number;
  max_iterations: number;
  iteration_count: number;
  error_message?: string;
  final_report_markdown?: string;
  evaluation_metrics?: EvaluationMetrics;
  citation_verification?: CitationVerificationResult;
  agent_logs?: AgentExecutionLog[];
}
