import 'package:flutter/material.dart';

class AnswerCard extends StatelessWidget {
  final String answer;

  const AnswerCard({super.key, required this.answer});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: scheme.primaryContainer.withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: scheme.primary.withValues(alpha: 0.3)),
      ),
      child: SelectableText(
        answer,
        style: Theme.of(context).textTheme.bodyLarge,
      ),
    );
  }
}
