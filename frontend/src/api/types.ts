import type { components } from "./schema";

type S = components["schemas"];

export type Account = S["AccountOut"];
export type Assessment = S["AssessmentOut"];
export type Propagation = S["PropagationOut"];
export type Shap = S["ShapOut"];
export type ShapContribution = S["ShapContribution"];
export type Features = S["FeaturesOut"];
export type FeatureValue = S["FeatureValueOut"];
export type Temporal = S["TemporalOut"];
export type Transaction = S["TransactionOut"];
export type TransactionPage = S["TransactionPage"];
export type Neighborhood = S["NeighborhoodOut"];
export type NeighborhoodNode = S["NeighborhoodNode"];
export type NeighborhoodEdge = S["NeighborhoodEdge"];
export type PathQuery = S["PathQueryOut"];
export type Path = S["PathOut"];
export type PathDetail = S["PathDetailOut"];
export type GraphMetrics = S["GraphMetricsOut"];
export type Community = S["CommunityOut"];
export type CommunityPage = S["CommunityPage"];
export type CommunityDetail = S["CommunityDetailOut"];
export type AccountCommunity = S["AccountCommunityOut"];
export type Context = S["ContextOut"];
export type Lineage = S["LineageOut"];
export type Case = S["CaseOut"];
export type Subject = S["SubjectOut"];
export type Finding = S["FindingOut"];
export type User = S["UserOut"];
export type LoginResponse = S["LoginResponse"];
export type IngestionRun = S["IngestionRunOut"];
export type IngestionAccepted = S["IngestionAccepted"];
export type PipelineRun = S["PipelineRunOut"];
export type PipelineAccepted = S["PipelineAccepted"];
export type Model = S["ModelOut"];
export type Profile = S["ProfileOut"];
export type AuditEvent = S["AuditEventOut"];
export type ErrorEnvelope = S["ErrorEnvelope"];

export interface Page<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  total_is_capped: boolean;
}

export type Role = "ADMIN" | "INVESTIGATOR" | "ANALYST";
export type Tier = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type CaseStatus = "OPEN" | "IN_REVIEW" | "ESCALATED" | "RESOLVED" | "FALSE_POSITIVE" | "CLOSED";
export type Priority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
