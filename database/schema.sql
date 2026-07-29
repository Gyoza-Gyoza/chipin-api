CREATE TABLE public.item_payers (
    item_id integer NOT NULL,
    user_id integer NOT NULL,
    paid boolean DEFAULT false NOT NULL
);

CREATE TABLE public.items (
    item_id integer NOT NULL,
    receipt_id integer NOT NULL,
    amount numeric NOT NULL,
    title character varying CONSTRAINT items_description_not_null NOT NULL,
    paid boolean DEFAULT false NOT NULL,
    item_count smallint CONSTRAINT items_count_not_null NOT NULL
);

CREATE SEQUENCE public.items_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.items_item_id_seq OWNED BY public.items.item_id;

CREATE TABLE public.receipt_sharers (
    receipt_id integer NOT NULL,
    sharer_id integer NOT NULL
);

CREATE TABLE public.receipts (
    receipt_id integer NOT NULL,
    owner_id integer CONSTRAINT receipts_payer_id_not_null NOT NULL,
    amount numeric NOT NULL,
    title character varying CONSTRAINT receipts_description_not_null NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    date timestamp with time zone,
    qr_ready bool DEFAULT false NOT NULL,
    service_tax bool DEFAULT false NOT NULL,
    gst bool DEFAULT false NOT NULL
);

CREATE SEQUENCE public.receipts_receipt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.receipts_receipt_id_seq OWNED BY public.receipts.receipt_id;

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying NOT NULL,
    password character varying NOT NULL,
    email character varying NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    phone_number integer CONSTRAINT "users_phone number_not_null" NOT NULL
);

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;
ALTER TABLE ONLY public.items ALTER COLUMN item_id SET DEFAULT nextval('public.items_item_id_seq'::regclass);
ALTER TABLE ONLY public.receipts ALTER COLUMN receipt_id SET DEFAULT nextval('public.receipts_receipt_id_seq'::regclass);
ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);
ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (item_id);
ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_pkey PRIMARY KEY (receipt_id);
ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username UNIQUE (username);
ALTER TABLE ONLY public.item_payers
    ADD CONSTRAINT item_payers_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(item_id) ON DELETE CASCADE;
ALTER TABLE ONLY public.item_payers
    ADD CONSTRAINT item_payers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;
ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_receipt_id_fkey FOREIGN KEY (receipt_id) REFERENCES public.receipts(receipt_id) ON DELETE CASCADE;
ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(user_id) ON DELETE CASCADE;
ALTER TABLE ONLY public.receipt_sharers
    ADD CONSTRAINT receipt_sharers_sharer_id_fkey FOREIGN KEY (sharer_id) REFERENCES public.users(user_id) ON DELETE CASCADE;
ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(user_id) ON DELETE CASCADE;