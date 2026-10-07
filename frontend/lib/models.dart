class RetrievedChunk {
  final String text;
  final String? crop;
  final String? region;
  final String? language;
  final String? source;
  final String? topic;

  RetrievedChunk({
    required this.text,
    this.crop,
    this.region,
    this.language,
    this.source,
    this.topic,
  });

  factory RetrievedChunk.fromJson(Map<String, dynamic> json) {
    return RetrievedChunk(
      text: json['text'] as String,
      crop: json['crop'] as String?,
      region: json['region'] as String?,
      language: json['language'] as String?,
      source: json['source'] as String?,
      topic: json['topic'] as String?,
    );
  }
}

class QueryResult {
  final String answer;
  final List<RetrievedChunk> sources;

  QueryResult({required this.answer, this.sources = const []});
}

class AudioQueryResult {
  final String transcription;
  final String answer;

  AudioQueryResult({required this.transcription, required this.answer});

  factory AudioQueryResult.fromJson(Map<String, dynamic> json) {
    return AudioQueryResult(
      transcription: json['transcription'] as String,
      answer: json['answer'] as String,
    );
  }
}
