create extension if not exists vector with schema extensions;

create type public.analysis_status as enum (
    'pending',
    'processing',
    'completed',
    'failed'
);

create type public.risk_level as enum (
    'low',
    'medium',
    'high'
);

create table public.documents (
    id uuid primary key default gen_random_uuid(),
    original_filename text not null,
    content_sha256 text not null,
    status public.analysis_status not null default 'pending',
    total_pages integer not null default 0 check (total_pages >= 0),
    total_chunks integer not null default 0 check (total_chunks >= 0),
    error_message text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    completed_at timestamptz,
    constraint documents_content_sha256_length check (char_length(content_sha256) = 64)
);

create table public.document_chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references public.documents(id) on delete cascade,
    chunk_index integer not null check (chunk_index >= 0),
    page_start integer check (page_start is null or page_start > 0),
    page_end integer check (page_end is null or page_end > 0),
    start_char integer not null check (start_char >= 0),
    end_char integer not null check (end_char > start_char),
    content text not null,
    embedding extensions.vector(1536) not null,
    created_at timestamptz not null default now(),
    constraint document_chunks_document_index_unique unique (document_id, chunk_index)
);

create table public.risk_dossiers (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null unique references public.documents(id) on delete cascade,
    overall_risk_level public.risk_level not null,
    executive_summary text not null,
    findings jsonb not null default '[]'::jsonb,
    technical_recommendations jsonb not null default '[]'::jsonb,
    model_name text,
    prompt_version text,
    generated_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    constraint risk_dossiers_findings_is_array check (jsonb_typeof(findings) = 'array'),
    constraint risk_dossiers_recommendations_is_array check (
        jsonb_typeof(technical_recommendations) = 'array'
    )
);

create index documents_status_created_at_idx
    on public.documents (status, created_at desc);

create index document_chunks_document_id_idx
    on public.document_chunks (document_id);

create index document_chunks_embedding_idx
    on public.document_chunks
    using ivfflat (embedding extensions.vector_cosine_ops)
    with (lists = 100);

create index risk_dossiers_document_id_idx
    on public.risk_dossiers (document_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create trigger documents_set_updated_at
before update on public.documents
for each row
execute function public.set_updated_at();
