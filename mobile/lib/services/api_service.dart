import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/scan_models.dart';

class ApiService {
  // Current local Wi-Fi IPv4 address: 10.148.3.32
  static const String defaultBaseUrl = 'http://10.148.3.32:8000';
  static const String prefsKey = 'backend_api_base_url';

  String _baseUrl;
  final http.Client _client;

  ApiService({String? baseUrl, http.Client? client})
      : _baseUrl = baseUrl ?? defaultBaseUrl,
        _client = client ?? http.Client() {
    _loadSavedUrl();
  }

  String get baseUrl => _baseUrl;

  Future<void> _loadSavedUrl() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final saved = prefs.getString(prefsKey);
      if (saved != null && saved.trim().isNotEmpty) {
        _baseUrl = saved.trim();
      }
    } catch (_) {}
  }

  Future<void> setBaseUrl(String newUrl) async {
    String formatted = newUrl.trim();
    if (!formatted.startsWith('http://') && !formatted.startsWith('https://')) {
      formatted = 'http://$formatted';
    }
    if (formatted.endsWith('/')) {
      formatted = formatted.substring(0, formatted.length - 1);
    }
    _baseUrl = formatted;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(prefsKey, _baseUrl);
    } catch (_) {}
  }

  Future<bool> checkHealth([String? targetUrl]) async {
    try {
      final urlToCheck = targetUrl ?? _baseUrl;
      final uri = Uri.parse(urlToCheck.endsWith('/') ? urlToCheck : '$urlToCheck/');
      final res = await _client.get(uri).timeout(const Duration(seconds: 4));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<ScanResponse> scanUrl(String targetUrl, {String siteType = 'general'}) async {
    final uri = Uri.parse('$_baseUrl/api/v1/scan');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'url': targetUrl,
        'site_type': siteType,
      }),
    ).timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = jsonDecode(response.body);
      return ScanResponse.fromJson(data);
    } else {
      String errorMessage = 'Scan request failed (${response.statusCode})';
      try {
        final errJson = jsonDecode(response.body);
        if (errJson['detail'] != null) {
          errorMessage = errJson['detail'].toString();
        }
      } catch (_) {}
      throw Exception(errorMessage);
    }
  }
}
