# AGENTS.md

## Project Context

This file is the authoritative working context for OpenAI Codex when modifying this repository.

The purpose of this file is **not** to teach Django or DRF from scratch. It documents the architecture, intent, constraints, decisions, testing approach, and development workflow that have been established while building this project.

Codex MUST read this file before making changes to the project.

---

# 1. Project Overview

This project is a REST API for a **media/counseling scheduling system**.

The repository is:

`MediasScedulerRESR-API`

The project is being developed incrementally using **Django + Django REST Framework**, with a strong **TDD (Test Driven Development)** workflow.

The main domain areas currently established are:

* Users
* Consultant profiles
* Rooms
* Scheduled sessions

The scheduling domain connects consultants, rooms, students, and time ranges.

The project is intentionally being implemented incrementally:

```text
Write test
    ↓
Run test
    ↓
Test fails
    ↓
Implement minimum required behavior
    ↓
Run test again
    ↓
Test passes
    ↓
Continue with next behavior
```

Do not bypass this workflow by implementing large amounts of functionality without corresponding tests.

---

# 2. Repository / Project Structure

The actual Django applications are located under `app/`.

Important structure confirmed during development:

```text
app/
├── users/
│   ├── migrations/
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_user_api.py
│   │   └── test_consultant_api.py
│   ├── models.py
│   ├── managers.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── rooms/
│   ├── migrations/
│   ├── tests/
│   │   ├── test_models.py
│   │   └── test_api.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── scheduling/
│   ├── migrations/
│   ├── tests/
│   │   └── test_models.py
│   │   └── test_api.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── manage.py
```

There may be additional files/modules in the repository. Codex should inspect the actual repository before making assumptions.

### Important path convention

From the repository root, Django apps are under `app/`.

For example:

```text
app/rooms/
app/users/
app/scheduling/
```

Therefore commands such as:

```bash
find rooms
```

from the repository root are incorrect.

Use:

```bash
find app/rooms
```

or inspect the actual repository tree.

---

# 3. Application Responsibilities

## `users`

Responsible for:

* Custom User model
* User creation
* Authentication-related endpoints
* Consultant profiles
* Consultant-related API behavior

Confirmed model relationship:

```text
User
  │
  │ OneToOne
  ▼
ConsultantProfile
```

`ConsultantProfile` currently has these confirmed fields:

```text
id
user
preferred_start_time
```

This was verified directly with Django:

```bash
docker compose exec app python manage.py shell -c "from users.models import ConsultantProfile; print(ConsultantProfile); print([(f.name, f.__class__.__name__) for f in ConsultantProfile._meta.fields])"
```

Result:

```text
[
    ('id', 'BigAutoField'),
    ('user', 'OneToOneField'),
    ('preferred_start_time', 'TimeField')
]
```

The project has tests ensuring that:

* a user can have only one consultant profile
* consultant profile string representation behaves correctly
* `preferred_start_time` is required

The user manager uses the project's custom user model and **does not use `username` as a model field**.

A previous bug occurred when a test attempted:

```python
create_user(username=...)
```

and Django raised:

```text
TypeError: User() got unexpected keyword arguments: 'username'
```

Therefore Codex MUST inspect the actual custom User model and manager before constructing users in new code or tests.

---

## `rooms`

Responsible for:

* Room model
* Room CRUD/API behavior
* Room validation
* Room availability constraints related to scheduling

Confirmed `Room` fields:

```text
id
name
```

Verified with:

```bash
docker compose exec app python manage.py shell -c "from rooms.models import Room; print(Room); print([(f.name, f.__class__.__name__) for f in Room._meta.fields])"
```

Result:

```text
[
    ('id', 'BigAutoField'),
    ('name', 'CharField')
]
```

The room API has already been developed and tested for behaviors including:

* authentication
* creation
* generated ID
* duplicate name handling
* empty name handling
* list
* retrieve
* authentication requirements

Room tests previously exposed an important authentication issue where endpoints returned:

```text
401
```

when tests expected successful authenticated responses.

The correct approach was to follow the authentication setup already established in the project rather than weakening permissions.

---

## `scheduling`

Responsible for:

* Scheduled sessions
* Relationships between consultants and rooms
* Time range validation
* Scheduling conflicts
* Session API

Confirmed `ScheduledSession` fields from test/database errors:

```text
id
student_id
start_time
end_time
session_type
consultant
room
```

The exact field types and any additional model metadata should be read from the actual model before modifying it.

The scheduling app depends conceptually on:

```text
users
  ↓
ConsultantProfile
  ↓
ScheduledSession
  ↑
Room
```

---

# 4. Overall Architecture

The project follows a conventional Django REST Framework layered architecture:

```text
Client
  │
  ▼
URL routing
  │
  ▼
View / APIView / GenericAPIView / ViewSet
  │
  ▼
Serializer
  │
  ├── API input validation
  │
  └── representation
  │
  ▼
Model
  │
  ├── persistence
  ├── domain/model validation
  └── relationships
  │
  ▼
Database
```

For scheduling:

```text
HTTP request
    ↓
config.urls
    ↓
scheduling.urls
    ↓
ScheduledSession view
    ↓
ScheduledSessionSerializer
    ↓
ScheduledSession model
    ↓
database
```

The project is being built from the outside behavior inward using tests.

---

# 5. Responsibilities of Each Layer

## Models

Models represent persistent domain entities and relationships.

They are responsible for:

* database structure
* relationships
* model-level business rules
* domain constraints that should remain true independently of the API

Example:

`ScheduledSession.clean()` contains scheduling rules such as:

* end time must be after start time
* a consultant cannot have overlapping sessions
* a room cannot have overlapping sessions

Do not remove these rules simply because equivalent API validation exists.

---

## Serializers

Serializers are responsible for:

* converting API input into validated Python/model data
* validating API-level input
* converting model instances to API responses

Important discovery during this project:

**Django REST Framework's `ModelSerializer` does not automatically call the model's `full_clean()` in the normal `.save()` path.**

Therefore a rule implemented only inside:

```python
ScheduledSession.clean()
```

was not enough to reject invalid API requests.

For scheduling, API validation was therefore also implemented in:

```python
ScheduledSessionSerializer.validate()
```

Current confirmed API validation responsibilities include:

* `end_time > start_time`
* consultant overlap prevention
* room overlap prevention

The serializer should not silently allow invalid scheduling data just because the model contains a `clean()` method.

---

## Views

Views connect URLs, serializers, permissions, and model/queryset behavior.

The project uses DRF generic views where appropriate.

For example, scheduling currently has a create endpoint based on:

```python
generics.CreateAPIView
```

with:

```python
permission_classes = [IsAuthenticated]
```

Do not replace a simple generic API view with a ViewSet unless there is a concrete architectural reason.

---

## URLs

URLs should remain responsible for routing only.

The scheduling API has an endpoint under:

```text
/api/scheduling/
```

The project uses app-level URL modules and includes them from the main project URL configuration.

Users currently have URL patterns including:

```text
/api/users/create/
/api/users/token/
/api/users/me/
```

and consultant-related routing under the users application.

The exact current URL configuration should always be checked before adding duplicate routes.

---

# 6. Authentication and Authorization

The project uses authenticated API endpoints.

The users URL configuration includes:

```python
TokenObtainPairView
```

from:

```python
rest_framework_simplejwt.views
```

Therefore JWT token authentication is part of the project's authentication design.

Confirmed user endpoints include:

```text
create/
token/
me/
```

Scheduling create API currently explicitly requires:

```python
permission_classes = [IsAuthenticated]
```

Authentication requirements are tested.

For example:

* authenticated users should be able to access protected endpoints
* unauthenticated users should receive `401`

Do NOT remove authentication from an endpoint merely to make tests pass.

If a new endpoint requires authorization beyond simple authentication, inspect existing project patterns and tests before introducing new permission classes.

---

# 7. Scheduling Business Rules

These are important domain rules established through tests.

## 7.1 Valid time range

A scheduled session must satisfy:

```text
end_time > start_time
```

The following is invalid:

```text
11:00 → 10:00
```

The API must return:

```text
400
```

for invalid input.

---

## 7.2 Consultant overlap

A consultant cannot have two overlapping scheduled sessions.

Example:

```text
Session 1:
10:00 ───────── 11:00

Session 2:
      10:30 ───────── 11:30
```

This is invalid.

The overlap condition used is conceptually:

```python
existing.start_time < new.end_time
and
existing.end_time > new.start_time
```

Equivalent ORM filtering currently used:

```python
start_time__lt=end_time,
end_time__gt=start_time,
```

The current session is excluded during update operations so that a session does not conflict with itself.

---

## 7.3 Room overlap

A room cannot be assigned to two overlapping sessions.

Example:

```text
Session 1 → Room 1 → 10:00–11:00
Session 2 → Room 1 → 10:30–11:30
```

Invalid.

The consultants may be different; the conflict is caused by the shared room.

---

## 7.4 Back-to-back sessions are allowed

These are valid:

```text
10:00–11:00
11:00–12:00
```

Likewise:

```text
10:00–11:00
09:00–10:00
```

The boundary itself is not considered overlap.

This behavior has explicit tests.

---

## 7.5 Nested overlap is invalid

Example:

```text
Existing:
10:00–12:00

New:
10:30–11:30
```

Invalid.

This has explicit model-level testing.

---

# 8. Important Validation Architecture Decision

The project currently has scheduling validation at two levels:

```text
Model
  └── clean()

Serializer
  └── validate()
```

This is intentional for the current implementation.

### Model validation

Protects domain/model behavior.

### Serializer validation

Protects the API boundary.

The reason for both is that DRF does not automatically invoke model `full_clean()` during normal serializer creation.

### Future architectural improvement

A possible future improvement is to avoid duplicating complex overlap logic between model and serializer by extracting shared business logic into a service/validator.

This is a **proposal**, not a current project rule.

Do not perform this refactor automatically unless explicitly requested or clearly justified by new requirements.

---

# 9. TDD Strategy

TDD is a core development practice in this project.

The normal workflow is:

```text
1. Identify one behavior
2. Write a focused test
3. Run the test
4. Observe the failure
5. Implement the minimum required code
6. Run the test again
7. Confirm it passes
8. Run the relevant test suite
9. Continue
```

Do not implement an entire feature first and write tests afterward.

The development process intentionally uses failures as information.

Example:

```text
Expected 400
Actual 201
```

This tells us that validation is missing from the API layer.

Another example:

```text
Expected 200
Actual 401
```

indicates an authentication/permission issue rather than a model issue.

---

# 10. Current Testing Status

The users model/API work was completed successfully.

The full users test suite was run and fixed successfully.

At one point:

```text
Ran 28 tests
```

with three `NameError` failures because `ConsultantProfile` was not imported in a test module.

After fixing that, the tests passed.

Users model tests currently include:

```text
Ran 9 tests
OK
```

The rooms tests are located under:

```text
app/rooms/tests/
```

A command from the repository root:

```bash
docker compose exec app python manage.py test rooms
```

previously returned:

```text
Found 0 test(s).
NO TESTS RAN
```

This was not because room tests were absent.

The tests actually exist at:

```text
app/rooms/tests/test_api.py
app/rooms/tests/test_models.py
```

The correct test labels should match the Django test discovery configuration/package structure.

`rooms.tests` was subsequently used successfully and the room tests passed.

---

# 11. Current Scheduling Test Progress

Scheduling model tests have been developed incrementally.

At the current checkpoint, the model suite reached:

```text
Ran 12 tests
OK
```

These include tests for:

* successful ScheduledSession creation
* consultant assignment
* room assignment
* required fields
* invalid time ranges
* consultant overlap
* room overlap
* back-to-back sessions
* nested overlap behavior

The scheduling API suite currently has passing tests for:

* successful session creation
* authentication requirement
* required consultant
* required room
* invalid time range
* consultant overlap

The room-overlap API test has been written as the next test in the sequence and should be run next.

Do not assume its result until it is actually executed.

---

# 12. Test Commands

The project is run through Docker Compose.

### Run all tests

```bash
docker compose exec app python manage.py test
```

### Run users tests

```bash
docker compose exec app python manage.py test users
```

### Run users model tests

```bash
docker compose exec app python manage.py test users.tests.test_models
```

### Run consultant API tests

```bash
docker compose exec app python manage.py test users.tests.test_consultant_api
```

### Run room tests

Depending on test discovery/package structure:

```bash
docker compose exec app python manage.py test rooms.tests
```

or specific test modules:

```bash
docker compose exec app python manage.py test rooms.tests.test_api
```

```bash
docker compose exec app python manage.py test rooms.tests.test_models
```

### Run scheduling model tests

```bash
docker compose exec app python manage.py test scheduling.tests.test_models
```

### Run scheduling API tests

```bash
docker compose exec app python manage.py test scheduling.tests.test_api
```

### Run the whole scheduling test suite

```bash
docker compose exec app python manage.py test scheduling.tests
```

If a test label gives a discovery error, inspect the actual package structure instead of guessing.

---

# 13. Docker / WSL Workflow

Development is done using WSL 2 and Docker Desktop.

The application runs inside the Docker Compose `app` service.

Commands are normally executed from the repository root:

```bash
docker compose ...
```

not:

```bash
docker-compose ...
```

The project previously had a Docker/WSL integration problem where:

```text
docker-compose
```

was unavailable inside WSL.

The solution was enabling WSL integration in Docker Desktop and using the modern:

```bash
docker compose
```

command.

A previous Docker permission problem was also resolved by configuring the user to access the Docker socket/group.

Do not modify Docker configuration unless necessary.

---

# 14. Migration Workflow

When model fields change:

```bash
docker compose exec app python manage.py makemigrations
```

or for a specific app:

```bash
docker compose exec app python manage.py makemigrations scheduling
```

Then:

```bash
docker compose exec app python manage.py migrate
```

To inspect migration state:

```bash
docker compose exec app python manage.py showmigrations scheduling
```

### Important migration lesson

When a new non-nullable field is added to a model with existing database rows, Django may ask:

```text
It is impossible to add a non-nullable field ...
without specifying a default.
```

Do not blindly select a one-off default.

First determine whether:

* existing rows should have a meaningful default
* the field should actually allow `NULL`
* existing rows need a migration/data migration
* the schema change is intentional

This happened when adding fields such as `consultant` to `ScheduledSession`.

The correct response depends on the domain model, not merely on making the migration command finish.

---

# 15. Useful Inspection Commands

When unsure about a model's actual schema, inspect it rather than guessing.

Example:

```bash
docker compose exec app python manage.py shell -c "from users.models import ConsultantProfile; print(ConsultantProfile); print([(f.name, f.__class__.__name__) for f in ConsultantProfile._meta.fields])"
```

For Room:

```bash
docker compose exec app python manage.py shell -c "from rooms.models import Room; print(Room); print([(f.name, f.__class__.__name__) for f in Room._meta.fields])"
```

These commands were used during development to resolve ambiguity about model structure.

---

# 16. Important Bugs Previously Encountered

## 16.1 `ConsultantProfile` not imported

Error:

```text
NameError: name 'ConsultantProfile' is not defined
```

This happened in tests.

Solution:

Import the model explicitly in the relevant module.

Do not assume Django automatically imports models into test modules.

---

## 16.2 `ConsultantCreateSerializer` undefined

Error:

```text
NameError: name 'ConsultantCreateSerializer' is not defined
```

The view referenced a serializer that had not been imported/defined correctly.

Solution was to ensure the correct serializer exists and is imported by the view.

---

## 16.3 Serializer field pointing to wrong object

Error:

```text
AttributeError:
'User' object has no attribute 'preferred_start_time'
```

The serializer was serializing a `User` while attempting to access:

```text
preferred_start_time
```

which belongs to `ConsultantProfile`.

This exposed the importance of understanding the:

```text
User → ConsultantProfile
```

relationship before designing serializer fields.

---

## 16.4 Consultant serializer expecting `email` on profile

Error:

```text
AttributeError:
'ConsultantProfile' object has no attribute 'email'
```

`email` belongs to the related User, not directly to `ConsultantProfile`.

The serializer needed to account for the relationship instead of assuming fields exist directly on the profile.

---

## 16.5 `401` instead of successful room API responses

Several room API tests initially returned:

```text
401
```

instead of expected:

```text
200
201
400
```

The issue was authentication setup.

The lesson:

**Do not debug business logic before confirming the test client has the required authentication.**

---

## 16.6 Retrieve room authentication mismatch

One room test initially had:

```text
Expected 200
Actual 401
```

while the authentication-required test had the inverse problem:

```text
Expected 401
Actual 200
```

This was fixed by correctly configuring authentication/permissions rather than weakening the endpoint.

---

## 16.7 `ModelSerializer` did not enforce `clean()`

The scheduling API accepted:

```text
start_time = 11:00
end_time = 10:00
```

and returned:

```text
201
```

even though `ScheduledSession.clean()` rejected the same invalid range.

Reason:

DRF serializer save does not automatically call model `full_clean()`.

Solution:

Implement corresponding API validation in:

```python
ScheduledSessionSerializer.validate()
```

---

## 16.8 Overlap was not enforced through API

The model correctly rejected overlapping sessions through `clean()`.

But API creation initially returned:

```text
201
```

instead of:

```text
400
```

Solution:

Add consultant and room overlap validation to the serializer.

---

## 16.9 `username` is not a User field

A test used:

```python
create_user(username=...)
```

and failed because the custom User model does not accept `username`.

Always inspect the actual User model and manager.

---

## 16.10 Test discovery under `rooms`

Running:

```bash
docker compose exec app python manage.py test rooms
```

returned:

```text
Found 0 test(s).
NO TESTS RAN
```

while the files existed under:

```text
app/rooms/tests/
```

The lesson is to distinguish:

```text
Django app path
```

from:

```text
filesystem path
```

and inspect the package structure when test discovery behaves unexpectedly.

---

## 16.11 Shell command syntax mistakes

A shell inspection command failed because a closing parenthesis was missing.

For example:

```text
SyntaxError: '(' was never closed
```

When using `manage.py shell -c`, keep commands simple and syntactically complete.

---

# 17. URL Architecture

The project uses a central URL configuration:

```text
config/urls.py
```

which includes application URL modules.

Confirmed from the project:

```python
path('api/users/', include('users.urls'))
```

The scheduling API is intended under:

```text
/api/scheduling/
```

The rooms API has its own app-level URLs.

Do not hardcode routes in multiple locations.

Each app should own its own URL patterns and the project-level URL configuration should include the app.

---

# 18. Coding Conventions

These are the conventions established by the current implementation.

## Use DRF generic views when appropriate

Prefer a focused generic view such as:

```python
generics.CreateAPIView
```

when the endpoint only needs create behavior.

Do not introduce ViewSets solely because DRF supports them.

---

## Keep serializers explicit

Fields are explicitly listed rather than exposing everything blindly.

For example:

```python
fields = [
    'id',
    'consultant',
    'room',
    'student_id',
    'start_time',
    'end_time',
    'session_type',
]
```

Use explicit fields for API contracts.

---

## IDs should not be client-controlled when generated by the database

The session ID is read-only in the serializer:

```python
read_only_fields = ['id']
```

Do not make database-generated IDs writable without a concrete requirement.

---

## Use descriptive tests

Tests should describe behavior:

```python
def test_create_scheduled_session_successful(self):
```

rather than implementation details.

Docstrings such as:

```python
"""Test consultant cannot have overlapping sessions."""
```

are used in the current tests.

---

## Keep one behavior per test

A test should ideally answer one clear question.

This is particularly important because the project is developed through TDD.

---

# 19. Things Codex MUST Check Before Changing Code

Before changing an existing behavior, Codex should inspect:

1. The relevant model
2. The relevant serializer
3. The relevant view
4. The relevant URL configuration
5. Existing tests
6. Related models and relationships
7. Existing migrations
8. Authentication/permission configuration
9. Existing naming conventions
10. Current test results

For scheduling specifically, always inspect:

```text
ScheduledSession
ConsultantProfile
Room
ScheduledSessionSerializer
scheduling views
scheduling URLs
scheduling tests
```

before modifying scheduling behavior.

---

# 20. Codex Must Not Guess

If a requirement is not explicitly established by:

* the code
* an existing test
* this file
* an explicit user instruction

Codex should not treat it as a project fact.

Examples of things that must NOT be invented:

* session type choices
* consultant roles
* room capacity
* maximum session duration
* working days
* timezone behavior
* cancellation rules
* student model structure
* pagination requirements
* deployment architecture
* production database details
* frontend behavior

If such functionality becomes necessary, inspect the repository and/or ask the user.

---

# 21. Changes Requiring Explanation / Confirmation

Codex should not silently make architectural changes such as:

* replacing the custom User model
* changing authentication mechanism
* changing JWT configuration
* changing database engine
* changing Docker architecture
* changing app boundaries
* moving apps between directories
* replacing generic views with ViewSets
* introducing a service layer
* changing model relationships
* making required fields nullable
* deleting migrations
* squashing migrations
* changing URL prefixes
* changing API response contracts
* removing authentication/authorization
* weakening business constraints
* changing existing tests merely to make them pass

If a test is wrong, explain why before changing the test.

If the implementation is wrong, fix the implementation first.

---

# 22. Do Not "Fix" Tests by Weakening Requirements

A failing test is information.

For example:

```text
Expected 400
Actual 201
```

should normally result in investigating missing validation.

Do not change:

```python
self.assertEqual(response.status_code, 400)
```

to:

```python
self.assertEqual(response.status_code, 201)
```

just to make the suite green.

Likewise, do not remove:

```python
IsAuthenticated
```

to solve a `401`.

The test represents intended behavior.

---

# 23. Model vs Serializer Rule

When implementing business logic, use this mental model:

### Model

Ask:

> Should this rule remain true regardless of how the object is created?

If yes, it belongs in the domain/model validation.

### Serializer

Ask:

> Should invalid API input be rejected before the object is created?

If yes, it also needs serializer/API validation.

This is especially relevant for scheduling.

---

# 24. Current Scheduling API Direction

The scheduling API is being developed incrementally.

Current create endpoint:

```text
POST /api/scheduling/
```

Expected successful request contains:

```json
{
    "consultant": <consultant_id>,
    "room": <room_id>,
    "student_id": "student-001",
    "start_time": "10:00:00",
    "end_time": "11:00:00",
    "session_type": "exam"
}
```

Successful creation returns:

```text
201
```

Authentication is required.

Invalid data returns:

```text
400
```

The following behaviors are already part of the test-driven implementation:

* create
* authentication
* required consultant
* required room
* valid time range
* consultant overlap protection

The next API behavior being developed is:

```text
room overlap protection
```

After that, the API is expected to grow toward list/retrieve/update/delete behavior, but those endpoints should be implemented only when tests/requirements establish them.

---

# 25. Current Development Checkpoint

The project has already reached several stable checkpoints.

Users:

```text
Tests passing
GitHub Actions green
Changes committed and pushed
```

Rooms:

```text
Model/API tests implemented
Authentication behavior tested
CRUD-related API behavior implemented
```

Scheduling:

```text
Model tests: 12 passing
API tests: currently developed incrementally
```

The latest active work is scheduling API testing.

At the latest known point:

```text
6 scheduling API tests passed
```

The next test concerns room overlap.

Do not claim additional tests are passing until they have actually been run.

---

# 26. Git / Checkpoint Workflow

The project uses Git for checkpoints.

After a meaningful green milestone:

```text
tests pass
    ↓
review diff
    ↓
commit
    ↓
push
    ↓
verify CI / GitHub Actions
```

A previous checkpoint was successfully:

* committed
* pushed
* verified through green GitHub Actions

Do not rewrite history or force-push unless explicitly requested.

Do not commit secrets.

---

# 27. GitHub Actions

The project uses GitHub Actions for automated checks.

A previous workflow issue was caused by:

```yaml
runs-one:
```

instead of:

```yaml
runs-on:
```

The workflow was corrected and GitHub Actions became green.

When modifying workflows, preserve valid GitHub Actions syntax and verify the workflow after changes.

---

# 28. Database / Persistence Principles

The project uses Django migrations for schema management.

Never manually modify the database schema as a substitute for Django migrations unless explicitly required.

When changing models:

```text
models.py
    ↓
makemigrations
    ↓
migration file
    ↓
migrate
    ↓
tests
```

For changes involving existing data, think about migration safety before accepting Django's interactive default suggestion.

---

# 29. Working With Existing Tests

Before adding a new test:

1. Search for similar existing tests.
2. Reuse existing helper methods.
3. Reuse existing setup/authentication patterns.
4. Match existing naming conventions.
5. Avoid duplicate coverage unless the new test covers a meaningful boundary.

For example, scheduling tests already have helper logic for creating consultants. Reuse it rather than creating a completely different helper unless necessary.

---

# 30. Important Boundary Cases for Scheduling

The following boundaries have already been considered and/or tested:

### Valid

```text
10:00–11:00
11:00–12:00
```

### Invalid

```text
10:00–11:00
10:30–11:30
```

### Invalid

```text
10:00–12:00
10:30–11:30
```

### Invalid

```text
10:00–11:00
09:30–10:30
```

### Valid

```text
10:00–11:00
09:00–10:00
```

The same overlap principle applies independently to:

```text
consultant
room
```

---

# 31. Architecture Decisions vs Future Suggestions

## Confirmed project decisions

These are established by implementation/tests:

* Django + Django REST Framework
* app-based architecture
* apps located under `app/`
* custom User model
* ConsultantProfile as a OneToOne relationship with User
* Room as a separate domain model
* ScheduledSession connecting consultant and room
* JWT token endpoint via SimpleJWT
* authenticated protected APIs
* TDD workflow
* model-level scheduling validation
* serializer-level scheduling API validation
* consultant overlap prevention
* room overlap prevention
* back-to-back sessions allowed
* explicit serializer fields
* Docker Compose development workflow
* WSL 2 development environment
* migrations managed by Django
* tests are the primary source of behavioral requirements

## Possible future improvements — NOT current requirements

These are suggestions only and must not be treated as existing architecture:

* extract scheduling conflict logic into a reusable service/validator
* introduce dedicated permission classes for role-based authorization
* add database-level exclusion constraints if supported and appropriate
* add transactional/concurrency protection around booking
* add pagination
* add filtering/search
* add API documentation
* add timezone-aware datetime scheduling
* introduce ViewSets if the CRUD surface becomes large
* add service-layer architecture

Codex must not implement these automatically.

---

# 32. Preferred Development Style

When asked to implement the next feature:

```text
1. Inspect current code
2. Identify the smallest behavior
3. Add one focused test
4. Run the test
5. Report/inspect the failure
6. Implement the smallest fix
7. Run the test
8. Run the relevant suite
9. Review the diff
10. Move to the next behavior
```

Do not jump directly to a large refactor.

The goal is not simply to get the code working.

The goal is to preserve:

```text
clarity
+
testability
+
domain correctness
+
API correctness
+
maintainability
```

---

# 33. How Codex Should Respond to Ambiguity

If the repository and this document do not establish an answer:

### Do not guess.

Instead:

1. inspect the relevant files;
2. search existing tests;
3. inspect migrations/models;
4. determine whether the requirement already exists elsewhere;
5. if still ambiguous, explain the ambiguity and ask before making an architectural decision.

For example, if `session_type` choices are not visible in the current model, Codex must not invent values such as:

```text
consultation
exam
follow-up
```

just because they seem reasonable.

Use only values confirmed by code/tests/user requirements.

---

# 34. Final Rule for Codex

The most important principle for this repository is:

> **Understand the existing architecture and tests before writing code.**

This project is being built deliberately through TDD.

A green test is not merely a technical result. It represents an established behavioral requirement.

A failing test is not an invitation to weaken the requirement. It is evidence about what implementation is missing or incorrect.

Before changing code, Codex should therefore ask:

```text
What behavior is being requested?
Where does that behavior belong?
What existing test establishes it?
What existing model/relationship does it depend on?
What authentication/permission rules already apply?
Will this change affect existing APIs or constraints?
Can the smallest change satisfy the requirement?
```

Preserve existing working behavior unless the user explicitly requests a change.

When uncertain, inspect first and ask rather than invent.
