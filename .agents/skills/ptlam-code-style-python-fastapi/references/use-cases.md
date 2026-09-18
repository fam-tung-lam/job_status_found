# FastAPI Use Cases

One application operation per verb-first file under
`features/<feature>/application/use_cases/`. Use cases are the only path from an
HTTP handler or a durable task to an application port.

## Keep the operation transport-neutral

- Import no `fastapi`, `starlette`, `Request`, `Depends`, or `HTTPException`.
- Receive collaborators in `__init__` and operation input in `__call__`.
- Use a command dataclass when an operation has several input fields; pass one
  scalar directly when it has one.
- Return a domain entity or an application DTO, and let presentation map it to
  the public response.
- Raise domain exceptions and let the application map them once.

```python
# features/users/application/use_cases/create_user.py
@dataclass(frozen=True)
class CreateUserCommand:
    email: str
    display_name: str


class CreateUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def __call__(self, command: CreateUserCommand) -> User:
        if await self._users.exists(email=command.email):
            raise EmailAlreadyRegistered(command.email)
        user = await self._users.add(
            User(email=command.email, display_name=command.display_name)
        )
        await self._users.commit()
        return user
```

## Own one transaction boundary

A write use case commits once, after its transactional work succeeds. A read use
case makes the no-commit decision explicit. Routers and repositories never
commit on the operation's behalf.

Keep a non-transactional remote effect after the commit only when its failure
and retry behavior is safe. Use an outbox or another durable handoff when the
database change and the effect must not drift apart.

Do not call a sibling use case. Extract shared rules into a narrowly named
feature policy so transaction boundaries stay visible. Prefer events or
composition-root coordination between features; when direct orchestration is
required, import only the other feature's facade.

## Assemble at the FastAPI boundary

```python
# features/users/di.py -- the feature composition seam
def get_create_user(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateUser:
    return CreateUser(SqlUserRepository(session))
```

```python
# features/users/presentation/http/users_controller.py
@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    create: Annotated[CreateUser, Depends(get_create_user)],
) -> User:
    return await create(CreateUserCommand(**body.model_dump()))
```

Use cases are the local-unit test surface: build one with controlled port and
integration fakes, call it directly, and assert its result or failure.

Finish when each operation has one file under `application/use_cases/`, one
transaction decision, ordinary typed inputs, no framework or infrastructure
import, and one feature-root provider that assembles it.
