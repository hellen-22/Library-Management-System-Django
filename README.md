# Library-Management-System-Django
A Simple Library Management System that helps in managing a library.

### Available Functionalities:
Definition: CRUD(Create, Read, Update and Delete)
1. Members Management (Allows CRUD operations on Library Members)
2. Books Management (Allows CRUD operations on Books)
3. Lending of Books to Members.
4. Returning of Books by Members.
5. Payment for Borrowing A Book/Books by Members
6. Payments for fines on overdue books By Members.

### To run the project locally, follow the following instructions:
- Clone the repository
  ```sql
  git clone https://github.com/hellen-22/Library-Management-System-Django.git
  ```
- Navigate to the project directory.
  ```sql
  cd Library-Management-System-Django
  ```
- Create virtual environment and activate it:
  ```sql
  python3 -m venv venv or python -m venv venv
  ```
  Activate: On Windows
  ```sql
  venv\Scripts\activate
  ```
  On Mac
  ```sql
  source venv\bin\activate
  ```
- Install libraries from the requirements.txt file.
  ```sql
  pip install -r requirement.txt
  ```
- Edit the *.env.sample* file to add your environment variables.
- Set up the database:
  ```sql
  python manage.py migrate
  ```
- Run the server:
  ```sql
  python manage.py runserver
  ```

### Hosted version
Hosted version of the project: https://library-wnd0.onrender.com/

Use the following credentials:
```sql
Email: admin@gmail.com
Password: Admin@LMS
```
Or register an account.

### Screenshots
Login and Register Pages.
<img width="1440" alt="Screenshot 2024-02-15 at 11 57 31" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/5843a91c-c721-4a6d-bbbc-761c0ff6a713">

<img width="1439" alt="Screenshot 2024-02-15 at 11 57 06" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/8ea7d534-8371-4e4c-afa1-1e62e4bd64f9">

Dashboard.
<img width="1426" alt="Screenshot 2024-02-15 at 12 05 50" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/db263fab-8589-474f-8b09-fb781fcd466c">

Members Pages.
<img width="1440" alt="Screenshot 2024-02-15 at 12 07 04" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/ffb20c12-8a48-46a5-88a4-64744e40cd40">

<img width="1424" alt="Screenshot 2024-02-15 at 12 06 48" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/26abb84b-0a3f-4e27-872f-b9a58e36f597">

Books Pages.
<img width="1424" alt="Screenshot 2024-02-15 at 12 09 15" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/7e18dd67-229f-4456-8278-f1252d66d387">

<img width="1423" alt="Screenshot 2024-02-15 at 12 08 49" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/74461a23-b1b9-4af8-a924-2d7312e4762f">

Other Pages.
<img width="1439" alt="Screenshot 2024-02-15 at 12 16 03" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/99f3dfc9-4136-4187-aa51-933a97ef161e">

<img width="1423" alt="Screenshot 2024-02-15 at 12 13 50" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/643579b1-7811-44c4-a07a-03b5196ccbe5">

<img width="1425" alt="Screenshot 2024-02-15 at 12 18 37" src="https://github.com/hellen-22/Library-Management-System-Django/assets/58620060/91cc7d5c-a15c-4755-ad1b-b112fd098420">


## PrivacyLib GDPR integration

Original framework: **[PrivacyLib-REGO](https://github.com/CS-UCY-SEIT-lab/PrivacyLib-REGO)**. Its unchanged Python router and eleven Rego modules are bundled in `integration/privacy_lib/`. The new `privacy` Django app supplies authentication-aware routes and a separate consent model.

### Setup and run

Use Python 3.12 with the original pinned `requirements.txt` and [OPA 1.x](https://www.openpolicyagent.org/docs). No new Python runtime package is required. Configure the original SECRET_KEY/PostgreSQL variables and apply migrations:

```sh
python manage.py migrate
```

Only `privacy.0001_initial` adds the separate `privacy_consent` table; it does not alter existing user/library records. Request handlers never create tables. Existing PostgreSQL deployment configuration remains available.

For a loopback-only SQLite demo, export a private `SECRET_KEY` and optionally an absolute `PRIVACY_DATABASE_PATH`, then use the supplied optional development settings:

```sh
python manage.py migrate --settings=integration.local_settings
python manage.py runserver 127.0.0.1:8042 --noreload --settings=integration.local_settings
```

The default local SQLite path is ignored `db.sqlite3`; environment/dependency/data files must stay out of Git. These development settings do not configure or validate the original PostgreSQL deployment.

In another terminal start OPA from the repository:

```sh
opa run --server --addr 127.0.0.1:8181 integration/privacy_lib/gdpr
```

`OPA_QUERY_URL` defaults to `http://localhost:8181/v1/query`; set it in the Django server environment for another address. Configure synthetic controller, retention, purpose and service metadata in `integration/privacy-config.json` for the intended use.

Register through the original `/register/` form using dummy details, sign in at `/login/`, then click **Privacy checks** in the top bar in the same browser tab/origin. The original registration does not require email verification. Existing browser session configuration is unchanged.

### Scope and permissions

Routes: `GET /gdpr/`, `GET /gdpr/csrf/`, `PATCH /gdpr/consent/`, and eleven `POST /gdpr/{operation}/` calls: consent, lawful, information, access, rectification, erasure, restriction, portability, objection, complaint and breach. Count:14 HTTP method/operation pairs. They use the original Django authentication and global CSRF middleware. JSON mutations require `X-CSRFToken`; invalid/missing CSRF returns native403. An unauthenticated page redirects to the original login; private API requests deny access.

Mapped fields are the current librarian's first_name, last_name, email and date_joined. Library members are a separate model with no librarian-account ownership link; books, loans and payments likewise cannot be attributed to the signed-in account. Those shared records are deliberately excluded rather than assigned to a user by matching email. Passwords, session data, roles and other profiles are excluded. The subject is always the authenticated librarian; client IDs, roles and trusted checks cannot override it.

Breach assessment requires the native active staff/superuser flags. Ordinary registered librarians receive403. Rectification permits first_name/last_name/email only. Consent persists in its own table. Other responses are decisions/proposed plans: profile edits, deletion, transfers, complaint delivery, notifications and audit writes are not executed. Access returns metadata; portability returns selected actual profile values. Synthetic metadata and passing checks do not establish legal compliance.

### Verify independently

```sh
python integration/test.py
```

Set `OPA_BINARY` when OPA is not on PATH. The native runner uses the current Python environment, a separate migrated SQLite fixture, random application key, cookie jars and local Django/OPA ports. It uses original registration/login/logout, a native superuser fixture, two-user isolation, shared catalogue/member exclusion, CSRF checks, all policies, strict input/body limits, withdrawal and OPA outage handling. It never uses the configured application database or browser session; temporary processes/files are cleaned before success is reported. No extra testing framework is needed and no evaluation reports are written into the repository. Original tests can also run with `python manage.py test library users` using an appropriate test database/settings.
