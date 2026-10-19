import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/scan_models.dart';
import '../services/api_service.dart';

class ScanState {
  final bool isLoading;
  final ScanResponse? currentScan;
  final String? errorMessage;
  final List<ScanResponse> recentScans;

  ScanState({
    this.isLoading = false,
    this.currentScan,
    this.errorMessage,
    this.recentScans = const [],
  });

  ScanState copyWith({
    bool? isLoading,
    ScanResponse? currentScan,
    String? errorMessage,
    List<ScanResponse>? recentScans,
    bool clearCurrentScan = false,
    bool clearError = false,
  }) {
    return ScanState(
      isLoading: isLoading ?? this.isLoading,
      currentScan: clearCurrentScan ? null : (currentScan ?? this.currentScan),
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      recentScans: recentScans ?? this.recentScans,
    );
  }
}

class ScanNotifier extends StateNotifier<ScanState> {
  final ApiService _apiService;

  ScanNotifier(this._apiService) : super(ScanState());

  Future<ScanResponse?> scan(String url, {String siteType = 'general'}) async {
    final trimmed = url.trim();
    if (trimmed.isEmpty) {
      state = state.copyWith(errorMessage: 'Please enter a valid URL');
      return null;
    }

    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final result = await _apiService.scanUrl(trimmed, siteType: siteType);
      final updatedHistory = [result, ...state.recentScans.where((s) => s.url != result.url)].take(10).toList();
      state = state.copyWith(
        isLoading: false,
        currentScan: result,
        recentScans: updatedHistory,
      );
      return result;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString().replaceFirst('Exception: ', ''),
      );
      return null;
    }
  }

  String get currentBaseUrl => _apiService.baseUrl;

  Future<void> updateBaseUrl(String newUrl) async {
    await _apiService.setBaseUrl(newUrl);
  }

  Future<bool> testConnection([String? testUrl]) async {
    return await _apiService.checkHealth(testUrl);
  }

  void setCurrentScan(ScanResponse scan) {
    state = state.copyWith(currentScan: scan, clearError: true);
  }

  void clearError() {
    state = state.copyWith(clearError: true);
  }
}

final apiServiceProvider = Provider<ApiService>((ref) => ApiService());

final scanProvider = StateNotifierProvider<ScanNotifier, ScanState>((ref) {
  final api = ref.watch(apiServiceProvider);
  return ScanNotifier(api);
});
