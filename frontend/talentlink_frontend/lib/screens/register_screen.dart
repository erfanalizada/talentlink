import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  String _selectedRole = 'employee';
  bool _loading = false;
  final AuthService _auth = AuthService();

  Future<void> _register() async {
    setState(() => _loading = true);
    final success = await _auth.register(
      _usernameController.text,
      _emailController.text,
      _passwordController.text,
      _selectedRole,
    );
    setState(() => _loading = false);

    if (success && mounted) {
      Navigator.pushReplacementNamed(context, '/login');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Registration failed')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Register')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(controller: _usernameController, decoration: const InputDecoration(labelText: 'Username')),
            TextField(controller: _emailController, decoration: const InputDecoration(labelText: 'Email')),
            TextField(controller: _passwordController, decoration: const InputDecoration(labelText: 'Password'), obscureText: true),
            const SizedBox(height: 20),
            DropdownButtonFormField<String>(
              value: _selectedRole,
              items: const [
                DropdownMenuItem(value: 'employee', child: Text('Employee')),
                DropdownMenuItem(value: 'employer', child: Text('Employer')),
              ],
              onChanged: (val) => setState(() => _selectedRole = val!),
              decoration: const InputDecoration(labelText: 'Role'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loading ? null : _register,
              child: _loading
                  ? const CircularProgressIndicator()
                  : const Text('Register'),
            ),
          ],
        ),
      ),
    );
  }
}
