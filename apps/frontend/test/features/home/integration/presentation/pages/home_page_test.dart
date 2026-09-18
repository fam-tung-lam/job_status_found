import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/health/health.dart';
import 'package:job_status_found/features/health/infrastructure/adapters/api_health_repository.dart';
import 'package:job_status_found/features/health/infrastructure/clients/health_api_client.dart';
import 'package:job_status_found/features/home/home.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../helpers/pump_app.dart';
import '../../../../../test_doubles/mock_job_status_found_http_client.dart';

void main() {
  group('HomePage', () {
    late MockJobStatusFoundHttpClient httpClient;
    late HomePage page;

    setUp(() {
      httpClient = MockJobStatusFoundHttpClient();
      page = HomePage(
        checkHealthUseCase: CheckHealthUseCase(
          ApiHealthRepository(HealthApiClient(httpClient)),
        ),
      );
    });

    testWidgets('shows its title and the backend health', (tester) async {
      // Given: a backend that reports that it is alive.
      when(() => httpClient.get('/health'))
          .thenAnswer((_) async => {'status': 'ok'});

      // When: the home page opens.
      await tester.pumpApp(page);
      await tester.pump();

      // Then: the page shows its title and says the backend is healthy.
      expect(find.text('Home'), findsOneWidget);
      expect(find.text('The backend is healthy.'), findsOneWidget);
    });
  });
}
