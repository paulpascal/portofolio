import 'package:flutter/material.dart';
import '../services/sync_service.dart';

class SubmitFormScreen extends StatefulWidget {
  const SubmitFormScreen({super.key});
  @override
  State<SubmitFormScreen> createState() => _SubmitFormScreenState();
}

class _SubmitFormScreenState extends State<SubmitFormScreen> {
  final _form = GlobalKey<FormState>();
  final _sync = SyncService('https://couch.example.org', 'medic');
  final _values = <String, String>{};
  String _status = '';

  Widget _field(String key, String label, {bool number = true}) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: TextFormField(
          decoration: InputDecoration(labelText: label, border: const OutlineInputBorder()),
          keyboardType: number ? TextInputType.number : TextInputType.text,
          validator: (v) => (v == null || v.isEmpty) ? 'Required' : null,
          onSaved: (v) => _values[key] = v ?? '',
        ),
      );

  Future<void> _submit() async {
    if (!_form.currentState!.validate()) return;
    _form.currentState!.save();
    final doc = {
      'form': 'chw_monthly',
      'site_id': _values['site_id'],
      'period': _values['period'],
      'target_households': int.tryParse(_values['target'] ?? '0'),
      'submitted_at': DateTime.now().toUtc().toIso8601String(),
      'metrics': {
        'households_visited': int.tryParse(_values['households'] ?? '0'),
        'children_screened': int.tryParse(_values['children'] ?? '0'),
        'referrals_made': int.tryParse(_values['referrals'] ?? '0'),
        'stockout_days': int.tryParse(_values['stockout'] ?? '0'),
      },
    };
    await _sync.submit(doc);
    setState(() => _status = 'Saved. It will sync when you are online.');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Monthly report')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _form,
          child: ListView(children: [
            _field('site_id', 'Site ID', number: false),
            _field('period', 'Period (YYYY-MM)', number: false),
            _field('target', 'Target households'),
            _field('households', 'Households visited'),
            _field('children', 'Children screened'),
            _field('referrals', 'Referrals made'),
            _field('stockout', 'Stockout days'),
            const SizedBox(height: 12),
            FilledButton(onPressed: _submit, child: const Text('Submit')),
            if (_status.isNotEmpty)
              Padding(padding: const EdgeInsets.only(top: 12), child: Text(_status)),
          ]),
        ),
      ),
    );
  }
}
