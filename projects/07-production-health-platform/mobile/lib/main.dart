import 'package:flutter/material.dart';
import 'screens/submit_form.dart';
import 'screens/dashboard.dart';

void main() => runApp(const HealthApp());

class HealthApp extends StatelessWidget {
  const HealthApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Health Platform',
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF1F6F8B),
        useMaterial3: true,
      ),
      home: const Home(),
    );
  }
}

class Home extends StatefulWidget {
  const Home({super.key});
  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  int _index = 0;
  final _pages = const [SubmitFormScreen(), DashboardScreen()];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.edit_note), label: 'Submit'),
          NavigationDestination(icon: Icon(Icons.insights), label: 'Dashboard'),
        ],
      ),
    );
  }
}
