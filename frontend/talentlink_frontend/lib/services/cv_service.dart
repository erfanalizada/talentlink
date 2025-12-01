import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/cv.dart';
import 'auth_service.dart';

class CVService {
  static const String baseUrl = "https://talentlink-erfan.nl/api/cv";

  Future<CV?> uploadCV(List<int> fileBytes, String fileName) async {
    final request = http.MultipartRequest('POST', Uri.parse("$baseUrl/upload"));
    request.headers['Authorization'] = 'Bearer ${AuthService.token}';
    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        fileBytes,
        filename: fileName,
      ),
    );

    final response = await request.send();

    if (response.statusCode == 201) {
      final responseBody = await response.stream.bytesToString();
      return CV.fromJson(jsonDecode(responseBody));
    } else {
      print("Failed to upload CV: ${response.statusCode}");
      return null;
    }
  }

  Future<CV?> getMyCV() async {
    final res = await http.get(
      Uri.parse("$baseUrl/my-cv"),
      headers: AuthService.getAuthHeaders(),
    );

    if (res.statusCode == 200) {
      return CV.fromJson(jsonDecode(res.body));
    } else if (res.statusCode == 404) {
      return null;
    } else {
      throw Exception('Failed to get CV');
    }
  }

  Future<CV?> getCV(String cvId) async {
    final res = await http.get(
      Uri.parse("$baseUrl/$cvId"),
      headers: AuthService.getAuthHeaders(),
    );

    if (res.statusCode == 200) {
      return CV.fromJson(jsonDecode(res.body));
    } else {
      return null;
    }
  }

  Future<List<int>?> downloadCV(String cvId) async {
    final res = await http.get(
      Uri.parse("$baseUrl/$cvId/download"),
      headers: {
        'Authorization': 'Bearer ${AuthService.token}',
      },
    );

    if (res.statusCode == 200) {
      return res.bodyBytes;
    } else {
      return null;
    }
  }
}
