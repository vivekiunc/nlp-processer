import 'package:flutter/material.dart';

import '../api_service.dart';
import '../models.dart';
import '../widgets/answer_card.dart';
import '../widgets/sources_list.dart';

class TextQueryScreen extends StatefulWidget {
  const TextQueryScreen({super.key});

  @override
  State<TextQueryScreen> createState() => _TextQueryScreenState();
}

class _TextQueryScreenState extends State<TextQueryScreen> {
  final _controller = TextEditingController();
  int _topK = 3;
  bool _loading = false;
  String? _error;
  String? _answer;
  List<RetrievedChunk> _sources = [];

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final question = _controller.text.trim();
    if (question.isEmpty) return;

    setState(() {
      _loading = true;
      _error = null;
      _answer = null;
      _sources = [];
    });

    try {
      final results = await Future.wait([
        ApiService.instance.query(question, topK: _topK),
        ApiService.instance.retrieve(question, topK: _topK),
      ]);
      final queryResult = results[0] as QueryResult;
      final sources = results[1] as List<RetrievedChunk>;
      setState(() {
        _answer = queryResult.answer;
        _sources = sources;
      });
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _controller,
            minLines: 2,
            maxLines: 5,
            decoration: const InputDecoration(
              labelText: 'Ask about crops, irrigation, pests, seeds...',
              border: OutlineInputBorder(),
            ),
            onSubmitted: (_) => _submit(),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              const Text('Top K:'),
              const SizedBox(width: 8),
              DropdownButton<int>(
                value: _topK,
                items: const [1, 2, 3, 4, 5, 10]
                    .map((k) => DropdownMenuItem(value: k, child: Text('$k')))
                    .toList(),
                onChanged: (v) => setState(() => _topK = v ?? 3),
              ),
              const Spacer(),
              FilledButton.icon(
                onPressed: _loading ? null : _submit,
                icon: _loading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.send),
                label: const Text('Ask'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (_error != null)
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.errorContainer,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _error!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.onErrorContainer,
                        ),
                      ),
                    ),
                  if (_answer != null) ...[
                    AnswerCard(answer: _answer!),
                    const SizedBox(height: 16),
                    SourcesList(sources: _sources),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
