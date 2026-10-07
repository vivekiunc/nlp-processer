import 'package:flutter/material.dart';

import 'screens/text_query_screen.dart';
import 'screens/voice_query_screen.dart';
import 'widgets/settings_dialog.dart';

void main() {
  runApp(const AgriRagApp());
}

class AgriRagApp extends StatelessWidget {
  const AgriRagApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Agri RAG Assistant',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Agri RAG Assistant'),
          bottom: const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.chat_bubble_outline), text: 'Ask'),
              Tab(icon: Icon(Icons.mic_none), text: 'Voice'),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.settings_outlined),
              tooltip: 'Backend settings',
              onPressed: () => showSettingsDialog(context),
            ),
          ],
        ),
        body: const TabBarView(
          children: [
            TextQueryScreen(),
            VoiceQueryScreen(),
          ],
        ),
      ),
    );
  }
}
