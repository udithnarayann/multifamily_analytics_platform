-- SQL-backed analytics summaries for the real-data-only MVP.
-- Apply in the Supabase SQL editor or through a migration workflow.

create or replace function public.mlpd_reporting_quarter_sort_key(p_quarter text)
returns integer
language sql
immutable
security invoker
as $$
  select case
    when p_quarter ~ '^y[0-9]{2}q[1-4]$' then
      (
        case
          when substring(p_quarter from 2 for 2)::int <= 49
            then 2000 + substring(p_quarter from 2 for 2)::int
          else 1900 + substring(p_quarter from 2 for 2)::int
        end
      ) * 10 + substring(p_quarter from 5 for 1)::int
    else null
  end;
$$;

create index if not exists idx_properties_state
on public.properties(state);

create index if not exists idx_properties_geocode_quality
on public.properties(geocode_quality);

create index if not exists idx_fm_obs_reporting_quarter
on public.freddie_mac_loan_quarter_observations(reporting_quarter);

create index if not exists idx_fm_obs_quarter_state
on public.freddie_mac_loan_quarter_observations(reporting_quarter, property_state);

create index if not exists idx_fm_obs_quarter_status
on public.freddie_mac_loan_quarter_observations(reporting_quarter, mortgage_status_code);

create index if not exists idx_fm_obs_quarter_metro
on public.freddie_mac_loan_quarter_observations(reporting_quarter, property_metro);

create index if not exists idx_ingestion_runs_source_started
on public.ingestion_runs(source_name, started_at desc);

create or replace view public.v_hud_property_totals as
select
  count(*)::bigint as total_hud_properties,
  coalesce(sum(total_units), 0)::bigint as total_units,
  coalesce(sum(total_assisted_units), 0)::bigint as total_assisted_units
from public.properties;

create or replace view public.v_hud_property_count_by_state as
select
  coalesce(state, 'unknown') as key,
  count(*)::bigint as count
from public.properties
group by coalesce(state, 'unknown');

create or replace view public.v_hud_property_count_by_geocode_quality as
select
  coalesce(geocode_quality, 'unknown') as key,
  count(*)::bigint as count
from public.properties
group by coalesce(geocode_quality, 'unknown');

create or replace view public.v_freddie_mac_mlpd_base_summary as
select
  count(*)::bigint as total_loan_quarter_observations,
  count(distinct loan_id)::bigint as distinct_loan_count,
  (
    select reporting_quarter
    from public.freddie_mac_loan_quarter_observations
    where public.mlpd_reporting_quarter_sort_key(reporting_quarter) is not null
    order by public.mlpd_reporting_quarter_sort_key(reporting_quarter), reporting_quarter
    limit 1
  ) as min_reporting_quarter,
  (
    select reporting_quarter
    from public.freddie_mac_loan_quarter_observations
    where public.mlpd_reporting_quarter_sort_key(reporting_quarter) is not null
    order by public.mlpd_reporting_quarter_sort_key(reporting_quarter) desc, reporting_quarter desc
    limit 1
  ) as max_reporting_quarter,
  avg(original_ltv) as average_original_ltv,
  avg(original_dcr) as average_original_dcr,
  avg(note_rate) as average_note_rate
from public.freddie_mac_loan_quarter_observations;

create or replace view public.v_freddie_mac_count_by_status as
select
  coalesce(mortgage_status_code::text, 'unknown') as key,
  count(*)::bigint as count
from public.freddie_mac_loan_quarter_observations
group by coalesce(mortgage_status_code::text, 'unknown');

create or replace view public.v_freddie_mac_count_by_property_state as
select
  coalesce(property_state, 'unknown') as key,
  count(*)::bigint as count
from public.freddie_mac_loan_quarter_observations
group by coalesce(property_state, 'unknown');

create or replace view public.v_freddie_mac_latest_quarter as
select reporting_quarter
from public.freddie_mac_loan_quarter_observations
where public.mlpd_reporting_quarter_sort_key(reporting_quarter) is not null
order by public.mlpd_reporting_quarter_sort_key(reporting_quarter) desc, reporting_quarter desc
limit 1;

create or replace view public.v_freddie_mac_latest_quarter_summary as
select
  l.reporting_quarter,
  count(f.*)::bigint as observation_count,
  count(distinct f.loan_id)::bigint as distinct_loan_count,
  sum(f.ending_balance) as total_ending_balance,
  avg(f.original_ltv) as average_original_ltv,
  avg(f.original_dcr) as average_original_dcr,
  avg(f.note_rate) as average_note_rate
from public.v_freddie_mac_latest_quarter l
left join public.freddie_mac_loan_quarter_observations f
  on f.reporting_quarter = l.reporting_quarter
group by l.reporting_quarter;

create or replace view public.v_freddie_mac_latest_quarter_count_by_status as
select
  coalesce(f.mortgage_status_code::text, 'unknown') as key,
  count(*)::bigint as count
from public.freddie_mac_loan_quarter_observations f
join public.v_freddie_mac_latest_quarter l
  on f.reporting_quarter = l.reporting_quarter
group by coalesce(f.mortgage_status_code::text, 'unknown');

create or replace view public.v_freddie_mac_latest_quarter_count_by_state as
select
  coalesce(f.property_state, 'unknown') as key,
  count(*)::bigint as count
from public.freddie_mac_loan_quarter_observations f
join public.v_freddie_mac_latest_quarter l
  on f.reporting_quarter = l.reporting_quarter
group by coalesce(f.property_state, 'unknown');

create or replace view public.v_freddie_mac_latest_quarter_top_metros_by_balance as
select
  coalesce(f.property_metro, 'unknown') as key,
  sum(f.ending_balance) as total_ending_balance,
  count(*)::bigint as observation_count
from public.freddie_mac_loan_quarter_observations f
join public.v_freddie_mac_latest_quarter l
  on f.reporting_quarter = l.reporting_quarter
group by coalesce(f.property_metro, 'unknown')
order by sum(f.ending_balance) desc nulls last, coalesce(f.property_metro, 'unknown')
limit 10;

create or replace function public.get_hud_property_summary()
returns jsonb
language sql
stable
security invoker
as $$
  select jsonb_build_object(
    'total_hud_properties', t.total_hud_properties,
    'total_units', t.total_units,
    'total_assisted_units', t.total_assisted_units,
    'property_count_by_state', coalesce((
      select jsonb_agg(jsonb_build_object('key', key, 'count', count) order by key)
      from public.v_hud_property_count_by_state
    ), '[]'::jsonb),
    'top_states_by_property_count', coalesce((
      select jsonb_agg(jsonb_build_object('key', key, 'count', count) order by count desc, key)
      from (
        select key, count
        from public.v_hud_property_count_by_state
        order by count desc, key
        limit 10
      ) s
    ), '[]'::jsonb),
    'count_by_geocode_quality', coalesce((
      select jsonb_agg(jsonb_build_object('key', key, 'count', count) order by key)
      from public.v_hud_property_count_by_geocode_quality
    ), '[]'::jsonb),
    'latest_hud_ingestion_run', (
      select jsonb_build_object(
        'id', r.id,
        'source_name', r.source_name,
        'status', r.status,
        'started_at', r.started_at,
        'completed_at', r.completed_at,
        'records_requested', r.records_requested,
        'records_fetched', r.records_fetched,
        'records_upserted', r.records_upserted,
        'records_failed', r.records_failed,
        'metadata', r.metadata
      )
      from public.ingestion_runs r
      where r.source_name = 'HUD Multifamily Properties - Assisted'
      order by r.started_at desc nulls last
      limit 1
    )
  )
  from public.v_hud_property_totals t;
$$;

create or replace function public.get_freddie_mac_mlpd_summary()
returns jsonb
language sql
stable
security invoker
as $$
  select jsonb_build_object(
    'total_loan_quarter_observations', b.total_loan_quarter_observations,
    'distinct_loan_count', b.distinct_loan_count,
    'min_reporting_quarter', b.min_reporting_quarter,
    'max_reporting_quarter', b.max_reporting_quarter,
    'total_ending_balance_for_latest_quarter', (
      select sum(ending_balance)
      from public.freddie_mac_loan_quarter_observations
      where reporting_quarter = b.max_reporting_quarter
    ),
    'average_original_ltv', b.average_original_ltv,
    'average_original_dcr', b.average_original_dcr,
    'average_note_rate', b.average_note_rate,
    'count_by_mortgage_status_code', coalesce((
      select jsonb_agg(jsonb_build_object('key', key, 'count', count) order by key)
      from public.v_freddie_mac_count_by_status
    ), '[]'::jsonb),
    'count_by_property_state', coalesce((
      select jsonb_agg(jsonb_build_object('key', key, 'count', count) order by key)
      from public.v_freddie_mac_count_by_property_state
    ), '[]'::jsonb),
    'latest_freddie_mac_ingestion_run', (
      select jsonb_build_object(
        'id', r.id,
        'source_name', r.source_name,
        'status', r.status,
        'started_at', r.started_at,
        'completed_at', r.completed_at,
        'records_requested', r.records_requested,
        'records_fetched', r.records_fetched,
        'records_upserted', r.records_upserted,
        'records_failed', r.records_failed,
        'metadata', r.metadata
      )
      from public.ingestion_runs r
      where r.source_name = 'Freddie Mac Multifamily Loan Performance Database'
      order by r.started_at desc nulls last
      limit 1
    )
  )
  from public.v_freddie_mac_mlpd_base_summary b;
$$;

create or replace function public.get_freddie_mac_latest_quarter_summary()
returns jsonb
language sql
stable
security invoker
as $$
  select jsonb_build_object(
    'reporting_quarter', s.reporting_quarter,
    'observation_count', s.observation_count,
    'distinct_loan_count', s.distinct_loan_count,
    'total_ending_balance', s.total_ending_balance,
    'average_original_ltv', s.average_original_ltv,
    'average_original_dcr', s.average_original_dcr,
    'average_note_rate', s.average_note_rate,
    'count_by_mortgage_status_code', coalesce((
      select jsonb_agg(jsonb_build_object('key', key, 'count', count) order by key)
      from public.v_freddie_mac_latest_quarter_count_by_status
    ), '[]'::jsonb),
    'count_by_property_state', coalesce((
      select jsonb_agg(jsonb_build_object('key', key, 'count', count) order by key)
      from public.v_freddie_mac_latest_quarter_count_by_state
    ), '[]'::jsonb),
    'top_property_metros_by_balance', coalesce((
      select jsonb_agg(
        jsonb_build_object(
          'key', key,
          'total_ending_balance', total_ending_balance,
          'observation_count', observation_count
        )
        order by total_ending_balance desc nulls last, key
      )
      from public.v_freddie_mac_latest_quarter_top_metros_by_balance
    ), '[]'::jsonb)
  )
  from public.v_freddie_mac_latest_quarter_summary s;
$$;

create or replace function public.get_recent_ingestion_runs(p_limit integer default 10)
returns jsonb
language sql
stable
security invoker
as $$
  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'id', r.id,
        'source_name', r.source_name,
        'status', r.status,
        'started_at', r.started_at,
        'completed_at', r.completed_at,
        'records_requested', r.records_requested,
        'records_fetched', r.records_fetched,
        'records_upserted', r.records_upserted,
        'records_failed', r.records_failed,
        'metadata', r.metadata
      )
      order by r.started_at desc nulls last
    ),
    '[]'::jsonb
  )
  from (
    select
      id,
      source_name,
      status,
      started_at,
      completed_at,
      records_requested,
      records_fetched,
      records_upserted,
      records_failed,
      metadata
    from public.ingestion_runs
    order by started_at desc nulls last
    limit greatest(1, least(p_limit, 100))
  ) r;
$$;

grant execute on function public.mlpd_reporting_quarter_sort_key(text) to authenticated;
grant execute on function public.get_hud_property_summary() to authenticated;
grant execute on function public.get_freddie_mac_mlpd_summary() to authenticated;
grant execute on function public.get_freddie_mac_latest_quarter_summary() to authenticated;
grant execute on function public.get_recent_ingestion_runs(integer) to authenticated;
