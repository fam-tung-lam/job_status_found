/// Text shown on the backend health page.
sealed class const HealthStrings() {
  /// Creates the strings.
  this;

  /// Title of the health page.
  String get pageTitle;

  /// Shown while the app waits for the backend to answer.
  String get checkInProgress;

  /// Shown when the backend reports that it can serve requests.
  String get statusHealthy;

  /// Shown when the backend did not answer.
  String get statusUnreachable;

  /// Shown when the backend answered with something the app does not
  /// understand.
  String get statusUnexpectedResponse;

  /// Label of the button that repeats the health check.
  String get checkAgainAction;
}

/// English [HealthStrings].
final class const EnHealthStrings() extends HealthStrings {
  /// Creates the English strings.
  this;

  @override
  String get pageTitle => 'Backend status';

  @override
  String get checkInProgress => 'Checking the backend…';

  @override
  String get statusHealthy => 'The backend is healthy.';

  @override
  String get statusUnreachable =>
      'Cannot reach the backend. Make sure it is running.';

  @override
  String get statusUnexpectedResponse =>
      'The backend sent a response this app does not understand.';

  @override
  String get checkAgainAction => 'Check again';
}
