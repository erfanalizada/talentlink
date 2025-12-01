import 'package:flutter/material.dart';
import 'services/auth_service.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/employee/employee_dashboard.dart';
import 'screens/employer/employer_dashboard.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AuthService.loadToken();
  runApp(const TalentLinkApp());
}

class TalentLinkApp extends StatelessWidget {
  const TalentLinkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TalentLink',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.indigo,
        scaffoldBackgroundColor: Colors.grey[50],
      ),
      initialRoute: _getInitialRoute(),
      routes: {
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/employee-dashboard': (context) => const EmployeeDashboard(),
        '/employer-dashboard': (context) => const EmployerDashboard(),
      },
    );
  }

  String _getInitialRoute() {
    if (AuthService.isLoggedIn) {
      if (AuthService.isEmployee) {
        return '/employee-dashboard';
      } else if (AuthService.isEmployer) {
        return '/employer-dashboard';
      }
    }
    return '/login';
  }
}
