CREATE OR REPLACE FUNCTION update_row_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF row(NEW.*) IS DISTINCT FROM row(OLD.*) THEN
        NEW.dt_changed = NOW();
        RETURN NEW;
    ELSE
        RETURN NULL;
    END IF;
END;
$$;

COMMENT ON FUNCTION update_row_timestamp() IS 'Updates dt_changed if anything changed.';

-- TOKENS --

CREATE TABLE tokens (
    id               bigserial NOT NULL,
    user_id          text NOT NULL CHECK(trim(user_id) != ''),
    scope            text NOT NULL,
    access           text NOT NULL CHECK(trim(access) != ''),
    refresh          text NOT NULL CHECK(trim(refresh) != ''),
    expires_at       bigint NOT NULL,
    dt_created       timestamp with time zone NOT NULL DEFAULT NOW(),
    dt_changed       timestamp with time zone NOT NULL DEFAULT NOW(),
    dt_deleted       timestamp with time zone NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ON tokens (dt_changed);
CREATE UNIQUE INDEX ON tokens (user_id, scope, (dt_deleted IS NULL)) WHERE dt_deleted IS NULL;

CREATE TRIGGER a_update_row_timestamp BEFORE UPDATE ON tokens FOR EACH ROW EXECUTE PROCEDURE update_row_timestamp();

COMMENT ON TABLE tokens IS 'Tokens to use in Spotify Web API requests';
