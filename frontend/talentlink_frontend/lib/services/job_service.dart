import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/job.dart';
import 'auth_service.dart';

class JobService {
  static const String baseUrl = "https://talentlink-erfan.nl/api/jobs";

  Future<List<Job>> getAllJobs() async {
    final res = await http.get(Uri.parse(baseUrl));

    if (res.statusCode == 200) {
      final List<dynamic> data = jsonDecode(res.body);
      return data.map((json) => Job.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load jobs');
    }
  }

  Future<Job?> getJob(String jobId) async {
    final res = await http.get(Uri.parse("$baseUrl/$jobId"));

    if (res.statusCode == 200) {
      return Job.fromJson(jsonDecode(res.body));
    } else {
      return null;
    }
  }

  Future<List<Job>> getMyJobs() async {
    final res = await http.get(
      Uri.parse("$baseUrl/my-jobs"),
      headers: AuthService.getAuthHeaders(),
    );

    if (res.statusCode == 200) {
      final List<dynamic> data = jsonDecode(res.body);
      return data.map((json) => Job.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load my jobs');
    }
  }

  Future<Job?> createJob(Job job) async {
    final res = await http.post(
      Uri.parse(baseUrl),
      headers: AuthService.getAuthHeaders(),
      body: jsonEncode(job.toJson()),
    );

    if (res.statusCode == 201) {
      return Job.fromJson(jsonDecode(res.body));
    } else {
      print("Failed to create job: ${res.body}");
      return null;
    }
  }

  Future<bool> updateJob(String jobId, Map<String, dynamic> updates) async {
    final res = await http.put(
      Uri.parse("$baseUrl/$jobId"),
      headers: AuthService.getAuthHeaders(),
      body: jsonEncode(updates),
    );

    return res.statusCode == 200;
  }

  Future<bool> deleteJob(String jobId) async {
    final res = await http.delete(
      Uri.parse("$baseUrl/$jobId"),
      headers: AuthService.getAuthHeaders(),
    );

    return res.statusCode == 200;
  }
}
