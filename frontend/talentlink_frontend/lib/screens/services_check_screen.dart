import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
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
  int _selectedIndex = 0;

  final List<Widget> _pages = const [
    ApiTestPage(title: "Hello Service", url: "/api/hello"),
    ApiTestPage(title: "Auth Service", url: "/api/auth/health"),
    ApiTestPage(title: "User Service", url: "/api/users/health"),
    ApiTestPage(title: "Job Service", url: "/api/jobs/health"),
    ApiTestPage(title: "CV Service", url: "/api/cv/health"),
    ApiTestPage(title: "Matching Service", url: "/api/matching/health"),
    ApiTestPage(title: "Notification Service", url: "/api/notifications/health"),
  ];

  void _onItemTapped(int index) {
    setState(() => _selectedIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        type: BottomNavigationBarType.fixed,
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

/// A reusable widget to call any service endpoint
class ApiTestPage extends StatefulWidget {
  final String title;
  final String url;

  const ApiTestPage({super.key, required this.title, required this.url});

  @override
  State<ApiTestPage> createState() => _ApiTestPageState();
}

class _ApiTestPageState extends State<ApiTestPage> {
  String _response = "No response yet";

  Future<void> _callApi() async {
    try {
      final res = await http.get(Uri.parse(widget.url));
      if (res.statusCode == 200) {
        setState(() => _response = res.body);
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
      appBar: AppBar(title: Text(widget.title)),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_response, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _callApi,
              child: Text("Call ${widget.title}"),
            ),
          ],
        ),
      ),
    );
  }
}
