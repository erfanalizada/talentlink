import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  static const String baseUrl = "https://talentlink-erfan.nl/api/auth";

  Future<Map<String, dynamic>?> login(String username, String password) async {
    final res = await http.post(
      Uri.parse("$baseUrl/login"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"username": username, "password": password}),
    );

    if (res.statusCode == 200) {
      return jsonDecode(res.body);
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
}
