CREATE OR REPLACE FUNCTION generate_uid() RETURNS BIGINT AS $$
DECLARE
    result bigint;
    now_millis bigint;
    random_data bytea;
    our_epoch bigint:= 1500000000000;
BEGIN
    SELECT FLOOR(EXTRACT(EPOCH FROM clock_timestamp()) * 1000) INTO now_millis;
    random_data := gen_random_bytes(3);
    result := (now_millis - our_epoch) << 24;
    result := result | get_byte(random_data,0) | (get_byte(random_data,1) << 8) | (get_byte(random_data,2)<<16);
    RETURN result;
END;
    $$ LANGUAGE PLPGSQL;
