import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

/// Mocktail double for the backend [JobStatusFoundHttpClient], the lowest
/// layer the health feature reaches before the network.
class MockJobStatusFoundHttpClient()
    extends Mock
    implements JobStatusFoundHttpClient;
