# Frontend shell

The shell is the app-wide plumbing every page runs inside: boot, layouts, routing and guards, the axios interceptors, the `context` store, demo mode, and Google Analytics. Key files: `src/main.ts`, `src/App.vue`, `src/layouts/` (`StandardLayout.vue`, `PeerAdvisor.vue`, `Login.vue`, `shared/`), `src/router.ts`, `src/lib/axios-utils.ts`, `src/stores/context.ts`, `src/lib/utils.ts`, and `src/lib/ga.ts`.

Role rules behind the route guards are in `.claude/docs/permissions.md`. Accessibility rules and helpers are in `src/CLAUDE.md`. This doc says where the shell implements them.

## Startup (`src/main.ts`)

`index.html` is a bare `<div id="app">` with `lang="en"`, a default `<title>Welcome | BOA</title>`, and a module script for `src/main.ts`.

```
createApp(App)
  app.config.errorHandler = appErrorHandler              # axios-utils.ts
  .use(axiosPlugin, CkeditorPlugin, createPinia(), setupCalendar, VueHighcharts, vuetify)
  .directive('accessibleGrade' | 'linkified' | 'tableCaption')
initializeAxios(axios)                                    # interceptors on the global axios
GET /api/config        → contextStore.setConfig({...data, apiBaseUrl, isVueAppDebugMode})
  GET /api/profile/my  → contextStore.setCurrentUser(data)   # also loads getDepartments() if authenticated
    → initGoogleAnalytics()
    → getServiceAnnouncement() → setServiceAnnouncement(data)
        → if config.pingFrequency: setInterval(GET /api/user/session_keep_alive, pingFrequency)
        → app.use(router).mount('#app')
```

- Nothing mounts until all four requests finish. None of them has a `.catch`, so a failure leaves a blank page.
- `apiBaseUrl` comes from `VITE_APP_API_BASE_URL`; `isVueAppDebugMode` from `VITE_APP_DEBUG`. Everything else in `config` comes from `GET /api/config` (`boac/api/config_controller.py`), including `csrfToken`, `pingFrequency`, `gaMeasurementId`, `isDemoModeAvailable`, and `fixedWarningOnAllPages`.
- **Directives:** `v-accessible-grade` replaces `-`/`+` with `&minus;`/`&plus;` so screen readers say them. `v-linkified` runs `linkify-html` over the element's HTML once, at `beforeMount`. `v-table-caption` (`src/directives/tableCaption.ts`) inserts an `sr-only` `<caption>` into the first `<table>` inside the element, waiting with a `MutationObserver` if the table isn't rendered yet; the text defaults to "Data table".
- **Vuetify** (`src/plugins/vuetify.ts`) registers components individually (an unregistered one won't render), the mdi SVG icon set, the `highchartsA11y`, `Intersect`, and `Resize` directives, breakpoints (`md` starts at 960px), and the light theme's color tokens (`category-*`, `on-category-*`, `service-announcement`, etc.).
- `src/plugins/axios.ts` adds `$axios` to `globalProperties`. No code uses it; API modules import the global `axios`, which is the instance with the interceptors.

## App and layouts

`src/App.vue` holds the `#announcer` live region (`aria-live` = `screenReaderAlert.politeness`, text = `screenReaderAlert.message`), the top-level `<router-view>`, and `DismissibleFooterAlert`. The last two get `aria-hidden` and `inert` while `contextStore.isModalOpen`. It also imports the global styles (`global.css`, `focus.scss`, CKEditor and v-calendar CSS).

| Layout | Used by | Contents |
|---|---|---|
| `Login.vue` | `/` when signed out | CAS sign-in button or `DevAuth` (if `config.devAuthEnabled`); shows `?error=`; announces "Sign-in page loaded." and focuses `dev-auth-uid` or `sign-in` |
| `StandardLayout.vue` | Advisor, director, admin, CE3, degree, peer-manager routes | Skip links, `v-app-bar` + `AppBar`, sidebar, spinner, `ServiceAnnouncement`, `#content`, `EditBatchNoteModal`, footer |
| `PeerAdvisor.vue` | `/peer_advisor/*` | Same, minus the sidebar, "Skip to navigation" link, and batch-note modal |
| none | `/degree/:id/print` | `PrintableDegreeTemplate` renders without a layout |

Shared pieces (`src/layouts/shared/`, `src/components/`):

- **Skip links** (`sr-only sr-only-focusable`): "Skip to main content" (`#content`), and in `StandardLayout` "Skip to navigation" (`#main-menu-nav`) plus "Skip navigation" at the top of the sidebar.
- **Landmarks:** the app bar is `role="banner"`, the sidebar is a `<nav aria-label="main menu">`, `#content` is `role="main"` with `tabindex="-1"` (and `aria-labelledby="page-header"` in `StandardLayout`), and the footer is `role="contentinfo"`.
- **`AppBar.vue`:** home link (`/home`), `AdvancedSearch`, and `HeaderMenu` (degree checks, peer-advisor management, Flight Data Recorder, admin pages, profile, and sign out via `getCasLogoutUrl()`, each shown by role).
- **Sidebar** (`src/components/sidebar/`): `Sidebar.vue` lists the user's cohorts and curated groups (and CE3 admit cohorts/groups when `canAccessAdmittedStudents`), with create links and "Everyone's Cohorts" / "Everyone's Groups" links. `SidebarFooter.vue` (when `canAccessAdvisingData`) has the batch-note button (non-admins) and `LinkToDraftNotes`. Below `md`, the drawer becomes an inline `<nav>` toggled by `v-app-bar-nav-icon` (`aria-expanded`, `aria-controls`). Details: `.claude/docs/cohorts.md`, `.claude/docs/curated-groups.md`.
- **Spinner:** while `contextStore.loading`, `PlaneGoRound` (`role="progressbar"`, `aria-label="page loading"`) shows and `#content` is hidden with `v-show`. The footer is also hidden while loading or after a `hide-footer` broadcast (`Course.vue`).
- **`ServiceAnnouncement.vue`:** shows the published announcement inside `aria-live="assertive" role="alert"` (rendered with `v-html`). Dismiss/restore swaps focus between `dismiss-service-announcement` and an `sr-only` "Restore BOA Service Alert" button. State is in the store only. When it's visible, the layout raises `scroll-margin-top` on `.scroll-margins` by the banner's height.
- **`DismissibleFooterAlert.vue`:** a fixed bottom bar with `config.fixedWarningOnAllPages`. In debug mode it shows the current screen-reader message instead, which is handy for checking announcements. An in-flow spacer, kept at the bar's height by a `ResizeObserver`, lets the end of the page (the footer) scroll clear of the bar at any text size.

## Router (`src/router.ts`)

- History mode (`createWebHistory`). Views are lazy imports, except `PeerAdvisorHome`.
- Routes are grouped under several `path: '/'` parents, each with one `beforeEnter` guard: advisor (`isAdvisor || isDirector || isAdmin`), peer-advisor manager (`/peer/management/:id`), peer advisor (`/peer_advisor/*`), admin, director (`/analytics/:deptCode`), CE3 (`/admit/*`), and degree progress (`$_requiresDegreeProgress`). See `.claude/docs/permissions.md` for each rule.
- Every guard sends an anonymous user to `/` with `?redirect=<fullPath>` (`$_goToLogin`) and an unauthorized user to `/404`. The login route forwards a signed-in user to `query.redirect` or `/home`.
- The last group (`/home`, `/profile`, `/error`, `/404`, and the `/:pathMatch(.*)*` catch-all, which redirects to `/404`) sends peer advisors to `/peer_advisor${to.fullPath}`.
- `beforeEach` calls `useSearchStore().resetAdvancedSearch()` on every route except `/search`.
- `afterEach` (unless it's a hash change on the same named route) calls `resetApplicationState()` and sets `document.title` to `<route name> | BOA`, or `Welcome | BOA` when unnamed. **Route names are the default page titles.** Views overwrite them with `setPageTitle()`.
- `meta.groupsType` (read by `BrowseAllGroups.vue`) is the only route meta any view reads.
- There's no `scrollBehavior`, and the router doesn't move focus after navigation. Each view does that itself (see "Wiring a new page").
- Layouts key their `<router-view>` on `route.fullPath` minus the hash, so a query change remounts the view. `NavLink.vue` adds a `_` query param that flips on each click (`setRouteKeyId`), so clicking a link to the current page reloads it.

## HTTP errors (`src/lib/axios-utils.ts`)

- `axios.defaults.withCredentials = true`.
- **CSRF:** a request interceptor adds `X-CSRFToken: config.csrfToken` to `post`, `put`, `patch`, and `delete`. The token is fetched once, at boot, from `/api/config`.
- **401/403:** the response interceptor re-fetches `/api/profile/my`, stores it with `setCurrentUser`, then runs `axiosErrorHandler`.
- `axiosErrorHandler` calls `loadingComplete()` (unless the request was cancelled), then:

| Condition (checked in order) | Result |
|---|---|
| `currentUser.isAuthenticated` is false | `router.push('/?m=Your session has expired')` |
| status 404 | `router.push('/404')` |
| anything else, not cancelled, URL not in `SKIP_REDIRECT_ON_ERROR` | `router.push('/error')` with query `c` (error class), `m` (message), `s` (status), `t` (status text) |

- A 403 from a signed-in user therefore lands on `/error`. `SKIP_REDIRECT_ON_ERROR` (user create/update and create peer advisor) lets those forms show their own errors.
- The promise is still rejected, so a caller's `.catch` runs after the redirect starts.
- `appErrorHandler` (uncaught component errors) logs the message and stack to the console and calls `setApplicationState(500, ...)`. No component reads `applicationState`.

## Stores

`src/stores/context.ts` (`useContextStore`):

| State | Purpose |
|---|---|
| `config`, `currentUser` (`ANONYMOUS_USER` until boot), `announcement` | Set at boot. `currentUser` is replaced by `setCurrentUser` on 401/403 and by `getUserProfile()` callers such as `Home.vue` |
| `allBerkeleyDepartments`, `allPeerAdvisingDepartments` | Loaded by `setCurrentUser` for signed-in users |
| `loading`, `loadingStartTime` | `loadingStart()` / `loadingComplete(focusId?)` |
| `screenReaderAlert` | `{message, politeness}`, written by `alertScreenReader()` |
| `isModalOpen` | Set by `toggleModalBackgroundDisabled()`; makes the app `inert` |
| `dismissedServiceAnnouncement`, `dismissedFooterAlert` | Banner dismissals, lost on reload |
| `eventHub` (mitt) | `broadcast(type, data)`, `setEventHandler`, `removeEventHandler` |
| `routeKeyId` | Used by `NavLink` (above) |

Common `eventHub` events: `note-created`/`note-updated`/`note-deleted`, `comment-*`, `my-curated-groups-updated`, `curated-group-*`, `termId-user-preference-change`, `hide-footer`, and `user-session-expired` (sets `noteStore.boaSessionExpired` in the note editors). Other app-wide stores: `search.ts` (header search) and `manifest.ts` (admin user list). Edit-session stores are per feature.

## Session keep-alive

If `config.pingFrequency` is set (`PING_FREQUENCY`, milliseconds, `config/default.py`), `main.ts` calls `GET /api/user/session_keep_alive` (`@login_required`) on that interval. A response with `isAuthenticated` false broadcasts `user-session-expired`. A 401 goes through the interceptor and ends at `/?m=Your session has expired`. `getUserProfile()` (`src/api/user.ts`) also broadcasts `user-session-expired` when the profile is anonymous.

## Demo mode

`currentUser.inDemoMode` (toggled by `DemoModeToggle.vue` → `POST /api/user/demo_mode`, offered only when `config.isDemoModeAvailable`) does two things:

- **Blur:** components add `demo-mode-blur` (or `img-blur` for photos) to personal fields; `global.css` makes the text transparent with a shadow. Views also call `setPageTitle('Student')`-style generic titles instead of the name.
- **Encoded IDs in URLs:** student links use `studentRoutePath(uid, inDemoMode)` (`src/lib/utils.ts`), which puts `window.btoa(uid)` in `/student/:uid`. `Student.vue`, `StudentDegreeCreate.vue`, and `StudentDegreeHistory.vue` decode with `window.atob`. Admit links do the same with the SID (`SortableAdmits.vue`, `AdmitStudentsTable.vue`, decoded in `AdmitStudent.vue`). Base64 hides the ID from a casual glance; it isn't encryption.

## Google Analytics (`src/lib/ga.ts`)

- `initGoogleAnalytics()` runs only when `currentUser.uid` is set, the user isn't an admin, and `config.gaMeasurementId` is set. It calls vue-gtag `configure()` with `user_id` = the signed-in user's UID and `user_properties` `{dept_code: [deptCodes], title, uid}`. No router page tracker is configured.
- `track(action, category, label?, id?)` sends `event(action, {event_category, event_label, value})` for any non-admin with a UID. It doesn't check `gaMeasurementId`.

| Category | Sent from | Actions (label) |
|---|---|---|
| `Search` | `src/api/search.ts` | the raw search phrase is the action (basic and peer-advisor search) |
| `Student` | `src/api/student.ts`, `src/api/admit.ts` | `view`, `dismiss alert`, `admit`, `admits`; `getStudentBySid` sends the **student's UID** as the action |
| `Cohort` | `src/api/cohort.ts`, `cohort-csv.ts`, `curated.ts` | `create`, `update`, `delete`, `view`, `download` (label: CSV filename or `Cohort: <name>` / `Curated group: <name>`). Curated groups report under `Cohort` |
| `Course` | `src/views/Course.vue` | `view` (section display name) |
| `Degree Progress` | `src/api/degree.ts` | `create`, `view`, `update`, `delete`, `clone`, `archive`, `unarchive` (fixed labels; batch create sends the count) |
| `Advising Note` | `src/api/notes.ts` | `view`, `read`, `update`, `delete` (no label) |
| `Note Template` | `src/api/note-templates.ts` | `create`, `update` (no label) |
| `Appointment` | `src/api/appointments.ts` | `read` (no label) |

`ga.curated()` exists but has no callers.

## Wiring a new page

1. Add a route as a child of the parent whose guard matches who may see it. Give it a unique `name`; it becomes the default title.
2. In `<script setup>`, call `contextStore.loadingStart()`. It shows the spinner and announces "Loading." (persistently, until the next announcement).
3. Load data through `src/api/`. Let the interceptor handle 404s and server errors unless the page needs its own message.
4. When data is ready, call `setPageTitle(...)` (generic text in demo mode), then `contextStore.loadingComplete('<h1 id>')`. With an ID it adds `tabindex="-1"` and `scroll-margins`, focuses, and scrolls that element, trying up to four times, 500ms apart. Without an ID it only clears `loading`.
5. Give the view one `<h1>`; `id="page-header"` matches `StandardLayout`'s `aria-labelledby` on `#content`.
6. Use `NavLink` or `router-link` for internal links, and `studentRoutePath()` for student links.

## Gotchas

- **Route names must be unique across the whole table.** vue-router drops an earlier route when a later one reuses its name, even under a different parent. Since names double as titles, pick a new one rather than copying a neighbor's.
- **Focus after navigation is per view.** Most views call `loadingComplete()` with no ID, so focus stays where it was. New pages should pass their `<h1>` ID.
- **`loading` hides `#content` with `v-show`.** Elements inside it exist but aren't focusable until `loadingComplete()`. Call `putFocusNextTick` after that, not before.
- **An error anywhere navigates away.** Any rejected axios call (other than a cancel or the two skipped URLs) sends the user to `/error` or `/404`, even from a background request. Cancelled requests (e.g. via `AbortController`) are the exception.
- **`config.isProduction` is not in the `/api/config` payload.** It's declared in `BoaConfig`, but checks against it (`loadingComplete`'s timing log, `Error.vue`'s status details) always see it as falsy.
- **The CSRF token is read from `config` on each request.** Don't send unsafe methods with another axios instance, or the header is missing.
- **`removeEventHandler(type)` without a handler removes every handler of that type** (mitt behavior). Pass the same function you registered.
- **`alertScreenReader` messages clear after 5 seconds** unless `persistent` is true. A new call clears the previous message first.
- **`/` is a global hotkey.** `AdvancedSearch` adds a document `keyup` listener so `/` focuses `basic-search-input` unless a text input has focus or `degreeStore.disableButtons` is set.
