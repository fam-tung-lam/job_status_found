# Routing

How a feature declares its routes and how the app composes them into one router.
These rules apply only in the monorepo described in
[SKILL.md](../SKILL.md#choose-the-layout). The single-package layout keeps every
route in `app_router.dart`, as [widgets.md](widgets.md#routes) describes; in
this monorepo a feature package declares its own routes and the app composes
them.

## The feature declares, the app composes

| Owner   | File                                                | Holds                                                                                       |
| ------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Feature | `lib/src/presentation/routes/<feature>_routes.dart` | Route name, path, and parameter constants, its `GoRoute` list, and typed navigation helpers |
| Feature | `lib/ptlam_agent_os_<feature>.dart`                 | Exports the route constants, helpers, and list under a feature-specific name                |
| App     | `lib/app/app_router.dart`                           | One `GoRouter`: initial location, shells, redirects, error page, and every feature's list   |

Each feature exposes its list under a feature-specific name, such as
`ordersRoutes` or `tasksRoutes`; the app spreads those lists into one `routes:`
argument. Shell routes, authentication redirects, and the not-found page belong
to the app because they span features.

## Navigating

Inside a feature, navigate through its own typed navigation helpers. To reach
another feature's page, declare a navigator port in the feature's
`application/ports/` and let the app implement it, as
[composition.md](composition.md#joining-features-in-the-app) describes.
