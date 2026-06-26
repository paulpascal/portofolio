# Mobile app (Flutter)

Offline-first form capture for community health workers, plus a light read-only dashboard.

- **Offline first.** Submissions are written to a local SQLite queue (`local_store.dart`) and pushed to
  CouchDB by `sync_service.dart` whenever connectivity returns. Nothing is lost offline; CouchDB handles
  the conflict-tolerant sync.
- **Capture** (`screens/submit_form.dart`): the monthly community-health form.
- **Dashboard** (`screens/dashboard.dart`): reads coverage by country from the platform API
  (`services/api_client.dart`).

## Run

```bash
flutter pub get
flutter run
```

Point `SyncService` at your CouchDB URL and `ApiClient` at the platform API base URL (or inject them via
build config). This is a focused reference app, not a full production build, but the offline-queue and
sync pattern is the real one.
