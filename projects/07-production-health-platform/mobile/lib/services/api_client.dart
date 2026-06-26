import 'dart:convert';
import 'package:http/http.dart' as http;

/// Read-only client for the platform API (the dashboard read views).
class ApiClient {
  ApiClient(this.baseUrl);
  final String baseUrl; // e.g. https://platform.example.org/api

  Future<List<dynamic>> countries() async {
    final res = await http.get(Uri.parse('$baseUrl/countries'));
    if (res.statusCode != 200) throw Exception('API error ${res.statusCode}');
    return jsonDecode(res.body) as List<dynamic>;
  }

  Future<List<dynamic>> sitesAtRisk({int limit = 20}) async {
    final res = await http.get(Uri.parse('$baseUrl/sites/at-risk?limit=$limit'));
    if (res.statusCode != 200) throw Exception('API error ${res.statusCode}');
    return jsonDecode(res.body) as List<dynamic>;
  }
}
