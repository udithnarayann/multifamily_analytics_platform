-- AI risk report persistence for real-data-only MVP.
--
-- This migration supports Freddie Mac MLPD loan-quarter observation reports first,
-- with nullable future support for HUD property reports. It intentionally does not
-- join HUD property records to Freddie Mac observations.
--
-- Recommended application approach:
--   Use create table if not exists for the portfolio/demo migration path so an
--   existing Supabase table is not destructively dropped. If you already created
--   an incompatible ai_risk_reports table manually, review differences and migrate
--   or recreate deliberately outside this script.

create extension if not exists pgcrypto;

create table if not exists public.ai_risk_reports (
  id uuid primary key default gen_random_uuid(),

  freddie_mac_observation_id uuid
    references public.freddie_mac_loan_quarter_observations(id)
    on delete cascade,

  hud_property_id uuid
    references public.properties(id)
    on delete cascade,

  risk_rating text not null,
  risk_score numeric(5,2) not null,
  summary text not null,
  key_risk_factors jsonb not null default '[]'::jsonb,
  loan_performance_analysis text not null,
  credit_metric_analysis text not null,
  property_analysis text,
  delinquency_analysis text not null,
  analyst_follow_up_questions jsonb not null default '[]'::jsonb,

  model_name text not null,
  model_version text,
  prompt_version text not null,

  input_snapshot jsonb not null default '{}'::jsonb,
  output_snapshot jsonb not null default '{}'::jsonb,
  data_source_labels jsonb not null default '[]'::jsonb,

  created_by uuid references auth.users(id),
  created_at timestamptz not null default now(),

  constraint ai_risk_reports_exactly_one_target_chk check (
    (
      case when freddie_mac_observation_id is not null then 1 else 0 end
      + case when hud_property_id is not null then 1 else 0 end
    ) = 1
  ),

  constraint ai_risk_reports_risk_rating_chk check (
    risk_rating in ('low', 'moderate', 'elevated', 'high', 'critical')
  ),

  constraint ai_risk_reports_risk_score_chk check (
    risk_score >= 0 and risk_score <= 100
  ),

  constraint ai_risk_reports_key_risk_factors_array_chk check (
    jsonb_typeof(key_risk_factors) = 'array'
  ),

  constraint ai_risk_reports_follow_up_questions_array_chk check (
    jsonb_typeof(analyst_follow_up_questions) = 'array'
  ),

  constraint ai_risk_reports_input_snapshot_object_chk check (
    jsonb_typeof(input_snapshot) = 'object'
  ),

  constraint ai_risk_reports_output_snapshot_object_chk check (
    jsonb_typeof(output_snapshot) = 'object'
  ),

  constraint ai_risk_reports_data_source_labels_array_chk check (
    jsonb_typeof(data_source_labels) = 'array'
  )
);

create index if not exists idx_ai_risk_reports_freddie_mac_observation_id
on public.ai_risk_reports(freddie_mac_observation_id);

create index if not exists idx_ai_risk_reports_hud_property_id
on public.ai_risk_reports(hud_property_id);

create index if not exists idx_ai_risk_reports_created_at_desc
on public.ai_risk_reports(created_at desc);

create index if not exists idx_ai_risk_reports_risk_rating
on public.ai_risk_reports(risk_rating);

create index if not exists idx_ai_risk_reports_key_risk_factors_gin
on public.ai_risk_reports using gin(key_risk_factors);

create index if not exists idx_ai_risk_reports_input_snapshot_gin
on public.ai_risk_reports using gin(input_snapshot);

alter table public.ai_risk_reports enable row level security;

drop policy if exists "Authenticated users can read AI risk reports"
on public.ai_risk_reports;

create policy "Authenticated users can read AI risk reports"
on public.ai_risk_reports
for select
to authenticated
using (true);

drop policy if exists "Authenticated users can insert own or local AI risk reports"
on public.ai_risk_reports;

create policy "Authenticated users can insert own or local AI risk reports"
on public.ai_risk_reports
for insert
to authenticated
with check (created_by = auth.uid() or created_by is null);

drop policy if exists "Users can update own AI risk reports"
on public.ai_risk_reports;

create policy "Users can update own AI risk reports"
on public.ai_risk_reports
for update
to authenticated
using (created_by = auth.uid())
with check (created_by = auth.uid());

drop policy if exists "Users can delete own AI risk reports"
on public.ai_risk_reports;

create policy "Users can delete own AI risk reports"
on public.ai_risk_reports
for delete
to authenticated
using (created_by = auth.uid());

grant select, insert, update, delete on table public.ai_risk_reports to authenticated;
grant select, insert, update, delete on table public.ai_risk_reports to service_role;
