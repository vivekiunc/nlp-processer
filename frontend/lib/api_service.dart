import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import 'models.dart';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}

/// Thin client for the Agri RAG FastAPI backend (see app/main.py).
class ApiService {
  ApiService._();
  static final ApiService instance = ApiService._();

  /// Overridable at runtime via the settings dialog so the app can point at
  /// a device, emulator, or deployed backend without a rebuild.
  String baseUrl = 'http://127.0.0.1:8000';

  Future<bool> checkHealth() async {
    try {
      final res = await http
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<QueryResult> query(String question, {int topK = 3}) async {
    final res = await http.post(
      Uri.parse('$baseUrl/query'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'query': question, 'top_k': topK}),
    );
    if (res.statusCode != 200) {
      throw ApiException(_extractError(res));
    }
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    return QueryResult(answer: body['answer'] as String);
  }

  Future<List<RetrievedChunk>> retrieve(String question, {int topK = 3}) async {
    final res = await http.post(
      Uri.parse('$baseUrl/retrieve'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'query': question, 'top_k': topK}),
    );
    if (res.statusCode != 200) {
      throw ApiException(_extractError(res));
    }
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    final chunks = (body['chunks'] as List)
        .map((c) => RetrievedChunk.fromJson(c as Map<String, dynamic>))
        .toList();
    return chunks;
  }

  Future<AudioQueryResult> audioQuery(
    Uint8List audioBytes,
    String filename, {
    int topK = 3,
    String language = 'te',
  }) async {
    final uri = Uri.parse('$baseUrl/audio-query?top_k=$topK&language=$language');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(
        http.MultipartFile.fromBytes('file', audioBytes, filename: filename),
      );
    final streamed = await request.send();
    final res = await http.Response.fromStream(streamed);
    if (res.statusCode != 200) {
      throw ApiException(_extractError(res));
    }
    return AudioQueryResult.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  String _extractError(http.Response res) {
    try {
      final body = jsonDecode(res.body);
      final detail = body['detail'];
      if (detail is String) return detail;
      if (detail is List && detail.isNotEmpty) {
        final first = detail.first;
        if (first is Map && first['msg'] != null) return first['msg'].toString();
      }
      return 'Request failed (${res.statusCode})';
    } catch (_) {
      return 'Request failed (${res.statusCode})';
    }
  }
}
