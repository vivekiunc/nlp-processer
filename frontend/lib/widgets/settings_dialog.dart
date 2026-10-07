import 'package:flutter/material.dart';

import '../api_service.dart';

Future<void> showSettingsDialog(BuildContext context) async {
  final controller = TextEditingController(text: ApiService.instance.baseUrl);
  await showDialog<void>(
    context: context,
    builder: (context) {
      return AlertDialog(
        title: const Text('Backend URL'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: 'http://127.0.0.1:8000',
            border: OutlineInputBorder(),
          ),
          keyboardType: TextInputType.url,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () {
              final value = controller.text.trim();
              if (value.isNotEmpty) {
                ApiService.instance.baseUrl =
                    value.endsWith('/') ? value.substring(0, value.length - 1) : value;
              }
              Navigator.of(context).pop();
            },
            child: const Text('Save'),
          ),
        ],
      );
    },
  );
}
