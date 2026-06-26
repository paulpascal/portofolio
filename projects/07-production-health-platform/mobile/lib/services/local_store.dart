import 'dart:convert';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as p;

/// Local offline queue backed by SQLite. Submissions live here until they sync to CouchDB.
class LocalStore {
  Database? _db;

  Future<Database> _open() async {
    if (_db != null) return _db!;
    _db = await openDatabase(
      p.join(await getDatabasesPath(), 'queue.db'),
      version: 1,
      onCreate: (db, _) => db.execute(
        'CREATE TABLE queue(id TEXT PRIMARY KEY, payload TEXT, synced INTEGER DEFAULT 0)',
      ),
    );
    return _db!;
  }

  Future<void> enqueue(Map<String, dynamic> form) async {
    final db = await _open();
    final id = '${form['site_id']}-${form['period']}';
    form['_id'] = id;
    await db.insert('queue', {'id': id, 'payload': jsonEncode(form), 'synced': 0},
        conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Map<String, dynamic>>> pending() async {
    final db = await _open();
    final rows = await db.query('queue', where: 'synced = 0');
    return rows
        .map((r) => {'_id': r['id'], 'payload': jsonDecode(r['payload'] as String)})
        .toList();
  }

  Future<void> markSynced(String id) async {
    final db = await _open();
    await db.update('queue', {'synced': 1}, where: 'id = ?', whereArgs: [id]);
  }
}
