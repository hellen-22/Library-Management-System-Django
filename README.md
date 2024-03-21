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
