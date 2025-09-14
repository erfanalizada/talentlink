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
    return MaterialApp(
      title: 'TalentLink Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String _message = "Click the button to call backend";

  Future<void> _callBackend() async {
    try {
      final response = await http.get(Uri.parse("/api/hello"));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _message = data["message"];
        });
      } else {
        setState(() {
          _message = "Error: ${response.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _message = "Exception: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("TalentLink")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_message, style: const TextStyle(fontSize: 18)),
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
