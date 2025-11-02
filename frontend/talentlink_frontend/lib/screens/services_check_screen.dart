import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _selectedIndex = 0;
  final List<Map<String, String>> _services = [
    {"title": "Hello Service", "url": "/api/hello"},
    {"title": "Auth Service", "url": "/api/auth/health"},
    {"title": "User Service", "url": "/api/users/health"},
    {"title": "Job Service", "url": "/api/jobs/health"},
    {"title": "CV Service", "url": "/api/cv/health"},
    {"title": "Matching Service", "url": "/api/matching/health"},
    {"title": "Notification Service", "url": "/api/notifications/health"},
  ];

  void _logout() {
    Navigator.pushReplacementNamed(context, '/login');
  }

  @override
  Widget build(BuildContext context) {
    final currentService = _services[_selectedIndex];
    return Scaffold(
      appBar: AppBar(
        title: Text(currentService['title']!),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.red),
            tooltip: "Logout",
            onPressed: _logout,
          )
        ],
      ),
      body: ApiTestPage(
        title: currentService['title']!,
        url: currentService['url']!,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.indigo,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.waving_hand), label: "Hello"),
          BottomNavigationBarItem(icon: Icon(Icons.lock), label: "Auth"),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: "User"),
          BottomNavigationBarItem(icon: Icon(Icons.work), label: "Jobs"),
          BottomNavigationBarItem(icon: Icon(Icons.description), label: "CV"),
          BottomNavigationBarItem(icon: Icon(Icons.search), label: "Match"),
          BottomNavigationBarItem(icon: Icon(Icons.notifications), label: "Notify"),
        ],
      ),
    );
  }
}

class ApiTestPage extends StatefulWidget {
  final String title;
  final String url;
  const ApiTestPage({super.key, required this.title, required this.url});

  @override
  State<ApiTestPage> createState() => _ApiTestPageState();
}

class _ApiTestPageState extends State<ApiTestPage> {
  String _response = "Press the button to test this service.";

  Future<void> _callApi() async {
    try {
      final res = await http.get(Uri.parse(widget.url));
      setState(() => _response = res.statusCode == 200
          ? res.body
          : "Error: ${res.statusCode}\n${res.body}");
    } catch (e) {
      setState(() => _response = "Failed to connect: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_response, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _callApi,
              icon: const Icon(Icons.api),
              label: Text("Test ${widget.title}"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.indigo,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 25, vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
