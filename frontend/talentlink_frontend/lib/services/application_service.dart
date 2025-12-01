import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/application.dart';
import 'auth_service.dart';

class ApplicationService {
  static const String baseUrl = "https://talentlink-erfan.nl/api/applications";

  Future<Application?> submitApplication(String jobId, String? cvId) async {
    final res = await http.post(
      Uri.parse(baseUrl),
      headers: AuthService.getAuthHeaders(),
      body: jsonEncode({
        'job_id': jobId,
        'cv_id': cvId,
      }),
    );

    if (res.statusCode == 201) {
      return Application.fromJson(jsonDecode(res.body));
    } else {
      print("Failed to submit application: ${res.body}");
      return null;
    }
  }

  Future<List<Application>> getMyApplications() async {
    final res = await http.get(
      Uri.parse("$baseUrl/my-applications"),
      headers: AuthService.getAuthHeaders(),
    );

    if (res.statusCode == 200) {
      final List<dynamic> data = jsonDecode(res.body);
      return data.map((json) => Application.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load applications');
    }
  }

  Future<List<Application>> getJobApplications(String jobId) async {
    final res = await http.get(
      Uri.parse("$baseUrl/job/$jobId"),
      headers: AuthService.getAuthHeaders(),
    );

    if (res.statusCode == 200) {
      final List<dynamic> data = jsonDecode(res.body);
      return data.map((json) => Application.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load job applications');
    }
  }

  Future<Application?> getApplication(String applicationId) async {
    final res = await http.get(
      Uri.parse("$baseUrl/$applicationId"),
      headers: AuthService.getAuthHeaders(),
    );

    if (res.statusCode == 200) {
      return Application.fromJson(jsonDecode(res.body));
    } else {
      return null;
    }
  }

  Future<bool> inviteCandidate(String applicationId) async {
    final res = await http.post(
      Uri.parse("$baseUrl/$applicationId/invite"),
      headers: AuthService.getAuthHeaders(),
    );

    return res.statusCode == 200;
  }

  Future<bool> updateStatus(String applicationId, String status) async {
    final res = await http.put(
      Uri.parse("$baseUrl/$applicationId/status"),
      headers: AuthService.getAuthHeaders(),
      body: jsonEncode({'status': status}),
    );

    return res.statusCode == 200;
  }
}
