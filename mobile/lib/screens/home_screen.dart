import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/scan_provider.dart';
import '../widgets/glass_container.dart';
import 'result_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final TextEditingController _urlController = TextEditingController();

  static const Color accentPink = Color(0xFFFF4D80);
  static const Color primaryPink = Color(0xFFFD366E);

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  void _triggerScan([String? prefilledUrl]) async {
    final targetUrl = prefilledUrl ?? _urlController.text;
    if (prefilledUrl != null) {
      _urlController.text = prefilledUrl;
    }

    final result = await ref.read(scanProvider.notifier).scan(targetUrl);
    if (!mounted) return;

    if (result != null) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => ResultScreen(scan: result)),
      );
    } else {
      final err = ref.read(scanProvider).errorMessage;
      if (err != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(err),
            backgroundColor: Colors.redAccent.shade700,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        );
      }
    }
  }

  void _pasteFromClipboard() async {
    final data = await Clipboard.getData('text/plain');
    if (data?.text != null && data!.text!.isNotEmpty) {
      setState(() {
        _urlController.text = data.text!;
      });
      _triggerScan(data.text!);
    }
  }

  void _showServerSettingsDialog() {
    final currentUrl = ref.read(scanProvider.notifier).currentBaseUrl;
    final serverController = TextEditingController(text: currentUrl);
    bool isTesting = false;
    String? testResult;
    bool? testSuccess;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) => Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
          ),
          child: GlassContainer(
            opacity: 0.16,
            blur: 24,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.settings_outlined, color: accentPink),
                        SizedBox(width: 10),
                        Text(
                          'Backend Server Settings',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                      ],
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.grey),
                      onPressed: () => Navigator.pop(ctx),
                    ),
                  ],
                ),
                const Divider(color: Colors.white12),
                const SizedBox(height: 12),
                const Text(
                  'API Base URL (FastAPI Host & Port):',
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white70),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: serverController,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    prefixIcon: const Icon(Icons.dns_outlined, color: primaryPink, size: 20),
                    hintText: 'http://10.148.3.32:8000',
                    hintStyle: const TextStyle(color: Colors.white38),
                    filled: true,
                    fillColor: Colors.white.withOpacity(0.05),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: const BorderSide(color: Colors.white12),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: const BorderSide(color: primaryPink),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Quick Presets:',
                  style: TextStyle(fontSize: 12, color: Colors.white54, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 6),
                Wrap(
                  spacing: 8,
                  runSpacing: 6,
                  children: [
                    ActionChip(
                      backgroundColor: Colors.white.withOpacity(0.06),
                      label: const Text('Wi-Fi (10.148.3.32:8000)', style: TextStyle(color: Colors.white70, fontSize: 11)),
                      onPressed: () {
                        setModalState(() {
                          serverController.text = 'http://10.148.3.32:8000';
                          testResult = null;
                        });
                      },
                    ),
                    ActionChip(
                      backgroundColor: Colors.white.withOpacity(0.06),
                      label: const Text('Emulator (10.0.2.2:8000)', style: TextStyle(color: Colors.white70, fontSize: 11)),
                      onPressed: () {
                        setModalState(() {
                          serverController.text = 'http://10.0.2.2:8000';
                          testResult = null;
                        });
                      },
                    ),
                    ActionChip(
                      backgroundColor: Colors.white.withOpacity(0.06),
                      label: const Text('Localhost (127.0.0.1:8000)', style: TextStyle(color: Colors.white70, fontSize: 11)),
                      onPressed: () {
                        setModalState(() {
                          serverController.text = 'http://127.0.0.1:8000';
                          testResult = null;
                        });
                      },
                    ),
                  ],
                ),
                if (testResult != null) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: (testSuccess == true ? const Color(0xFF10B981) : Colors.redAccent).withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: (testSuccess == true ? const Color(0xFF10B981) : Colors.redAccent).withOpacity(0.3),
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          testSuccess == true ? Icons.check_circle_outline : Icons.error_outline,
                          color: testSuccess == true ? const Color(0xFF34D399) : Colors.redAccent,
                          size: 18,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            testResult!,
                            style: TextStyle(
                              color: testSuccess == true ? const Color(0xFF34D399) : Colors.redAccent,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 18),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          side: const BorderSide(color: Colors.white24),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                        onPressed: isTesting
                            ? null
                            : () async {
                                setModalState(() {
                                  isTesting = true;
                                  testResult = null;
                                });
                                final ok = await ref.read(scanProvider.notifier).testConnection(serverController.text);
                                setModalState(() {
                                  isTesting = false;
                                  testSuccess = ok;
                                  testResult = ok ? 'Connection verified! (200 OK)' : 'Failed to reach server. Check Wi-Fi & port 8000';
                                });
                              },
                        icon: isTesting
                            ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white70))
                            : const Icon(Icons.wifi_tethering, size: 18, color: Colors.white70),
                        label: Text(isTesting ? 'Testing...' : 'Test Ping', style: const TextStyle(color: Colors.white70)),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: primaryPink,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                        onPressed: () async {
                          final newUrl = serverController.text.trim();
                          if (newUrl.isNotEmpty) {
                            await ref.read(scanProvider.notifier).updateBaseUrl(newUrl);
                            setState(() {});
                            if (ctx.mounted) Navigator.pop(ctx);
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Server URL updated to: $newUrl'),
                                  backgroundColor: const Color(0xFF19191D),
                                  behavior: SnackBarBehavior.floating,
                                ),
                              );
                            }
                          }
                        },
                        icon: const Icon(Icons.save_outlined, size: 18),
                        label: const Text('Save & Apply', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showGlassMenu() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (ctx) => GlassContainer(
        opacity: 0.16,
        blur: 24,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Row(
                  children: [
                    Icon(Icons.widgets_outlined, color: accentPink),
                    SizedBox(width: 10),
                    Text(
                      'Application Options',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.grey),
                  onPressed: () => Navigator.pop(ctx),
                ),
              ],
            ),
            const Divider(color: Colors.white12),
            const SizedBox(height: 8),
            ListTile(
              leading: const Icon(Icons.dns_outlined, color: accentPink),
              title: const Text('Server Configuration', style: TextStyle(color: Colors.white)),
              subtitle: Text(
                ref.read(scanProvider.notifier).currentBaseUrl,
                style: const TextStyle(color: Colors.white54, fontSize: 12),
              ),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              onTap: () {
                Navigator.pop(ctx);
                _showServerSettingsDialog();
              },
            ),
            ListTile(
              leading: const Icon(Icons.history_rounded, color: Colors.white70),
              title: const Text('Recent Scan History', style: TextStyle(color: Colors.white)),
              subtitle: Text(
                '${ref.read(scanProvider).recentScans.length} scans saved in memory',
                style: const TextStyle(color: Colors.white54, fontSize: 12),
              ),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              onTap: () {
                Navigator.pop(ctx);
              },
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final scanState = ref.watch(scanProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF141416),
      body: Stack(
        children: [
          // Background ambient light orbs in warm pink
          Positioned(
            top: -60,
            left: -60,
            child: Container(
              width: 260,
              height: 260,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: primaryPink.withOpacity(0.12),
              ),
            ),
          ),
          Positioned(
            bottom: 100,
            right: -60,
            child: Container(
              width: 280,
              height: 280,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: primaryPink.withOpacity(0.08),
              ),
            ),
          ),

          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Glass Top Bar
                  GlassContainer(
                    opacity: 0.08,
                    borderRadius: BorderRadius.circular(20),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.shield_outlined, color: accentPink, size: 24),
                            SizedBox(width: 10),
                            Text(
                              'Safety Shield',
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17, color: Colors.white),
                            ),
                          ],
                        ),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFF10B981).withOpacity(0.15),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: const Color(0xFF10B981).withOpacity(0.3)),
                              ),
                              child: const Text(
                                ':8000 LIVE',
                                style: TextStyle(color: Color(0xFF34D399), fontSize: 10, fontWeight: FontWeight.bold),
                              ),
                            ),
                            const SizedBox(width: 4),
                            IconButton(
                              icon: const Icon(Icons.settings_outlined, color: Colors.white70),
                              tooltip: 'Server Settings',
                              onPressed: _showServerSettingsDialog,
                            ),
                            IconButton(
                              icon: const Icon(Icons.menu_rounded, color: Colors.white70),
                              onPressed: _showGlassMenu,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Hero Glass Banner
                  GlassContainer(
                    opacity: 0.06,
                    borderRadius: BorderRadius.circular(24),
                    padding: const EdgeInsets.all(22),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: primaryPink.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Icon(Icons.bolt_rounded, color: accentPink, size: 20),
                            ),
                            const SizedBox(width: 10),
                            const Text(
                              'Multi-Category Analysis',
                              style: TextStyle(color: accentPink, fontSize: 12, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Inspect Any Website',
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Parallel security analysis across Phishing, Malware, E-Commerce, Scam, TLS, and Trackers.',
                          style: TextStyle(fontSize: 13, color: Colors.white70),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Glass URL Input Bar
                  GlassContainer(
                    opacity: 0.08,
                    borderRadius: BorderRadius.circular(20),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    child: Row(
                      children: [
                        const Icon(Icons.link_rounded, color: accentPink),
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextField(
                            controller: _urlController,
                            style: const TextStyle(color: Colors.white),
                            decoration: const InputDecoration(
                              hintText: 'Paste or type URL...',
                              hintStyle: TextStyle(color: Colors.white38),
                              border: InputBorder.none,
                            ),
                            keyboardType: TextInputType.url,
                            onSubmitted: (_) => _triggerScan(),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.content_paste_rounded, color: Colors.white70),
                          tooltip: 'Paste from clipboard',
                          onPressed: _pasteFromClipboard,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Primary Scan Button
                  ElevatedButton(
                    onPressed: scanState.isLoading ? null : () => _triggerScan(),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: primaryPink,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      elevation: 4,
                      shadowColor: primaryPink.withOpacity(0.5),
                    ),
                    child: scanState.isLoading
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              color: Colors.white,
                            ),
                          )
                        : const Text(
                            'Scan Website Safety',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                  ),
                  const SizedBox(height: 36),

                  // Recent Scans Section
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Recent Scans',
                        style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      if (scanState.recentScans.isNotEmpty)
                        Text(
                          '${scanState.recentScans.length} cached',
                          style: const TextStyle(color: Colors.white38, fontSize: 12),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  if (scanState.recentScans.isEmpty)
                    GlassContainer(
                      opacity: 0.04,
                      padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 16),
                      child: const Center(
                        child: Text(
                          'No recent scans yet.\nEnter or share a URL above to inspect.',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.white38, fontSize: 13),
                        ),
                      ),
                    )
                  else
                    ListView.separated(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: scanState.recentScans.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 10),
                      itemBuilder: (context, index) {
                        final item = scanState.recentScans[index];
                        final isDangerous = item.overall.verdict == 'DANGEROUS';
                        final isSuspicious = item.overall.verdict == 'SUSPICIOUS';
                        final color = isDangerous
                            ? Colors.redAccent
                            : (isSuspicious ? Colors.orangeAccent : const Color(0xFF34D399));

                        return GlassContainer(
                          opacity: 0.06,
                          borderRadius: BorderRadius.circular(16),
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                          child: InkWell(
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => ResultScreen(scan: item),
                                ),
                              );
                            },
                            child: Row(
                              children: [
                                Container(
                                  width: 38,
                                  height: 38,
                                  decoration: BoxDecoration(
                                    color: color.withOpacity(0.15),
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(color: color.withOpacity(0.3)),
                                  ),
                                  alignment: Alignment.center,
                                  child: Text(
                                    '${item.overall.score}',
                                    style: TextStyle(
                                      color: color,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        item.domain,
                                        style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 14),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        item.overall.label,
                                        style: TextStyle(color: color, fontSize: 11),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ],
                                  ),
                                ),
                                const Icon(Icons.chevron_right_rounded, color: Colors.white38),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
