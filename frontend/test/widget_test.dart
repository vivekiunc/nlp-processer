import 'package:flutter_test/flutter_test.dart';

import 'package:agri_rag_app/main.dart';

void main() {
  testWidgets('Home screen shows Ask and Voice tabs', (WidgetTester tester) async {
    await tester.pumpWidget(const AgriRagApp());

    expect(find.text('Agri RAG Assistant'), findsOneWidget);
    expect(find.text('Ask'), findsWidgets);
    expect(find.text('Voice'), findsOneWidget);
  });
}
