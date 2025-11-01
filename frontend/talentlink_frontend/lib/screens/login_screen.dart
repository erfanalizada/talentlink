import 'package:flutter/material.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import '../services/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _loading = false;
  final AuthService _auth = AuthService();

Future<void> _login() async {
  setState(() => _loading = true);
  final tokenData = await _auth.login(
    _usernameController.text,
    _passwordController.text,
  );
  setState(() => _loading = false);

  if (tokenData != null && mounted) {
    final token = tokenData['access_token'];
    final decoded = JwtDecoder.decode(token);

    // Extract roles from token (usually stored in realm_access)
    final roles = decoded['realm_access']?['roles'] ?? [];
    print("✅ Logged in! Roles: $roles");

    // Optionally, redirect based on role
    if (roles.contains('employer')) {
      Navigator.pushReplacementNamed(context, '/employerDashboard');
    } else if (roles.contains('employee')) {
      Navigator.pushReplacementNamed(context, '/employeeDashboard');
    } else {
      Navigator.pushReplacementNamed(context, '/services');
    }
  } else {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Login failed')),
    );
  }
}


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Login')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(controller: _usernameController, decoration: const InputDecoration(labelText: 'Username')),
            TextField(controller: _passwordController, decoration: const InputDecoration(labelText: 'Password'), obscureText: true),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loading ? null : _login,
              child: _loading ? const CircularProgressIndicator() : const Text('Login'),
            ),
            TextButton(
              onPressed: () => Navigator.pushNamed(context, '/register'),
              child: const Text('Create account'),
            ),
          ],
        ),
      ),
    );
  }
}
