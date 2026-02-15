export type AnyRecord = Record<string, unknown>;

export interface DecisionRow {
  rank: number;
  strategy: string;
  risk_adjusted_score: number;
  weighted_prob_loss: number;
  weighted_mean_contribution_eur: number;
}

export interface ScenarioRow {
  scenario: string;
  strategy: string;
  mean_contribution_eur: number;
  prob_loss: number;
}

export interface CityRow {
  city: string;
  state: string;
  lat: number;
  lon: number;
  launch_wave: string;
  strategy: string;
  board_signal: string;
  city_rank: number;
  risk_adjusted_city_score: number;
  city_prob_loss: number;
  expected_contribution_eur: number;
}

export interface RegulatoryRow {
  id: string;
  category: string;
  regulation: string;
  jurisdiction: string;
  requirement: string;
  effective_date: string;
  deadline_or_trigger: string;
  maximum_sanction: string;
  severity_score_1_to_5: number;
  likelihood_score_1_to_5: number;
  operational_owner: string;
  source_url: string;
  source_note: string;
}

export interface RegulatorySummary {
  count_total: number;
  count_high_severity: number;
  near_term_2026_2027: number;
  max_explicit_fine_eur: number;
  categories: Record<string, number>;
}

export interface ExecutiveSummary {
  recommended_strategy_risk_adjusted_score?: number;
  recommended_strategy_npv_5y_eur?: number;
  base_standard_prob_loss?: number;
  marketing_reject_count?: number;
  refresh_ok_sources?: number;
  refresh_total_sources?: number;
}

export interface KeyDecision {
  top_strategy?: string;
  top_strategy_npv?: number;
  is_stage_gated?: boolean;
}

export interface PresentationData {
  meta?: AnyRecord;
  executive_summary?: ExecutiveSummary;
  key_decision?: KeyDecision;
  decision_matrix?: DecisionRow[];
  scenario_summary?: ScenarioRow[];
  city_portfolio_plan?: CityRow[];
  city_recommendations?: CityRow[];
  regulatory_environment?: RegulatoryRow[];
  regulatory_summary?: RegulatorySummary;
}
