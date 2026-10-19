import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:app_links/app_links.dart';
import 'package:receive_sharing_intent/receive_sharing_intent.dart';
import 'providers/scan_provider.dart';
import 'screens/home_screen.dart';
import 'screens/result_screen.dart';

void main() {
  runApp(
    const ProviderScope(
      child: WebsiteSafetyCheckerApp(),
    ),
  );
}

class WebsiteSafetyCheckerApp extends ConsumerStatefulWidget {
  const WebsiteSafetyCheckerApp({super.key});

  @override
  ConsumerState<WebsiteSafetyCheckerApp> createState() =>
      _WebsiteSafetyCheckerAppState();
}

class _WebsiteSafetyCheckerAppState
    extends ConsumerState<WebsiteSafetyCheckerApp> {
  late final AppLinks _appLinks;
  StreamSubscription<Uri>? _appLinksSubscription;
  StreamSubscription<String>? _intentDataStreamSubscription;
  final GlobalKey<NavigatorState> _navigatorKey = GlobalKey<NavigatorState>();

  String? _lastProcessedUrl;
  DateTime? _lastProcessedTime;

  @override
  void initState() {
    super.initState();
    _initInterceptors();
  }

  void _initInterceptors() async {
    // 1. AppLinks for VIEW intents (clicking links in WhatsApp, SMS, browser)
    _appLinks = AppLinks();

    // Cold-start link handling
    try {
      final initialUri = await _appLinks.getInitialLink();
      if (initialUri != null) {
        _handleIncomingUrl(initialUri.toString());
      }
    } catch (e) {
      debugPrint("AppLinks getInitialLink error: $e");
    }

    // Stream for link clicks while app is in background or memory
    _appLinksSubscription = _appLinks.uriLinkStream.listen(
      (Uri uri) {
        _handleIncomingUrl(uri.toString());
      },
      onError: (err) {
        debugPrint("AppLinks uriLinkStream error: $err");
      },
    );

    // 2. ReceiveSharingIntent for OS Share Sheet (sharing text from apps)
    _intentDataStreamSubscription =
        ReceiveSharingIntent.instance.getTextStream().listen((String text) {
      if (text.isNotEmpty) {
        _handleIncomingUrl(text);
      }
    }, onError: (err) {
      debugPrint("ReceiveSharingIntent error: $err");
    });

    ReceiveSharingIntent.instance.getInitialText().then((String? text) {
      if (text != null && text.isNotEmpty) {
        _handleIncomingUrl(text);
      }
    });
  }

  void _handleIncomingUrl(String rawText) async {
    // Extract URL pattern from rawText if needed
    final RegExp urlRegExp = RegExp(
      r'((https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}([\/\w\.-]*)*\/?(\?[^\s]*)?)',
      caseSensitive: false,
    );
    final match = urlRegExp.firstMatch(rawText);
    final targetUrl = match != null ? match.group(0)! : rawText.trim();
    if (targetUrl.isEmpty) return;

    // Deduplicate duplicate triggers within 2.5 seconds
    final now = DateTime.now();
    if (_lastProcessedUrl == targetUrl &&
        _lastProcessedTime != null &&
        now.difference(_lastProcessedTime!).inMilliseconds < 2500) {
      return;
    }
    _lastProcessedUrl = targetUrl;
    _lastProcessedTime = now;

    // Give time for UI mount if cold start
    await Future.delayed(const Duration(milliseconds: 150));

    final messenger = ScaffoldMessenger.maybeOf(_navigatorKey.currentContext ?? context);
    messenger?.showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFFD366E)),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'Intercepted & scanning: $targetUrl',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white, fontSize: 13),
              ),
            ),
          ],
        ),
        duration: const Duration(seconds: 2),
        backgroundColor: const Color(0xFF19191D),
      ),
    );

    final result = await ref.read(scanProvider.notifier).scan(targetUrl);
    if (result != null && _navigatorKey.currentState != null) {
      _navigatorKey.currentState!.push(
        MaterialPageRoute(builder: (_) => ResultScreen(scan: result)),
      );
    }
  }

  @override
  void dispose() {
    _appLinksSubscription?.cancel();
    _intentDataStreamSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: _navigatorKey,
      title: 'Website Safety Checker',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.system,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        colorSchemeSeed: Colors.blueAccent,
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        cardColor: Colors.white,
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFFF8FAFC),
          elevation: 0,
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorSchemeSeed: const Color(0xFFFD366E),
        scaffoldBackgroundColor: const Color(0xFF141416),
        cardColor: const Color(0xFF19191D),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
