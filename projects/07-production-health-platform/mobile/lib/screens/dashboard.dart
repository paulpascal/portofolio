import 'package:flutter/material.dart';
import '../services/api_client.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _api = ApiClient('https://platform.example.org/api');
  late Future<List<dynamic>> _future;

  @override
  void initState() {
    super.initState();
    _future = _api.countries();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Coverage by country')),
      body: FutureBuilder<List<dynamic>>(
        future: _future,
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snap.hasError) {
            return Center(child: Text('Could not load: ${snap.error}'));
          }
          final rows = snap.data ?? [];
          return ListView.separated(
            itemCount: rows.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, i) {
              final r = rows[i] as Map<String, dynamic>;
              return ListTile(
                title: Text(r['country'].toString()),
                subtitle: Text('Attainment: ${r['avg_attainment']}'),
                trailing: Text('${r['households_visited']}'),
              );
            },
          );
        },
      ),
    );
  }
}
