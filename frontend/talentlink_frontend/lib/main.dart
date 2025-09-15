import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _response = "No response yet";

  Future<void> _callBackend() async {
    try {
      final res = await http.get(Uri.parse('/api/hello'));
      if (res.statusCode == 200) {
        final body = jsonDecode(res.body);
        setState(() {
          _response = body['message'] ?? "No message field";
        });
      } else {
        setState(() => _response = "Error: ${res.statusCode}");
      }
    } catch (e) {
      setState(() => _response = "Failed: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Talentlink Minimal UI")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_response, style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _callBackend,
              child: const Text("Call Backend"),
            ),
          ],
        ),
      ),
    );
  }
}
//ddd