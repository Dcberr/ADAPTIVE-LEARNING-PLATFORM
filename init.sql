--
-- PostgreSQL database dump
--

\restrict T3BFihsBeYJ96koN6AzAiRBMcvB6fEGP6HSSbZGe5qmrvkrmItMKOAyqrWA0LNP

-- Dumped from database version 15.17 (Debian 15.17-1.pgdg13+1)
-- Dumped by pg_dump version 15.17 (Debian 15.17-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assignment_problems; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.assignment_problems (
    id uuid NOT NULL,
    assignment_id uuid,
    problem_id uuid
);


--
-- Name: assignments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.assignments (
    id uuid NOT NULL,
    created_at timestamp(6) with time zone,
    deadline timestamp(6) with time zone,
    description character varying(255),
    title character varying(255),
    topic_id uuid,
    difficulty character varying(255),
    status character varying(255),
    tag character varying(255)[]
);


--
-- Name: class_enrollments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.class_enrollments (
    id uuid NOT NULL,
    class_id uuid,
    joined_at timestamp(6) with time zone,
    student_id uuid
);


--
-- Name: classes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.classes (
    id uuid NOT NULL,
    created_at timestamp(6) with time zone,
    description character varying(255),
    instructor_id uuid,
    name character varying(255),
    status character varying(255),
    schedule character varying(255)
);


--
-- Name: code_reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.code_reviews (
    id uuid NOT NULL,
    created_at timestamp(6) with time zone,
    detail text,
    review_items_json text,
    submission_id uuid,
    summary text
);


--
-- Name: documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.documents (
    id uuid NOT NULL,
    created_at timestamp(6) with time zone,
    description character varying(255),
    file_url character varying(255),
    title character varying(255),
    topic_id uuid,
    type character varying(255)
);


--
-- Name: problem_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.problem_tags (
    id uuid NOT NULL,
    problem_id uuid,
    tag character varying(255)
);


--
-- Name: problems; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.problems (
    id uuid NOT NULL,
    created_at timestamp(6) with time zone,
    description text,
    difficulty character varying(255),
    external_id character varying(255),
    source character varying(255),
    title character varying(255)
);


--
-- Name: submissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.submissions (
    id uuid NOT NULL,
    code text,
    created_at timestamp(6) with time zone,
    language character varying(255),
    passed_testcases integer,
    problem_id uuid,
    runtime bigint,
    status character varying(255),
    total_testcases integer,
    user_id uuid,
    score character varying(255)
);


--
-- Name: testcases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.testcases (
    id uuid NOT NULL,
    expected_output text,
    input text,
    is_sample boolean NOT NULL,
    problem_id uuid,
    explanation character varying(255)
);


--
-- Name: topics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.topics (
    id uuid NOT NULL,
    class_id uuid,
    created_at timestamp(6) with time zone,
    description character varying(255),
    title character varying(255)
);


--
-- Name: user_code_sequences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_code_sequences (
    id uuid NOT NULL,
    role character varying(255),
    year integer,
    current_value integer
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(255),
    name character varying(255),
    picture character varying(255),
    provider character varying(255),
    role character varying(255),
    user_code character varying(255),
    gpa double precision,
    CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['STUDENT'::character varying, 'INSTRUCTOR'::character varying])::text[])))
);


--
-- Data for Name: assignment_problems; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.assignment_problems (id, assignment_id, problem_id) FROM stdin;
c3b12a30-cc8a-4996-83c4-d3f0248c6877	882c7e72-e3bb-4670-a7e6-d907e3bca5d1	c3b12a30-cc8a-4996-83c4-d3f0248c6877
f31eb336-4c7f-408c-8830-3d467bc45556	882c7e72-e3bb-4670-a7e6-d907e3bca5d1	1c3473d7-4271-4535-8440-f934d68f5e00
462d8cf2-d201-4ba1-9224-703d31236dbe	abd93784-2fca-4b55-90f1-6111849d8aee	f492aa41-bc93-4136-959e-5ed914c012d8
deee7367-e750-4641-aeea-ff63e88091b5	e4ccaaa5-4073-41bd-b976-f7090e3bb822	ac67defd-4f30-4ba2-bd76-200ab27f5455
\.


--
-- Data for Name: assignments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.assignments (id, created_at, deadline, description, title, topic_id, difficulty, status, tag) FROM stdin;
882c7e72-e3bb-4670-a7e6-d907e3bca5d1	2026-03-13 17:39:05.580891+00	2026-03-20 23:59:59+00	Solve graph problems	Graph Assignment	ae9d86e3-632d-43d6-9dfd-d7df9958acf6	\N	\N	\N
abd93784-2fca-4b55-90f1-6111849d8aee	2026-03-21 17:22:53.403627+00	2026-04-01 23:59:00+00	\N	Assignment Test 1	ae9d86e3-632d-43d6-9dfd-d7df9958acf6	EASY	PENDING	\N
e4ccaaa5-4073-41bd-b976-f7090e3bb822	2026-03-21 17:36:36.354328+00	2026-04-01 23:59:00+00	\N	Assignment Test 1	ae9d86e3-632d-43d6-9dfd-d7df9958acf6	EASY	PENDING	\N
\.


--
-- Data for Name: class_enrollments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.class_enrollments (id, class_id, joined_at, student_id) FROM stdin;
9db76446-edd6-4f8c-9472-ef671050aa80	8c2f3a2a-5fdc-469f-b9db-9960034f0c32	2026-03-13 17:22:44.162965+00	777638ff-5ed4-45e6-942b-7ed7d2c71841
777c29fd-db72-462a-896c-49a899426891	8c2f3a2a-5fdc-469f-b9db-9960034f0c32	2026-03-13 17:28:31.688534+00	34c8907f-c564-485b-a4e1-7ded2ee9a2bd
\.


--
-- Data for Name: classes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.classes (id, created_at, description, instructor_id, name, status, schedule) FROM stdin;
8c2f3a2a-5fdc-469f-b9db-9960034f0c32	2026-03-13 16:57:43.49+00	Course for DS	03487d4b-3d99-4240-bd11-8ad631702dc9	Data Structures	IN_PROGRESS	Thứ 2, Thứ 4 14:00 - 16:00
\.


--
-- Data for Name: code_reviews; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.code_reviews (id, created_at, detail, review_items_json, submission_id, summary) FROM stdin;
0554b704-ec1c-4557-85f1-027388b9cab1	2026-03-17 16:39:05.278747+00	Review completed	{"summary":"Unable to generate overview at this time.","detail":"Review completed","testcaseResults":null}	7b072976-7506-4b4f-9931-f43bc2125cfe	Unable to generate overview at this time.
\.


--
-- Data for Name: documents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.documents (id, created_at, description, file_url, title, topic_id, type) FROM stdin;
8559c0cf-cfec-4726-9a3e-e67d97345a86	2026-03-20 03:30:20.245432+00	test upload	http://localhost:9000/datn-bucket/uploads/f9513570-9e0e-4ec8-a698-0306adf51b73.pdf	test	ae9d86e3-632d-43d6-9dfd-d7df9958acf6	application/pdf
d30b74bb-096e-4b06-8a68-1457e536ec6d	2026-03-20 13:51:49.483149+00	test upload	http://localhost:9000/datn-bucket/uploads/ff91e3cb-1e6d-41a4-8ed0-99fca679a398.mov	test 2	ae9d86e3-632d-43d6-9dfd-d7df9958acf6	video/quicktime
d05f8bcc-03f9-49ee-be69-f7ccc1f229b8	2026-03-20 13:54:24.811448+00	test upload	http://localhost:9000/datn-bucket/uploads/18700ea5-0d42-40be-9be6-fdc6ad05a510.mp4	test 3	ae9d86e3-632d-43d6-9dfd-d7df9958acf6	video/mp4
\.


--
-- Data for Name: problem_tags; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.problem_tags (id, problem_id, tag) FROM stdin;
\.


--
-- Data for Name: problems; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.problems (id, created_at, description, difficulty, external_id, source, title) FROM stdin;
c3b12a30-cc8a-4996-83c4-d3f0248c6877	2026-03-13 17:42:59.683937+00	Find two numbers that sum to target	EASY	\N	internal	Two Sum
1c3473d7-4271-4535-8440-f934d68f5e00	2026-03-15 16:05:11.324932+00	a	EASY	\N	al	a
f492aa41-bc93-4136-959e-5ed914c012d8	2026-03-21 17:22:53.430286+00	Tính tổng 2 số nguyên a và b	\N	\N	\N	\N
ac67defd-4f30-4ba2-bd76-200ab27f5455	2026-03-21 17:36:36.372699+00	Tính tổng 2 số nguyên a và b	\N	\N	\N	\N
\.


--
-- Data for Name: submissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.submissions (id, code, created_at, language, passed_testcases, problem_id, runtime, status, total_testcases, user_id, score) FROM stdin;
7b072976-7506-4b4f-9931-f43bc2125cfe	a,b=map(int,input().split());print(a+b)	2026-03-16 14:43:36.490684+00	python3	10	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N	ACCEPTED	10	5643c0fb-4d84-4607-951e-e9c1fa188ece	100.0
0862ed16-802b-4dc1-9329-27d9251bad54	a,b=map(int,input().split());print(a+b)	2026-03-15 05:22:52.684795+00	python3	10	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N	ACCEPTED	10	5643c0fb-4d84-4607-951e-e9c1fa188ece	90.0
\.


--
-- Data for Name: testcases; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.testcases (id, expected_output, input, is_sample, problem_id, explanation) FROM stdin;
cb9095f4-6492-4169-8a9f-dd5013ad82d3	3	1 2	t	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
043a26a7-fcb1-46dc-8768-b4e7b2c3aeac	12	5 7	f	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
3fcdd504-09f9-49f1-88b6-d29bda3f854a	30	10 20	f	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
2bc54e51-1968-4ec4-9ec7-6ae237953ad0	300	100 200	f	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
f85a5e62-62e1-443a-8397-31f8f22ea562	0	0 0	f	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
4754efbe-1c8a-458c-83ea-4df659b675d1	5	-5 10	f	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
7523747c-46ba-429e-ac0c-879e09e7f743	-300	-100 -200	f	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
508ebf99-07ce-4a6f-b0c6-1e429f9aff58	100000	99999 1	f	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
e4691a5d-a345-4734-8e78-04a6d08133f6	777777	123456 654321	f	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
7c55be99-851f-4de7-bd31-71e30587b646	2147483648	2147483647 1	f	c3b12a30-cc8a-4996-83c4-d3f0248c6877	\N
bc66eb7a-4a27-46bb-a3ba-0fff929e63ec	3	1 2	f	f492aa41-bc93-4136-959e-5ed914c012d8	\N
9e0b1ae8-d8d1-4bbd-b7dd-b68ab2cf44d8	30	10 20	f	f492aa41-bc93-4136-959e-5ed914c012d8	\N
a308f3b1-6724-4a17-97b6-1a50c4eaf018	0	-5 5	f	f492aa41-bc93-4136-959e-5ed914c012d8	\N
1691a458-2f7e-40d1-9802-cc066fdb1968	3	1 2	f	ac67defd-4f30-4ba2-bd76-200ab27f5455	\N
5d7c76c0-bec6-4d7f-95ae-4f0ed1beddfa	30	10 20	f	ac67defd-4f30-4ba2-bd76-200ab27f5455	\N
f5d7aa62-bd83-42ab-aa11-34681f040cdf	0	-5 5	f	ac67defd-4f30-4ba2-bd76-200ab27f5455	\N
\.


--
-- Data for Name: topics; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.topics (id, class_id, created_at, description, title) FROM stdin;
ae9d86e3-632d-43d6-9dfd-d7df9958acf6	8c2f3a2a-5fdc-469f-b9db-9960034f0c32	2026-03-13 17:34:21.368306+00	Graph algorithms	Graph
\.


--
-- Data for Name: user_code_sequences; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_code_sequences (id, role, year, current_value) FROM stdin;
368b28f5-0cc2-44b0-9aed-8c76c43ebc7a	STUDENT	2026	6
b2f1fc58-dbcc-4b24-ab2f-691202020348	INSTRUCTOR	2026	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, email, name, picture, provider, role, user_code, gpa) FROM stdin;
03487d4b-3d99-4240-bd11-8ad631702dc9	cong.nguyenkhmtbkuk22@hcmut.edu.vn	CÔNG NGUYỄN NGỌC CHIẾN	https://lh3.googleusercontent.com/a/ACg8ocKR42iityp1Wyg2hD8mf3LVOoX6HP2_rpYheWXu9ln9LrHyA7w=s96-c	google	STUDENT	STU-2026-00003	0
dff27972-8fb1-4a5c-bc47-ab2ed7b9727a	congnnc.cs@gmail.com	Công Nguyễn Ngọc Chiến	https://lh3.googleusercontent.com/a/ACg8ocI7jeY9lbOVkXAF--iLqvo19m13wbE3swV1aM2vD0pOYt-3lXY=s96-c	google	INSTRUCTOR	INS-2026-00001	0
\.


--
-- Name: assignment_problems assignment_problems_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assignment_problems
    ADD CONSTRAINT assignment_problems_pkey PRIMARY KEY (id);


--
-- Name: assignments assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT assignments_pkey PRIMARY KEY (id);


--
-- Name: class_enrollments class_enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_enrollments
    ADD CONSTRAINT class_enrollments_pkey PRIMARY KEY (id);


--
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (id);


--
-- Name: code_reviews code_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.code_reviews
    ADD CONSTRAINT code_reviews_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: problem_tags problem_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.problem_tags
    ADD CONSTRAINT problem_tags_pkey PRIMARY KEY (id);


--
-- Name: problems problems_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_pkey PRIMARY KEY (id);


--
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);


--
-- Name: testcases testcases_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.testcases
    ADD CONSTRAINT testcases_pkey PRIMARY KEY (id);


--
-- Name: topics topics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_pkey PRIMARY KEY (id);


--
-- Name: users uk6dotkott2kjsp8vw4d0m25fb7; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uk6dotkott2kjsp8vw4d0m25fb7 UNIQUE (email);


--
-- Name: user_code_sequences user_code_sequences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_code_sequences
    ADD CONSTRAINT user_code_sequences_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_user_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_code_key UNIQUE (user_code);


--
-- PostgreSQL database dump complete
--

\unrestrict T3BFihsBeYJ96koN6AzAiRBMcvB6fEGP6HSSbZGe5qmrvkrmItMKOAyqrWA0LNP

