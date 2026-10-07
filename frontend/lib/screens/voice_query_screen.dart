import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:record/record.dart';

import '../api_service.dart';
import '../widgets/answer_card.dart';

class VoiceQueryScreen extends StatefulWidget {
  const VoiceQueryScreen({super.key});

  @override
  State<VoiceQueryScreen> createState() => _VoiceQueryScreenState();
}

const _kSupportedLanguages = {'te': 'Telugu', 'mr': 'Marathi'};

class _VoiceQueryScreenState extends State<VoiceQueryScreen> {
  final _recorder = AudioRecorder();
  bool _recording = false;
  bool _loading = false;
  String? _error;
  String? _transcription;
  String? _answer;
  String? _pickedFileName;
  String _language = 'te';

  @override
  void dispose() {
    _recorder.dispose();
    super.dispose();
  }

  Future<void> _toggleRecording() async {
    if (_recording) {
      final path = await _recorder.stop();
      setState(() => _recording = false);
      if (path != null) {
        await _sendRecording(path);
      }
      return;
    }

    final hasPermission = await _recorder.hasPermission();
    if (!hasPermission) {
      setState(() => _error = 'Microphone permission was denied.');
      return;
    }

    setState(() {
      _error = null;
      _answer = null;
      _transcription = null;
    });

    await _recorder.start(
      const RecordConfig(encoder: AudioEncoder.wav),
      path: 'telugu_query.wav',
    );
    setState(() => _recording = true);
  }

  Future<void> _sendRecording(String pathOrBlobUrl) async {
    setState(() => _loading = true);
    try {
      final res = await http.get(Uri.parse(pathOrBlobUrl));
      await _sendAudio(res.bodyBytes, 'recording.wav');
    } catch (e) {
      setState(() => _error = 'Could not read recording: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['wav', 'mp3', 'm4a', 'flac', 'ogg'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;

    final file = result.files.first;
    final bytes = file.bytes;
    if (bytes == null) {
      setState(() => _error = 'Could not read the selected file.');
      return;
    }

    setState(() {
      _pickedFileName = file.name;
      _error = null;
      _answer = null;
      _transcription = null;
    });
    await _sendAudio(bytes, file.name);
  }

  Future<void> _sendAudio(Uint8List bytes, String filename) async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await ApiService.instance.audioQuery(
        bytes,
        filename,
        language: _language,
      );
      setState(() {
        _transcription = result.transcription;
        _answer = result.answer;
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
          Center(
            child: Column(
              children: [
                SegmentedButton<String>(
                  segments: [
                    for (final entry in _kSupportedLanguages.entries)
                      ButtonSegment(value: entry.key, label: Text(entry.value)),
                  ],
                  selected: {_language},
                  onSelectionChanged: _loading
                      ? null
                      : (selection) => setState(() => _language = selection.first),
                ),
                const SizedBox(height: 16),
                GestureDetector(
                  onTap: _loading ? null : _toggleRecording,
                  child: CircleAvatar(
                    radius: 48,
                    backgroundColor: _recording
                        ? Colors.redAccent
                        : Theme.of(context).colorScheme.primary,
                    child: Icon(
                      _recording ? Icons.stop : Icons.mic,
                      size: 40,
                      color: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Text(_recording ? 'Recording... tap to stop' : 'Tap to record'),
                const SizedBox(height: 16),
                TextButton.icon(
                  onPressed: _loading ? null : _pickFile,
                  icon: const Icon(Icons.upload_file),
                  label: Text(_pickedFileName ?? 'Or upload an audio file'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          if (_loading) const Center(child: CircularProgressIndicator()),
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
                  if (_transcription != null) ...[
                    Text(
                      'Transcription',
                      style: Theme.of(context).textTheme.labelLarge,
                    ),
                    const SizedBox(height: 4),
                    Text(_transcription!, style: Theme.of(context).textTheme.bodyMedium),
                    const SizedBox(height: 16),
                  ],
                  if (_answer != null) AnswerCard(answer: _answer!),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
