import 'package:flutter/material.dart';

import '../models.dart';

class SourcesList extends StatelessWidget {
  final List<RetrievedChunk> sources;

  const SourcesList({super.key, required this.sources});

  @override
  Widget build(BuildContext context) {
    if (sources.isEmpty) return const SizedBox.shrink();

    return ExpansionTile(
      tilePadding: EdgeInsets.zero,
      title: Text(
        'Retrieved sources (${sources.length})',
        style: Theme.of(context).textTheme.labelLarge,
      ),
      children: sources.map((c) => _SourceTile(chunk: c)).toList(),
    );
  }
}

class _SourceTile extends StatelessWidget {
  final RetrievedChunk chunk;

  const _SourceTile({required this.chunk});

  @override
  Widget build(BuildContext context) {
    final tags = <String>[
      if (chunk.crop != null) chunk.crop!,
      if (chunk.region != null) chunk.region!,
      if (chunk.topic != null) chunk.topic!,
      if (chunk.language != null) chunk.language!.toUpperCase(),
    ];

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (chunk.source != null)
              Text(
                chunk.source!,
                style: Theme.of(context)
                    .textTheme
                    .labelMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
            if (tags.isNotEmpty) ...[
              const SizedBox(height: 6),
              Wrap(
                spacing: 6,
                runSpacing: 4,
                children: tags
                    .map((t) => Chip(
                          label: Text(t, style: const TextStyle(fontSize: 11)),
                          visualDensity: VisualDensity.compact,
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ))
                    .toList(),
              ),
            ],
            const SizedBox(height: 8),
            Text(
              chunk.text,
              maxLines: 6,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
