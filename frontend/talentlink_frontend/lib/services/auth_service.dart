import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:jwt_decoder/jwt_decoder.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const String baseUrl = "https://talentlink-erfan.nl/api/auth";

  static String? _token;
  static String? _userId;
  static List<String>? _roles;

  static String? get token => _token;
  static String? get userId => _userId;
  static List<String>? get roles => _roles;

  static bool get isLoggedIn => _token != null;

  static bool hasRole(String role) {
    return _roles?.contains(role) ?? false;
  }

  static bool get isEmployee => hasRole('employee');
  static bool get isEmployer => hasRole('employer');

  Future<Map<String, dynamic>?> login(String username, String password) async {
    final res = await http.post(
      Uri.parse("$baseUrl/login"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"username": username, "password": password}),
    );

    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      final token = data['access_token'];

      // Save token
      await _saveToken(token);

      return data;
    } else {
      print("Login failed: ${res.body}");
      return null;
    }
  }

  Future<bool> register(String username, String email, String password, String role) async {
    final res = await http.post(
      Uri.parse("$baseUrl/register"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "username": username,
        "email": email,
        "password": password,
        "role": role,
      }),
    );

    if (res.statusCode == 201) {
      return true;
    } else {
      print("Registration failed: ${res.body}");
      return false;
    }
  }

  static Future<void> _saveToken(String token) async {
    _token = token;
    final decoded = JwtDecoder.decode(token);
    _userId = decoded['sub'];
    _roles = List<String>.from(decoded['realm_access']?['roles'] ?? []);

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
  }

  static Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token != null && !JwtDecoder.isExpired(token)) {
      _token = token;
      final decoded = JwtDecoder.decode(token);
      _userId = decoded['sub'];
      _roles = List<String>.from(decoded['realm_access']?['roles'] ?? []);
    }
  }

  static Future<void> logout() async {
    _token = null;
    _userId = null;
    _roles = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
  }

  static Map<String, String> getAuthHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $_token',
    };
  }
}
