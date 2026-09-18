/// Text shown on the home page.
sealed class const HomeStrings() {
  /// Creates the strings.
  this;

  /// Title of the home page.
  String get pageTitle;
}

/// English [HomeStrings].
final class const EnHomeStrings() extends HomeStrings {
  /// Creates the English strings.
  this;

  @override
  String get pageTitle => 'Home';
}
