import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:connectivity_plus/connectivity_plus.dart';
import 'local_store.dart';

/// Offline-first sync. Submissions are written to a local queue first, then pushed to CouchDB
/// whenever connectivity is available. Nothing is lost when the device is offline.
class SyncService {
  SyncService(this.couchBaseUrl, this.db);

  final String couchBaseUrl; // e.g. https://couch.example.org
  final String db;           // e.g. medic
  final LocalStore _store = LocalStore();

  Future<void> submit(Map<String, dynamic> form) async {
    await _store.enqueue(form);
    await sync();
  }

  Future<int> sync() async {
    final online = await Connectivity().checkConnectivity();
    if (online.contains(ConnectivityResult.none)) return 0;

    final pending = await _store.pending();
    var pushed = 0;
    for (final item in pending) {
      final res = await http.put(
        Uri.parse('$couchBaseUrl/$db/${item['_id']}'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(item['payload']),
      );
      if (res.statusCode == 201 || res.statusCode == 202) {
        await _store.markSynced(item['_id'] as String);
        pushed++;
      }
    }
    return pushed;
  }
}
